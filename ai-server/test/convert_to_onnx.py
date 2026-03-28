import os
import subprocess
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent

MODELS = [
    ROOT / "runs/hand_detect_yolov5s_b32/weights/best.pt",
    ROOT / "runs/digits_detect_yolov5b64/weights/best.pt",
    ROOT / "runs/letters_detect_yolov5m_v12/weights/best.pt"
]

def convert_models():
    print("🚀 准备开始批量转换 YOLO 模型为 ONNX 格式 (适用于 CPU 推理提速)...")
    success_count = 0
    
    for pt_path in MODELS:
        if not pt_path.exists():
            print(f"⚠️ 找不到权重文件: {pt_path}")
            continue
            
        print(f"🔄 正在转换: {pt_path.name} ({pt_path.parent.parent.name})")
        # 直接调用底层的 export.py
        cmd = [
            "python", str(ROOT / "export.py"), 
            "--weights", str(pt_path), 
            "--include", "onnx", 
            "--simplify" # 简化计算图，加快推理
        ]
        
        try:
            # 运行命令，截获输出
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ {pt_path.name} 转换成功！生成在原位！\n")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ 转换 {pt_path.name} 失败: {e}")
            print("错误输出:\n", e.stderr)

    print(f"🎉 全部转换完毕！共成功转换 {success_count} 个模型。")

if __name__ == "__main__":
    convert_models()
