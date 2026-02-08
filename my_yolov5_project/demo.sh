#!/usr/bin/env bash
# 测试图片
python demo.py --image_dir "data/test_image" --weights "data/model/yolov5s_640/weights/best.pt" --imgsz 640 --out_dir "runs/result"

# 测试视频文件
python demo.py --video_file "data/test-video.mp4" --weights "data/model/yolov5s_640/weights/best.pt" --imgsz 640 --out_dir "runs/result"

# 测试摄像头
python demo.py --weights "data/model/yolov5s05_320/weights/best.pt" --imgsz 640 --out_dir "runs/result"
python demo.py --video_file 0 --weights "runs/yolov5s05/weights/best.pt" --imgsz 640 --out_dir "runs/result"
