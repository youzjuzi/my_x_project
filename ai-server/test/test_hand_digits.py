import argparse
import sys
import pathlib
from pathlib import Path

import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parent.parent  # ai-server root
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

DEFAULT_HAND_WEIGHTS = ROOT / "runs/hand_detect_yolov5s_b32/weights/best.pt"
DEFAULT_DIGIT_WEIGHTS = ROOT / "runs/digits_detect_yolov5b64/weights/best.pt"
DEFAULT_SOURCE = "0"
DEFAULT_IMGSZ = 640
DEFAULT_HAND_CONF = 0.25
DEFAULT_DIGIT_CONF = 0.25
DEFAULT_IOU_THRES = 0.45
DEFAULT_DEVICE = "cpu"
DEFAULT_VIEW_SCALE = 1.0
DEFAULT_MAX_DET = 100
DEFAULT_MARGIN = 10

if sys.platform.startswith("win"):
    pathlib.PosixPath = pathlib.WindowsPath

from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.general import check_img_size, cv2, non_max_suppression, scale_boxes
from utils.torch_utils import select_device


def parse_args():
    parser = argparse.ArgumentParser(description="Two-stage webcam inference: hand -> digits")
    parser.add_argument(
        "--hand-weights",
        type=str,
        default=str(DEFAULT_HAND_WEIGHTS),
        help="hand detector weights",
    )
    parser.add_argument(
        "--digit-weights",
        type=str,
        default=str(DEFAULT_DIGIT_WEIGHTS),
        help="digit detector weights",
    )
    parser.add_argument("--source", type=str, default=DEFAULT_SOURCE, help="camera index or video path")
    parser.add_argument("--imgsz", type=int, default=DEFAULT_IMGSZ, help="inference size")
    parser.add_argument("--hand-conf", type=float, default=DEFAULT_HAND_CONF, help="hand confidence threshold")
    parser.add_argument("--digit-conf", type=float, default=DEFAULT_DIGIT_CONF, help="digit confidence threshold")
    parser.add_argument("--iou-thres", type=float, default=DEFAULT_IOU_THRES, help="NMS IoU threshold")
    parser.add_argument("--device", default=DEFAULT_DEVICE, help="cuda device, i.e. 0 or cpu")
    parser.add_argument("--view-scale", type=float, default=DEFAULT_VIEW_SCALE, help="display scale")
    parser.add_argument("--max-det", type=int, default=DEFAULT_MAX_DET, help="max detections per stage")
    parser.add_argument("--margin", type=int, default=DEFAULT_MARGIN, help="extra pixels around hand ROI")
    return parser.parse_args()


class YOLOStage:
    def __init__(self, weights, device, imgsz):
        self.model = DetectMultiBackend(weights, device=device, fp16=False)
        self.device = device
        self.names = self.model.names
        self.stride = self.model.stride
        self.imgsz = check_img_size((imgsz, imgsz), s=self.stride)
        self.model.warmup(imgsz=(1, 3, *self.imgsz))

    def infer(self, image, conf_thres, iou_thres, max_det):
        processed, _, _ = letterbox(image, self.imgsz, stride=self.stride, auto=self.model.pt)
        processed = processed.transpose((2, 0, 1))[::-1]
        processed = torch.from_numpy(processed.copy()).to(self.device).float()
        processed /= 255.0
        processed = processed.unsqueeze(0)

        pred = self.model(processed)
        pred = non_max_suppression(pred, conf_thres, iou_thres, max_det=max_det)
        det = pred[0]
        if len(det):
            det[:, :4] = scale_boxes(processed.shape[2:], det[:, :4], image.shape).round()
        return det


def clamp_box(x1, y1, x2, y2, width, height):
    x1 = max(0, min(int(x1), width - 1))
    y1 = max(0, min(int(y1), height - 1))
    x2 = max(0, min(int(x2), width - 1))
    y2 = max(0, min(int(y2), height - 1))
    return x1, y1, x2, y2


def draw_box(image, xyxy, label, color, thickness=2):
    x1, y1, x2, y2 = map(int, xyxy)
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
    if label:
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        top = max(0, y1 - h - 8)
        cv2.rectangle(image, (x1, top), (x1 + w + 6, y1), color, -1)
        cv2.putText(image, label, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def main():
    args = parse_args()
    device = select_device(args.device)

    hand_stage = YOLOStage(args.hand_weights, device, args.imgsz)
    digit_stage = YOLOStage(args.digit_weights, device, args.imgsz)

    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open source: {args.source}")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        output = frame.copy()
        hand_det = hand_stage.infer(frame, args.hand_conf, args.iou_thres, args.max_det)

        for *hand_xyxy, hand_conf, _ in hand_det.tolist():
            hx1, hy1, hx2, hy2 = map(int, hand_xyxy)
            hx1 -= args.margin
            hy1 -= args.margin
            hx2 += args.margin
            hy2 += args.margin
            hx1, hy1, hx2, hy2 = clamp_box(hx1, hy1, hx2, hy2, frame.shape[1], frame.shape[0])
            if hx2 <= hx1 or hy2 <= hy1:
                continue

            hand_roi = frame[hy1:hy2, hx1:hx2]
            digit_det = digit_stage.infer(hand_roi, args.digit_conf, args.iou_thres, args.max_det)

            draw_box(output, (hx1, hy1, hx2, hy2), f"hand {hand_conf:.2f}", (0, 255, 0), thickness=2)

            digits_found = []
            for *digit_xyxy, digit_conf, digit_cls in digit_det.tolist():
                dx1, dy1, dx2, dy2 = map(int, digit_xyxy)
                gx1, gy1 = hx1 + dx1, hy1 + dy1
                gx2, gy2 = hx1 + dx2, hy1 + dy2
                digit_name = str(digit_stage.names[int(digit_cls)])
                digits_found.append((gx1, digit_name))
                draw_box(output, (gx1, gy1, gx2, gy2), f"{digit_name} {digit_conf:.2f}", (0, 165, 255), thickness=2)

            if digits_found:
                digits_found.sort(key=lambda item: item[0])
                digit_text = "".join(name for _, name in digits_found)
                cv2.putText(
                    output,
                    f"digits: {digit_text}",
                    (hx1, min(frame.shape[0] - 10, hy2 + 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2,
                )

        if args.view_scale != 1.0:
            output = cv2.resize(output, None, fx=args.view_scale, fy=args.view_scale)

        cv2.imshow("hand_digits", output)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
