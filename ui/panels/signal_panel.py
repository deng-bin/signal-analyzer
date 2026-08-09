"""信号管理面板 — 信号列表 + 生成器 + 导入导出"""
import os
import numpy as np
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QComboBox, QDoubleSpinBox,
    QGroupBox, QLineEdit, QCheckBox, QMessageBox, QFileDialog,
    QTreeWidget, QTreeWidgetItem,
)
from PyQt6.QtCore import Qt, pyqtSignal

from signal_engine import Signal, SignalGenerator
from ui.logger import log, op, err, warn, debug


class SignalManager:
    """信号管理器 — 信号列表 + 勾选状态 + 变更通知"""
    def __init__(self):
        self.signals: list[Signal] = []
        self.selected: Optional[Signal] = None
        self._checked: set = set()  # 已勾选的 signal id
        self.callbacks = []
        self._refresh_pending = False  # 延迟刷新标志

    def add(self, s: Signal):
        self.signals.append(s)
        self._checked.add(s.id)  # 新信号默认勾选
        if not self.selected:
            self.selected = s
        op("signal_add", name=s.name, type=s.signal_type, n=len(self.signals))
        self._notify()

    def remove(self, s: Signal):
        name = s.name
        if any(sig.id == s.id for sig in self.signals):
            self.signals = [sig for sig in self.signals if sig.id != s.id]
        self._checked.discard(s.id)
        if self.selected and self.selected.id == s.id:
            self.selected = self.signals[-1] if self.signals else None
        op("signal_remove", name=name, remaining=len(self.signals))
        self._notify()

    def clear(self):
        n = len(self.signals)
        self.signals.clear()
        self._checked.clear()
        self.selected = None
        op("signal_clear", cleared=n)
        self._notify()

    def get(self, name: str) -> Optional[Signal]:
        for s in self.signals:
            if s.name == name:
                return s
        return None

    def is_checked(self, s: Signal) -> bool:
        return s.id in self._checked

    def set_checked(self, s: Signal, checked: bool):
        if checked:
            self._checked.add(s.id)
        else:
            self._checked.discard(s.id)
        debug("signal_check", name=s.name, checked=checked, total_checked=len(self._checked))
        self._notify()

    def toggle_checked(self, s: Signal):
        if s.id in self._checked:
            self._checked.discard(s.id)
        else:
            self._checked.add(s.id)
        self._notify()

    def check_all(self):
        for s in self.signals:
            self._checked.add(s.id)
        op("signal_check_all", total=len(self.signals))
        self._notify()

    def uncheck_all(self):
        op("signal_uncheck_all", total=len(self.signals))
        self._checked.clear()
        self._notify()

    @property
    def checked_signals(self) -> list[Signal]:
        """返回已勾选的信号列表（按 signals 顺序）"""
        return [s for s in self.signals if s.id in self._checked]

    @property
    def first_checked(self) -> Optional[Signal]:
        """第一个勾选的信号；无勾选返回 None"""
        cs = self.checked_signals
        return cs[0] if cs else None

    def on_change(self, cb):
        self.callbacks.append(cb)

    def _notify(self):
        for cb in self.callbacks:
            try:
                cb()
            except Exception as e:
                err("notify_callback_error", e)


class SignalGenPanel(QWidget):
    """信号管理面板 — 树形列表 + 生成器表单"""
    signal_changed = pyqtSignal()

    def __init__(self, manager: SignalManager):
        super().__init__()
        self.manager = manager
        self._setup_ui()
        manager.on_change(lambda: self._update_list_status())

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # 搜索框
        self.search = QLineEdit()
        self.search.setPlaceholderText("搜索信号...")
        layout.addWidget(self.search)

        # 信号树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["信号", "类型", "点数"])
        self.tree.setColumnWidth(0, 160)
        self.tree.setColumnWidth(1, 60)
        self.tree.setColumnWidth(2, 60)
        self.tree.itemClicked.connect(self._on_select)
        self.tree.itemChanged.connect(self._on_check_changed)
        layout.addWidget(self.tree)

        # 操作按钮
        btn_row = QHBoxLayout()
        for text, slot in [("删除", self._remove), ("清空", self._clear),
                           ("复制", self._copy), ("导出CSV", self._export_csv)]:
            btn = QPushButton(text)
            btn.setStyleSheet(
                "QPushButton { background: #3c3c3c; padding: 4px 10px; }"
                "QPushButton:hover { background: #555; }"
            )
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

        # 全选 / 全不选
        sel_row = QHBoxLayout()
        btn_all = QPushButton("全选")
        btn_all.setStyleSheet("QPushButton { background: #3c3c3c; padding: 3px 8px; font-size: 11px; } QPushButton:hover { background: #555; }")
        btn_all.clicked.connect(lambda: self._check_all(True))
        sel_row.addWidget(btn_all)
        btn_none = QPushButton("全不选")
        btn_none.setStyleSheet("QPushButton { background: #3c3c3c; padding: 3px 8px; font-size: 11px; } QPushButton:hover { background: #555; }")
        btn_none.clicked.connect(lambda: self._check_all(False))
        sel_row.addWidget(btn_none)
        sel_row.addStretch()
        self.lbl_checked = QLabel("")
        self.lbl_checked.setStyleSheet("color: #888; font-size: 11px;")
        sel_row.addWidget(self.lbl_checked)
        layout.addLayout(sel_row)

        # 信号生成表单
        gen_grp = QGroupBox("信号生成器")
        gen_layout = QFormLayout(gen_grp)

        self.combo_type = QComboBox()
        self.combo_type.addItems([
            "正弦 sin", "余弦 cos", "方波 square", "锯齿波 sawtooth",
            "三角波 triangle", "线性调频 chirp", "冲激 δ(t)", "阶跃 u(t)",
            "高斯脉冲", "sinc 脉冲", "指数衰减", "AM 调制", "FM 调制",
            "多频合成", "谐波级数", "ECG 模拟", "白噪声", "粉红噪声", "自定义表达式"
        ])
        gen_layout.addRow("类型:", self.combo_type)

        self.spin_freq = QDoubleSpinBox()
        self.spin_freq.setRange(0.01, 50000)
        self.spin_freq.setValue(5.0)
        gen_layout.addRow("频率(Hz):", self.spin_freq)

        self.spin_amp = QDoubleSpinBox()
        self.spin_amp.setRange(0.01, 100)
        self.spin_amp.setValue(1.0)
        gen_layout.addRow("幅值:", self.spin_amp)

        self.spin_dur = QDoubleSpinBox()
        self.spin_dur.setRange(0.1, 60)
        self.spin_dur.setValue(2.0)
        gen_layout.addRow("时长(s):", self.spin_dur)

        self.spin_fs = QDoubleSpinBox()
        self.spin_fs.setRange(10, 100000)
        self.spin_fs.setValue(1000.0)
        gen_layout.addRow("采样率(Hz):", self.spin_fs)

        self.chk_disc = QCheckBox("离散")
        gen_layout.addRow("", self.chk_disc)

        self.line_expr = QLineEdit("sin(2*pi*5*t) + sin(2*pi*50*t)")
        gen_layout.addRow("表达式:", self.line_expr)

        self.btn_gen = QPushButton("Gen 生成信号")
        self.btn_gen.clicked.connect(self._generate)
        gen_layout.addRow("", self.btn_gen)
        layout.addWidget(gen_grp)

    def _generate(self):
        sig_type = self.combo_type.currentText()
        freq = self.spin_freq.value()
        amp = self.spin_amp.value()
        dur = self.spin_dur.value()
        fs = self.spin_fs.value()
        disc = self.chk_disc.isChecked()
        op("gen_start", type=sig_type, freq=freq, amp=amp, dur=dur, fs=fs)

        mapping = {
            "正弦 sin": lambda: SignalGenerator.sine(freq, amp, duration=dur, fs=fs, discrete=disc),
            "余弦 cos": lambda: SignalGenerator.cosine(freq, amp, duration=dur, fs=fs, discrete=disc),
            "方波 square": lambda: SignalGenerator.square(freq, amp, duration=dur, fs=fs, discrete=disc),
            "锯齿波 sawtooth": lambda: SignalGenerator.sawtooth(freq, amp, duration=dur, fs=fs, discrete=disc),
            "三角波 triangle": lambda: SignalGenerator.triangle(freq, amp, duration=dur, fs=fs, discrete=disc),
            "线性调频 chirp": lambda: SignalGenerator.chirp(f0=freq, f1=freq * 10, amp=amp, duration=dur, fs=fs, discrete=disc),
            "冲激 δ(t)": lambda: SignalGenerator.impulse(duration=dur, fs=fs, discrete=disc),
            "阶跃 u(t)": lambda: SignalGenerator.step(duration=dur, fs=fs, discrete=disc),
            "高斯脉冲": lambda: SignalGenerator.gaussian_pulse(duration=dur, fs=fs, discrete=disc),
            "sinc 脉冲": lambda: SignalGenerator.sinc_pulse(fc=freq, amp=amp, duration=dur, fs=fs, discrete=disc),
            "指数衰减": lambda: SignalGenerator.exponential_decay(duration=dur, fs=fs, discrete=disc),
            "AM 调制": lambda: SignalGenerator.am_modulation(carrier=freq * 10, modulator=freq, duration=dur, fs=fs, discrete=disc),
            "FM 调制": lambda: SignalGenerator.fm_modulation(carrier=freq * 10, modulator=freq, duration=dur, fs=fs, discrete=disc),
            "多频合成": lambda: SignalGenerator.multi_tone([freq, freq * 3, freq * 5], [amp, amp / 3, amp / 5], duration=dur, fs=fs, discrete=disc),
            "谐波级数": lambda: SignalGenerator.harmonic_series(f0=freq, n_harmonics=5, duration=dur, fs=fs, discrete=disc),
            "ECG 模拟": lambda: SignalGenerator.ecg_like(duration=dur, fs=fs, discrete=disc),
            "白噪声": lambda: SignalGenerator.noise(duration=dur, fs=fs, std=amp * 0.3, color='white', discrete=disc),
            "粉红噪声": lambda: SignalGenerator.noise(duration=dur, fs=fs, std=amp * 0.3, color='pink', discrete=disc),
            "自定义表达式": lambda: SignalGenerator.custom_expression(self.line_expr.text(), duration=dur, fs=fs, discrete=disc),
        }

        try:
            sig = mapping.get(sig_type, lambda: SignalGenerator.sine(5, 1))()
            self.manager.add(sig)
            self._refresh_list()
            self.signal_changed.emit()
            op("gen_ok", name=sig.name, n_samples=sig.n_samples)
        except Exception as e:
            err("gen_fail", e, type=sig_type, expr=self.line_expr.text())
            QMessageBox.warning(self, "错误", str(e))

    def _update_list_status(self):
        """仅更新勾选计数，不重建树"""
        self._update_status()

    def _refresh_list(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        for sig in self.manager.signals:
            item = QTreeWidgetItem([sig.name, sig.signal_type, str(sig.n_samples)])
            item.setData(0, Qt.ItemDataRole.UserRole, sig.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Checked if self.manager.is_checked(sig) else Qt.CheckState.Unchecked)
            self.tree.addTopLevelItem(item)
        self.tree.blockSignals(False)
        self._update_status()

    def _on_select(self, item, column):
        """点击信号行选中"""
        if item is None:
            return
        sig_id = item.data(0, Qt.ItemDataRole.UserRole)
        for s in self.manager.signals:
            if s.id == sig_id:
                self.manager.selected = s
                self.signal_changed.emit()
                break

    def _on_check_changed(self, item, column):
        """勾选状态变化 — 不重建树，仅更新数据模型"""
        if item is None:
            return
        try:
            sig_id = item.data(0, Qt.ItemDataRole.UserRole)
            checked = item.checkState(0) == Qt.CheckState.Checked
            for s in self.manager.signals:
                if s.id == sig_id:
                    self.manager._checked.add(s.id) if checked else self.manager._checked.discard(s.id)
                    self.manager._notify()
                    self.signal_changed.emit()
                    self._update_status()
                    break
        except Exception as e:
            err("check_changed_error", e)

    def _remove(self):
        if self.manager.selected:
            self.manager.remove(self.manager.selected)
            self._refresh_list()
            self.signal_changed.emit()

    def _clear(self):
        self.manager.clear()
        self._refresh_list()
        self.signal_changed.emit()

    def _copy(self):
        if self.manager.selected:
            self.manager.add(self.manager.selected.copy())
            self._refresh_list()
            self.signal_changed.emit()

    def _export_csv(self):
        if not self.manager.selected:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "导出", f"{self.manager.selected.name}.csv", "CSV (*.csv)"
        )
        if path:
            SignalGenerator.export_csv(self.manager.selected, path)

    def _check_all(self, checked: bool):
        """全选/全不选 — 直接修改树项状态，避免重建"""
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        self.tree.blockSignals(True)
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setCheckState(0, state)
            sig_id = item.data(0, Qt.ItemDataRole.UserRole)
            for s in self.manager.signals:
                if s.id == sig_id:
                    if checked:
                        self.manager._checked.add(s.id)
                    else:
                        self.manager._checked.discard(s.id)
                    break
        self.tree.blockSignals(False)
        self.manager._notify()
        self.signal_changed.emit()
        self._update_status()

    def _update_status(self):
        n = len(self.manager.checked_signals)
        total = len(self.manager.signals)
        self.lbl_checked.setText(f"已选 {n}/{total}")
