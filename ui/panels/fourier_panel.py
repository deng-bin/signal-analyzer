"""傅里叶变换面板 — FFT/DFT/STFT/CWT/Hilbert/倒谱/相干性"""
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox,
    QMessageBox, QInputDialog,
)
from plot_canvas import InteractiveCanvas
from transform_engine import (
    FourierTransform, HilbertTransform, WaveletTransform, TransformResult,
)
from ui.logger import log, op, err


class FourierPanel(QWidget):
    """频域分析面板"""

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.result = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.combo_method = QComboBox()
        self.combo_method.addItems([
            "FFT", "DFT", "STFT 频谱图", "功率谱 PSD", "倒谱 Cepstrum",
            "希尔伯特变换", "小波变换 CWT", "相干性", "符号傅里叶",
        ])
        toolbar.addWidget(QLabel("方法:"))
        toolbar.addWidget(self.combo_method)

        self.combo_win = QComboBox()
        self.combo_win.addItems(
            ["none", "hamming", "hann", "blackman", "bartlett", "kaiser", "flattop"]
        )
        toolbar.addWidget(QLabel("窗:"))
        toolbar.addWidget(self.combo_win)

        self.spin_n = QSpinBox()
        self.spin_n.setRange(16, 65536)
        self.spin_n.setValue(2048)
        toolbar.addWidget(QLabel("N:"))
        toolbar.addWidget(self.spin_n)

        self.btn_compute = QPushButton("计算")
        self.btn_compute.clicked.connect(self._compute)
        self.btn_compute.setStyleSheet("QPushButton { background: #0e639c; }")
        toolbar.addWidget(self.btn_compute)

        self.btn_peak = QPushButton("标峰")
        self.btn_peak.clicked.connect(self._annotate_peaks)
        self.btn_peak.setStyleSheet("QPushButton { background: #3c3c3c; }")
        toolbar.addWidget(self.btn_peak)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.canvas = InteractiveCanvas(nrows=2, ncols=2, figsize=(10, 7), dark=True)
        layout.addWidget(self.canvas, 1)

    def _compute(self):
        sig = self.manager.first_checked
        if not sig:
            self.clear_on_empty()
            return QMessageBox.warning(self, "提示", "请至少勾选一个信号")
        method = self.combo_method.currentText()
        n = self.spin_n.value()
        win = self.combo_win.currentText()

        self.canvas.clear_all()
        try:
            if method == "FFT":
                r = FourierTransform.fft(sig, n=n, window=win)
                self._plot_bode(r, 0, 1)
            elif method == "DFT":
                r = FourierTransform.dft(sig, N=n)
                self._plot_bode(r, 0, 1)
            elif method == "STFT 频谱图":
                f, t, Sxx = FourierTransform.stft(sig)
                ax = self.canvas.axes[0]
                im = ax.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-15),
                                   shading='gouraud', cmap='inferno')
                ax.set_xlabel("Time (s)")
                ax.set_ylabel("Freq (Hz)")
                self.canvas.fig.colorbar(im, ax=ax, label="dB")
                for a in self.canvas.axes[1:]:
                    a.set_visible(False)
            elif method == "功率谱 PSD":
                r = FourierTransform.power_spectrum(sig)
                ax = self.canvas.axes[0]
                ax.plot(r.data_x, r.data_y, 'steelblue', linewidth=1)
                ax.set_xlabel(r.xlabel)
                ax.set_ylabel(r.ylabel)
                ax.grid(True, alpha=0.3)
                for a in self.canvas.axes[1:]:
                    a.set_visible(False)
            elif method == "倒谱 Cepstrum":
                r = FourierTransform.cepstrum(sig)
                ax = self.canvas.axes[0]
                ax.plot(r.data_x, r.data_y, 'steelblue', linewidth=1)
                ax.set_xlabel(r.xlabel)
                ax.set_ylabel(r.ylabel)
                ax.grid(True, alpha=0.3)
                for a in self.canvas.axes[1:]:
                    a.set_visible(False)
            elif method == "希尔伯特变换":
                r = HilbertTransform.analytic_signal(sig)
                axes = self.canvas.axes
                axes[0].plot(r.data_x, sig.y, 'steelblue', alpha=0.5, label='Signal')
                axes[0].plot(r.data_x, r.data_y, 'coral', label='Envelope')
                axes[0].legend(fontsize=8)
                axes[0].grid(True, alpha=0.3)
                axes[0].set_xlabel("Time (s)")
                axes[1].plot(r.data_x, r.data_y2, 'darkgreen', linewidth=1)
                axes[1].set_ylabel("Phase (rad)")
                axes[1].grid(True, alpha=0.3)
                axes[2].plot(r.data_x, r.data_y3, 'coral', linewidth=1)
                axes[2].set_ylabel("Inst. Freq (Hz)")
                axes[2].grid(True, alpha=0.3)
                axes[2].set_xlabel("Time (s)")
                axes[3].set_visible(False)
            elif method == "小波变换 CWT":
                r = WaveletTransform.cwt(sig)
                ax = self.canvas.axes[0]
                im = ax.pcolormesh(r.data_x, r.data_y, r.data_y2,
                                   shading='gouraud', cmap='viridis')
                ax.set_xlabel("Time (s)")
                ax.set_ylabel("Scale")
                self.canvas.fig.colorbar(im, ax=ax)
                for a in self.canvas.axes[1:]:
                    a.set_visible(False)
            elif method == "相干性":
                if len(self.manager.signals) < 2:
                    return QMessageBox.warning(self, "提示", "需要至少2个信号计算相干性")
                idx = self.manager.signals.index(sig)
                s2 = self.manager.signals[(idx + 1) % len(self.manager.signals)]
                r = FourierTransform.coherence(sig, s2)
                ax = self.canvas.axes[0]
                ax.plot(r.data_x, r.data_y, 'steelblue', linewidth=1)
                ax.set_xlabel(r.xlabel)
                ax.set_ylabel(r.ylabel)
                ax.set_ylim(0, 1)
                ax.grid(True, alpha=0.3)
                for a in self.canvas.axes[1:]:
                    a.set_visible(False)
            elif method == "符号傅里叶":
                self._symbolic_fourier()
                return
            self.result = r
            self.canvas.refresh()
            op("fft_compute", method=method, n=n, window=win)
        except Exception as e:
            err("fft_compute_fail", e, method=method)
            QMessageBox.warning(self, "错误", str(e))

    def _plot_bode(self, r: TransformResult, ax_i, ax_j):
        self.canvas.axes[ax_i].plot(r.data_x, r.data_y, 'steelblue', linewidth=1)
        self.canvas.axes[ax_i].set_xlabel(r.xlabel)
        self.canvas.axes[ax_i].set_ylabel(r.ylabel)
        self.canvas.axes[ax_i].grid(True, alpha=0.3)
        self.canvas.axes[ax_i].set_title("幅度")
        if r.data_y2 is not None:
            self.canvas.axes[ax_j].plot(r.data_x, r.data_y2, 'coral', linewidth=1)
            self.canvas.axes[ax_j].set_xlabel(r.xlabel)
            self.canvas.axes[ax_j].set_ylabel(r.y2label)
            self.canvas.axes[ax_j].grid(True, alpha=0.3)
            self.canvas.axes[ax_j].set_title("相位")
        else:
            self.canvas.axes[ax_j].set_visible(False)

    def _annotate_peaks(self):
        if self.result and len(self.canvas.axes[0].lines) > 0:
            line = self.canvas.axes[0].lines[0]
            self.canvas.find_peaks_plot(0, line.get_xdata(), line.get_ydata())
            self.canvas.refresh()

    def clear_on_empty(self):
        """无勾选信号时清空显示"""
        self.result = None
        self.canvas.clear_all()
        for ax in self.canvas.axes:
            ax.set_visible(True)
        self.canvas.refresh()

    def _symbolic_fourier(self):
        expr, ok = QInputDialog.getText(
            self, "符号傅里叶变换", "f(t) =", text="exp(-t) * Heaviside(t)"
        )
        if ok and expr:
            r = FourierTransform.symbolic_forward(expr)
            if "error" in r:
                QMessageBox.warning(self, "错误", r["error"])
            else:
                msg = f"<b>f(t)</b> = {r['input']}<br><b>F(ω)</b> = {r['result']}"
                QMessageBox.information(self, "结果", msg)
