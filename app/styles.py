COLORS = {

    "sidebar_bg":           "#16293A",
    "sidebar_header_bg":    "#0F1F2E",
    "sidebar_border":       "#1E3A4E",
    "sidebar_hover":        "#1E3A4E",
    "sidebar_active":       "#243F54",

    "content_bg":           "#F7F5F0",
    "surface":              "#FFFFFF",
    "surface_alt":          "#FAF8F4",
    "border":               "#E8E3D8",
    "border_light":         "#F0ECE4",

    "text_primary":         "#1A2B38",
    "text_secondary":       "#6B7A85",
    "text_muted":           "#A0AAB0",
    "text_sidebar":         "#D0DCE4",
    "text_sidebar_muted":   "#7A9EB0",

    "gold":                 "#C9A84C",
    "gold_light":           "#F0DFA0",
    "gold_dark":            "#A07828",
    "gold_bg":              "#FDF8EC",

    "danger":               "#D94040",
    "danger_bg":            "#FEF2F2",
    "danger_border":        "#FABABA",

    "warning":              "#B07B10",
    "warning_bg":           "#FFFBEB",
    "warning_border":       "#F5D68A",

    "success":              "#1A7A50",
    "success_bg":           "#F0FDF8",
    "success_border":       "#86EFCA",

    "info":                 "#1A6E9E",
    "info_bg":              "#EFF8FF",
    "info_border":          "#BAE0F5",

    "teal":                 "#2A8AB4",
    "teal_light":           "#BFE4F4",
}

APP_STYLE = """
/* ════════════════════════════════════════════════
   BASE & RESET
   ════════════════════════════════════════════════ */
* {
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    outline: none;
}
QMainWindow, QDialog {
    background-color: #F7F5F0;
    color: #1A2B38;
}
QWidget {
    color: #1A2B38;
    background: transparent;
}
QLabel      { background: transparent; }
QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }

/* ════════════════════════════════════════════════
   SIDEBAR  (kiri — deep navy teal)
   ════════════════════════════════════════════════ */
#sidebar {
    background-color: #16293A;
    border-right: 1px solid #1E3A4E;
    min-width: 300px;
    max-width: 340px;
}
#sidebar_brand {
    background-color: #0F1F2E;
    border-bottom: 2px solid #C9A84C;
    padding: 0px;
}
#brand_title {
    font-size: 15px; font-weight: 800;
    color: #FFFFFF; letter-spacing: 1.2px;
}
#brand_sub {
    font-size: 10px; color: #C9A84C;
    letter-spacing: 2.5px; margin-top: 2px;
}
#brand_version_badge {
    background-color: rgba(201,168,76,0.15);
    border: 1px solid rgba(201,168,76,0.4);
    color: #C9A84C; font-size: 10px; font-weight: 600;
    border-radius: 4px; padding: 1px 7px;
}
#step_badge {
    background-color: #C9A84C; color: #0F1F2E;
    font-size: 10px; font-weight: 800; border-radius: 11px;
    min-width: 22px; max-width: 22px; min-height: 22px; max-height: 22px;
}
#step_badge_done {
    background-color: #1A7A50; color: #FFFFFF;
    font-size: 10px; font-weight: 800; border-radius: 11px;
    min-width: 22px; max-width: 22px; min-height: 22px; max-height: 22px;
}
#step_title {
    font-size: 11px; font-weight: 700; color: #C9A84C;
    letter-spacing: 1.2px; text-transform: uppercase;
}
#step_divider {
    background-color: rgba(255,255,255,0.06);
    max-height: 1px; min-height: 1px; margin: 8px 0;
}
#sidebar_label {
    font-size: 11px; color: #7A9EB0;
    font-weight: 600; letter-spacing: 0.3px; margin-bottom: 2px;
}

/* ════════════════════════════════════════════════
   INPUTS (dalam sidebar)
   ════════════════════════════════════════════════ */
#sidebar QLineEdit,
#sidebar QDoubleSpinBox,
#sidebar QSpinBox,
#sidebar QComboBox {
    background-color: #1E3A4E; border: 1.5px solid #2A4F65;
    border-radius: 8px; padding: 8px 11px; color: #E8EFF4;
    font-size: 12px;
    selection-background-color: #C9A84C; selection-color: #0F1F2E;
}
#sidebar QLineEdit:focus,
#sidebar QDoubleSpinBox:focus,
#sidebar QSpinBox:focus {
    border-color: #C9A84C; background-color: #172D40;
}
#sidebar QLineEdit[readOnly="true"] {
    color: #7A9EB0; background-color: #172030; border-color: #1E3A4E;
}
#sidebar QLineEdit::placeholder { color: #3A6070; }
#sidebar QDoubleSpinBox::up-button, #sidebar QDoubleSpinBox::down-button,
#sidebar QSpinBox::up-button,       #sidebar QSpinBox::down-button {
    background-color: #2A4F65; border: none; width: 18px;
    border-radius: 3px; margin: 2px 2px 2px 0;
}
#sidebar QDoubleSpinBox::up-button:hover, #sidebar QDoubleSpinBox::down-button:hover,
#sidebar QSpinBox::up-button:hover,        #sidebar QSpinBox::down-button:hover {
    background-color: #C9A84C;
}

/* ════════════════════════════════════════════════
   BUTTONS
   ════════════════════════════════════════════════ */
#btn_run {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #D9B65C, stop:1 #B89030);
    color: #0F1F2E; border: none; border-radius: 10px;
    font-size: 13px; font-weight: 800; padding: 13px 0; letter-spacing: 0.5px;
}
#btn_run:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #EAC464, stop:1 #C9A03C);
}
#btn_run:pressed  { background-color: #A07828; }
#btn_run:disabled { background: #243F54; color: #3A6070; }

#btn_stop {
    background-color: transparent; color: #E07878;
    border: 1.5px solid #E07878; border-radius: 10px;
    font-size: 12px; font-weight: 700; padding: 10px 0;
}
#btn_stop:hover    { background-color: #D94040; color: #FFFFFF; border-color: #D94040; }
#btn_stop:disabled { color: #2A4F65; border-color: #2A4F65; }

#btn_browse {
    background-color: #1E3A4E; color: #90C4DC;
    border: 1.5px solid #2A4F65; border-radius: 8px;
    font-size: 11px; font-weight: 600; padding: 8px 14px; min-width: 80px;
}
#btn_browse:hover { background-color: #2A4F65; color: #E8EFF4; border-color: #4A7A90; }

#btn_map {
    background-color: #142D22; color: #4EC89A;
    border: 1.5px solid #1E5040; border-radius: 8px;
    font-size: 11px; font-weight: 600; padding: 8px 14px;
}
#btn_map:hover { background-color: #1E5040; color: #7ADFB8; border-color: #3A7A64; }

#btn_output {
    background-color: #FFFFFF; color: #1A2B38;
    border: 1.5px solid #E8E3D8; border-radius: 9px;
    font-size: 11px; font-weight: 600; padding: 10px 14px; text-align: left;
}
#btn_output:hover    { background-color: #FDF8EC; border-color: #C9A84C; color: #8B6914; }
#btn_output:disabled { color: #BFBAB0; border-color: #EAE6DE; background-color: #FAF8F4; }

/* ── Point selector buttons (di header dashboard) ── */
#point_selector_btn {
    background-color: #F4F1EA; color: #6B7A85;
    border: 1.5px solid #DED9CF; border-radius: 14px;
    font-size: 11px; font-weight: 600; padding: 3px 12px;
}
#point_selector_btn:hover { background-color: #FDF8EC; border-color: #C9A84C; color: #8B6914; }

#point_selector_btn_active {
    background-color: #FDF8EC; color: #8B6914;
    border: 1.5px solid #C9A84C; border-radius: 14px;
    font-size: 11px; font-weight: 700; padding: 3px 12px;
}

/* ════════════════════════════════════════════════
   ADVANCED SETTINGS COLLAPSIBLE
   ════════════════════════════════════════════════ */
#adv_toggle {
    background-color: rgba(255,255,255,0.04); color: #7A9EB0;
    border: 1.5px solid #243F54; border-radius: 8px;
    font-size: 11px; font-weight: 600; padding: 8px 12px; text-align: left;
}
#adv_toggle:hover { color: #B0D0E0; border-color: #3A6880; background-color: #1E3A4E; }
#adv_content {
    background-color: #0F1F2E; border: 1.5px solid #1E3A4E;
    border-radius: 9px; margin-top: 2px;
}
#adv_param_label { color: #7A9EB0; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; }
#adv_param_hint  { color: #3A5868; font-size: 10px; font-style: italic; line-height: 1.4; }

/* ════════════════════════════════════════════════
   LOCATION PREVIEW CARD
   ════════════════════════════════════════════════ */
#loc_preview_card {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0E2D1F, stop:1 #142A1A);
    border: 1.5px solid #1A5038; border-radius: 10px; padding: 10px 14px;
}
#loc_preview_icon   { font-size: 20px; }
#loc_preview_name   { color: #6ADBA8; font-size: 12px; font-weight: 700; }
#loc_preview_coords { color: #3A8C68; font-size: 10px; font-family: 'Cascadia Code','Consolas',monospace; margin-top: 2px; }

/* ════════════════════════════════════════════════
   VIDEO PREVIEW CARD
   ════════════════════════════════════════════════ */
#video_preview_card {
    background-color: #1E3A4E; border: 1.5px solid #2A4F65;
    border-radius: 10px; padding: 10px 14px;
}
#video_preview_name { color: #E8EFF4; font-size: 12px; font-weight: 600; }
#video_preview_meta { color: #5A8899; font-size: 10px; font-family: 'Cascadia Code','Consolas',monospace; margin-top: 2px; }

/* ════════════════════════════════════════════════
   CONTENT AREA (kanan)
   ════════════════════════════════════════════════ */
#content_area { background-color: #F7F5F0; }
#content_header {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E8E3D8;
    padding: 16px 24px;
}
#content_title    { font-size: 18px; font-weight: 700; color: #1A2B38; letter-spacing: 0.3px; }
#content_subtitle { font-size: 12px; color: #7A8A94; margin-top: 3px; }

/* ════════════════════════════════════════════════
   EMPTY STATE
   ════════════════════════════════════════════════ */
#empty_state { background: transparent; }
#empty_icon  { font-size: 64px; margin-bottom: 8px; }
#empty_title { font-size: 22px; font-weight: 700; color: #1A2B38; margin-bottom: 6px; }
#empty_desc  { font-size: 13px; color: #7A8A94; line-height: 1.6; margin-bottom: 24px; }
#empty_hint_card  { background-color: #FFFFFF; border: 1px solid #E8E3D8; border-radius: 12px; max-width: 360px; }
#empty_hint_title { font-size: 10px; font-weight: 800; color: #C9A84C; letter-spacing: 2px; text-transform: uppercase; }
#empty_hint_step  { font-size: 12px; color: #4A5A66; line-height: 1.7; }

/* ════════════════════════════════════════════════
   STATUS BAR
   ════════════════════════════════════════════════ */
#status_bar_widget { background-color: #FFFFFF; border-top: 1px solid #E8E3D8; }
#status_dot_idle    { color: #A0AAB0; font-size: 10px; }
#status_dot_running { color: #2A8AB4; font-size: 10px; }
#status_dot_done    { color: #1A7A50; font-size: 10px; }
#status_dot_error   { color: #D94040; font-size: 10px; }
#status_text_idle    { color: #A0AAB0; font-size: 12px; }
#status_text_running { color: #1A6E9E; font-size: 12px; font-weight: 700; }
#status_text_done    { color: #1A7A50; font-size: 12px; font-weight: 700; }
#status_text_error   { color: #D94040; font-size: 12px; font-weight: 700; }
#status_time { color: #A0AAB0; font-size: 11px; font-family: 'Cascadia Code','Consolas',monospace; }

/* ════════════════════════════════════════════════
   PROGRESS BAR
   ════════════════════════════════════════════════ */
QProgressBar {
    background-color: #EAE6DE; border: none; border-radius: 3px; font-size: 0px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2A8AB4, stop:1 #3ABF90);
    border-radius: 3px;
}

/* ════════════════════════════════════════════════
   LOG AREA
   ════════════════════════════════════════════════ */
#log_area {
    background-color: #0F1F2E; border: none;
    color: #6A9EB8; font-family: 'Cascadia Code','Consolas','Courier New',monospace;
    font-size: 11px; padding: 10px 16px;
    selection-background-color: #243F54; line-height: 1.5;
}
#log_header       { background-color: #0A1820; border-top: 1px solid #1E3A4E; }
#log_header_label { font-size: 10px; font-weight: 700; color: #3A6070; letter-spacing: 1.8px; text-transform: uppercase; }

/* ════════════════════════════════════════════════
   METRIC CARDS
   ════════════════════════════════════════════════ */
#metric_card {
    background-color: #FFFFFF; border: 1.5px solid #EAE6DE;
    border-radius: 14px; padding: 18px 20px;
}
#metric_card:hover { border-color: #C9A84C; background-color: #FFFDF8; }
#card_icon_bg {
    background-color: #F4F1EA; border-radius: 12px;
    min-width: 44px; max-width: 44px; min-height: 44px; max-height: 44px;
}
#card_icon_lbl  { font-size: 22px; }
#card_label     { font-size: 10px; font-weight: 700; color: #9AA5AE; letter-spacing: 1.5px; text-transform: uppercase; }
#card_value     { font-size: 30px; font-weight: 800; color: #1A2B38; line-height: 1.1; }
#card_unit      { font-size: 11px; color: #B0B8BE; margin-top: 2px; }
#card_trend_up   { color: #D94040; font-size: 10px; font-weight: 600; }
#card_trend_down { color: #1A7A50; font-size: 10px; font-weight: 600; }
#card_trend_flat { color: #B0B8BE; font-size: 10px; }

/* ════════════════════════════════════════════════
   LABEL BADGES
   ════════════════════════════════════════════════ */
#crowd_badge_container {
    background-color: #FFFFFF; border: 1.5px solid #EAE6DE;
    border-radius: 14px; padding: 16px 18px;
}
#crowd_badge_title { font-size: 10px; font-weight: 700; color: #9AA5AE; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px; }
#badge_high     { background-color: #FEF2F2; border: 2px solid #FABABA; border-radius: 10px; color: #C02020; font-size: 16px; font-weight: 800; padding: 10px 24px; letter-spacing: 1px; }
#badge_medium   { background-color: #FFFBEB; border: 2px solid #F5D68A; border-radius: 10px; color: #986010; font-size: 16px; font-weight: 800; padding: 10px 24px; letter-spacing: 1px; }
#badge_low      { background-color: #F0FDF8; border: 2px solid #86EFCA; border-radius: 10px; color: #1A7A50; font-size: 16px; font-weight: 800; padding: 10px 24px; letter-spacing: 1px; }
#badge_neutral  { background-color: #F7F5F0; border: 2px solid #DED9CF; border-radius: 10px; color: #9AA5AE; font-size: 15px; font-weight: 700; padding: 10px 24px; letter-spacing: 1px; }
#badge_tersendat{ background-color: #FEF2F2; border: 2px solid #FABABA; border-radius: 10px; color: #C02020; font-size: 14px; font-weight: 700; padding: 8px 18px; }
#badge_lancar   { background-color: #F0FDF8; border: 2px solid #86EFCA; border-radius: 10px; color: #1A7A50; font-size: 14px; font-weight: 700; padding: 8px 18px; }

/* Alert strips */
#alert_strip_high   { background-color: #FEF2F2; border: none; border-left: 4px solid #D94040; border-radius: 0 8px 8px 0; padding: 8px 14px; }
#alert_strip_medium { background-color: #FFFBEB; border: none; border-left: 4px solid #C9A84C; border-radius: 0 8px 8px 0; padding: 8px 14px; }
#alert_strip_low    { background-color: #F0FDF8; border: none; border-left: 4px solid #1A7A50; border-radius: 0 8px 8px 0; padding: 8px 14px; }
#alert_strip_text   { font-size: 12px; font-weight: 600; color: #1A2B38; }

/* ════════════════════════════════════════════════
   TAB WIDGET
   Main tabs (Peta / Dashboard) — lebih besar, prominent
   ════════════════════════════════════════════════ */

/* Main tab widget khusus */
#main_tab_widget::pane {
    background-color: transparent;
    border: none;
    top: 0;
}
#main_tab_widget QTabBar::tab {
    background-color: #1E3A4E;
    color: #7A9EB0;
    font-size: 12px; font-weight: 600;
    padding: 11px 24px;
    border: none;
    border-right: 1px solid #243F54;
    border-bottom: 2px solid transparent;
    margin: 0;
    min-width: 160px;
}
#main_tab_widget QTabBar::tab:selected {
    background-color: #0F1F2E;
    color: #C9A84C;
    border-bottom: 2px solid #C9A84C;
    font-weight: 700;
}
#main_tab_widget QTabBar::tab:hover:!selected {
    background-color: #243F54;
    color: #D0DCE4;
}
#main_tab_widget QTabBar {
    background-color: #16293A;
    border-bottom: 1px solid #1E3A4E;
}

/* Inner tabs (Data Window / Trend) */
QTabWidget::pane {
    background-color: #FFFFFF;
    border: 1.5px solid #EAE6DE;
    border-radius: 0 12px 12px 12px;
    top: -1px;
}
QTabBar::tab {
    background-color: #F0EDE5; color: #8A9AA4;
    font-size: 11px; font-weight: 600; padding: 9px 20px;
    border: 1.5px solid #E0DCD4; border-bottom: none;
    border-radius: 8px 8px 0 0; margin-right: 3px;
}
QTabBar::tab:selected {
    background-color: #FFFFFF; color: #1A2B38;
    border-bottom-color: #FFFFFF; border-top: 2.5px solid #C9A84C;
    font-weight: 700;
}
QTabBar::tab:hover:!selected { background-color: #EDE9E0; color: #4A3A1A; }

/* ════════════════════════════════════════════════
   TABLE
   ════════════════════════════════════════════════ */
QTableWidget {
    background-color: #FFFFFF; border: none;
    gridline-color: #F4F1EA; color: #1A2B38; font-size: 12px;
    selection-background-color: #FDF8EC; alternate-background-color: #FAF8F4;
}
QTableWidget::item { padding: 8px 12px; border-bottom: 1px solid #F4F1EA; }
QTableWidget::item:selected { background-color: #FDF8EC; color: #5A3A00; }
QHeaderView::section {
    background-color: #F4F1EA; color: #6A7A84;
    font-size: 10px; font-weight: 700; letter-spacing: 0.8px;
    text-transform: uppercase; padding: 10px 12px;
    border: none; border-right: 1px solid #E8E3D8; border-bottom: 2px solid #C9A84C;
}

/* ════════════════════════════════════════════════
   MAP DIALOG
   ════════════════════════════════════════════════ */
#map_dialog      { background-color: #FFFFFF; }
#map_toolbar     { background-color: #F7F5F0; border-bottom: 1px solid #E8E3D8; }
#map_instruction { font-size: 12px; color: #5A4A2A; font-weight: 500; }
#map_coord_display {
    background-color: #1A2B38; color: #7A9EB0;
    font-size: 11px; font-family: 'Cascadia Code','Consolas',monospace;
    border-radius: 7px; padding: 6px 14px;
}
#btn_map_confirm { background-color: #1A7A50; color: #FFFFFF; border: none; border-radius: 8px; font-size: 12px; font-weight: 700; padding: 9px 22px; }
#btn_map_confirm:hover    { background-color: #15895A; }
#btn_map_confirm:disabled { background-color: #C0C0B8; color: #888888; }
#btn_map_cancel {
    background-color: transparent; color: #8A9AA4;
    border: 1.5px solid #DED9CF; border-radius: 8px;
    font-size: 12px; padding: 9px 22px;
}
#btn_map_cancel:hover { background-color: #F0EDE5; }

/* ════════════════════════════════════════════════
   MONITORING MAP CONTAINER
   ════════════════════════════════════════════════ */
#monitor_map_container {
    background-color: #0F1F2E;
    border: none;
}

/* ════════════════════════════════════════════════
   SCROLLBAR
   ════════════════════════════════════════════════ */
QScrollBar:vertical { background: transparent; width: 6px; border-radius: 3px; margin: 2px; }
QScrollBar::handle:vertical { background-color: #DED9CF; border-radius: 3px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background-color: #B0ABA0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 6px; }
QScrollBar::handle:horizontal { background-color: #DED9CF; border-radius: 3px; }

/* ════════════════════════════════════════════════
   TOOLTIP
   ════════════════════════════════════════════════ */
QToolTip {
    background-color: #1A2B38; color: #E8EFF4;
    border: 1px solid #C9A84C; border-radius: 6px;
    font-size: 11px; padding: 6px 10px;
}

/* ════════════════════════════════════════════════
   SPLITTER
   ════════════════════════════════════════════════ */
QSplitter::handle:horizontal { background-color: #DED9CF; width: 1px; }

/* ════════════════════════════════════════════════
   MESSAGE BOX
   ════════════════════════════════════════════════ */
QMessageBox { background-color: #F7F5F0; }
QMessageBox QLabel { color: #1A2B38; font-size: 13px; }
QMessageBox QPushButton {
    background-color: #1A2B38; color: #F7F5F0;
    border: none; border-radius: 7px; padding: 8px 20px;
    font-weight: 600; min-width: 80px;
}
QMessageBox QPushButton:hover { background-color: #243F54; }
"""