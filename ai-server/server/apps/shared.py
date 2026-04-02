from typing import Dict, Optional, Set

from aiortc import RTCPeerConnection

from .. import config
from ..detector import DetectorRegistry
from ..strategies.pq_hybrid_detector import PQHybridDetector

MODEL_SETTINGS = {
    "digits": {
        "source_module": "server.yolo_stage",
        "hand_weights": config.HAND_WEIGHTS,
        "target_weights": config.DIGIT_WEIGHTS,
        "imgsz": config.IMGSZ,
        "hand_conf": config.HAND_CONF,
        "target_conf": config.DIGIT_CONF,
        "iou_thres": config.IOU_THRES,
        "max_det": config.MAX_DET,
        "margin": config.MARGIN,
    },
}


class SharedAppResources:
    def __init__(self) -> None:
        self.registry = DetectorRegistry(
            device_name=config.DEVICE,
            jpeg_quality=config.JPEG_QUALITY,
            model_settings=MODEL_SETTINGS,
        )
        self.peer_connections: Set[RTCPeerConnection] = set()
        self._pq_detector = None
        self._pq_detector_error: Optional[str] = None

    def get_pq_detector(self):
        if self._pq_detector is not None:
            return self._pq_detector
        if self._pq_detector_error is not None:
            raise RuntimeError(self._pq_detector_error)

        try:
            self._pq_detector = PQHybridDetector(
                hand_weights=config.HAND_WEIGHTS,
                letters_weights=config.LETTER_WEIGHTS,
                mediapipe_model_path=config.MEDIAPIPE_TASK,
                imgsz=config.IMGSZ,
                hand_conf=config.HAND_CONF,
                letters_conf=config.LETTER_CONF,
                iou_thres=config.IOU_THRES,
                device_name=config.DEVICE,
                max_det=config.MAX_DET,
                margin=config.MARGIN,
                jpeg_quality=config.JPEG_QUALITY,
                pq_exit_grace_seconds=config.PQ_EXIT_GRACE_SECONDS,
                mn_exit_grace_seconds=config.MN_EXIT_GRACE_SECONDS,
                ij_dz_exit_grace_seconds=config.IJ_DZ_EXIT_GRACE_SECONDS,
            )
            return self._pq_detector
        except Exception as exc:
            self._pq_detector_error = str(exc)
            raise RuntimeError(self._pq_detector_error) from exc

    def get_detector(self, mode: str):
        if mode == "letters":
            return self.get_pq_detector()
        return self.registry.get("digits")

    def health_payload(self) -> Dict[str, object]:
        errors = [self.registry.get_error(mode) for mode in MODEL_SETTINGS]
        errors = [item for item in errors if item]
        if self._pq_detector_error:
            errors.append(self._pq_detector_error)
        if errors:
            return {"status": "error", "detail": errors[0], "connections": len(self.peer_connections)}
        return {"status": "ok", "detail": "ready", "connections": len(self.peer_connections)}


shared_resources = SharedAppResources()
