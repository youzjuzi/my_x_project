import base64
import importlib
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class TwoStageDetector:
    def __init__(
        self,
        mode: str,
        source_module: str,
        hand_weights: str,
        target_weights: str,
        imgsz: int,
        hand_conf: float,
        target_conf: float,
        iou_thres: float,
        device_name: str,
        max_det: int,
        margin: int,
        jpeg_quality: int,
    ) -> None:
        module = importlib.import_module(source_module)
        yolo_stage = getattr(module, "YOLOStage")
        select_device = getattr(module, "select_device")

        self._helpers = {
            "clamp_box": getattr(module, "clamp_box"),
            "cv2": getattr(module, "cv2"),
            "draw_box": getattr(module, "draw_box"),
        }
        self.mode = mode
        self.device = select_device(device_name)
        self.hand_stage = yolo_stage(hand_weights, self.device, imgsz)
        self.target_stage = yolo_stage(target_weights, self.device, imgsz)
        self.hand_conf = hand_conf
        self.target_conf = target_conf
        self.iou_thres = iou_thres
        self.max_det = max_det
        self.margin = margin
        self.jpeg_quality = jpeg_quality

    def process_jpeg_bytes(self, payload: bytes) -> Dict[str, Any]:
        frame = self._decode_jpeg(payload)
        return self.process_frame(frame)

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        started = time.perf_counter()
        output = frame.copy()
        clamp_box = self._helpers["clamp_box"]
        draw_box = self._helpers["draw_box"]
        cv2 = self._helpers["cv2"]

        hand_det = self.hand_stage.infer(frame, self.hand_conf, self.iou_thres, self.max_det)
        hands: List[Dict[str, Any]] = []
        all_texts: List[str] = []

        for hand_index, (*hand_xyxy, hand_conf, _) in enumerate(hand_det.tolist(), start=1):
            hx1, hy1, hx2, hy2 = map(int, hand_xyxy)
            hx1 -= self.margin
            hy1 -= self.margin
            hx2 += self.margin
            hy2 += self.margin
            hx1, hy1, hx2, hy2 = clamp_box(hx1, hy1, hx2, hy2, frame.shape[1], frame.shape[0])
            if hx2 <= hx1 or hy2 <= hy1:
                continue

            hand_roi = frame[hy1:hy2, hx1:hx2]
            target_det = self.target_stage.infer(hand_roi, self.target_conf, self.iou_thres, self.max_det)
            draw_box(output, (hx1, hy1, hx2, hy2), "hand {0:.2f}".format(hand_conf), (0, 255, 0), thickness=2)

            detections: List[Dict[str, Any]] = []
            ordered_labels: List[Tuple[int, str]] = []
            for *target_xyxy, target_confidence, target_cls in target_det.tolist():
                dx1, dy1, dx2, dy2 = map(int, target_xyxy)
                gx1, gy1 = hx1 + dx1, hy1 + dy1
                gx2, gy2 = hx1 + dx2, hy1 + dy2
                label = str(self.target_stage.names[int(target_cls)])
                ordered_labels.append((gx1, label))
                detections.append(
                    {
                        "label": label,
                        "confidence": round(float(target_confidence), 4),
                        "box": [gx1, gy1, gx2, gy2],
                    }
                )
                draw_box(
                    output,
                    (gx1, gy1, gx2, gy2),
                    "{0} {1:.2f}".format(label, target_confidence),
                    (0, 165, 255),
                    thickness=2,
                )

            hand_text = ""
            if ordered_labels:
                ordered_labels.sort(key=lambda item: item[0])
                hand_text = "".join(item[1] for item in ordered_labels)
                all_texts.append(hand_text)
                cv2.putText(
                    output,
                    "{0}: {1}".format(self.mode, hand_text),
                    (hx1, min(frame.shape[0] - 10, hy2 + 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2,
                )

            hands.append(
                {
                    "handIndex": hand_index,
                    "confidence": round(float(hand_conf), 4),
                    "box": [hx1, hy1, hx2, hy2],
                    "text": hand_text,
                    "detections": detections,
                }
            )

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        encoded = self._encode_jpeg(output)
        combined_text = " | ".join(item for item in all_texts if item)
        return {
            "type": "result",
            "mode": self.mode,
            "latencyMs": latency_ms,
            "imageWidth": int(frame.shape[1]),
            "imageHeight": int(frame.shape[0]),
            "handCount": len(hands),
            "text": combined_text,
            "hands": hands,
            "annotatedFrame": "data:image/jpeg;base64,{0}".format(encoded),
        }

    def _decode_jpeg(self, payload: bytes) -> np.ndarray:
        cv2 = self._helpers["cv2"]
        array = np.frombuffer(payload, dtype=np.uint8)
        frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Unable to decode JPEG frame")
        return frame

    def _encode_jpeg(self, frame: np.ndarray) -> str:
        cv2 = self._helpers["cv2"]
        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
        if not ok:
            raise ValueError("Unable to encode annotated frame")
        return base64.b64encode(encoded.tobytes()).decode("ascii")


class DetectorRegistry:
    def __init__(self, device_name: str, jpeg_quality: int, model_settings: Dict[str, Dict[str, Any]]) -> None:
        self.device_name = device_name
        self.jpeg_quality = jpeg_quality
        self.model_settings = model_settings
        self.detectors: Dict[str, TwoStageDetector] = {}
        self.errors: Dict[str, str] = {}

    def get(self, mode: str) -> TwoStageDetector:
        normalized_mode = mode if mode in self.model_settings else "digits"
        if normalized_mode in self.detectors:
            return self.detectors[normalized_mode]
        if normalized_mode in self.errors:
            raise RuntimeError(self.errors[normalized_mode])

        settings = self.model_settings[normalized_mode]
        try:
            detector = TwoStageDetector(
                mode=normalized_mode,
                source_module=settings["source_module"],
                hand_weights=settings["hand_weights"],
                target_weights=settings["target_weights"],
                imgsz=settings["imgsz"],
                hand_conf=settings["hand_conf"],
                target_conf=settings["target_conf"],
                iou_thres=settings["iou_thres"],
                device_name=self.device_name,
                max_det=settings["max_det"],
                margin=settings["margin"],
                jpeg_quality=self.jpeg_quality,
            )
            self.detectors[normalized_mode] = detector
            return detector
        except Exception as exc:
            self.errors[normalized_mode] = str(exc)
            raise RuntimeError(self.errors[normalized_mode])

    def get_error(self, mode: str) -> Optional[str]:
        return self.errors.get(mode)
