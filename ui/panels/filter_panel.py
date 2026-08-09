"""滤波器设计面板 — FIR/IIR 设计 + 分析 + 应用"""
import numpy as np
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QMessageBox,
)
import matplotlib.pyplot as plt
from plot_canvas import InteractiveCanvas
from filter_engine import FIRFilter, IIRFilter, FilterBank, FilterResult
from ui.logger import log, op, err


class FilterPanel(QWidget):
    """滤波器设计与分析面板"""

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.current_filter: Optional[FilterResult] = None
        self.filter_list: list[FilterResult] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 设计区域
        des = QGroupBox("滤波器设计")
        fl = QFormLayout(des)

        self.combo_family = QComboBox()
        self.combo_family.addItems([
            "FIR-窗函数", "FIR-Remez", "IIR-Butterworth",
            "IIR-Chebyshev I", "IIR-Chebyshev II", "IIR-Elliptic",
            "IIR-Bessel", "IIR-Notch", "IIR-Peak",
        ])
        fl.addRow("类型:", self.combo_family)

        self.combo_ftype = QComboBox()
        self.combo_ftype.addItems(["lowpass", "highpass", "bandpass", "bandstop"])
        fl.addRow("通带:", self.combo_ftype)

        self.spin_order = QSpinBox()
        self.spin_order.setRange(1, 500)
        self.spin_order.setValue(4)
        fl.addRow("阶数:", self.spin_order)

        self.spin_cut = QDoubleSpinBox()
        self.spin_cut.setRange(0.1, 10000)
        self.spin_cut.setValue(100.0)
        fl.addRow("截止(Hz):", self.spin_cut)

        self.spin_rp = QDoubleSpinBox()
        self.spin_rp.setRange(0.01, 10)
        self.spin_rp.setValue(1.0)
        fl.addRow("波纹(dB):", self.spin_rp)

        self.spin_rs = QDoubleSpinBox()
        self.spin_rs.setRange(1, 200)
        self.spin_rs.setValue(40.0)
        fl.addRow("阻带衰减(dB):", self.spin_rs)

        self.combo_win_fir = QComboBox()
        self.combo_win_fir.addItems(FIRFilter.WINDOWS)
        fl.addRow("FIR窗:", self.combo_win_fir)

        self.btn_design = QPushButton("Design 设计滤波器")
        self.btn_design.clicked.connect(self._design)
        fl.addRow("", self.btn_design)
        layout.addWidget(des)

        # 操作按钮
        btn_row = QHBoxLayout()
        self.btn_apply = QPushButton("应用滤波")
        self.btn_apply.clicked.connect(self._apply)
        self.btn_apply.setStyleSheet("background: #0e639c;")
        self.btn_filtfilt = QPushButton("零相位滤波")
        self.btn_filtfilt.clicked.connect(self._apply_filtfilt)
        self.btn_filtfilt.setStyleSheet("background: #3c3c3c;")
        self.btn_compare = QPushButton("多滤波器对比")
        self.btn_compare.clicked.connect(self._compare)
        self.btn_compare.setStyleSheet("background: #3c3c3c;")
        btn_row.addWidget(self.btn_apply)
        btn_row.addWidget(self.btn_filtfilt)
        btn_row.addWidget(self.btn_compare)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.lbl_info = QLabel("未设计滤波器")
        self.lbl_info.setStyleSheet("color: #4ec9b0; font-style: italic;")
        layout.addWidget(self.lbl_info)

        self.canvas = InteractiveCanvas(nrows=2, ncols=2, figsize=(10, 7), dark=True)
        layout.addWidget(self.canvas, 1)

    def _design(self):
        family = self.combo_family.currentText()
        ftype = self.combo_ftype.currentText()
        order = self.spin_order.value()
        cutoff = self.spin_cut.value()
        rp = self.spin_rp.value()
        rs = self.spin_rs.value()
        fs = self.manager.first_checked.fs if self.manager.first_checked else 1000.0

        try:
            if "窗函数" in family:
                flt = FIRFilter.window_method(
                    cutoff, fs, numtaps=order + 1,
                    window=self.combo_win_fir.currentText()
                )
            elif "Remez" in family:
                nyq = fs / 2
                if "low" in ftype:
                    bands, desired = [0, cutoff / nyq, cutoff * 1.1 / nyq, 1], [1, 0]
                elif "high" in ftype:
                    bands, desired = [0, cutoff * 0.9 / nyq, cutoff / nyq, 1], [0, 1]
                else:
                    bands, desired = (
                        [0, cutoff * 0.9 / nyq, cutoff / nyq,
                         cutoff * 2 / nyq, cutoff * 2.1 / nyq, 1],
                        [0, 1, 0],
                    )
                flt = FIRFilter.remez(bands, desired, fs, numtaps=order + 1)
            elif "Butterworth" in family:
                flt = IIRFilter.butterworth(order, cutoff, fs, btype=ftype)
            elif "Chebyshev I" in family:
                flt = IIRFilter.chebyshev1(order, cutoff, rp, fs, btype=ftype)
            elif "Chebyshev II" in family:
                flt = IIRFilter.chebyshev2(order, cutoff, rs, fs, btype=ftype)
            elif "Elliptic" in family:
                flt = IIRFilter.elliptic(order, cutoff, rp, rs, fs, btype=ftype)
            elif "Bessel" in family:
                flt = IIRFilter.bessel(order, cutoff, fs, btype=ftype)
            elif "Notch" in family:
                flt = IIRFilter.iirnotch(cutoff, 30, fs)
            elif "Peak" in family:
                flt = IIRFilter.iirpeak(cutoff, 10, fs)
            else:
                return

            self.current_filter = flt
            self.filter_list.append(flt)
            if len(self.filter_list) > 10:
                self.filter_list = self.filter_list[-10:]
            self._plot_filter(flt)
            self.lbl_info.setText(flt.cutoff_info)
            op("filter_design", family=family, ftype=ftype, order=order, cutoff=cutoff)
        except Exception as e:
            err("filter_design_fail", e, family=family, ftype=ftype)
            QMessageBox.warning(self, "错误", str(e))

    def _plot_filter(self, flt: FilterResult):
        self.canvas.clear_all()
        ax0, ax1, ax2, ax3 = self.canvas.axes

        # 幅频响应
        ax0.plot(flt.freq, flt.mag, '#569cd6', linewidth=1.5)
        ax0.axhline(-3, color='red', ls='--', alpha=0.5)
        ax0.set_xlabel("Freq (Hz)")
        ax0.set_ylabel("dB")
        ax0.set_title("幅频响应")
        ax0.grid(True, alpha=0.3)

        # 相频响应
        ax1.plot(flt.freq, flt.phase, color='coral', linewidth=1.5)
        ax1.set_xlabel("Freq (Hz)")
        ax1.set_ylabel("Phase (rad)")
        ax1.set_title("相频响应")
        ax1.grid(True, alpha=0.3)

        # 零极点
        ax2.plot(flt.zeros.real, flt.zeros.imag, 'o', color='#4ec9b0',
                 markersize=6, markerfacecolor='none')
        ax2.plot(flt.poles.real, flt.poles.imag, 'x', color='#d16969', markersize=8)
        theta = np.linspace(0, 2 * np.pi, 200)
        ax2.plot(np.cos(theta), np.sin(theta), 'gray', ls='--', alpha=0.5)
        ax2.axhline(0, color='gray', lw=0.5)
        ax2.axvline(0, color='gray', lw=0.5)
        ax2.set_aspect('equal')
        ax2.set_title("零极点图 (Z平面)")
        all_v = np.concatenate([
            flt.zeros.real, flt.zeros.imag, flt.poles.real, flt.poles.imag,
        ])
        lim = max(np.max(np.abs(all_v)) * 1.3, 1.5)
        ax2.set_xlim(-lim, lim)
        ax2.set_ylim(-lim, lim)
        ax2.grid(True, alpha=0.2)

        # 冲激响应
        n_ir, ir = flt.impulse_response(100)
        ml, sl, bl = ax3.stem(n_ir, ir)
        plt.setp(ml, 'color', '#569cd6')
        plt.setp(sl, 'color', '#569cd6')
        plt.setp(bl, 'color', '#569cd6')
        ax3.set_xlabel("n")
        ax3.set_ylabel("h[n]")
        ax3.set_title("冲激响应")
        ax3.grid(True, alpha=0.3)
        self.canvas.refresh()

    def _apply(self):
        sig = self.manager.first_checked
        if not self.current_filter or not sig:
            return QMessageBox.warning(self, "提示", "需要滤波器和已勾选的信号")
        try:
            result = self.current_filter.apply(sig)
            self.manager.add(result)
            op("filter_apply", filter=self.current_filter.name, signal=result.name)
        except Exception as e:
            err("filter_apply_fail", e, filter=self.current_filter.name)
            QMessageBox.warning(self, "错误", str(e))

    def _apply_filtfilt(self):
        sig = self.manager.first_checked
        if not self.current_filter or not sig:
            return QMessageBox.warning(self, "提示", "需要滤波器和已勾选的信号")
        try:
            result = self.current_filter.apply_filtfilt(sig)
            self.manager.add(result)
            op("filter_filtfilt", filter=self.current_filter.name, signal=result.name)
        except Exception as e:
            err("filter_filtfilt_fail", e)
            QMessageBox.warning(self, "错误", str(e))

    def _compare(self):
        if len(self.filter_list) < 2:
            return QMessageBox.warning(self, "提示", "需要至少2个滤波器对比")
        self.canvas.clear_all()
        ax = self.canvas.axes[0]
        colors = ['#569cd6', '#dcdcaa', '#ce9178', '#4ec9b0',
                  '#c586c0', '#d16969', '#9cdcfe', '#608b4e']
        for i, flt in enumerate(self.filter_list):
            ax.plot(flt.freq, flt.mag, colors[i % len(colors)],
                    linewidth=1, label=flt.name)
        ax.set_xlabel("Freq (Hz)")
        ax.set_ylabel("dB")
        ax.set_title("滤波器幅频对比")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        for a in self.canvas.axes[1:]:
            a.set_visible(False)
        self.canvas.refresh()

    def clear_on_empty(self):
        """无勾选信号时不清空（滤波器独立于信号）"""
        pass
