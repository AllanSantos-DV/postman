"""
Estilos da aplicação
"""

# Estilo padrão claro
LIGHT_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #f5f5f5;
    color: #212121;
}

QToolBar {
    background-color: #e0e0e0;
    border-bottom: 1px solid #bdbdbd;
    spacing: 5px;
}

QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #bdbdbd;
    border-radius: 3px;
    padding: 5px 15px;
    color: #212121;
}

QPushButton:hover {
    background-color: #d0d0d0;
}

QPushButton:pressed {
    background-color: #bdbdbd;
}

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #bdbdbd;
    border-radius: 3px;
    padding: 3px;
    color: #212121;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f0f0f0;
    border: 1px solid #bdbdbd;
    color: #212121;
}

QTableWidget::item:selected {
    background-color: #bbdefb;
    color: #212121;
}

QHeaderView::section {
    background-color: #e0e0e0;
    border: 1px solid #bdbdbd;
    padding: 4px;
    color: #212121;
}

QTabWidget::pane {
    border: 1px solid #bdbdbd;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #e0e0e0;
    border: 1px solid #bdbdbd;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 5px 10px;
    margin-right: 2px;
    color: #757575;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #212121;
}

QTabBar::tab:!selected {
    margin-top: 2px;
}

QSplitter::handle {
    background-color: #bdbdbd;
}

QTreeView {
    background-color: #ffffff;
    alternate-background-color: #f0f0f0;
    border: 1px solid #bdbdbd;
    color: #212121;
}

QTreeView::item:selected {
    background-color: #bbdefb;
    color: #212121;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #bdbdbd;
    color: #212121;
}

QMenu::item {
    padding: 5px 20px;
}

QMenu::item:selected {
    background-color: #bbdefb;
    color: #212121;
}

QMenuBar {
    background-color: #e0e0e0;
    color: #212121;
}

QMenuBar::item {
    padding: 5px 10px;
    background-color: transparent;
}

QMenuBar::item:selected, QMenuBar::item:pressed {
    background-color: #bbdefb;
    color: #212121;
}

QStatusBar {
    background-color: #e0e0e0;
    color: #212121;
}
"""

# Estilo escuro
DARK_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #121212;
    color: #f5f5f5;
}

QToolBar {
    background-color: #1e1e1e;
    border-bottom: 1px solid #333333;
    spacing: 5px;
}

QPushButton {
    background-color: #2c2c2c;
    border: 1px solid #333333;
    border-radius: 3px;
    padding: 5px 15px;
    color: #f5f5f5;
}

QPushButton:hover {
    background-color: #3c3c3c;
}

QPushButton:pressed {
    background-color: #444444;
}

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #333333;
    border-radius: 3px;
    padding: 3px;
    color: #f5f5f5;
}

QTableWidget {
    background-color: #1e1e1e;
    alternate-background-color: #252525;
    border: 1px solid #333333;
    color: #f5f5f5;
    gridline-color: #333333;
}

QTableWidget::item:selected {
    background-color: #2c5e80;
    color: #f5f5f5;
}

QHeaderView::section {
    background-color: #2c2c2c;
    border: 1px solid #333333;
    padding: 4px;
    color: #f5f5f5;
}

QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #1e1e1e;
}

QTabBar::tab {
    background-color: #2c2c2c;
    border: 1px solid #333333;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 5px 10px;
    margin-right: 2px;
    color: #9e9e9e;
}

QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #f5f5f5;
}

QTabBar::tab:!selected {
    margin-top: 2px;
}

QSplitter::handle {
    background-color: #333333;
}

QTreeView {
    background-color: #1e1e1e;
    alternate-background-color: #252525;
    border: 1px solid #333333;
    color: #f5f5f5;
}

QTreeView::item:selected {
    background-color: #2c5e80;
    color: #f5f5f5;
}

QMenu {
    background-color: #1e1e1e;
    border: 1px solid #333333;
    color: #f5f5f5;
}

QMenu::item {
    padding: 5px 20px;
}

QMenu::item:selected {
    background-color: #2c5e80;
    color: #f5f5f5;
}

QMenuBar {
    background-color: #1e1e1e;
    color: #f5f5f5;
}

QMenuBar::item {
    padding: 5px 10px;
    background-color: transparent;
}

QMenuBar::item:selected, QMenuBar::item:pressed {
    background-color: #2c5e80;
    color: #f5f5f5;
}

QStatusBar {
    background-color: #1e1e1e;
    color: #f5f5f5;
}

QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #3c3c3c;
    min-height: 20px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #505050;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 12px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #3c3c3c;
    min-width: 20px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #505050;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    border: 1px solid #333333;
    color: #f5f5f5;
    selection-background-color: #2c5e80;
    selection-color: #f5f5f5;
}

QListWidget {
    background-color: #1e1e1e;
    alternate-background-color: #252525;
    border: 1px solid #333333;
    color: #f5f5f5;
}

QListWidget::item:selected {
    background-color: #2c5e80;
    color: #f5f5f5;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #0078d7;
}
""" 