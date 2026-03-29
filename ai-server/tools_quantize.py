"""
YOLOv5 ONNX 纯静态量化 (INT8) 工具
====================================
使用指定的本地图像数据集，对三个 FP32 ONNX 模型进行自动校准和量化。
输出的新模型包含 "_int8" 后缀，**绝对不会覆盖原文件**。

依赖:
pip install onnx onnxruntime
"""

import os
import sys
import cv2
import numpy as np
import onnxruntime
from pathlib import Path

# ======================================================
# 用户配置区
# ======================================================
CALIB_DIR = r"E:\Dataset\datasets\hands\new\valid\images"
MAX_CALIB_IMAGES = 100  # 使用多少张图片来提取特征分布（50~100张最普遍）

# ai-server 根目录
ROOT = Path(__file__).resolve().parent

# 需要被量化的三个模型路径
MODELS_TO_QUANTIZE = [
    ROOT / "runs/hand_detect_yolov5s_b32/weights/best.onnx",
    ROOT / "runs/digits_detect_yolov5b64/weights/best.onnx",
    ROOT / "runs/letters_detect_yolov5m_v12/weights/best.onnx"
]
# ======================================================

# 为了直接复用 YOLOv5 官方的预处理逻辑，我们把 yolov5 utils 加入环境变量
sys.path.append(str(ROOT))
try:
    from utils.augmentations import letterbox
except ImportError:
    print("❌ 无法导入 YOLOv5 的 letterbox，请确保你在 ai-server 目录下运行此脚本。")
    sys.exit(1)

# 确保安装了 onnx
try:
    from onnxruntime.quantization import quantize_static, CalibrationDataReader, QuantType, QuantFormat
except ImportError:
    print("❌ 缺少 onnxruntime，请运行: pip install onnx onnxruntime")
    sys.exit(1)


class YOLOCalibrationDataReader(CalibrationDataReader):
    """
    数据读取器：根据我们要喂给 ONNX 引擎的要求，把手部图片转为 1x3x640x640 的浮点张量矩阵。
    """
    def __init__(self, image_folder, input_name, model_size=(640, 640), max_examples=100):
        self.image_folder = image_folder
        self.input_name = input_name
        self.model_size = model_size
        self.max_examples = max_examples
        
        # 扫描并收集图片
        valid_exts = {".jpg", ".jpeg", ".png", ".bmp"}
        if not os.path.exists(image_folder):
            raise FileNotFoundError(f"找不到校准图片目录: {image_folder}")
            
        all_files = [
            f for f in os.listdir(image_folder) 
            if os.path.splitext(f)[-1].lower() in valid_exts
        ]
        if len(all_files) == 0:
            raise ValueError(f"目录 {image_folder} 内没有找到常见图片文件！")
            
        self.image_list = [os.path.join(image_folder, f) for f in all_files][:self.max_examples]
        self.enum_data = iter(self.image_list)
        print(f"   ✓ 成功从 {image_folder} 加载了 {len(self.image_list)} 张校准图片。")

    def get_next(self):
        try:
            img_path = next(self.enum_data)
        except StopIteration:
            return None
            
        img = cv2.imread(img_path)
        if img is None:
            return self.get_next()  # 如果这张图损坏了，直接跳过看下一张
            
        # 完完全全复刻实际推理过程中的处理步骤！
        # 1. Resize and Pad
        img, _, _ = letterbox(img, self.model_size, auto=False)
        # 2. BGR to RGB, HWC to CHW
        img = img.transpose((2, 0, 1))[::-1]
        img = np.ascontiguousarray(img).astype(np.float32)
        # 3. 归一化 (0-255 -> 0.0-1.0)
        img /= 255.0
        # 4. 增加 batch size 维度 [1, 3, 640, 640]
        img = np.expand_dims(img, axis=0)
        
        return {self.input_name: img}


def quantize_yolo(onnx_path, img_dir, max_examples=100):
    if not os.path.exists(onnx_path):
        print(f"\n⚠️ 找不到模型文件跳过: {onnx_path}")
        return
        
    out_path = str(onnx_path).replace(".onnx", "_int8.onnx")
    if os.path.exists(out_path):
        print(f"\n⚡ 发现目标 INT8 模型已存在，跳过: {out_path}")
        return
        
    print(f"\n======================================")
    print(f"🚀 开始静态量化模型: {Path(onnx_path).name}")
    print(f"======================================")
    
    # 获取 ONNX 第一个输入节点的名字（YOLOv5 通常叫 "images" 或 "input"）
    sess = onnxruntime.InferenceSession(str(onnx_path), providers=['CPUExecutionProvider'])
    input_name = sess.get_inputs()[0].name
    
    # 实例化我们的专属阅卷官（读取器）
    data_reader = YOLOCalibrationDataReader(
        image_folder=img_dir,
        input_name=input_name,
        max_examples=max_examples
    )
    
    print(f"   ⏳ 正在压榨并缩减权重与层（约耗时 1~3 分钟，请耐心等待）...")
    
    # 执行静态量化核心命令
    try:
        quantize_static(
            model_input=str(onnx_path),
            model_output=out_path,
            calibration_data_reader=data_reader,
            quant_format=QuantFormat.QOperator,  # QOperator格式最适配没有专业NPU的传统 CPU
            op_types_to_quantize=['Conv', 'MatMul', 'Add', 'Mul'],  # 将最消耗CPU寿命的层替换掉
            per_channel=False,                   # 对于 x86 CPU，关掉逐通道量化反而速度更快
            weight_type=QuantType.QInt8,         # 权重设为 有符号8位 （非常小）
            activation_type=QuantType.QUInt8     # 激活层设为 无符号8位 （更适合卷积计算）
        )
        
        size_mb_old = os.path.getsize(onnx_path) / (1024*1024)
        size_mb_new = os.path.getsize(out_path) / (1024*1024)
        
        print(f"\n   🎉 量化圆满完成！")
        print(f"   💾 原模型大小   : {size_mb_old:.2f} MB")
        print(f"   📦 INT8新模型大小: {size_mb_new:.2f} MB (缩小至原先的 {size_mb_new/size_mb_old*100:.1f}%)")
        print(f"   📂 新模型路径   : {out_path}")
        print(f"   （放心，绝没有覆盖您的旧 {Path(onnx_path).name}！）")
        
    except Exception as e:
        print(f"\n❌ 量化 {Path(onnx_path).name} 时出现极其严重的错误:")
        print(e)

if __name__ == "__main__":
    print(f"🔥 初始化环境，开始 YOLOv5 的终极手术...\n")
    for pt_path in MODELS_TO_QUANTIZE:
        quantize_yolo(str(pt_path), CALIB_DIR, max_examples=MAX_CALIB_IMAGES)
    
    print(f"\n✅ 所有模型处理完毕。如果生成成功，请去 ai-server/.env 中把它改成带 _int8 的名字来享受速度吧！")
