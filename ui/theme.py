"""VS Code 风格暗色主题 CSS"""

DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #1e1e1e;
    color: #cccccc;
}
QWidget {
    background-color: #1e1e1e;
    color: #cccccc;
    font-size: 12px;
}
QMenuBar {
    background-color: #2d2d2d;
    color: #cccccc;
    border-bottom: 1px solid #3c3c3c;
}
QMenuBar::item:selected {
    background-color: #094771;
}
QMenu {
    background-color: #2d2d2d;
    color: #cccccc;
    border: 1px solid #3c3c3c;
}
QMenu::item:selected {
    background-color: #094771;
}
QTabWidget::pane {
    border: 1px solid #3c3c3c;
    background-color: #1e1e1e;
}
QTabBar::tab {
    background-color: #2d2d2d;
    color: #969696;
    padding: 6px 16px;
    border: 1px solid #3c3c3c;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #ffffff;
    border-bottom: 2px solid #007acc;
}
QTabBar::tab:hover:!selected {
    background-color: #333333;
}
QGroupBox {
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 12px;
    font-weight: bold;
    color: #cccccc;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #569cd6;
}
QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    padding: 6px 14px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1177bb;
}
QPushButton:pressed {
    background-color: #094771;
}
QPushButton:disabled {
    background-color: #3c3c3c;
    color: #666;
}
QComboBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px 8px;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #cccccc;
    selection-background-color: #094771;
}
QSpinBox, QDoubleSpinBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px;
}
QLineEdit {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px 8px;
}
QTextEdit {
    background-color: #1e1e1e;
    color: #cccccc;
    border: 1px solid #3c3c3c;
}
QListWidget, QTreeWidget {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    outline: none;
}
QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #094771;
}
QListWidget::item:hover, QTreeWidget::item:hover {
    background-color: #2a2d2e;
}
QSplitter::handle {
    background-color: #3c3c3c;
    width: 2px;
}
QScrollBar:vertical {
    background: #1e1e1e;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #424242;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QStatusBar {
    background-color: #007acc;
    color: white;
    font-size: 11px;
}
QDockWidget {
    color: #cccccc;
    titlebar-close-icon: none;
}
QDockWidget::title {
    background-color: #252526;
    padding: 4px 8px;
    border-bottom: 1px solid #3c3c3c;
}
QLabel {
    color: #cccccc;
}
QCheckBox {
    color: #cccccc;
}
QRadioButton {
    color: #cccccc;
}
QSlider::groove:horizontal {
    background: #3c3c3c;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #569cd6;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
"""
