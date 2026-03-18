import argparse
import sys
from pathlib import Path

import torch

AI_SERVER_ROOT = Path("/home/youzilite/IdeaProjects/my_x_project/ai-server")
if str(AI_SERVER_ROOT) not in sys.path:
    sys.path.append(str(AI_SERVER_ROOT))

from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.general import check_img_size, cv2, non_max_suppression, scale_boxes
from utils.torch_utils import select_device


def parse_args():
    parser = argparse.ArgumentParser(description="Two-stage webcam inference: hand -> letters")
    parser.add_argument(
        "--hand-weights",
        type=str,
        default=str(AI_SERVER_ROOT / "runs/hand_detect_yolov5s_b32/weights/best.pt"),
        help="hand detector weights",
    )
    parser.add_argument(
        "--letters-weights",
        type=str,
        default=str(AI_SERVER_ROOT / "runs/letters_detect_yolov5m_v12/weights/best.pt"),
        help="letters detector weights",
    )
    parser.add_argument("--source", type=str, default="0", help="camera index or video path")
    parser.add_argument("--imgsz", type=int, default=640, help="inference size")
    parser.add_argument("--hand-conf", type=float, default=0.25, help="hand confidence threshold")
    parser.add_argument("--letters-conf", type=float, default=0.25, help="letters confidence threshold")
    parser.add_argument("--iou-thres", type=float, default=0.45, help="NMS IoU threshold")
    parser.add_argument("--device", default="", help="cuda device, i.e. 0 or cpu")
    parser.add_argument("--view-scale", type=float, default=1.0, help="display scale")
    parser.add_argument("--max-det", type=int, default=100, help="max detections per stage")
    parser.add_argument("--margin", type=int, default=10, help="extra pixels around hand ROI")
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
    letters_stage = YOLOStage(args.letters_weights, device, args.imgsz)

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
            letter_det = letters_stage.infer(hand_roi, args.letters_conf, args.iou_thres, args.max_det)

            draw_box(output, (hx1, hy1, hx2, hy2), f"hand {hand_conf:.2f}", (0, 255, 0), thickness=2)

            letters_found = []
            for *letter_xyxy, letter_conf, letter_cls in letter_det.tolist():
                dx1, dy1, dx2, dy2 = map(int, letter_xyxy)
                gx1, gy1 = hx1 + dx1, hy1 + dy1
                gx2, gy2 = hx1 + dx2, hy1 + dy2
                letter_name = str(letters_stage.names[int(letter_cls)])
                letters_found.append((gx1, letter_name, letter_conf))
                draw_box(output, (gx1, gy1, gx2, gy2), f"{letter_name} {letter_conf:.2f}", (0, 165, 255), thickness=2)

            if letters_found:
                letters_found.sort(key=lambda item: item[0])
                letter_text = "".join(name for _, name, _ in letters_found)
                cv2.putText(
                    output,
                    f"letters: {letter_text}",
                    (hx1, min(frame.shape[0] - 10, hy2 + 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2,
                )

        if args.view_scale != 1.0:
            output = cv2.resize(output, None, fx=args.view_scale, fy=args.view_scale)

        cv2.imshow("hand_letters", output)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
