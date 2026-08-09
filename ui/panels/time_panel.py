"""时域分析面板"""
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QCheckBox, QGroupBox,
)
from plot_canvas import SignalCanvas
from ui.logger import log, err


class TimeDomainPanel(QWidget):
    """时域波形显示 + 信号测量统计"""

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.chk_stem = QCheckBox("离散点")
        self.chk_peaks = QCheckBox("峰值检测")
        toolbar.addWidget(self.chk_stem)
        toolbar.addWidget(self.chk_peaks)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.canvas = SignalCanvas(dark=True)
        layout.addWidget(self.canvas, 1)

        # 测量面板
        meas = QGroupBox("信号测量")
        grid = QGridLayout(meas)
        self.lbls = {}
        labels = ["min", "max", "mean", "std", "rms", "energy", "pp", "dur"]
        names = ["最小值", "最大值", "均值", "标准差", "RMS", "能量", "峰峰值", "时长"]
        for i, k in enumerate(labels):
            lbl = QLabel("--")
            lbl.setStyleSheet("color: #4ec9b0; font-weight: bold;")
            grid.addWidget(QLabel(names[i] + ":"), i // 4, (i % 4) * 2)
            grid.addWidget(lbl, i // 4, (i % 4) * 2 + 1)
            self.lbls[k] = lbl
        layout.addWidget(meas)

    def plot(self):
        self.canvas.clear_all()
        signals = self.manager.checked_signals
        if not signals:
            self.canvas.refresh()
            # 清空测量值
            for k in self.lbls:
                self.lbls[k].setText("--")
            return
        style = 'stem' if self.chk_stem.isChecked() else 'line'
        colors = ['#569cd6', '#dcdcaa', '#ce9178', '#4ec9b0',
                  '#c586c0', '#9cdcfe', '#d16969', '#608b4e']
        for i, s in enumerate(signals):
            self.canvas.plot_signal(s, style=style, color=colors[i % len(colors)], alpha=0.8)
        if self.chk_peaks.isChecked():
            sig = self.manager.selected or signals[0]
            self.canvas.find_peaks_plot(0, sig.t, sig.y)
        # 更新测量值（基于选中信号）
        sig = self.manager.selected or signals[0]
        if sig:
            self.lbls["min"].setText(f"{sig.y.min():.4f}")
            self.lbls["max"].setText(f"{sig.y.max():.4f}")
            self.lbls["mean"].setText(f"{sig.y.mean():.4f}")
            self.lbls["std"].setText(f"{sig.y.std():.4f}")
            self.lbls["rms"].setText(f"{np.sqrt(np.mean(sig.y ** 2)):.4f}")
            self.lbls["energy"].setText(f"{np.sum(sig.y ** 2) * sig.dt:.4f}")
            self.lbls["pp"].setText(f"{sig.y.max() - sig.y.min():.4f}")
            self.lbls["dur"].setText(f"{sig.duration:.3f}s")
