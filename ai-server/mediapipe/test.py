import matplotlib.pyplot as plt
import numpy as np

# 该脚本用于生成论文中的动态字母轨迹示意图。
# 说明：这里绘制的是示意轨迹，而非实时采样结果。

# 设置学术论文常用的字体风格
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 1. 生成 30 帧的动态字母示意轨迹
# J 在当前系统实现中主要依据 20 号点（小指指尖）动态轨迹进行判别
# Z 在当前系统实现中主要依据 8 号点（食指指尖）动态轨迹进行判别
frames = np.arange(1, 31)

# === 模拟 J 字手语动作轨迹（20号点） ===
# J 字以纵向轨迹变化为主，并伴有轻微横向摆动
y_j = 0.22 + 0.48 * np.power((frames - 18) / 12, 2)
x_j = 0.52 + 0.03 * np.sin(frames / 4.5)

# === 模拟 Z 字手语动作轨迹（8号点） ===
# Z 字以横向折线运动为主，同时伴随阶段性纵向变化
x_z = np.array(
    [0.26 if f <= 8 else 0.26 + 0.42 * (f - 8) / 8 if f <= 16 else 0.68 - 0.34 * (f - 16) / 14 for f in frames]
)
y_z = np.array(
    [0.22 if f <= 10 else 0.22 + 0.42 * (f - 10) / 10 if f <= 20 else 0.64 for f in frames]
)

# 2. 开始绘图：创建 1x2 拼图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

# === 图 (a) 垂直方向时序轨迹 ===
ax1.plot(frames, y_j, color="#d62728", label='Gesture "J" (Point 20)', linewidth=2.5, linestyle="-")
ax1.plot(frames, y_z, color="#1f77b4", label='Gesture "Z" (Point 8)', linewidth=2.5, linestyle="--")

ax1.set_title("(a) 垂直方向时序轨迹", fontsize=13, fontproperties="SimSun")
ax1.set_xlabel("帧号", fontsize=12, fontproperties="SimSun")
ax1.set_ylabel("归一化 Y 坐标", fontsize=12, fontproperties="SimSun")
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.set_xlim(1, 30)
ax1.set_ylim(0, 1)
ax1.invert_yaxis()  # MediaPipe Y轴原点在上方
ax1.legend(loc="upper right", fontsize=10)

# === 图 (b) 水平方向时序轨迹 ===
ax2.plot(frames, x_j, color="#d62728", label='Gesture "J" (Point 20)', linewidth=2.5, linestyle="-")
ax2.plot(frames, x_z, color="#1f77b4", label='Gesture "Z" (Point 8)', linewidth=2.5, linestyle="--")

ax2.set_title("(b) 水平方向时序轨迹", fontsize=13, fontproperties="SimSun")
ax2.set_xlabel("帧号", fontsize=12, fontproperties="SimSun")
ax2.set_ylabel("归一化 X 坐标", fontsize=12, fontproperties="SimSun")
ax2.grid(True, linestyle=":", alpha=0.6)
ax2.set_xlim(1, 30)
ax2.set_ylim(0, 1)
ax2.legend(loc="upper right", fontsize=10)

# 3. 整体标题与排版
plt.tight_layout()
plt.subplots_adjust(top=0.86)

# 4. 保存为高质量图片
plt.savefig("figure_4_10_jz_trajectory.png", dpi=300, bbox_inches="tight")
plt.show()

print("图 4.10 生成成功，文件名为：figure_4_10_jz_trajectory.png")
