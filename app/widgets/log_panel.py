from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QProgressBar, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QTextCursor


class LogPanel(QWidget):

    STATUS_COLORS = {
        "IDLE":     ("⬤", "#64748b"),
        "RUNNING":  ("⬤", "#3b82f6"),
        "STOPPING": ("⬤", "#f59e0b"),
        "DONE":     ("⬤", "#10b981"),
        "CANCELLED":("⬤", "#94a3b8"),
        "ERROR":    ("⬤", "#ef4444"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(6)

        status_row = QHBoxLayout()
        self._dot = QLabel("⬤")
        self._dot.setStyleSheet("color: #64748b; font-size: 10px;")
        self._status_lbl = QLabel("IDLE")
        self._status_lbl.setObjectName("status_indicator")
        self._status_lbl.setStyleSheet("color: #64748b;")
        self._time_lbl = QLabel("")
        self._time_lbl.setStyleSheet("color: #4a5568; font-size: 10px;")
        self._time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        status_row.addWidget(self._dot)
        status_row.addWidget(self._status_lbl)
        status_row.addStretch()
        status_row.addWidget(self._time_lbl)
        layout.addLayout(status_row)

        # progres
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # area log
        self.log_area = QTextEdit()
        self.log_area.setObjectName("log_area")
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(100)
        self.log_area.setMaximumHeight(180)
        layout.addWidget(self.log_area)

    def atur_status(self, status: str):
        """status: 'IDLE' | 'RUNNING' | 'DONE' | 'ERROR'"""
        dot_char, color = self.STATUS_COLORS.get(status, ("⬤", "#64748b"))
        self._dot.setStyleSheet(f"color: {color}; font-size: 10px;")
        self._status_lbl.setText(status)
        self._status_lbl.setStyleSheet(f"color: {color}; font-weight: 700; font-size: 11px;")
        if status == "RUNNING":
            self._time_lbl.setText(f"Dimulai {QTime.currentTime().toString('hh:mm:ss')}")
        elif status == "DONE":
            self._time_lbl.setText(f"Selesai {QTime.currentTime().toString('hh:mm:ss')}")

    def tambah_log(self, message: str):
        self.log_area.append(message)
        cursor = self.log_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_area.setTextCursor(cursor)

    def set_progress(self, value: int):
        self.progress_bar.setValue(value)

    def clear(self):
        self.log_area.clear()
        self.progress_bar.setValue(0)
        self.atur_status("IDLE")
        self._time_lbl.setText("")