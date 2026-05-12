from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QTextEdit, QPushButton, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QTextCursor, QColor


_KONFIGURASI_STATUS = {
    "IDLE":      ("#A0AAB0",  "Siap",                 "color:#A0AAB0;"),
    "RUNNING":   ("#3AB4E0",  "Memproses video...",   "color:#1A8ABE; font-weight:700;"),
    "STOPPING":  ("#E0C040",  "Menghentikan...",      "color:#C9A84C; font-weight:700;"),
    "DONE":      ("#3ABF90",  "Selesai  ✓",           "color:#1A8A60; font-weight:700;"),
    "CANCELLED": ("#E0C040",  "Dihentikan",           "color:#C9A84C; font-weight:600;"),
    "ERROR":     ("#E07878",  "Error",                "color:#C04040; font-weight:700;"),
}

_PESAN_ERROR = {
    "Cannot open video":    "⚠  Video tidak bisa dibuka. Pastikan format didukung.",
    "best.pt":              "⚠  File model (best.pt) tidak ditemukan di folder project.",
    "ModuleNotFoundError":  "⚠  Ada library yang belum terinstall. Cek requirements.",
    "out of memory":        "⚠  Memori tidak cukup. Coba gunakan video resolusi lebih rendah.",
    "CUDA":                 "⚠  GPU tidak tersedia — pipeline berjalan di CPU.",
}


class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("status_bar_widget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._current_state = "IDLE"
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header log
        log_hdr = QWidget()
        log_hdr.setObjectName("log_header")
        lh = QHBoxLayout(log_hdr)
        lh.setContentsMargins(16, 6, 16, 6)

        log_hdr_lbl = QLabel("LOG PROSES")
        log_hdr_lbl.setObjectName("log_header_label")
        lh.addWidget(log_hdr_lbl)
        lh.addStretch()

        clear_btn = QPushButton("Bersihkan")
        clear_btn.setStyleSheet(
            "background: transparent; color: #3A6070; font-size: 10px; "
            "border: none; padding: 0;"
        )
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(lambda: self._log.clear())
        lh.addWidget(clear_btn)
        root.addWidget(log_hdr)

        # Area log
        self._log = QTextEdit()
        self._log.setObjectName("log_area")
        self._log.setReadOnly(True)
        self._log.setFixedHeight(108)
        root.addWidget(self._log)

        # Bar bawah: status + progress
        bot = QWidget()
        bot.setObjectName("status_bar_widget")
        bot.setFixedHeight(46)
        bl = QHBoxLayout(bot)
        bl.setContentsMargins(20, 0, 20, 0)
        bl.setSpacing(8)

        self._dot = QLabel("●")
        self._dot.setStyleSheet("color: #A0AAB0; font-size: 9px;")
        self._dot.setFixedWidth(14)

        self._status_lbl = QLabel("Siap")
        self._status_lbl.setStyleSheet("color: #A0AAB0; font-size: 12px;")

        self._time_lbl = QLabel("")
        self._time_lbl.setObjectName("status_time")

        self._progress = QProgressBar()
        self._progress.setValue(0)
        self._progress.setFixedHeight(4)
        self._progress.setFixedWidth(180)
        self._progress.setTextVisible(False)

        self._frame_lbl = QLabel("")
        self._frame_lbl.setObjectName("status_time")
        self._frame_lbl.setFixedWidth(36)
        self._frame_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        bl.addWidget(self._dot)
        bl.addWidget(self._status_lbl)
        bl.addWidget(self._time_lbl)
        bl.addStretch()
        bl.addWidget(self._frame_lbl)
        bl.addWidget(self._progress)
        root.addWidget(bot)

    def atur_status(self, state: str):
        self._current_state = state
        dot_color, text, lbl_style = _KONFIGURASI_STATUS.get(state, _KONFIGURASI_STATUS["IDLE"])

        self._dot.setStyleSheet(f"color:{dot_color}; font-size:9px;")
        self._status_lbl.setStyleSheet(lbl_style + " font-size:12px;")
        self._status_lbl.setText(text)

        ts = QTime.currentTime().toString("hh:mm:ss")
        self._time_lbl.setText(f"·  {ts}")

        if state in ("IDLE", "CANCELLED"):
            self._progress.setValue(0)
            self._frame_lbl.setText("")

    def set_progress(self, pct: int):
        self._progress.setValue(pct)
        self._frame_lbl.setText(f"{pct}%")

    def tambah_log(self, msg: str):
        self._log.append(msg)
        cursor = self._log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._log.setTextCursor(cursor)

    def tambah_error(self, raw_msg: str):
        # Coba cocokkan dengan pesan error yang sudah dikenal
        for key, friendly in _PESAN_ERROR.items():
            if key.lower() in raw_msg.lower():
                self.tambah_log(friendly)
                return
        first_line = raw_msg.strip().split("\n")[0]
        self.tambah_log(f"❌  {first_line}")

    def clear(self):
        self._log.clear()
        self._progress.setValue(0)
        self._frame_lbl.setText("")
        self.atur_status("IDLE")