#!/usr/bin/env python3
"""
信号分析工具箱 v2.1 — VS Code 风格界面（重构版）
活动栏 | 侧面板 | 中央标签页 | 底部面板 | 状态栏
"""
import sys
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QTabWidget, QSplitter, QFileDialog, QMessageBox,
    QStatusBar, QDockWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction

import matplotlib
matplotlib.use('QtAgg')

from ui.theme import DARK_STYLE
from ui.logger import log, op, err, warn
from ui.activity_bar import ActivityBar
from ui.panels.signal_panel import SignalManager, SignalGenPanel
from ui.panels.time_panel import TimeDomainPanel
from ui.panels.fourier_panel import FourierPanel
from ui.panels.laplace_panel import LaplacePanel
from ui.panels.filter_panel import FilterPanel
from ui.panels.dsp_panel import DSPPanel
from ui.panels.audio_panel import AudioPanel
from ui.panels.import_panel import ImportPanel
from ui.panels.help_panel import HelpPanel
from signal_engine import SignalGenerator


class MainWindow(QMainWindow):
    """主窗口 — VS Code 风格信号分析工具箱"""

    def __init__(self):
        super().__init__()
        self.manager = SignalManager()
        self.setWindowTitle("信号分析工具箱 v2.1 — Signal Analyzer Pro")
        self.resize(1360, 820)
        self.setMinimumSize(1000, 600)
        op("app_init", size=f"{1360}x{820}")

        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width() - 1360) // 2, (screen.height() - 820) // 2)

        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()

        # 默认生成一个信号
        try:
            sig = SignalGenerator.multi_tone([5, 20, 50], [1, 0.5, 0.3])
            self.manager.add(sig)
            self.signal_panel._refresh_list()
            self.signal_panel.signal_changed.emit()
            op("default_signal", name=sig.name)
        except Exception as e:
            err("default_signal_fail", e)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 活动栏
        self.activity_bar = ActivityBar()
        main_layout.addWidget(self.activity_bar)

        # 左侧面板（信号管理）
        self.signal_panel = SignalGenPanel(self.manager)
        self.signal_panel.signal_changed.connect(self._on_signal_changed)
        left_dock = QDockWidget("信号资源管理器")
        left_dock.setWidget(self.signal_panel)
        left_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        left_dock.setMinimumWidth(280)
        left_dock.setStyleSheet("QDockWidget::title { background: #252526; text-align: left; }")

        # 中央标签页
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.time_panel = TimeDomainPanel(self.manager)
        self.fourier_panel = FourierPanel(self.manager)
        self.laplace_panel = LaplacePanel(self.manager)
        self.filter_panel = FilterPanel(self.manager)
        self.dsp_panel = DSPPanel(self.manager)
        self.audio_panel = AudioPanel(self.manager)
        self.import_panel = ImportPanel(self.manager)
        self.import_panel.signal_imported.connect(self._on_signal_changed)
        self.help_panel = HelpPanel()

        self.tabs.addTab(self.time_panel, "Time 时域")
        self.tabs.addTab(self.fourier_panel, "FFT 傅里叶")
        self.tabs.addTab(self.laplace_panel, "Lap 拉普拉斯")
        self.tabs.addTab(self.filter_panel, "Filt 滤波器")
        self.tabs.addTab(self.dsp_panel, "DSP 频谱")
        self.tabs.addTab(self.audio_panel, "Mic 音频")
        self.tabs.addTab(self.import_panel, "File 导入")
        self.tabs.addTab(self.help_panel, "Help 帮助")

        # 活动栏切换标签页
        self.activity_bar.tab_changed.connect(
            lambda i: self.tabs.setCurrentIndex(min(i, self.tabs.count() - 1))
        )

        # 信号变更时自动刷新时域面板
        self.manager.on_change(lambda: self.time_panel.plot())

        # 组装布局
        right_splitter = QSplitter(Qt.Orientation.Horizontal)
        right_splitter.addWidget(left_dock)
        right_splitter.addWidget(self.tabs)
        right_splitter.setSizes([300, 1200])
        main_layout.addWidget(right_splitter)

    def _setup_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("QMenuBar { background: #2d2d2d; color: #ccc; }")

        file_menu = menubar.addMenu("文件")
        for text, slot in [
            ("导入CSV", lambda: self._import("csv")),
            ("导入WAV", lambda: self._import("wav")),
            ("导入MAT", lambda: self._import("mat")),
            ("导出CSV", self._export_csv),
            ("导出图片", self._export_fig),
        ]:
            act = QAction(text, self)
            act.triggered.connect(slot)
            file_menu.addAction(act)
        file_menu.addSeparator()
        act_quit = QAction("退出", self)
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        help_menu = menubar.addMenu("帮助")
        act_about = QAction("关于", self)
        act_about.triggered.connect(lambda: QMessageBox.about(
            self, "关于",
            "信号分析工具箱 v2.1\n\n"
            "🎯 20+种信号类型 | 10+种分析方法\n"
            "FIR/IIR滤波器设计 | 实时音频\n"
            "📊 CWT/希尔伯特/倒谱/相干性\n"
            "🎨 VS Code 风格暗色界面\n"
            "🔧 重构版: 模块化 UI 架构\n\n"
            "Powered by: PyQt6 + NumPy + SciPy + SymPy + Matplotlib",
        ))
        help_menu.addAction(act_about)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.statusbar.setStyleSheet(
            "QStatusBar { background: #007acc; color: white; }"
        )
        self.statusbar.showMessage("就绪 — 选择一个信号开始分析")
        self.setStatusBar(self.statusbar)

    def _on_signal_changed(self):
        try:
            sel = self.manager.selected
            name = sel.name if sel else 'None'
            n_checked = len(self.manager.checked_signals)
            n_total = len(self.manager.signals)
            self.statusbar.showMessage(
                f"当前信号: {name}  |  已勾选 {n_checked}/{n_total} 个信号"
            )
            # 无勾选信号时清空所有面板
            if n_checked == 0:
                self.fourier_panel.clear_on_empty()
                self.dsp_panel.clear_on_empty()
                self.filter_panel.clear_on_empty()
                self.laplace_panel.clear_on_empty()
        except Exception as e:
            err("statusbar_update", e)

    def _import(self, fmt):
        op("menu_import", format=fmt)
        self.tabs.setCurrentIndex(6)  # File tab

    def _export_csv(self):
        if self.manager.selected:
            path, _ = QFileDialog.getSaveFileName(
                self, "导出CSV", f"{self.manager.selected.name}.csv", "CSV (*.csv)"
            )
            if path:
                try:
                    SignalGenerator.export_csv(self.manager.selected, path)
                    op("export_csv", path=path, name=self.manager.selected.name)
                    self.statusbar.showMessage(f"CSV 已导出: {path}")
                except Exception as e:
                    err("export_csv_fail", e, path=path)
                    QMessageBox.warning(self, "错误", str(e))

    def _export_fig(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "导出图片", "figure.png", "PNG (*.png);;SVG (*.svg)"
        )
        if path:
            try:
                current_tab = self.tabs.currentWidget()
                if hasattr(current_tab, 'canvas'):
                    current_tab.canvas.save_figure(path)
                    op("export_fig", path=path)
                    self.statusbar.showMessage(f"图片已导出: {path}")
                else:
                    warn("export_fig", "no canvas on current tab")
            except Exception as e:
                err("export_fig_fail", e, path=path)
                QMessageBox.warning(self, "错误", str(e))


def main():
    op("app_start")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)

    font = QFont("Microsoft YaHei UI", 9)
    app.setFont(font)
    try:
        import matplotlib
        matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
    except Exception:
        pass
    matplotlib.rcParams['axes.unicode_minus'] = False

    try:
        window = MainWindow()
        window.show()
        op("window_shown")
        exit_code = app.exec()
        op("app_exit", code=exit_code)
        sys.exit(exit_code)
    except Exception as e:
        err("app_crash", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
