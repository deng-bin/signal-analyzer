"""实时音频面板 — 麦克风录制 + 波形/频谱显示"""
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QApplication,
)
from PyQt6.QtCore import Qt
from plot_canvas import InteractiveCanvas
from signal_engine import Signal


class AudioPanel(QWidget):
    """实时音频录制与分析面板"""

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.stream = None
        self.recording = False
        self.audio_data = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel(
            "实时音频输入 — 需要麦克风权限\n使用 sounddevice 库采集音频"
        )
        info.setStyleSheet("color: #888; font-size: 14px; padding: 20px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        ctrl = QHBoxLayout()
        self.btn_record = QPushButton("Rec 录制 3秒")
        self.btn_record.clicked.connect(self._record)
        self.btn_record.setStyleSheet(
            "QPushButton { background: #d16969; font-size: 14px; padding: 10px 20px; }"
        )
        ctrl.addStretch()
        ctrl.addWidget(self.btn_record)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.canvas = InteractiveCanvas(nrows=2, ncols=1, figsize=(10, 5), dark=True)
        layout.addWidget(self.canvas, 1)

    def _record(self):
        try:
            import sounddevice as sd

            fs = 44100
            duration = 3
            self.btn_record.setEnabled(False)
            self.btn_record.setText("Rec 录制中...")
            QApplication.processEvents()

            data = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()
            data = data.flatten()
            t = np.arange(len(data)) / fs

            sig = Signal(
                name=f"audio_{len(self.manager.signals)}",
                t=t, y=data, fs=fs,
                signal_type="discrete",
                description="麦克风录音",
            )
            self.manager.add(sig)

            self.canvas.clear_all()
            self.canvas.axes[0].plot(t, data, '#569cd6', lw=0.8)
            self.canvas.axes[0].set_xlabel("Time (s)")
            self.canvas.axes[0].set_ylabel("Amplitude")
            self.canvas.axes[0].grid(True, alpha=0.3)

            Y = np.fft.fft(data)
            freqs = np.fft.fftfreq(len(data), d=1 / fs)
            half = len(data) // 2
            self.canvas.axes[1].plot(
                freqs[:half],
                20 * np.log10(np.abs(Y[:half]) / len(data) * 2 + 1e-15),
                '#dcdcaa', lw=0.8,
            )
            self.canvas.axes[1].set_xlabel("Freq (Hz)")
            self.canvas.axes[1].set_ylabel("dB")
            self.canvas.axes[1].set_xlim(0, fs / 2)
            self.canvas.axes[1].grid(True, alpha=0.3)
            self.canvas.refresh()
        except Exception as e:
            QMessageBox.warning(self, "音频错误", str(e))
        finally:
            self.btn_record.setEnabled(True)
            self.btn_record.setText("Rec 录制 3秒")
