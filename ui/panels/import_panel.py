"""文件导入面板 — CSV/WAV/MAT 导入"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QMessageBox, QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from signal_engine import SignalGenerator
from ui.logger import log, op, err


class ImportPanel(QWidget):
    """文件导入面板"""

    signal_imported = pyqtSignal()

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("导入信号数据")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #569cd6;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        for text, slot in [
            ("CSV 导入 CSV 文件", self._import_csv),
            ("WAV 导入 WAV 音频", self._import_wav),
            ("MAT 导入 MAT 文件", self._import_mat),
        ]:
            btn = QPushButton(text)
            btn.setFixedSize(300, 60)
            btn.setStyleSheet(
                "QPushButton { background: #3c3c3c; font-size: 16px;"
                " border: 1px solid #555; border-radius: 8px; }"
                "QPushButton:hover { background: #555; border-color: #007acc; }"
            )
            btn.clicked.connect(slot)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def _import_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "导入CSV", "", "CSV (*.csv);;TXT (*.txt)"
        )
        if path:
            try:
                sig = SignalGenerator.import_csv(path)
                self.manager.add(sig)
                op("import_csv", path=path, name=sig.name)
                self.signal_imported.emit()
            except Exception as e:
                err("import_csv_fail", e, path=path)
                QMessageBox.warning(self, "错误", str(e))

    def _import_wav(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "导入WAV", "", "WAV (*.wav)"
        )
        if path:
            try:
                sig = SignalGenerator.import_wav(path)
                self.manager.add(sig)
                op("import_wav", path=path, name=sig.name)
                self.signal_imported.emit()
            except Exception as e:
                err("import_wav_fail", e, path=path)
                QMessageBox.warning(self, "错误", str(e))

    def _import_mat(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "导入MAT", "", "MAT (*.mat)"
        )
        if path:
            try:
                sigs = SignalGenerator.import_mat(path)
                for s in sigs:
                    self.manager.add(s)
                op("import_mat", path=path, count=len(sigs))
                self.signal_imported.emit()
            except Exception as e:
                err("import_mat_fail", e, path=path)
                QMessageBox.warning(self, "错误", str(e))
