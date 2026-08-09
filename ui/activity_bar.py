"""VS Code 风格活动栏"""
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSignal


class ActivityBar(QFrame):
    """VS Code 风格左侧图标活动栏"""
    tab_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(56)
        self.setStyleSheet("background-color: #333333; border-right: 1px solid #3c3c3c;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(4)

        self.buttons: list[QPushButton] = []
        icons = ["Time", "FFT", "Lap", "Filt", "DSP", "Mic", "File", "Help"]
        tips = ["时域分析 Time", "傅里叶 FFT", "拉普拉斯 Laplace",
                "滤波器 Filter", "DSP 频谱", "实时音频 Mic", "文件导入 File",
                "帮助 Help"]

        for i, (icon, tip) in enumerate(zip(icons, tips)):
            btn = QPushButton(icon)
            btn.setFixedSize(48, 40)
            btn.setToolTip(tip)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton { background: transparent; border: none; font-size: 11px;
                    font-weight: bold; color: #858585; border-radius: 4px; padding: 2px; }
                QPushButton:hover { background: #444; color: #ccc; }
                QPushButton:checked { background: #37373d; color: #fff;
                    border-left: 2px solid #007acc; }
            """)
            btn.clicked.connect(lambda checked, idx=i: self._on_click(idx))
            self.buttons.append(btn)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        self.buttons[0].setChecked(True)

    def _on_click(self, idx):
        for i, b in enumerate(self.buttons):
            b.setChecked(i == idx)
        self.tab_changed.emit(idx)
