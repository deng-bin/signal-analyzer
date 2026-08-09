# 信号分析工具箱 v2.1 — Signal Analyzer Pro

> VS Code 风格界面的信号处理与分析平台

## 🚀 快速开始

```bash
# 安装依赖
uv sync

# 运行
uv run python main.py
```

## ✨ 核心功能

| 模块 | 功能 |
|------|------|
| **时域分析** | 多信号叠加显示、光标测量、缩放平移、峰值检测 |
| **FFT 频域** | FFT/DFT/STFT/功率谱/倒谱/希尔伯特/小波变换/相干性/符号傅里叶 |
| **拉普拉斯** | 正/逆符号变换、传递函数频率响应、零极点图 |
| **滤波器** | FIR(窗函数/Remez) + IIR(Butterworth/Chebyshev/Elliptic/Bessel/Notch/Peak) |
| **DSP 频谱** | 四象限频谱、信号运算(求导/积分/卷积/互相关)、Z 变换 |
| **音频** | 麦克风录制、实时播放、声谱图 |
| **文件导入** | CSV / WAV / MAT 导入导出 |

## 🎛️ 界面

- VS Code 风格暗色主题 + 活动栏
- 8 个分析标签页：Time / FFT / Lap / Filt / DSP / Mic / File / Help
- 信号勾选系统 — 仅已勾选的信号参与分析，全取消则清空所有面板
- 鼠标交互 — 滚轮缩放、右键/中键拖动平移、双击还原

## 📊 信号类型 (20+)

正弦、余弦、方波、锯齿波、三角波、线性调频、冲激、阶跃、高斯脉冲、sinc 脉冲、指数衰减、AM/FM 调制、多频合成、谐波级数、ECG 模拟、白噪声、粉红噪声、自定义表达式

## 🧪 测试

```bash
uv run pytest tests/ -v
```

## 🏗️ 架构

```
signal-analyzer/
├── main.py              # 主窗口入口
├── signal_engine.py      # 信号生成引擎
├── filter_engine.py      # FIR/IIR 滤波器引擎
├── transform_engine.py   # FFT/Laplace/Z/Wavelet 变换引擎
├── plot_canvas.py        # 交互式 matplotlib 画布
├── ui/
│   ├── theme.py          # 暗色主题
│   ├── activity_bar.py   # 活动栏
│   ├── logger.py         # AI 友好 JSON 日志
│   └── panels/           # 8 个分析面板
└── tests/                # 60 个单元测试
```
