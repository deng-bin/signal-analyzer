"""交互式绘图画布 v2.0 — 光标测量、缩放平移、峰值检测"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor, SpanSelector
from PyQt6.QtCore import Qt


class InteractiveCanvas(FigureCanvas):
    """增强版 matplotlib 画布 — 内置游标、缩放平移、跨度选择"""
    def __init__(self, nrows=1, ncols=1, figsize=(8, 5), dpi=100, dark=True):
        self.dark_mode = dark
        self._setup_style()
        self.fig = Figure(figsize=figsize, dpi=dpi, tight_layout=True)
        self.axes_arr = self.fig.subplots(nrows, ncols, squeeze=False)
        self.axes = self.axes_arr.flatten()
        super().__init__(self.fig)
        self.cursors: list[Cursor] = []
        self.span_selectors: list[SpanSelector] = []
        self.annotations: list = []
        self._pan_start = None
        self._home_views = {}  # 保存各子图初始视图范围
        self._setup_cursor()
        self._connect_events()

    def _setup_style(self):
        if self.dark_mode:
            matplotlib.rcParams.update({
                'figure.facecolor': '#1e1e1e',
                'axes.facecolor': '#252526',
                'axes.edgecolor': '#555',
                'axes.labelcolor': '#cccccc',
                'text.color': '#cccccc',
                'xtick.color': '#999',
                'ytick.color': '#999',
                'grid.color': '#444',
                'grid.alpha': 0.5,
            })

    def _setup_cursor(self):
        for ax in self.axes:
            self.cursors.append(Cursor(ax, useblit=True, color='#888', linewidth=0.5, linestyle='--'))

    def _connect_events(self):
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.fig.canvas.mpl_connect('button_press_event', self._on_press)
        self.fig.canvas.mpl_connect('button_release_event', self._on_release)
        self.fig.canvas.mpl_connect('scroll_event', self._on_scroll)
        self._hover_annot = None
        self._pan_ax = None

    def _on_motion(self, event):
        """鼠标移动 — 悬停坐标 + 拖拽平移"""
        # 状态栏坐标
        if event.inaxes and hasattr(self, '_status_cb') and self._status_cb:
            self._status_cb(f"x={event.xdata:.4f}, y={event.ydata:.4f}")
        # 平移
        if self._pan_ax is None or self._pan_start is None:
            return
        if event.inaxes is None:
            return
        dx = self._pan_start[0] - event.xdata
        dy = self._pan_start[1] - event.ydata
        xl = self._pan_ax.get_xlim()
        yl = self._pan_ax.get_ylim()
        self._pan_ax.set_xlim(xl[0] + dx, xl[1] + dx)
        self._pan_ax.set_ylim(yl[0] + dy, yl[1] + dy)
        self.draw()

    def _on_press(self, event):
        if event.inaxes is None:
            return
        # 中键/右键拖动平移
        if event.button in (2, 3):  # 中键=2, 右键=3
            self._pan_ax = event.inaxes
            self._pan_start = (event.xdata, event.ydata)
            # 第一次平移前保存初始视图
            self._home_views.setdefault(event.inaxes,
                (event.inaxes.get_xlim(), event.inaxes.get_ylim()))
            # 手型光标
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        # 双击重置
        elif event.dblclick and event.button == 1:
            # 还原到初始视图
            for ax in self.axes:
                ax.autoscale()
                ax.relim()
            if event.inaxes in self._home_views:
                xl, yl = self._home_views[event.inaxes]
                event.inaxes.set_xlim(xl)
                event.inaxes.set_ylim(yl)
                del self._home_views[event.inaxes]
            self.draw()

    def _on_release(self, event):
        self._pan_ax = None
        self._pan_start = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _on_scroll(self, event):
        if event.inaxes is None:
            return
        scale = 0.85 if event.button == 'up' else 1.15
        xl = event.inaxes.get_xlim()
        yl = event.inaxes.get_ylim()
        cx, cy = event.xdata, event.ydata
        # 第一次滚轮时保存初始视图
        self._home_views.setdefault(event.inaxes, (xl, yl))
        event.inaxes.set_xlim([cx - (cx - xl[0]) * scale, cx + (xl[1] - cx) * scale])
        event.inaxes.set_ylim([cy - (cy - yl[0]) * scale, cy + (yl[1] - cy) * scale])
        self.draw()

    def set_status_callback(self, cb):
        self._status_cb = cb

    def clear_all(self):
        for ax in self.axes:
            ax.clear()
        self.annotations.clear()

    def add_span_selector(self, ax_idx=0, callback=None):
        """添加跨度选择器"""
        ss = SpanSelector(self.axes[ax_idx], callback or (lambda xmin, xmax: None),
                         'horizontal', useblit=True,
                         props=dict(alpha=0.2, facecolor='#569cd6'))
        self.span_selectors.append(ss)
        return ss

    def annotate_peak(self, ax_idx=0, x=None, y=None, text=None):
        if x is None or y is None:
            return
        ann = self.axes[ax_idx].annotate(
            text or f'({x:.3f}, {y:.3f})', xy=(x, y),
            xytext=(10, 10), textcoords='offset points',
            color='white', fontsize=8,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#333', alpha=0.8),
            arrowprops=dict(arrowstyle='->', color='#569cd6')
        )
        self.annotations.append(ann)

    def find_peaks_plot(self, ax_idx=0, data_x=None, data_y=None, n_peaks=5):
        """自动找峰值并标注"""
        from scipy.signal import find_peaks
        if data_y is None and len(self.axes[ax_idx].lines) > 0:
            line = self.axes[ax_idx].lines[-1]
            data_x = line.get_xdata()
            data_y = line.get_ydata()
        if data_y is None:
            return
        peaks, props = find_peaks(np.abs(data_y), distance=10)
        if len(peaks) > n_peaks:
            idx = np.argsort(np.abs(data_y[peaks]))[-n_peaks:]
            peaks = peaks[idx]
        for p in peaks:
            self.annotate_peak(ax_idx, data_x[p], data_y[p],
                              f'{data_x[p]:.2f}, {data_y[p]:.3f}')

    def refresh(self):
        self.fig.tight_layout()
        self.draw()

    def save_figure(self, path: str):
        self.fig.savefig(path, dpi=150, facecolor=self.fig.get_facecolor())


class SignalCanvas(InteractiveCanvas):
    """信号专用画布 — 可切换连续/离散显示"""
    def __init__(self, dark=True, figsize=(10, 6)):
        super().__init__(nrows=1, ncols=1, figsize=figsize, dark=dark)

    def plot_signal(self, signal, style='line', color='#569cd6', alpha=1.0):
        ax = self.axes[0]
        if style == 'stem':
            step = max(1, len(signal.t) // 500)
            ml, sl, bl = ax.stem(signal.t[::step], signal.y[::step],
                                 label=signal.name)
            plt.setp(ml, 'color', color)
            plt.setp(sl, 'color', color)
            plt.setp(bl, 'color', color)
        elif style == 'dots':
            ax.scatter(signal.t, signal.y, s=1, color=color, alpha=alpha, label=signal.name)
        else:
            ax.plot(signal.t, signal.y, color=color, linewidth=1, alpha=alpha, label=signal.name)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(True, alpha=0.3)
        if len(self.axes[0].lines) > 1:
            ax.legend(fontsize=8)
        self.refresh()

    def plot_multi(self, signals: list, colors=None):
        ax = self.axes[0]
        if colors is None:
            colors = ['#569cd6', '#dcdcaa', '#ce9178', '#4ec9b0', '#c586c0',
                      '#9cdcfe', '#d16969', '#608b4e']
        for sig, c in zip(signals, colors * (len(signals)//len(colors)+1)):
            ax.plot(sig.t, sig.y, color=c, linewidth=1, label=sig.name, alpha=0.8)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc='upper right')
        self.refresh()
