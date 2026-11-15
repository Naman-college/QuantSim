"""
theme.py - Linear.app Aesthetic Design System & Qt Style Sheet (QSS).
Maintained by Member 4 (UI/UX Developer).
"""

# Linear Color Tokens
COLOR_CANVAS = "#08090A"           # App background
COLOR_SURFACE = "#0F1012"          # Panels and card background
COLOR_SURFACE_ELEVATED = "#16181D" # Elevated modals, dropdowns
COLOR_BORDER = "#232530"           # Subtle 1px crisp borders
COLOR_BORDER_FOCUS = "#3B3F50"     # Active input borders

COLOR_ACCENT = "#5E6AD2"           # Linear signature electric indigo
COLOR_ACCENT_HOVER = "#7170FF"     # Lighter indigo hover state
COLOR_ACCENT_MUTED = "rgba(94, 106, 210, 0.15)"

COLOR_SUCCESS = "#27C384"          # Profit green
COLOR_DANGER = "#F43F5E"           # Drawdown / loss red
COLOR_WARNING = "#F59E0B"          # Cash / neutral amber

COLOR_TEXT_PRIMARY = "#F3F4F6"     # High contrast primary text
COLOR_TEXT_SECONDARY = "#8A8F98"   # Muted labels and subtitles
COLOR_TEXT_MUTED = "#525866"       # Disabled / hint text

# Comprehensive Linear.app Qt Style Sheet
LINEAR_STYLESHEET = f"""
QMainWindow {{
    background-color: {COLOR_CANVAS};
}}

QWidget {{
    background-color: {COLOR_CANVAS};
    color: {COLOR_TEXT_PRIMARY};
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
    font-size: 13px;
}}

/* Surface Panels */
QFrame#sidebarPanel, QFrame#cardPanel, QFrame#chartContainer {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
}}

/* Typography */
QLabel#sectionHeader {{
    color: {COLOR_TEXT_SECONDARY};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel#metricTitle {{
    color: {COLOR_TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 500;
}}

QLabel#metricValue {{
    color: {COLOR_TEXT_PRIMARY};
    font-size: 20px;
    font-weight: 700;
    font-family: "JetBrains Mono", "Consolas", monospace;
}}

/* Buttons */
QPushButton {{
    background-color: {COLOR_SURFACE_ELEVATED};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 500;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: #1F2128;
    border-color: {COLOR_BORDER_FOCUS};
}}

QPushButton:pressed {{
    background-color: #16171D;
}}

QPushButton#primaryButton {{
    background-color: {COLOR_ACCENT};
    color: #FFFFFF;
    border: 1px solid {COLOR_ACCENT_HOVER};
    font-weight: 600;
}}

QPushButton#primaryButton:hover {{
    background-color: {COLOR_ACCENT_HOVER};
}}

/* Inputs, ComboBoxes, and DateEdits */
QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {{
    background-color: {COLOR_SURFACE_ELEVATED};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
    border: 1px solid {COLOR_ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLOR_SURFACE_ELEVATED};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER};
    selection-background-color: {COLOR_ACCENT};
    selection-color: #FFFFFF;
    outline: none;
    padding: 4px;
}}

/* Tabs */
QTabWidget::pane {{
    border: 1px solid {COLOR_BORDER};
    background-color: {COLOR_SURFACE};
    border-radius: 8px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLOR_TEXT_SECONDARY};
    padding: 8px 16px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    color: {COLOR_TEXT_PRIMARY};
    border-bottom: 2px solid {COLOR_ACCENT};
}}

QTabBar::tab:hover:!selected {{
    color: {COLOR_TEXT_PRIMARY};
}}

/* ScrollBars */
QScrollBar:vertical {{
    background: {COLOR_CANVAS};
    width: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLOR_BORDER_FOCUS};
    min-height: 20px;
    border-radius: 3px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Tables */
QTableWidget {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    gridline-color: {COLOR_BORDER};
    color: {COLOR_TEXT_PRIMARY};
    font-family: "JetBrains Mono", "Consolas", monospace;
    font-size: 12px;
}}

QHeaderView::section {{
    background-color: {COLOR_SURFACE_ELEVATED};
    color: {COLOR_TEXT_SECONDARY};
    border: none;
    border-bottom: 1px solid {COLOR_BORDER};
    padding: 6px;
    font-family: "Inter", sans-serif;
    font-size: 11px;
    font-weight: 600;
}}

/* Splitters for Dynamic Drag & Resize Tiles */
QSplitter::handle {{
    background-color: {COLOR_BORDER};
}}

QSplitter::handle:hover {{
    background-color: {COLOR_ACCENT};
}}

QSplitter::handle:pressed {{
    background-color: {COLOR_ACCENT_HOVER};
}}

QSplitter::handle:horizontal {{
    width: 6px;
}}

QSplitter::handle:vertical {{
    height: 6px;
}}

/* CheckBoxes */
QCheckBox {{
    color: {COLOR_TEXT_PRIMARY};
    spacing: 8px;
    font-size: 12px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    background-color: {COLOR_SURFACE_ELEVATED};
}}

QCheckBox::indicator:hover {{
    border-color: {COLOR_ACCENT};
}}

QCheckBox::indicator:checked {{
    background-color: {COLOR_ACCENT};
    border-color: {COLOR_ACCENT};
}}
"""

