# Python 识别端答辩代码导览

> 目标：答辩时快速说明 Python AI 识别端的代码结构。  
> 原则：只讲项目核心链路，不深入 YOLOv5 官方源码细节。

## 1. 先分清三类代码

### A. 项目核心代码，必须会讲

这些文件是本项目真正的 AI 服务业务逻辑：

```text
ai-server/main.py
ai-server/server/app.py
ai-server/server/apps/factory.py
ai-server/server/webrtc/
ai-server/server/scenes/
ai-server/server/detector.py
ai-server/server/yolo_stage.py
ai-server/server/strategies/
ai-server/server/config.py
```

答辩时主要围绕这些文件讲。

### B. YOLOv5 基础工程代码，知道来源即可

这些主要是 YOLOv5 原项目结构或训练、验证、导出相关代码：

```text
ai-server/models/
ai-server/utils/
ai-server/train.py
ai-server/val.py
ai-server/detect.py
ai-server/export.py
ai-server/hubconf.py
```

答辩时不用逐行解释。可以说：

> 这部分主要来自 YOLOv5 工程基础代码，我在项目中主要复用了其模型加载、预处理、NMS 和推理能力，并在 `server/yolo_stage.py` 中做了封装。

### C. 测试、调试、历史辅助代码，简单带过

```text
ai-server/test/
ai-server/mediapipe/
ai-server/tools_quantize.py
ai-server/server/static/
```

这些用于模型测试、手势规则调试、量化实验或本地调试页面，不是答辩主线。

## 2. 答辩主流程

可以按下面这条线讲 Python 识别端：

```text
main.py
  启动 FastAPI 服务

server/app.py
  挂载 recognition / practice / challenge 三个场景

server/apps/factory.py
  提供 /webrtc/offer 接口，建立 WebRTC 连接

server/webrtc/tracks.py
  接收浏览器摄像头视频帧

server/webrtc/runtime.py
  循环取最新帧，调用识别器推理

server/yolo_stage.py
  封装 YOLOv5 模型加载、预处理、NMS 和坐标还原

server/detector.py
  数字识别：手部检测 + 数字检测的两阶段流程

server/strategies/pq_hybrid_detector.py
  字母识别：YOLOv5 初筛 + MediaPipe 辅助判断

server/scenes/recognition_session.py
  多帧投票、拼写缓存、拼音候选、功能手势处理

DataChannel
  将 JSON 识别结果实时返回前端
```

## 3. 核心文件怎么讲

### `main.py`

作用：AI 服务启动入口。

重点：

- 读取 `server/config.py` 中的端口和主机配置。
- 使用 `uvicorn.run("server.app:app", ...)` 启动 FastAPI。

### `server/app.py`

作用：统一 FastAPI 入口。

重点：

- `/recognition`：实时识别场景。
- `/practice`：跟练场景。
- `/challenge`：闯关挑战场景。
- 三个场景复用同一套 WebRTC 建连和推理机制。

### `server/apps/factory.py`

作用：创建每个识别场景的 FastAPI 子应用。

重点：

- `/webrtc/offer` 接收前端 SDP offer。
- 创建 `RTCPeerConnection`。
- 注册 DataChannel、视频 track 事件。
- 启动 `run_inference_loop` 推理任务。
- 返回 WebRTC answer 给前端。

### `server/webrtc/runtime.py`

作用：实时推理主循环。

重点：

- 从 session 中取最新视频帧。
- CPU 模式下做限帧和降分辨率。
- 根据当前模式选择数字、字母或命令手势识别。
- 推理完成后构造结果，并通过 DataChannel 发回前端。

### `server/yolo_stage.py`

作用：把 YOLOv5 推理封装成一个简单类。

重点：

- `DetectMultiBackend` 加载 `.pt` 权重。
- `letterbox` 做图像缩放填充。
- `non_max_suppression` 去除重复框。
- `scale_boxes` 把检测框还原到原始图像坐标。

### `server/detector.py`

作用：数字识别的两阶段检测。

重点：

- 第一阶段：用手部检测模型定位手部。
- 第二阶段：裁剪手部 ROI，在 ROI 内识别数字。
- 这样可以减少背景干扰，提高识别稳定性。

### `server/strategies/pq_hybrid_detector.py`

作用：字母识别核心。

重点：

- 普通字母主要由 YOLOv5 识别。
- 对 P/Q、M/N/T、I/J、D/Z、F 等易混字母，使用 MediaPipe 手部 21 个关键点辅助判断。
- 动态字母通过轨迹缓存和多帧投票稳定输出。

### `server/strategies/hand_command.py`

作用：双手功能手势识别。

重点：

- 双手张开：确认。
- 双手食指向下：删除。
- 双手握拳：清空。
- 双手食指向上：下一个候选。
- 双手拇指向上：提交。
- 每个命令都有计数阈值，避免误触发。

### `server/scenes/recognition_session.py`

作用：实时识别场景的状态管理。

重点：

- 多帧投票，避免单帧误识别。
- 缓存稳定字母，形成拼音输入。
- 拼音转中文候选。
- 处理确认、删除、清空、下一个、提交等命令。

## 4. 老师可能问的问题

### Q1：为什么目录里有这么多 Python 文件？

答：

> 因为识别端复用了 YOLOv5 的基础工程结构，包括模型、工具函数、训练和验证脚本。真正和系统业务强相关的代码集中在 `server` 目录下，主要包括 WebRTC 通信、模型推理封装、识别策略和场景状态管理。

### Q2：YOLOv5 源码你改了吗？

答：

> 没有大规模改 YOLOv5 源码，主要是复用其模型加载、图像预处理和 NMS 推理流程。我在 `server/yolo_stage.py` 中做了封装，使业务代码可以直接调用 `infer` 方法完成推理。

### Q3：为什么要分 `recognition`、`practice`、`challenge`？

答：

> 三个场景的底层识别链路相同，但业务语义不同。实时识别需要拼音缓存和候选词，跟练需要稳定匹配目标字符，挑战需要计时计分和题目推进，所以拆成不同 session 类，便于复用底层识别能力，同时保持业务逻辑清晰。

### Q4：MediaPipe 和 YOLOv5 是什么关系？

答：

> YOLOv5 负责主要的手部和手势检测，MediaPipe 负责补充关键点信息。对于静态且区分度高的手势，YOLOv5 可以直接识别；对于 P/Q、M/N/T、I/J、D/Z 等容易混淆或带动态特征的字母，使用 MediaPipe 的 21 个手部关键点做规则判断和轨迹分析。

### Q5：怎么减少误识别？

答：

> 系统没有直接采用单帧结果，而是使用多帧投票、稳定时间、命令阈值和动作抑制机制。只有连续多帧结果稳定后才进入缓存或触发命令，从而降低抖动和偶然误识别带来的影响。

## 5. 答辩时建议打开的文件顺序

如果老师让你现场讲 Python 代码，按这个顺序打开：

1. `ai-server/main.py`
2. `ai-server/server/app.py`
3. `ai-server/server/apps/factory.py`
4. `ai-server/server/webrtc/runtime.py`
5. `ai-server/server/yolo_stage.py`
6. `ai-server/server/detector.py`
7. `ai-server/server/strategies/pq_hybrid_detector.py`
8. `ai-server/server/strategies/hand_command.py`
9. `ai-server/server/scenes/recognition_session.py`

不要从 `models/` 或 `utils/` 开始讲，否则会陷进 YOLOv5 底层实现。

