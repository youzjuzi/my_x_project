import torch
from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.general import check_img_size, cv2, non_max_suppression, scale_boxes
from utils.torch_utils import select_device

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
