"""内置帮助面板 — 完整功能说明与示例（中英双语切换）"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton,
    QTreeWidget, QTreeWidgetItem, QSplitter, QComboBox, QLabel,
)
from PyQt6.QtCore import Qt

# ============================================================
# 中文帮助 HTML
# ============================================================
HELP_HTML_ZH = """
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body { font-family: "Microsoft YaHei UI", sans-serif; font-size: 13px;
       color: #ccc; background: #1e1e1e; padding: 20px; line-height: 1.7; }
h1 { color: #569cd6; border-bottom: 2px solid #569cd6; padding-bottom: 6px; }
h2 { color: #4ec9b0; margin-top: 28px; border-bottom: 1px solid #444; padding-bottom: 4px; }
h3 { color: #dcdcaa; margin-top: 20px; }
code { background: #333; color: #ce9178; padding: 2px 6px; border-radius: 3px; font-size: 12px; }
pre { background: #252526; color: #d4d4d4; padding: 12px; border-radius: 6px;
      border: 1px solid #3c3c3c; overflow-x: auto; font-size: 12px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; }
th { background: #333; color: #569cd6; padding: 8px 12px; text-align: left;
     border: 1px solid #444; }
td { padding: 6px 12px; border: 1px solid #444; }
tr:hover { background: #2a2a2a; }
.warn { color: #d16969; font-weight: bold; }
.tip { color: #4ec9b0; }
a { color: #569cd6; text-decoration: none; }
</style></head><body>

<h1>🎛 信号分析工具箱 v2.1 — 完整指南</h1>
<p>本工具集成了<strong>信号生成、时域分析、频域变换、滤波器设计、DSP 运算</strong>和<strong>实时音频</strong>功能，适用于信号与系统、数字信号处理课程学习与工程实验。</p>

<h2 id="overview">一、界面布局</h2>
<table>
<tr><th>区域</th><th>位置</th><th>说明</th></tr>
<tr><td>活动栏</td><td>最左侧</td><td>图标按钮切换功能面板：Time / FFT / Lap / Filt / DSP / Mic / File / Help</td></tr>
<tr><td>信号浏览器</td><td>左侧面板</td><td>树形列表（可勾选）管理所有信号、搜索、生成器表单</td></tr>
<tr><td>中央标签页</td><td>中央区域</td><td>各分析面板的绘图与控件区域</td></tr>
<tr><td>状态栏</td><td>底部</td><td>当前信号名称、数量、坐标信息</td></tr>
</table>

<h3>鼠标交互</h3>
<table>
<tr><th>操作</th><th>效果</th></tr>
<tr><td>鼠标悬停</td><td>状态栏显示当前坐标 (x, y)</td></tr>
<tr><td>滚轮上下</td><td>以光标为中心缩放图形（避免信号移出视野）</td></tr>
<tr><td>右键/中键拖动</td><td>平移图形，拖动信号到视野中央</td></tr>
<tr><td>双击左键</td><td>还原到缩放前视图</td></tr>
</table>

<h3>勾选机制</h3>
<table>
<tr><th>操作</th><th>效果</th></tr>
<tr><td>勾选复选框</td><td>该信号参与所有分析和显示</td></tr>
<tr><td>取消所有勾选</td><td>所有面板清空，不显示任何数据</td></tr>
<tr><td>全选/全不选按钮</td><td>快速切换所有信号的勾选状态</td></tr>
</table>

<h2 id="signal">二、信号生成与管理 (Sig)</h2>

<h3>2.1 内置信号类型（19 种）</h3>
<table>
<tr><th>类型</th><th>说明</th><th>关键参数</th></tr>
<tr><td>正弦 sin</td><td>单频正弦波 y = A·sin(2πft)</td><td>频率、幅值</td></tr>
<tr><td>余弦 cos</td><td>单频余弦波 y = A·cos(2πft)</td><td>频率、幅值</td></tr>
<tr><td>方波 square</td><td>方波信号</td><td>频率、幅值、占空比</td></tr>
<tr><td>锯齿波 sawtooth</td><td>锯齿波信号</td><td>频率、幅值</td></tr>
<tr><td>三角波 triangle</td><td>对称三角波</td><td>频率、幅值</td></tr>
<tr><td>线性调频 chirp</td><td>频率线性变化的扫频信号</td><td>起始频率、终止频率=10×freq</td></tr>
<tr><td>冲激 δ(t)</td><td>单位冲激函数</td><td>—</td></tr>
<tr><td>阶跃 u(t)</td><td>单位阶跃函数</td><td>—</td></tr>
<tr><td>高斯脉冲</td><td>高斯包络脉冲</td><td>—</td></tr>
<tr><td>sinc 脉冲</td><td>sinc 函数脉冲</td><td>截止频率</td></tr>
<tr><td>指数衰减</td><td>e^(−t/τ) 指数衰减</td><td>—</td></tr>
<tr><td>AM 调制</td><td>调幅信号 (1+m·sin(ωₘt))·cos(ω_c t)</td><td>调制频率、载波=10×freq</td></tr>
<tr><td>FM 调制</td><td>调频信号</td><td>调制频率、载波=10×freq</td></tr>
<tr><td>多频合成</td><td>多频正弦叠加</td><td>基频 + 3次 + 5次谐波</td></tr>
<tr><td>谐波级数</td><td>基频 + 5 次谐波（等比衰减）</td><td>基频</td></tr>
<tr><td>ECG 模拟</td><td>模拟心电信号 (P-QRS-T 波)</td><td>心率 BPM</td></tr>
<tr><td>白噪声</td><td>高斯白噪声</td><td>标准差</td></tr>
<tr><td>粉红噪声</td><td>1/f 粉红噪声</td><td>标准差</td></tr>
<tr><td>自定义表达式</td><td>任意数学表达式</td><td>见 2.2 节</td></tr>
</table>

<h3>2.2 自定义表达式语法</h3>
<table>
<tr><th>符号</th><th>含义</th><th>示例</th></tr>
<tr><td><code>t</code></td><td>时间变量（自动生成）</td><td><code>sin(2*pi*5*t)</code></td></tr>
<tr><td><code>pi</code></td><td>圆周率 π ≈ 3.14159</td><td><code>cos(pi*t)</code></td></tr>
<tr><td><code>sin(x)</code></td><td>正弦</td><td><code>sin(2*pi*10*t)</code></td></tr>
<tr><td><code>cos(x)</code></td><td>余弦</td><td><code>cos(2*pi*20*t)</code></td></tr>
<tr><td><code>tan(x)</code></td><td>正切</td><td><code>tan(pi*t/4)</code></td></tr>
<tr><td><code>exp(x)</code></td><td>e^x</td><td><code>exp(-2*t)</code></td></tr>
<tr><td><code>sqrt(x)</code></td><td>平方根</td><td><code>sqrt(t)</code></td></tr>
<tr><td><code>log(x)</code></td><td>自然对数 ln(x)</td><td><code>log(t+0.01)</code></td></tr>
<tr><td><code>abs(x)</code></td><td>绝对值</td><td><code>abs(sin(pi*t))</code></td></tr>
<tr><td><code>sinc(x)</code></td><td>sinc(x)=sin(πx)/(πx)</td><td><code>sinc(5*t)</code></td></tr>
<tr><td><code>sinh(x)</code></td><td>双曲正弦</td><td><code>sinh(2*t)</code></td></tr>
<tr><td><code>cosh(x)</code></td><td>双曲余弦</td><td><code>cosh(t)</code></td></tr>
</table>

<h4>表达式示例</h4>
<pre>sin(2*pi*5*t)                          ← 单一 5Hz 正弦波
sin(2*pi*10*t) * exp(-t)               ← 衰减正弦（阻尼振荡）
sin(2*pi*5*t) + sin(2*pi*50*t)         ← 两个正弦叠加
(1 + 0.8*sin(2*pi*2*t)) * sin(2*pi*50*t) ← AM 调幅
sin(2*pi*50*t + 5*sin(2*pi*3*t))       ← FM 调频
exp(-100*(t-1)**2)                     ← 高斯脉冲（t=1 处尖峰）
abs(sin(2*pi*5*t))                     ← 全波整流
(sin(2*pi*5*t) + abs(sin(2*pi*5*t))) / 2  ← 半波整流
exp(-((t-1)/0.3)**2) * sin(2*pi*30*t)  ← 高斯包络正弦
sin(2*pi*50*t) + 0.3*sin(2*pi*150*t)   ← 基波+3次谐波
sin(2*pi*5*t) + sin(2*pi*15*t)/3 + sin(2*pi*25*t)/5  ← 方波近似
sin(2*pi*5*t) - sin(2*pi*10*t)/2 + sin(2*pi*15*t)/3  ← 锯齿波近似
exp(-2*t)                              ← 指数衰减
log(t + 1)                             ← 对数增长
exp(-0.5*((t-1)/0.2)**2)              ← 高斯函数
t * exp(-5*t)                          ← 临界阻尼
exp(-t) - exp(-10*t)                   ← 过阻尼
sinc(10*(t-1))                         ← Sinc 脉冲</pre>

<h3>2.3 信号管理操作</h3>
<p><b>勾选框</b> — 勾选/取消勾选信号，控制图表中显示哪些信号<br>
<b>全选</b> — 勾选全部信号<br>
<b>全不选</b> — 取消全部勾选<br>
<b>删除</b> — 删除当前选中信号<br>
<b>清空</b> — 清除全部信号<br>
<b>复制</b> — 复制当前信号（含 "_copy" 后缀）<br>
<b>导出CSV</b> — 导出信号为 CSV 文件（时间,幅值 两列）<br>
<b>搜索框</b> — 输入关键词过滤信号树<br>
<b>菜单 → 导出图片</b> — 将当前面板图形导出为 PNG/SVG</p>

<h2 id="time">三、时域分析 (Time)</h2>

<h3>3.1 显示选项</h3>
<p><b>离散点</b> — 以 stem 图显示离散采样点<br>
<b>峰值检测</b> — 自动标注信号峰值</p>

<p>时域面板自动显示<strong>所有已勾选</strong>的信号（不同颜色），取消勾选则隐藏。</p>

<h3>3.2 信号测量指标</h3>
<table>
<tr><th>指标</th><th>含义</th><th>公式</th></tr>
<tr><td>最小值</td><td>最小幅值</td><td>min(y)</td></tr>
<tr><td>最大值</td><td>最大幅值</td><td>max(y)</td></tr>
<tr><td>均值</td><td>算术平均</td><td>1/N·Σy</td></tr>
<tr><td>标准差</td><td>离散程度</td><td>σ(y)</td></tr>
<tr><td>RMS</td><td>有效值</td><td>√(1/N·Σy²)</td></tr>
<tr><td>能量</td><td>信号总能量</td><td>Σy²·dt</td></tr>
<tr><td>峰峰值</td><td>最大−最小</td><td>max−min</td></tr>
<tr><td>时长</td><td>信号持续时间</td><td>t_last − t_first</td></tr>
</table>

<h3>操作示例</h3>
<pre>1. 在左侧生成"正弦 sin" 5Hz，幅值2，时长2s
2. 切换至 Time 面板 → 勾选该信号即可显示
3. 再生成"正弦 sin" 20Hz，幅值0.5（同时勾选）
4. 在 Time 面板可看到两信号叠加显示
5. 勾选"峰值检测"可看到自动标注的波峰</pre>

<h2 id="fft">四、傅里叶变换 (FFT)</h2>

<h3>4.1 分析方法一览</h3>
<table>
<tr><th>方法</th><th>应用场景</th><th>输出</th></tr>
<tr><td>FFT</td><td>快速傅里叶变换，适合分析周期信号频率成分</td><td>幅度谱 + 相位谱</td></tr>
<tr><td>DFT</td><td>N 点离散傅里叶变换（直接矩阵乘法）</td><td>幅度谱 + 相位谱</td></tr>
<tr><td>STFT 频谱图</td><td>短时傅里叶变换，显示频率随时间变化</td><td>时频谱热力图 (dB)</td></tr>
<tr><td>功率谱 PSD</td><td>功率谱密度估计 (periodogram / welch)</td><td>dB/Hz</td></tr>
<tr><td>倒谱 Cepstrum</td><td>倒谱分析，检测回波/谐波周期</td><td>Quefrency (s)</td></tr>
<tr><td>希尔伯特变换</td><td>提取包络、瞬时相位、瞬时频率</td><td>包络 + 相位 + 瞬时频率</td></tr>
<tr><td>小波变换 CWT</td><td>连续小波变换，时频分析</td><td>时频热力图</td></tr>
<tr><td>相干性</td><td>两信号频域相干系数 γ² (0~1)</td><td>γ² vs 频率</td></tr>
<tr><td>符号傅里叶</td><td>SymPy 符号推导傅里叶变换</td><td>公式结果弹窗</td></tr>
</table>

<h3>4.2 使用示例</h3>
<pre>FFT 峰值检测:
  1. 生成"多频合成"信号 (基频 50Hz)
  2. 切换至 FFT 面板
  3. 方法选"FFT"，窗选"hamming"，N=4096
  4. 点击"计算" → 幅度谱中可见 50/150/250Hz 三个峰值
  5. 点击"标峰" → 自动标注最高峰值频率

STFT 频谱图:
  1. 生成"线性调频 chirp"信号 (f0=5, f1=50)
  2. 方法选"STFT 频谱图"
  3. 点击"计算" → 可见频率从低到高的斜线

希尔伯特变换:
  1. 生成"AM 调制"信号 (载波500Hz, 调制50Hz)
  2. 方法选"希尔伯特变换"
  3. 第一行显示原始波形 + 包络线
  4. 第二行显示瞬时相位
  5. 第三行显示瞬时频率

符号傅里叶:
  1. 方法选"符号傅里叶"
  2. 输入 exp(-t) * Heaviside(t)
  3. 弹出结果: F(ω) = 1/(1 + jω)</pre>

<h3>4.3 窗函数选择建议</h3>
<table>
<tr><th>窗函数</th><th>特点</th><th>适用场景</th></tr>
<tr><td>none</td><td>矩形窗，主瓣最窄、旁瓣最高</td><td>整周期采样</td></tr>
<tr><td>hamming</td><td>通用，旁瓣衰减−43dB</td><td>一般频谱分析</td></tr>
<tr><td>hann</td><td>旁瓣−31.5dB，频率分辨率好</td><td>单频信号</td></tr>
<tr><td>blackman</td><td>旁瓣−58dB，低泄漏</td><td>高动态范围</td></tr>
<tr><td>flattop</td><td>平顶窗，幅值精度最高</td><td>精确测量幅值</td></tr>
<tr><td>kaiser</td><td>可调 β，灵活</td><td>需要自定义旁瓣</td></tr>
</table>

<h2 id="lap">五、拉普拉斯变换 (Lap)</h2>

<h3>5.1 功能说明</h3>
<table>
<tr><th>功能</th><th>说明</th><th>示例输入</th></tr>
<tr><td>正变换 f(t)→F(s)</td><td>SymPy 符号计算拉普拉斯正变换</td><td><code>sin(2*t)</code></td></tr>
<tr><td>逆变换 F(s)→f(t)</td><td>SymPy 符号计算拉普拉斯逆变换</td><td><code>1/(s**2 + 1)</code></td></tr>
<tr><td>传递函数 H(jω)</td><td>输入分子/分母系数，绘制 Bode 图 + 零极点图</td><td>分子 <code>1</code>, 分母 <code>1,1,1</code></td></tr>
</table>

<h3>5.2 使用示例</h3>
<pre>正变换:
  f(t) = sin(2*t)        →  F(s) = 2/(s² + 4)
  f(t) = exp(-3*t) * Heaviside(t)  →  F(s) = 1/(s + 3)
  f(t) = t * exp(-2*t)   →  F(s) = (s + 2)⁻²

逆变换:
  F(s) = 1/(s**2 + 1)    →  f(t) = sin(t)·θ(t)
  F(s) = 1/s             →  f(t) = θ(t)  (阶跃函数)
  F(s) = (s+1)/(s**2+4)  →  f(t) = cos(2t)+0.5·sin(2t)

传递函数分析:
  分子: 1      分母: 1, 2, 1    (表示 s² + 2s + 1 = (s+1)²)
  → 二阶临界阻尼系统
  → Bode 幅频: −40dB/dec 下降, −3dB 截止在 ω=1
  → 零极点图: s=−1 处二重极点(x), 无零点(o)</pre>

<h2 id="filt">六、滤波器设计 (Filt)</h2>

<h3>6.1 滤波器类型</h3>
<table>
<tr><th>类型</th><th>特点</th><th>参数</th></tr>
<tr><td>FIR-窗函数</td><td>线性相位，稳定，阶数较高</td><td>截止频率、阶数、窗类型</td></tr>
<tr><td>FIR-Remez</td><td>等波纹最优设计 (Parks-McClellan)</td><td>频带边界、期望增益、阶数</td></tr>
<tr><td>IIR-Butterworth</td><td>通带最平坦</td><td>截止频率、阶数</td></tr>
<tr><td>IIR-Chebyshev I</td><td>通带等波纹，陡峭过渡</td><td>截止、阶数、通带波纹 dB</td></tr>
<tr><td>IIR-Chebyshev II</td><td>阻带等波纹</td><td>截止、阶数、阻带衰减 dB</td></tr>
<tr><td>IIR-Elliptic</td><td>通带阻带均等波纹，最陡过渡</td><td>截止、阶数、波纹、阻带衰减</td></tr>
<tr><td>IIR-Bessel</td><td>最平坦群延迟（线性相位近似）</td><td>截止频率、阶数</td></tr>
<tr><td>IIR-Notch</td><td>陷波器，抑制特定频率</td><td>陷波频率、Q 值</td></tr>
<tr><td>IIR-Peak</td><td>峰值滤波器，增强特定频率</td><td>峰值频率、Q 值</td></tr>
</table>

<h3>6.2 四图说明</h3>
<p>设计滤波器后自动显示四个子图：<br>
<b>幅频响应</b> — |H(f)| (dB)，红色虚线为 −3dB 线<br>
<b>相频响应</b> — ∠H(f) (rad)<br>
<b>零极点图 (Z平面)</b> — ○零点 ×极点，虚线为单位圆<br>
<b>冲激响应</b> — h[n] 时域响应</p>

<h3>6.3 使用示例</h3>
<pre>低通滤波去除噪声:
  1. 生成"正弦 sin" 5Hz + 再生成"白噪声"
  2. 在 Time 面板勾选"叠加"可看到含噪波形
  3. 切换 Filt → 类型选"IIR-Butterworth"
  4. 通带选 lowpass，阶数 4，截止 30Hz
  5. 点击 Design → 查看四图
  6. 点击"应用滤波" → 信号列表多出 filtered 信号
  7. 回到 Time 面板对比原始和滤波后波形

零相位滤波:
  1. 同上设计滤波器
  2. 点击"零相位滤波" → 调用 filtfilt
  3. 零相位滤波不引入相位失真，适合离线处理

多滤波器对比:
  1. 依次设计 Butterworth 4阶、Chebyshev I 4阶
  2. 点击"多滤波器对比"
  3. 可直观比较两种滤波器的过渡带陡峭程度

50Hz 工频陷波:
  1. 类型选 IIR-Notch，截止 50Hz
  2. Design → 应用，可去除 50Hz 工频干扰

共振增强:
  1. 类型选 IIR-Peak，截止 100Hz
  2. 可增强信号中 100Hz 分量</pre>

<h2 id="dsp">七、DSP 频谱与运算 (DSP)</h2>

<h3>7.1 四象限频谱</h3>
<p>点击"计算频谱"后显示：<br>
<b>左上</b> — 时域波形（前 5000 点）<br>
<b>右上</b> — 幅度谱 (dB 或线性)<br>
<b>左下</b> — 相位谱<br>
<b>右下</b> — 功率谱 (对数坐标)</p>

<p>参数说明：<b>FFT N</b> — 点数越多频率分辨率越高；<b>窗</b> — 减少频谱泄漏；<b>dB</b> — 切换 dB/线性显示</p>

<h3>7.2 信号运算</h3>
<table>
<tr><th>运算</th><th>说明</th><th>公式</th></tr>
<tr><td>缩放</td><td>幅值缩放</td><td>y' = factor × y</td></tr>
<tr><td>求导</td><td>数值微分</td><td>y' = dy/dt</td></tr>
<tr><td>积分</td><td>累积积分</td><td>y' = ∫y dt</td></tr>
<tr><td>整流</td><td>全波整流</td><td>y' = |y|</td></tr>
<tr><td>半波整流</td><td>仅保留正值</td><td>y' = max(y, 0)</td></tr>
<tr><td>归一化</td><td>归一化到 ±1</td><td>y' = y / max(|y|)</td></tr>
<tr><td>卷积</td><td>两信号卷积</td><td>y' = y₁ ∗ y₂</td></tr>
<tr><td>互相关</td><td>两信号互相关</td><td>y' = y₁ ⋆ y₂</td></tr>
</table>

<h3>7.3 Z 变换</h3>
<p>点击"单位圆 Z 变换"沿单位圆 (|z|=1) 计算并显示 |H(e^{jω})| 和相位 ∠H(e^{jω})。</p>

<pre>DSP 操作示例:
  1. 生成"正弦 sin" 5Hz
  2. 切换 DSP 面板，点击"计算频谱"
  3. 四象限图显示时域/幅度谱/相位谱/功率谱
  4. 点击"求导" → 生成导数信号 cos(2πft)
  5. 点击"积分" → 生成积分信号
  6. 切换 FFT 面板查看运算前后频谱变化

卷积示例:
  1. 生成"冲激 δ(t)" 和 "正弦 sin" 5Hz
  2. 选中冲激信号，点击"卷积"
  3. 与 δ(t) 卷积 = 原信号

互相关示例:
  1. 生成两个相同频率的正弦
  2. 点击"互相关"
  3. 峰值位于 0 处表示两信号对齐</pre>

<h2 id="audio">八、实时音频 (Mic)</h2>
<p>使用麦克风录制 3 秒音频，自动生成信号并显示波形和频谱。</p>
<p><b>要求</b>：系统麦克风可用，采样率 44100Hz，单声道。</p>
<pre>操作步骤:
  1. 切换至 Mic 面板
  2. 点击"Rec 录制 3秒"
  3. 说话或播放声音
  4. 录制完成后自动显示波形(上)和频谱(下)
  5. 信号自动添加到列表，可在其他面板分析</pre>

<h2 id="import">九、文件导入 (File)</h2>
<table>
<tr><th>格式</th><th>说明</th><th>方法</th></tr>
<tr><td>CSV</td><td>逗号分隔文本（第1列时间，第2列幅值，跳过标题行）</td><td>numpy.loadtxt</td></tr>
<tr><td>WAV</td><td>WAV 音频文件（自动取第1声道）</td><td>scipy.io.wavfile</td></tr>
<tr><td>MAT</td><td>MATLAB .mat 文件（自动提取所有变量为独立信号）</td><td>scipy.io.loadmat</td></tr>
</table>

<h2 id="tips">十、技巧与建议</h2>
<table>
<tr><th>分析目标</th><th>推荐方法</th><th>面板</th></tr>
<tr><td>查看波形</td><td>时域分析</td><td>Time</td></tr>
<tr><td>找频率成分</td><td>FFT + 标峰</td><td>FFT</td></tr>
<tr><td>观察频率随时间变化</td><td>STFT / CWT</td><td>FFT</td></tr>
<tr><td>求包络/瞬时频率</td><td>希尔伯特变换</td><td>FFT</td></tr>
<tr><td>检测回波/基频</td><td>倒谱 Cepstrum</td><td>FFT</td></tr>
<tr><td>符号推导传递函数</td><td>拉普拉斯变换</td><td>Lap</td></tr>
<tr><td>评估系统稳定性</td><td>零极点图</td><td>Lap / Filt</td></tr>
<tr><td>设计抗混叠滤波器</td><td>Butterworth / Elliptic</td><td>Filt</td></tr>
<tr><td>去除工频干扰</td><td>IIR Notch 50Hz</td><td>Filt</td></tr>
<tr><td>信号相似度</td><td>相干性 / 互相关</td><td>FFT / DSP</td></tr>
<tr><td>音频分析</td><td>麦克风录制</td><td>Mic</td></tr>
<tr><td>精确幅值测量</td><td>FFT + flattop 窗</td><td>FFT</td></tr>
</table>

<h3>常见问题</h3>
<p><b class="warn">Q: 频谱中有泄漏/旁瓣？</b><br>
<span class="tip">A:</span> 使用 hamming 或 blackman 窗，增加信号时长。</p>

<p><b class="warn">Q: 滤波器设计失败？</b><br>
<span class="tip">A:</span> 检查截止频率是否 &lt; 采样率/2（Nyquist）；阶数勿超过信号长度。</p>

<p><b class="warn">Q: 拉普拉斯变换报错？</b><br>
<span class="tip">A:</span> 确保使用 Heaviside(t) 或 DiracDelta(t)。</p>

<p><b class="warn">Q: 麦克风无法录制？</b><br>
<span class="tip">A:</span> 确认 sounddevice 已安装，系统麦克风权限已开启。</p>

<br><hr>
<p style="text-align:center; color:#888;">
信号分析工具箱 v2.1 · PyQt6 + NumPy + SciPy + SymPy + Matplotlib
</p>
</body></html>
"""

# ============================================================
# English help HTML
# ============================================================
HELP_HTML_EN = """
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body { font-family: "Segoe UI", sans-serif; font-size: 13px;
       color: #ccc; background: #1e1e1e; padding: 20px; line-height: 1.7; }
h1 { color: #569cd6; border-bottom: 2px solid #569cd6; padding-bottom: 6px; }
h2 { color: #4ec9b0; margin-top: 28px; border-bottom: 1px solid #444; padding-bottom: 4px; }
h3 { color: #dcdcaa; margin-top: 20px; }
code { background: #333; color: #ce9178; padding: 2px 6px; border-radius: 3px; font-size: 12px; }
pre { background: #252526; color: #d4d4d4; padding: 12px; border-radius: 6px;
      border: 1px solid #3c3c3c; overflow-x: auto; font-size: 12px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; }
th { background: #333; color: #569cd6; padding: 8px 12px; text-align: left;
     border: 1px solid #444; }
td { padding: 6px 12px; border: 1px solid #444; }
tr:hover { background: #2a2a2a; }
.warn { color: #d16969; font-weight: bold; }
.tip { color: #4ec9b0; }
a { color: #569cd6; text-decoration: none; }
</style></head><body>

<h1>🎛 Signal Analyzer Toolbox v2.1 — Complete Guide</h1>
<p>Integrated <strong>Signal Generation, Time-Domain Analysis, Frequency-Domain Transforms, Filter Design, DSP Operations</strong> and <strong>Real-Time Audio</strong> — suitable for Signals &amp; Systems and DSP coursework and engineering experiments.</p>

<h2 id="overview">1. Interface Layout</h2>
<table>
<tr><th>Region</th><th>Position</th><th>Description</th></tr>
<tr><td>Activity Bar</td><td>Far left</td><td>Icon buttons to switch panels: Time / FFT / Lap / Filt / DSP / Mic / File / Help</td></tr>
<tr><td>Signal Explorer</td><td>Left panel</td><td>Tree list (checkable) managing all signals, search, generator form</td></tr>
<tr><td>Central Tabs</td><td>Center</td><td>Plot and control area for each analysis panel</td></tr>
<tr><td>Status Bar</td><td>Bottom</td><td>Current signal name, count, coordinate info</td></tr>
</table>

<h3>Mouse Interaction</h3>
<table>
<tr><th>Action</th><th>Effect</th></tr>
<tr><td>Hover</td><td>Show current coordinates (x, y) in status bar</td></tr>
<tr><td>Scroll wheel</td><td>Zoom in/out centered on cursor (signal stays visible)</td></tr>
<tr><td>Right/Middle drag</td><td>Pan the plot, drag signal back into view</td></tr>
<tr><td>Double-click left</td><td>Reset to pre-zoom view</td></tr>
</table>

<h3>Checkbox System</h3>
<table>
<tr><th>Action</th><th>Effect</th></tr>
<tr><td>Check a box</td><td>That signal participates in all analysis and display</td></tr>
<tr><td>Uncheck all</td><td>All panels clear — no data shown anywhere</td></tr>
<tr><td>Check / Uncheck All</td><td>Quickly toggle all signal checkboxes</td></tr>
</table>

<h2 id="signal">2. Signal Generation &amp; Management (Sig)</h2>

<h3>2.1 Built-in Signal Types (19 types)</h3>
<table>
<tr><th>Type</th><th>Description</th><th>Key Parameters</th></tr>
<tr><td>Sine</td><td>Single-frequency sine y = A·sin(2πft)</td><td>Frequency, amplitude</td></tr>
<tr><td>Cosine</td><td>Single-frequency cosine y = A·cos(2πft)</td><td>Frequency, amplitude</td></tr>
<tr><td>Square</td><td>Square wave</td><td>Frequency, amplitude, duty</td></tr>
<tr><td>Sawtooth</td><td>Sawtooth wave</td><td>Frequency, amplitude</td></tr>
<tr><td>Triangle</td><td>Symmetric triangle wave</td><td>Frequency, amplitude</td></tr>
<tr><td>Chirp</td><td>Linear frequency sweep</td><td>Start freq, end freq=10×freq</td></tr>
<tr><td>Impulse δ(t)</td><td>Unit impulse function</td><td>—</td></tr>
<tr><td>Step u(t)</td><td>Unit step function</td><td>—</td></tr>
<tr><td>Gaussian Pulse</td><td>Gaussian envelope pulse</td><td>—</td></tr>
<tr><td>Sinc Pulse</td><td>Sinc function pulse</td><td>Cutoff frequency</td></tr>
<tr><td>Exponential Decay</td><td>e^(−t/τ) decay</td><td>—</td></tr>
<tr><td>AM Modulation</td><td>Amplitude modulated signal</td><td>Modulator freq, carrier=10×freq</td></tr>
<tr><td>FM Modulation</td><td>Frequency modulated signal</td><td>Modulator freq, carrier=10×freq</td></tr>
<tr><td>Multi-tone</td><td>Multiple sine superposition</td><td>Fundamental + 3rd + 5th harmonics</td></tr>
<tr><td>Harmonic Series</td><td>Fundamental + 5 harmonics (geometric decay)</td><td>Fundamental frequency</td></tr>
<tr><td>ECG Simulation</td><td>Simulated ECG (P-QRS-T waves)</td><td>Heart rate BPM</td></tr>
<tr><td>White Noise</td><td>Gaussian white noise</td><td>Standard deviation</td></tr>
<tr><td>Pink Noise</td><td>1/f pink noise</td><td>Standard deviation</td></tr>
<tr><td>Custom Expression</td><td>Any mathematical expression</td><td>See section 2.2</td></tr>
</table>

<h3>2.2 Custom Expression Syntax</h3>
<table>
<tr><th>Symbol</th><th>Meaning</th><th>Example</th></tr>
<tr><td><code>t</code></td><td>Time variable (auto-generated)</td><td><code>sin(2*pi*5*t)</code></td></tr>
<tr><td><code>pi</code></td><td>π ≈ 3.14159</td><td><code>cos(pi*t)</code></td></tr>
<tr><td><code>sin(x)</code></td><td>Sine</td><td><code>sin(2*pi*10*t)</code></td></tr>
<tr><td><code>cos(x)</code></td><td>Cosine</td><td><code>cos(2*pi*20*t)</code></td></tr>
<tr><td><code>tan(x)</code></td><td>Tangent</td><td><code>tan(pi*t/4)</code></td></tr>
<tr><td><code>exp(x)</code></td><td>e^x</td><td><code>exp(-2*t)</code></td></tr>
<tr><td><code>sqrt(x)</code></td><td>Square root</td><td><code>sqrt(t)</code></td></tr>
<tr><td><code>log(x)</code></td><td>Natural log ln(x)</td><td><code>log(t+0.01)</code></td></tr>
<tr><td><code>abs(x)</code></td><td>Absolute value</td><td><code>abs(sin(pi*t))</code></td></tr>
<tr><td><code>sinc(x)</code></td><td>sinc(x)=sin(πx)/(πx)</td><td><code>sinc(5*t)</code></td></tr>
<tr><td><code>sinh(x)</code></td><td>Hyperbolic sine</td><td><code>sinh(2*t)</code></td></tr>
<tr><td><code>cosh(x)</code></td><td>Hyperbolic cosine</td><td><code>cosh(t)</code></td></tr>
</table>

<h4>Expression Examples</h4>
<pre>sin(2*pi*5*t)                          ← Single 5Hz sine wave
sin(2*pi*10*t) * exp(-t)               ← Damped sine (decaying oscillation)
sin(2*pi*5*t) + sin(2*pi*50*t)         ← Two-tone superposition
(1 + 0.8*sin(2*pi*2*t)) * sin(2*pi*50*t) ← AM modulation
sin(2*pi*50*t + 5*sin(2*pi*3*t))       ← FM modulation
exp(-100*(t-1)**2)                     ← Gaussian pulse (peak at t=1)
abs(sin(2*pi*5*t))                     ← Full-wave rectification
(sin(2*pi*5*t) + abs(sin(2*pi*5*t))) / 2  ← Half-wave rectification
exp(-((t-1)/0.3)**2) * sin(2*pi*30*t)  ← Gaussian-enveloped sine
sin(2*pi*50*t) + 0.3*sin(2*pi*150*t)   ← Fundamental + 3rd harmonic
sin(2*pi*5*t) + sin(2*pi*15*t)/3 + sin(2*pi*25*t)/5  ← Square wave approx.
sin(2*pi*5*t) - sin(2*pi*10*t)/2 + sin(2*pi*15*t)/3  ← Sawtooth approx.
exp(-2*t)                              ← Exponential decay
log(t + 1)                             ← Logarithmic growth
exp(-0.5*((t-1)/0.2)**2)              ← Gaussian function
t * exp(-5*t)                          ← Critically damped
exp(-t) - exp(-10*t)                   ← Overdamped
sinc(10*(t-1))                         ← Sinc pulse</pre>

<h3>2.3 Signal Management</h3>
<p><b>Checkbox</b> — Check/uncheck signals to control which are displayed<br>
<b>Select All</b> — Check all signals<br>
<b>Deselect All</b> — Uncheck all signals<br>
<b>Delete</b> — Remove selected signal<br>
<b>Clear</b> — Remove all signals<br>
<b>Copy</b> — Duplicate selected signal (with "_copy" suffix)<br>
<b>Export CSV</b> — Export signal as a CSV file (time, amplitude)<br>
<b>Search box</b> — Filter signals by keyword<br>
<b>Menu → Export Image</b> — Export current panel figure as PNG/SVG</p>

<h2 id="time">3. Time-Domain Analysis (Time)</h2>

<h3>3.1 Display Options</h3>
<p><b>Discrete</b> — Display as stem plot for discrete samples<br>
<b>Peak Detection</b> — Auto-annotate signal peaks</p>

<p>The time panel automatically shows <strong>all checked</strong> signals (different colors). Uncheck to hide.</p>

<h3>3.2 Signal Measurements</h3>
<table>
<tr><th>Metric</th><th>Meaning</th><th>Formula</th></tr>
<tr><td>Min</td><td>Minimum amplitude</td><td>min(y)</td></tr>
<tr><td>Max</td><td>Maximum amplitude</td><td>max(y)</td></tr>
<tr><td>Mean</td><td>Arithmetic mean</td><td>1/N·Σy</td></tr>
<tr><td>Std</td><td>Standard deviation</td><td>σ(y)</td></tr>
<tr><td>RMS</td><td>Root mean square</td><td>√(1/N·Σy²)</td></tr>
<tr><td>Energy</td><td>Total signal energy</td><td>Σy²·dt</td></tr>
<tr><td>Peak-to-Peak</td><td>Max − Min</td><td>max−min</td></tr>
<tr><td>Duration</td><td>Signal duration</td><td>t_last − t_first</td></tr>
</table>

<h3>Example</h3>
<pre>1. Generate "Sine" 5Hz, amplitude 2, duration 2s
2. Switch to Time panel → ensure it's checked
3. Generate another "Sine" 20Hz, amplitude 0.5 (both checked)
4. Time panel shows both signals overlaid
5. Check "Peak Detection" to see auto-annotated peaks</pre>

<h2 id="fft">4. Fourier Transform (FFT)</h2>

<h3>4.1 Analysis Methods</h3>
<table>
<tr><th>Method</th><th>Use Case</th><th>Output</th></tr>
<tr><td>FFT</td><td>Fast Fourier Transform for periodic signal frequency analysis</td><td>Magnitude + Phase spectrum</td></tr>
<tr><td>DFT</td><td>N-point DFT (direct matrix multiplication)</td><td>Magnitude + Phase</td></tr>
<tr><td>STFT Spectrogram</td><td>Short-time FT, shows frequency over time</td><td>Time-freq heatmap (dB)</td></tr>
<tr><td>PSD</td><td>Power spectral density (periodogram / welch)</td><td>dB/Hz</td></tr>
<tr><td>Cepstrum</td><td>Cepstral analysis, detect echoes/harmonic periods</td><td>Quefrency (s)</td></tr>
<tr><td>Hilbert Transform</td><td>Envelope, instantaneous phase &amp; frequency</td><td>Envelope + Phase + Inst. Freq</td></tr>
<tr><td>CWT</td><td>Continuous Wavelet Transform, time-frequency analysis</td><td>Time-scale heatmap</td></tr>
<tr><td>Coherence</td><td>Frequency-domain coherence γ² (0~1) between two signals</td><td>γ² vs Freq</td></tr>
<tr><td>Symbolic Fourier</td><td>SymPy symbolic Fourier transform derivation</td><td>Formula popup</td></tr>
</table>

<h3>4.2 Examples</h3>
<pre>FFT Peak Detection:
  1. Generate "Multi-tone" signal (fundamental 50Hz)
  2. Switch to FFT panel
  3. Method: "FFT", Window: "hamming", N=4096
  4. Click "Compute" → 50/150/250Hz peaks visible
  5. Click "Annotate Peaks" → auto-annotate peak frequencies

STFT Spectrogram:
  1. Generate "Chirp" signal (f0=5, f1=50)
  2. Method: "STFT Spectrogram"
  3. Click "Compute" → diagonal line from low to high freq

Hilbert Transform:
  1. Generate "AM Modulation" (carrier 500Hz, modulator 50Hz)
  2. Method: "Hilbert Transform"
  3. Row 1: original waveform + envelope
  4. Row 2: instantaneous phase
  5. Row 3: instantaneous frequency

Symbolic Fourier:
  1. Method: "Symbolic Fourier"
  2. Enter: exp(-t) * Heaviside(t)
  3. Result: F(ω) = 1/(1 + jω)</pre>

<h3>4.3 Window Selection Guide</h3>
<table>
<tr><th>Window</th><th>Characteristics</th><th>Best For</th></tr>
<tr><td>none</td><td>Rectangular, narrowest main lobe, highest sidelobes</td><td>Integer-period sampling</td></tr>
<tr><td>hamming</td><td>General-purpose, −43dB sidelobes</td><td>General spectrum analysis</td></tr>
<tr><td>hann</td><td>−31.5dB sidelobes, good frequency resolution</td><td>Single-frequency signals</td></tr>
<tr><td>blackman</td><td>−58dB sidelobes, low leakage</td><td>High dynamic range</td></tr>
<tr><td>flattop</td><td>Flat top, best amplitude accuracy</td><td>Precise amplitude measurement</td></tr>
<tr><td>kaiser</td><td>Adjustable β, flexible</td><td>Custom sidelobe requirements</td></tr>
</table>

<h2 id="lap">5. Laplace Transform (Lap)</h2>

<h3>5.1 Functions</h3>
<table>
<tr><th>Function</th><th>Description</th><th>Example Input</th></tr>
<tr><td>Forward f(t)→F(s)</td><td>SymPy symbolic Laplace forward transform</td><td><code>sin(2*t)</code></td></tr>
<tr><td>Inverse F(s)→f(t)</td><td>SymPy symbolic Laplace inverse transform</td><td><code>1/(s**2 + 1)</code></td></tr>
<tr><td>Transfer Function H(jω)</td><td>Numerator/denominator coeffs, Bode + pole-zero plots</td><td>Num <code>1</code>, Den <code>1,1,1</code></td></tr>
</table>

<h3>5.2 Examples</h3>
<pre>Forward:
  f(t) = sin(2*t)        →  F(s) = 2/(s² + 4)
  f(t) = exp(-3*t) * Heaviside(t)  →  F(s) = 1/(s + 3)

Inverse:
  F(s) = 1/(s**2 + 1)    →  f(t) = sin(t)·θ(t)
  F(s) = 1/s             →  f(t) = θ(t)  (unit step)

Transfer Function:
  Numerator: 1    Denominator: 1, 2, 1    (s² + 2s + 1 = (s+1)²)
  → Second-order critically damped system
  → Bode magnitude: −40dB/dec rolloff, −3dB at ω=1
  → Pole-zero: double pole(x) at s=−1, no zeros(o)</pre>

<h2 id="filt">6. Filter Design (Filt)</h2>

<h3>6.1 Filter Types</h3>
<table>
<tr><th>Type</th><th>Characteristics</th><th>Parameters</th></tr>
<tr><td>FIR Window</td><td>Linear phase, stable, higher order</td><td>Cutoff, order, window type</td></tr>
<tr><td>FIR Remez</td><td>Equiripple optimal (Parks-McClellan)</td><td>Band edges, desired gain, order</td></tr>
<tr><td>IIR Butterworth</td><td>Maximally flat passband</td><td>Cutoff, order</td></tr>
<tr><td>IIR Chebyshev I</td><td>Equiripple passband, steep transition</td><td>Cutoff, order, passband ripple dB</td></tr>
<tr><td>IIR Chebyshev II</td><td>Equiripple stopband</td><td>Cutoff, order, stopband attenuation dB</td></tr>
<tr><td>IIR Elliptic</td><td>Equiripple both bands, steepest transition</td><td>Cutoff, order, ripple, stop attenuation</td></tr>
<tr><td>IIR Bessel</td><td>Maximally flat group delay (approx linear phase)</td><td>Cutoff, order</td></tr>
<tr><td>IIR Notch</td><td>Band-reject filter, suppresses one frequency</td><td>Notch frequency, Q factor</td></tr>
<tr><td>IIR Peak</td><td>Band-pass peak filter, boosts one frequency</td><td>Peak frequency, Q factor</td></tr>
</table>

<h3>6.2 Four-Plot Display</h3>
<p>Upon designing a filter, four subplots are shown:<br>
<b>Magnitude Response</b> — |H(f)| (dB), red dashed line at −3dB<br>
<b>Phase Response</b> — ∠H(f) (rad)<br>
<b>Pole-Zero Plot (Z-plane)</b> — ○zeros ×poles, dashed unit circle<br>
<b>Impulse Response</b> — h[n] time domain</p>

<h3>6.3 Examples</h3>
<pre>Low-pass Denoising:
  1. Generate "Sine" 5Hz + "White Noise"
  2. Time panel → Check "Overlay" to see noisy waveform
  3. Switch to Filt → Type: "IIR-Butterworth"
  4. Passband: lowpass, Order: 4, Cutoff: 30Hz
  5. Click "Design" → view four plots
  6. Click "Apply Filter" → filtered signal added to list
  7. Back to Time panel to compare

Zero-Phase Filtering:
  1. Design a filter as above
  2. Click "Zero-Phase Filtering" → uses filtfilt
  3. No phase distortion, ideal for offline processing

Multi-Filter Comparison:
  1. Design Butterworth 4th-order, then Chebyshev I 4th-order
  2. Click "Compare Filters"
  3. Visually compare transition band steepness

50Hz Power Line Notch:
  1. Type: IIR-Notch, Cutoff: 50Hz
  2. Design → Apply, removes 50Hz mains hum

Resonance Enhancement:
  1. Type: IIR-Peak, Cutoff: 100Hz
  2. Boosts 100Hz component</pre>

<h2 id="dsp">7. DSP Spectrum &amp; Operations (DSP)</h2>

<h3>7.1 Four-Quadrant Spectrum</h3>
<p>Click "Compute Spectrum" to view:<br>
<b>Top-left</b> — Time domain (first 5000 points)<br>
<b>Top-right</b> — Magnitude spectrum (dB or linear)<br>
<b>Bottom-left</b> — Phase spectrum<br>
<b>Bottom-right</b> — Power spectrum (log scale)</p>

<h3>7.2 Signal Operations</h3>
<table>
<tr><th>Operation</th><th>Description</th><th>Formula</th></tr>
<tr><td>Scale</td><td>Amplitude scaling</td><td>y' = factor × y</td></tr>
<tr><td>Diff</td><td>Numerical derivative</td><td>y' = dy/dt</td></tr>
<tr><td>Int</td><td>Cumulative integral</td><td>y' = ∫y dt</td></tr>
<tr><td>Rectify</td><td>Full-wave rectification</td><td>y' = |y|</td></tr>
<tr><td>Half-Rectify</td><td>Keep only positive values</td><td>y' = max(y, 0)</td></tr>
<tr><td>Normalize</td><td>Normalize to ±1</td><td>y' = y / max(|y|)</td></tr>
<tr><td>Convolve</td><td>Convolution of two signals</td><td>y' = y₁ ∗ y₂</td></tr>
<tr><td>Cross-Correlate</td><td>Cross-correlation of two signals</td><td>y' = y₁ ⋆ y₂</td></tr>
</table>

<h3>7.3 Z-Transform</h3>
<p>Click "Unit Circle Z-Transform" to compute and display |H(e^{jω})| and ∠H(e^{jω}) along the unit circle (|z|=1).</p>

<pre>DSP Examples:
  1. Generate "Sine" 5Hz
  2. Switch to DSP, click "Compute Spectrum"
  3. Four-quadrant view: time/magnitude/phase/power
  4. Click "Diff" → derivative signal cos(2πft)
  5. Click "Int" → integral signal
  6. Switch to FFT panel to compare spectra

Convolution Example:
  1. Generate "Impulse δ(t)" and "Sine" 5Hz
  2. Select impulse, click "Convolve"
  3. Convolution with δ(t) = original signal

Cross-Correlation Example:
  1. Generate two same-frequency sines
  2. Click "Cross-Correlate"
  3. Peak at 0 indicates aligned signals</pre>

<h2 id="audio">8. Real-Time Audio (Mic)</h2>
<p>Record 3 seconds of audio from microphone, auto-generate signal with waveform and spectrum.</p>
<p><b>Requirements</b>: system microphone available, 44100Hz sample rate, mono.</p>
<pre>Steps:
  1. Switch to Mic panel
  2. Click "Rec Record 3s"
  3. Speak or play sound
  4. Waveform (top) and spectrum (bottom) displayed automatically
  5. Signal added to list for further analysis</pre>

<h2 id="import">9. File Import (File)</h2>
<table>
<tr><th>Format</th><th>Description</th><th>Method</th></tr>
<tr><td>CSV</td><td>Comma-separated (col 1=time, col 2=amplitude, header skipped)</td><td>numpy.loadtxt</td></tr>
<tr><td>WAV</td><td>WAV audio file (auto-selects channel 1)</td><td>scipy.io.wavfile</td></tr>
<tr><td>MAT</td><td>MATLAB .mat file (extracts all variables as separate signals)</td><td>scipy.io.loadmat</td></tr>
</table>

<h2 id="tips">10. Tips &amp; Recommendations</h2>
<table>
<tr><th>Goal</th><th>Recommended Method</th><th>Panel</th></tr>
<tr><td>View waveform</td><td>Time-domain analysis</td><td>Time</td></tr>
<tr><td>Find frequency components</td><td>FFT + peak annotation</td><td>FFT</td></tr>
<tr><td>Frequency vs. time</td><td>STFT / CWT</td><td>FFT</td></tr>
<tr><td>Envelope / instantaneous frequency</td><td>Hilbert Transform</td><td>FFT</td></tr>
<tr><td>Detect echoes / fundamental</td><td>Cepstrum</td><td>FFT</td></tr>
<tr><td>Symbolic transfer function</td><td>Laplace Transform</td><td>Lap</td></tr>
<tr><td>System stability</td><td>Pole-Zero Plot</td><td>Lap / Filt</td></tr>
<tr><td>Anti-aliasing filter</td><td>Butterworth / Elliptic</td><td>Filt</td></tr>
<tr><td>Remove mains hum</td><td>IIR Notch 50Hz</td><td>Filt</td></tr>
<tr><td>Signal similarity</td><td>Coherence / Cross-Correlation</td><td>FFT / DSP</td></tr>
<tr><td>Audio analysis</td><td>Microphone recording</td><td>Mic</td></tr>
<tr><td>Precise amplitude</td><td>FFT + flattop window</td><td>FFT</td></tr>
</table>

<h3>FAQ</h3>
<p><b class="warn">Q: Spectral leakage / sidelobes?</b><br>
<span class="tip">A:</span> Use hamming or blackman window, increase signal duration.</p>

<p><b class="warn">Q: Filter design fails?</b><br>
<span class="tip">A:</span> Check cutoff &lt; fs/2 (Nyquist); order should not exceed signal length.</p>

<p><b class="warn">Q: Laplace transform error?</b><br>
<span class="tip">A:</span> Use Heaviside(t) or DiracDelta(t) explicitly.</p>

<p><b class="warn">Q: Microphone not recording?</b><br>
<span class="tip">A:</span> Verify sounddevice is installed and microphone permissions granted.</p>

<br><hr>
<p style="text-align:center; color:#888;">
Signal Analyzer Toolbox v2.1 · PyQt6 + NumPy + SciPy + SymPy + Matplotlib
</p>
</body></html>
"""

# ============================================================
# 语言-内容映射
# ============================================================
_LANG_HTML = {"zh": HELP_HTML_ZH, "en": HELP_HTML_EN}

# 各语言的导航标题
_LANG_NAV = {
    "zh": {
        "界面布局": "overview",
        "信号生成与管理": "signal",
        "时域分析": "time",
        "傅里叶变换 (FFT)": "fft",
        "拉普拉斯变换 (Lap)": "lap",
        "滤波器设计 (Filt)": "filt",
        "DSP 频谱与运算": "dsp",
        "实时音频 (Mic)": "audio",
        "文件导入 (File)": "import",
        "技巧与建议": "tips",
    },
    "en": {
        "Interface Layout": "overview",
        "Signal Generation & Mgmt": "signal",
        "Time-Domain Analysis": "time",
        "Fourier Transform (FFT)": "fft",
        "Laplace Transform (Lap)": "lap",
        "Filter Design (Filt)": "filt",
        "DSP Spectrum & Ops": "dsp",
        "Real-Time Audio (Mic)": "audio",
        "File Import (File)": "import",
        "Tips & Recommendations": "tips",
    },
}


class HelpPanel(QWidget):
    """内置帮助浏览器 — 支持中英双语切换"""

    def __init__(self):
        super().__init__()
        self._current_lang = "zh"
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 顶部工具栏：语言切换
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(8, 6, 8, 4)
        toolbar.addStretch()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["中文", "English"])
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        self.lang_combo.setFixedWidth(100)
        self.lang_combo.setStyleSheet(
            "QComboBox { background: #3c3c3c; color: #ccc; border: 1px solid #555;"
            " border-radius: 4px; padding: 4px 8px; }"
        )
        toolbar.addWidget(QLabel("语言 / Language:"))
        toolbar.addWidget(self.lang_combo)
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧导航树
        self.nav = QTreeWidget()
        self.nav.setHeaderHidden(True)
        self.nav.setFixedWidth(200)
        self.nav.setStyleSheet(
            "QTreeWidget { background: #252526; border-right: 1px solid #3c3c3c; }"
            "QTreeWidget::item { padding: 4px 8px; }"
        )
        self.nav.itemClicked.connect(self._on_nav_click)
        self._build_nav()

        # 右侧内容区
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setHtml(HELP_HTML_ZH)
        self.browser.anchorClicked.connect(self._on_anchor_click)

        splitter.addWidget(self.nav)
        splitter.addWidget(self.browser)
        splitter.setSizes([200, 1000])

        layout.addWidget(splitter)

    def _build_nav(self):
        """按当前语言重建导航树"""
        self.nav.clear()
        for title, anchor in _LANG_NAV[self._current_lang].items():
            item = QTreeWidgetItem([title])
            item.setData(0, Qt.ItemDataRole.UserRole, anchor)
            self.nav.addTopLevelItem(item)

    def _on_lang_changed(self, idx):
        """语言切换"""
        self._current_lang = "en" if idx == 1 else "zh"
        self._build_nav()
        self.browser.setHtml(_LANG_HTML[self._current_lang])

    def _on_nav_click(self, item):
        anchor = item.data(0, Qt.ItemDataRole.UserRole)
        if anchor:
            self.browser.scrollToAnchor(anchor)

    def _on_anchor_click(self, url):
        anchor = url.toString()
        self.browser.scrollToAnchor(anchor)
