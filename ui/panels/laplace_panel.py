"""拉普拉斯变换面板 — 符号正/逆变换 + 传递函数 + 零极点"""
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit,
    QGroupBox, QMessageBox,
)
from plot_canvas import InteractiveCanvas
from transform_engine import LaplaceTransform


class LaplacePanel(QWidget):
    """拉普拉斯变换分析面板"""

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.poles, self.zeros = [], []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 正变换
        g1 = QGroupBox("正变换 f(t) → F(s)")
        l1 = QHBoxLayout(g1)
        l1.addWidget(QLabel("f(t) ="))
        self.fwd_in = QLineEdit("sin(2*t)")
        l1.addWidget(self.fwd_in)
        b1 = QPushButton("→ F(s)")
        b1.clicked.connect(self._forward)
        l1.addWidget(b1)
        self.fwd_out = QTextEdit()
        self.fwd_out.setReadOnly(True)
        self.fwd_out.setMaximumHeight(50)
        l1.addWidget(self.fwd_out)
        layout.addWidget(g1)

        # 逆变换
        g2 = QGroupBox("逆变换 F(s) → f(t)")
        l2 = QHBoxLayout(g2)
        l2.addWidget(QLabel("F(s) ="))
        self.inv_in = QLineEdit("1/(s**2 + 1)")
        l2.addWidget(self.inv_in)
        b2 = QPushButton("→ f(t)")
        b2.clicked.connect(self._inverse)
        l2.addWidget(b2)
        self.inv_out = QTextEdit()
        self.inv_out.setReadOnly(True)
        self.inv_out.setMaximumHeight(50)
        l2.addWidget(self.inv_out)
        layout.addWidget(g2)

        # 传递函数
        g3 = QGroupBox("传递函数频率响应")
        l3 = QFormLayout(g3)
        self.tf_num = QLineEdit("1")
        l3.addRow("分子:", self.tf_num)
        self.tf_den = QLineEdit("1,1,1")
        l3.addRow("分母:", self.tf_den)
        b3 = QPushButton("计算 H(jω)")
        b3.clicked.connect(self._tf_response)
        l3.addRow("", b3)
        layout.addWidget(g3)

        self.canvas = InteractiveCanvas(nrows=2, ncols=2, figsize=(10, 6), dark=True)
        layout.addWidget(self.canvas, 1)

    def _forward(self):
        r = LaplaceTransform.forward(self.fwd_in.text())
        if "error" in r:
            return QMessageBox.warning(self, "错误", r["error"])
        self.fwd_out.setText(f"F(s) = {r['raw']}")
        self.poles, self.zeros = r.get("poles", []), r.get("zeros", [])
        self._plot_pz()

    def _inverse(self):
        r = LaplaceTransform.inverse(self.inv_in.text())
        if "error" in r:
            return QMessageBox.warning(self, "错误", r["error"])
        self.inv_out.setText(f"f(t) = {r['raw']}")

    def _tf_response(self):
        try:
            num = [float(x.strip()) for x in self.tf_num.text().split(",")]
            den = [float(x.strip()) for x in self.tf_den.text().split(",")]
        except ValueError:
            return QMessageBox.warning(self, "错误", "系数格式错误")
        r = LaplaceTransform.transfer_response(num, den)
        self.poles = [complex(p) for p in np.roots(den)]
        self.zeros = [complex(z) for z in np.roots(num)]
        self._plot_pz()
        self._plot_tf(r)

    def _plot_pz(self):
        ax = self.canvas.axes[0]
        ax.clear()
        for z in self.zeros:
            ax.plot(z.real, z.imag, 'o', color='#4ec9b0', markersize=8,
                    markerfacecolor='none', markeredgewidth=2)
        for p in self.poles:
            ax.plot(p.real, p.imag, 'x', color='#d16969', markersize=10, markeredgewidth=2)
        ax.axhline(0, color='gray', lw=0.5)
        ax.axvline(0, color='gray', lw=0.5)
        ax.set_title("零极点图 (o=零点 x=极点)")
        ax.set_xlabel("Re")
        ax.set_ylabel("Im")
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        all_v = [v.real for v in self.poles + self.zeros] + \
                [v.imag for v in self.poles + self.zeros]
        if all_v:
            lim = max(abs(v) for v in all_v) * 1.5 + 1
            ax.set_xlim(-lim, lim)
            ax.set_ylim(-lim, lim)
        self.canvas.refresh()

    def _plot_tf(self, r):
        self.canvas.axes[1].clear()
        self.canvas.axes[2].clear()
        w = r.data_x
        # 仅保留正值，避免 semilogx 报警
        mask = w > 1e-15
        if np.any(mask) and np.sum(mask) >= 2:
            self.canvas.axes[1].semilogx(w[mask], r.data_y[mask], color='steelblue', linewidth=1)
            self.canvas.axes[2].semilogx(w[mask], r.data_y2[mask], color='coral', linewidth=1)
        else:
            self.canvas.axes[1].plot(w, r.data_y, color='steelblue', linewidth=1)
            self.canvas.axes[2].plot(w, r.data_y2, color='coral', linewidth=1)
        self.canvas.axes[1].set_xlabel("ω (rad/s)")
        self.canvas.axes[1].set_ylabel("dB")
        self.canvas.axes[1].grid(True, alpha=0.3)
        self.canvas.axes[1].set_title("Bode 幅频")
        self.canvas.axes[2].set_xlabel("ω (rad/s)")
        self.canvas.axes[2].set_ylabel("Phase (rad)")
        self.canvas.axes[2].grid(True, alpha=0.3)
        self.canvas.axes[2].set_title("Bode 相频")
        self.canvas.axes[3].set_visible(False)
        self.canvas.refresh()

    def clear_on_empty(self):
        """无勾选信号时清空显示"""
        self.canvas.clear_all()
        self.canvas.refresh()
