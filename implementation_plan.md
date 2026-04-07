# 手语识别核心三大问题 - 深度分析与修复方案

## 问题概览

经过全链路代码分析，你提到的三个问题有着明确的因果关系和技术根因。下面逐一拆解。

---

## 问题一：频繁误识别为 Q

### 根因分析

误识别为 Q 主要发生在 **两个阶段**，原因各不相同：

#### 1. YOLO 阶段：任意物体/非标手势被 YOLO 识别为 "Q"

> [!IMPORTANT]
> 这是最核心的问题。YOLO 字母模型（`letters_stage`）的 **置信度阈值太低**（`LETTER_CONF = 0.25`），导致它对各种非标手型、桌面物品、甚至手臂，都可能输出一个低置信度的 "Q"。

- 在 [config.py:54](file:///d:/code/my_x_project/ai-server/server/config.py#L54) 中，`LETTER_CONF = 0.25`，这意味着只要模型输出 25% 以上的置信度就会报告检测结果
- Q 的手势（拳头向下、食指向下弯曲）在 YOLO 的训练数据中可能与很多"半闭合"姿态重叠，导致 Q 变成了一个"兜底类别"
- 当场景中无明确手势时，YOLO 仍然有较高概率输出 Q

#### 2. MediaPipe 阶段（PQ hybrid detector）：uncertain 时 Q 仍被返回

在 [pq_hybrid_detector.py:130-140](file:///d:/code/my_x_project/ai-server/server/strategies/pq_hybrid_detector.py#L130-L140) 中：

```python
q_like = (not middle_ok) and index_down and thumb_down and thumb_open and tips_same_level
# ...
if p_like and not q_like:
    cls = "P"
elif q_like and not p_like:
    cls = "Q"
elif p_like and q_like:
    cls = "P"
else:
    cls = "uncertain"
```

Q 的判定条件比 P **宽松得多**：
- P 需要：中指伸直 `middle_ok` + 拇指在食指中指间 `p_seg_dist < 0.22`（很严格的空间约束）
- Q 需要：中指弯曲 `not middle_ok` + 食指向下 + 拇指向下 + 拇指张开 + 指尖高度差小

当手型模糊时（比如自然下垂的手），Q 的条件更容易被满足，因为核心判断 `index_down` 和 `thumb_down` 的阈值很宽：
- `TH_INDEX_DOWN_RATIO = 0.60` — 食指只要有一点向下就会触发
- `TH_THUMB_DOWN_RATIO = 0.35` — 拇指更宽松

#### 3. 投票稳定器的 "回退" 机制会放大 Q

在 [pq_hybrid_detector.py:186-192](file:///d:/code/my_x_project/ai-server/server/strategies/pq_hybrid_detector.py#L186-L192)：

```python
def stabilize_cls(history, vote_min=VOTE_MIN):
    if len(history) == 0:
        return "none"
    top_cls, top_count = Counter(history).most_common(1)[0]
    if top_count >= vote_min:
        return top_cls
    return history[-1]  # ← 问题在这里！
```

当投票窗口内没有任何类别达到 `VOTE_MIN=3` 时，**直接返回最新一帧的原始分类**。如果最新一帧恰好是 Q（很常见），就会直接输出 Q 而跳过稳定机制。

### 修复方案

#### 修改 1：提高 YOLO 字母置信度阈值
**文件**: [config.py](file:///d:/code/my_x_project/ai-server/server/config.py)

```diff
-LETTER_CONF = 0.25
+LETTER_CONF = 0.35
```

#### 修改 2：收紧 Q 的 MediaPipe 判定条件
**文件**: [pq_hybrid_detector.py](file:///d:/code/my_x_project/ai-server/server/strategies/pq_hybrid_detector.py)

```diff
-TH_Q_OPEN = 0.38
-TH_Q_TIP_Y_DIFF = 0.55
-TH_INDEX_DOWN_RATIO = 0.60
-TH_THUMB_DOWN_RATIO = 0.35
+TH_Q_OPEN = 0.45          # 拇指要更明显地张开
+TH_Q_TIP_Y_DIFF = 0.40    # 指尖高度差容忍度收紧
+TH_INDEX_DOWN_RATIO = 0.80 # 食指必须更明确地朝下
+TH_THUMB_DOWN_RATIO = 0.50 # 拇指也要更明确
```

#### 修改 3：投票稳定器不再 fallback 到最新帧
**文件**: [pq_hybrid_detector.py](file:///d:/code/my_x_project/ai-server/server/strategies/pq_hybrid_detector.py)

```diff
 def stabilize_cls(history, vote_min=VOTE_MIN):
     if len(history) == 0:
         return "none"
     top_cls, top_count = Counter(history).most_common(1)[0]
     if top_count >= vote_min:
         return top_cls
-    return history[-1]
+    # 没有达到投票阈值时，返回 uncertain 而非最后一帧的噪声值
+    return "uncertain"
```

---

## 问题二：总是进入命令模式 / 其他物品误识别为手势

### 根因分析

命令模式的激活依赖以下链条：

```
YOLO 手部检测 → handCount >= 2 → 激活命令模式
```

#### 关键问题 1：YOLO 手部检测器太敏感

- `HAND_CONF = 0.30`（[config.py:52](file:///d:/code/my_x_project/ai-server/server/config.py#L52)）—— 只要 30% 把握就认为是"手"
- **桌面上的物品**（杯子、遥控器、鼠标等）都可能被误检为"手"
- 当场景中有 1 只真手 + 1 个被误检的物品时，`handCount = 2`，就会触发命令模式

#### 关键问题 2：命令模式激活没有"确认等待期"

在 [runtime.py:96-99](file:///d:/code/my_x_project/ai-server/server/webrtc/runtime.py#L96-L99)：

```python
if session.allows_detector_command_mode() and session.can_activate_command_mode(hand_count):
    session.activate_command_mode()  # ← 一帧双手就立即激活！
```

只要 **单帧** YOLO 报告 `handCount >= 2`，立即激活命令模式。没有任何帧数缓冲或确认机制。

#### 关键问题 3：YOLO 字母检测在双手场景下的误识别

虽然 runtime.py 第 91-94 行已经有了处理：
```python
# 双手在画面中时，YOLOv5 的字符识别不可靠（常误识别为 Q），
# 清空 text 防止污染 vote_buffer
if hand_count >= 2:
    result["text"] = ""
```

但这只是清空了 text，**没有阻止命令模式被激活**。text 被清空后，系统认为没有字母识别结果，但 `handCount = 2` 仍然触发了命令模式。

### 修复方案

#### 修改 1：提高手部检测器置信度
**文件**: [config.py](file:///d:/code/my_x_project/ai-server/server/config.py)

```diff
-HAND_CONF = 0.30
+HAND_CONF = 0.40
```

#### 修改 2：命令模式激活添加"连续多帧确认"机制
**文件**: [base_session.py](file:///d:/code/my_x_project/ai-server/server/scenes/base_session.py)

在 `__init__` 中添加：
```python
# 命令模式激活需要连续多帧看到双手
self._command_activate_consecutive = 0
self._command_activate_threshold = 3  # 连续3帧才激活
```

修改 `can_activate_command_mode`：
```python
def can_activate_command_mode(self, hand_count: int) -> bool:
    self.update_command_reentry_gate(hand_count)
    if hand_count >= 2 and not self.command_reentry_requires_release:
        self._command_activate_consecutive += 1
        return self._command_activate_consecutive >= self._command_activate_threshold
    else:
        self._command_activate_consecutive = 0
        return False
```

#### 修改 3（可选）：在 PQHybridDetector 中过滤掉 YOLO 低置信度的双手
**文件**: [pq_hybrid_detector.py](file:///d:/code/my_x_project/ai-server/server/strategies/pq_hybrid_detector.py) 中的 `_run_yolo_letters`

可以在返回 `handCount` 时只计算**高置信度**的手：

```python
# 只有置信度 > 0.5 的手才计入 handCount（用于命令模式判断）
high_conf_hands = [h for h in hands if h["confidence"] > 0.5]
return {
    "handCount": len(high_conf_hands),  # 用于命令模式判定
    "hands": hands,                      # 全量手信息保留给字母识别
    "text": " | ".join(item for item in hand_texts if item),
}
```

---

## 问题三：命令模式识别完成后出现双手识别问题

### 根因分析

这个问题的时序是：

1. 用户双手做命令手势（如 CONFIRM）
2. 命令执行成功，`deactivate_command_mode()` 被调用
3. 用户开始收回双手 → 但此时画面中仍有双手
4. 在用户完全收手之前的那几帧：
   - YOLO 再次检测到 `handCount >= 2`
   - `can_activate_command_mode()` 被触发
   - **命令模式再次被错误激活**

#### `command_reentry_requires_release` 机制不够

虽然代码中有 [base_session.py:219-225](file:///d:/code/my_x_project/ai-server/server/scenes/base_session.py#L219-L225)：

```python
def update_command_reentry_gate(self, hand_count: int) -> None:
    if hand_count < 2:
        self.command_reentry_requires_release = False

def can_activate_command_mode(self, hand_count: int) -> bool:
    self.update_command_reentry_gate(hand_count)
    return hand_count >= 2 and not self.command_reentry_requires_release
```

这个机制要求用户先收手让 `handCount < 2`，然后才能重新进入命令模式。但问题是：

1. **YOLO 的 handCount 不稳定** — 双手收回过程中，可能跳变为 0/1/2
2. 如果 YOLO 在某一帧恰好报告 `handCount = 1`（比如一只手先离开画面），`command_reentry_requires_release` 立刻被设为 `False`
3. 下一帧如果 YOLO 又看到 2 只手（另一只手还没完全离开），命令模式就被重新激活了

#### `action_suppression` 只抑制了识别更新，没有抑制命令模式激活

在 [base_session.py:163-172](file:///d:/code/my_x_project/ai-server/server/scenes/base_session.py#L163-L172)：

```python
def _is_in_action_suppression(self) -> bool:
    # ...

def _start_action_suppression(self) -> None:
    self.action_suppression_until = time.perf_counter() + self.action_suppression_seconds
```

`action_suppression` 被 `recognition_session.py` 的 `update_display_state` 使用来忽略识别结果，但在 `runtime.py` 中，命令模式的激活判断 **完全没有检查 action_suppression**。

### 修复方案

#### 修改 1：在 action_suppression 期间禁止激活命令模式
**文件**: [base_session.py](file:///d:/code/my_x_project/ai-server/server/scenes/base_session.py)

```diff
 def can_activate_command_mode(self, hand_count: int) -> bool:
     self.update_command_reentry_gate(hand_count)
-    return hand_count >= 2 and not self.command_reentry_requires_release
+    if self._is_in_action_suppression():
+        return False
+    if hand_count >= 2 and not self.command_reentry_requires_release:
+        self._command_activate_consecutive += 1
+        return self._command_activate_consecutive >= self._command_activate_threshold
+    else:
+        self._command_activate_consecutive = 0
+        return False
```

#### 修改 2：增加 reentry gate 的去抖 — 需要连续多帧 < 2 才解锁
**文件**: [base_session.py](file:///d:/code/my_x_project/ai-server/server/scenes/base_session.py)

```python
# 在 __init__ 中：
self._reentry_release_consecutive = 0
self._reentry_release_threshold = 5  # 连续5帧看不到双手才解锁

# 修改 update_command_reentry_gate：
def update_command_reentry_gate(self, hand_count: int) -> None:
    if hand_count < 2:
        self._reentry_release_consecutive += 1
        if self._reentry_release_consecutive >= self._reentry_release_threshold:
            self.command_reentry_requires_release = False
    else:
        self._reentry_release_consecutive = 0
```

#### 修改 3：增加 action_suppression 的持续时间
**文件**: [base_session.py](file:///d:/code/my_x_project/ai-server/server/scenes/base_session.py)

当前 `action_suppression_seconds = 1.5`，可以适当增加到 `2.0` 秒，给用户充分的收手时间。

---

## 修改汇总

### 涉及文件

| 文件 | 修改内容 |
|------|---------|
| [config.py](file:///d:/code/my_x_project/ai-server/server/config.py) | 提高 HAND_CONF 和 LETTER_CONF |
| [pq_hybrid_detector.py](file:///d:/code/my_x_project/ai-server/server/strategies/pq_hybrid_detector.py) | 收紧 Q 阈值 + 修复 stabilize fallback |
| [base_session.py](file:///d:/code/my_x_project/ai-server/server/scenes/base_session.py) | 命令模式多帧确认 + reentry去抖 + suppression期间禁止激活 |

### 风险点

> [!WARNING]
> 1. 提高 `HAND_CONF` 和 `LETTER_CONF` 可能导致**距离较远**或**光线较暗**时的正常手势被漏检。建议先从 0.35/0.40 开始测试，如有问题再微调。
> 2. 收紧 Q 的 MediaPipe 阈值可能导致**真正的 Q 手势需要更标准**才能识别到。需要用户实际测试。
> 3. 命令模式增加 3 帧确认会引入大约 **100-200ms** 的延迟（取决于帧率），这在可接受范围内。

## Open Questions

> [!IMPORTANT]
> 1. 你目前的实际帧率大概是多少？这会影响"多帧确认"的阈值设定。如果帧率低（如 10fps），3帧 = 300ms，可以考虑降为 2 帧。
> 2. Q 的误识别是否主要发生在**正常拼写时**（比如比 A、B 等其他字母时被误报为 Q），还是在**手不做任何手势时**就会出现？这决定了修复重点在 YOLO 侧还是 MediaPipe 侧。
> 3. 命令模式退出后的"双手残留"问题，是否伴随错误的命令执行（比如重复 CONFIRM），还是只是 UI 上显示了命令模式但没有执行动作？

## 验证计划

### 自动化测试
- 修改代码后启动服务 `python main.py` 验证无启动报错
- 观察日志中 command_mode 激活和退出的时序

### 手动测试
1. **Q 误识别测试**: 不做任何手势 → 观察是否还出现 Q
2. **命令模式测试**: 桌面放置物品 → 观察是否误触发命令模式
3. **命令退出测试**: 执行 CONFIRM 命令后慢慢收手 → 观察是否重复进入命令模式
4. **正常识别回归测试**: 逐个做 P、Q、M、N、T、I、D、F 手势 → 确认准确率没有下降
