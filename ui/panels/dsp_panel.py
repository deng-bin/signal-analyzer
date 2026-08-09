"""DSP 频谱面板 — 四象限频谱 + 信号运算 + Z变换"""
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QGroupBox, QMessageBox,
)
from plot_canvas import InteractiveCanvas
from signal_engine import SignalOps
from transform_engine import FourierTransform, ZTransform
from ui.logger import log, op, err


class DSPPanel(QWidget):
    """DSP 频谱分析 + 运算面板"""

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        ctrl = QHBoxLayout()
        self.spin_n = QSpinBox()
        self.spin_n.setRange(16, 65536)
        self.spin_n.setValue(2048)
        ctrl.addWidget(QLabel("FFT N:"))
        ctrl.addWidget(self.spin_n)

        self.combo_win = QComboBox()
        self.combo_win.addItems(["none", "hamming", "hann", "blackman", "kaiser", "flattop"])
        ctrl.addWidget(QLabel("窗:"))
        ctrl.addWidget(self.combo_win)

        self.chk_db = QCheckBox("dB")
        self.chk_db.setChecked(True)
        ctrl.addWidget(self.chk_db)

        self.btn_calc = QPushButton("计算频谱")
        self.btn_calc.clicked.connect(self._compute)
        self.btn_calc.setStyleSheet("background: #0e639c;")
        ctrl.addWidget(self.btn_calc)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.canvas = InteractiveCanvas(nrows=2, ncols=2, figsize=(10, 7), dark=True)
        layout.addWidget(self.canvas, 1)

        # 信号运算
        ops = QGroupBox("信号运算")
        ol = QHBoxLayout(ops)
        self.spin_scale = QDoubleSpinBox()
        self.spin_scale.setValue(2.0)
        ol.addWidget(QLabel("缩放:"))
        ol.addWidget(self.spin_scale)

        for text, op in [
            ("缩放", "scale"), ("求导", "diff"), ("积分", "int"),
            ("整流", "rect"), ("半波整流", "half_rect"), ("归一化", "norm"),
        ]:
            btn = QPushButton(text)
            btn.setStyleSheet(
                "QPushButton { background: #3c3c3c; }"
                "QPushButton:hover { background: #555; }"
            )
            btn.clicked.connect(lambda checked, o=op: self._op(o))
            ol.addWidget(btn)

        ol.addWidget(QLabel("   "))
        self.btn_conv = QPushButton("卷积")
        self.btn_conv.clicked.connect(lambda: self._op("conv"))
        self.btn_conv.setStyleSheet("background: #3c3c3c;")
        self.btn_corr = QPushButton("互相关")
        self.btn_corr.clicked.connect(lambda: self._op("corr"))
        self.btn_corr.setStyleSheet("background: #3c3c3c;")
        ol.addWidget(self.btn_conv)
        ol.addWidget(self.btn_corr)
        ol.addStretch()
        layout.addWidget(ops)

        # Z 变换
        zgrp = QGroupBox("Z 变换")
        zl = QHBoxLayout(zgrp)
        self.btn_z = QPushButton("单位圆 Z 变换")
        self.btn_z.clicked.connect(self._z_transform)
        self.btn_z.setStyleSheet("background: #0e639c;")
        zl.addWidget(self.btn_z)
        zl.addStretch()
        layout.addWidget(zgrp)

    def _compute(self):
        sig = self.manager.first_checked
        if not sig:
            self.clear_on_empty()
            return QMessageBox.warning(self, "提示", "请至少勾选一个信号")

        n = self.spin_n.value()
        win = self.combo_win.currentText()
        op("dsp_compute", name=sig.name, n=n, window=win)
        y = sig.y.copy()

        if win != "none":
            wf = {
                "hamming": np.hamming, "hann": np.hanning,
                "blackman": np.blackman,
                "kaiser": lambda n: np.kaiser(n, 14),
                "flattop": lambda n: np.kaiser(n, 0.5),
            }
            w = wf[win](min(len(y), n))
            y = y[:len(w)] * w

        Y = np.fft.fft(y, n=n)
        freqs = np.fft.fftfreq(n, d=1 / sig.fs)
        half = n // 2

        self.canvas.clear_all()
        ax = self.canvas.axes.reshape(2, 2)

        ax[0, 0].plot(sig.t[:5000], sig.y[:5000], '#569cd6', lw=0.8)
        ax[0, 0].set_title("时域")
        ax[0, 0].set_xlabel("t(s)")
        ax[0, 0].set_ylabel("Amp")
        ax[0, 0].grid(True, alpha=0.3)

        mag = np.abs(Y[:half]) / n * 2
        if self.chk_db.isChecked():
            mag = 20 * np.log10(mag + 1e-15)
        ax[0, 1].plot(freqs[:half], mag, '#569cd6', lw=0.8)
        ax[0, 1].set_title("幅度谱")
        ax[0, 1].set_xlabel("Hz")
        ax[0, 1].grid(True, alpha=0.3)

        ax[1, 0].plot(freqs[:half], np.angle(Y[:half]), color='coral', lw=0.8)
        ax[1, 0].set_title("相位谱")
        ax[1, 0].set_xlabel("Hz")
        ax[1, 0].grid(True, alpha=0.3)

        psd = np.abs(Y[:half]) ** 2 / (n * sig.fs)
        psd_safe = np.maximum(psd, 1e-30)
        ax[1, 1].semilogy(freqs[:half], psd_safe, '#4ec9b0', lw=0.8)
        ax[1, 1].set_title("功率谱")
        ax[1, 1].set_xlabel("Hz")
        ax[1, 1].grid(True, alpha=0.3)
        self.canvas.refresh()

    def _op(self, op_name: str):
        sig = self.manager.first_checked
        if not sig:
            return
        try:
            if op_name == "scale":
                res = SignalOps.scale(sig, self.spin_scale.value())
            elif op_name == "diff":
                res = SignalOps.derivative(sig)
            elif op_name == "int":
                res = SignalOps.integral(sig)
            elif op_name == "rect":
                res = SignalOps.rect(sig)
            elif op_name == "half_rect":
                res = SignalOps.half_rect(sig)
            elif op_name == "norm":
                res = SignalOps.normalize(sig)
            elif op_name == "conv":
                if len(self.manager.signals) < 2:
                    return
                idx = (self.manager.signals.index(sig) + 1) % len(self.manager.signals)
                res = SignalOps.convolve(sig, self.manager.signals[idx])
            elif op_name == "corr":
                if len(self.manager.signals) < 2:
                    return
                idx = (self.manager.signals.index(sig) + 1) % len(self.manager.signals)
                res = SignalOps.correlate(sig, self.manager.signals[idx])
            else:
                return
            self.manager.add(res)
            op("dsp_op", op=op_name, result=res.name)
        except Exception as e:
            err("dsp_op_fail", e, op=op_name)

    def _z_transform(self):
        sig = self.manager.first_checked
        if not sig:
            return
        r = ZTransform.numeric(sig)
        self.canvas.clear_all()
        self.canvas.axes[0].plot(r.data_x, r.data_y, '#569cd6', lw=1)
        self.canvas.axes[0].set_xlabel(r.xlabel)
        self.canvas.axes[0].set_ylabel(r.ylabel)
        self.canvas.axes[0].grid(True, alpha=0.3)
        self.canvas.axes[1].plot(r.data_x, r.data_y2, color='coral', lw=1)
        self.canvas.axes[1].set_xlabel(r.xlabel)
        self.canvas.axes[1].set_ylabel(r.y2label)
        self.canvas.axes[1].grid(True, alpha=0.3)
        self.canvas.axes[2].set_visible(False)
        self.canvas.axes[3].set_visible(False)
        self.canvas.refresh()

    def clear_on_empty(self):
        """无勾选信号时清空显示"""
        self.canvas.clear_all()
        self.canvas.refresh()
