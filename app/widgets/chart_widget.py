from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt

try:
    import matplotlib
    matplotlib.use("QtAgg")
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False

C_BLUE   = "#1A6E9E"
C_GOLD   = "#C9A84C"
C_GRID   = "#F4F1EA"
C_TEXT   = "#9AA5AE"
C_BG     = "#FFFFFF"
C_FILL_B = "#EFF8FF"
C_FILL_G = "#FFFBEB"


class TrendChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(220)

        self._x: list[float] = []
        self._counts: list[float] = []
        self._slows: list[float] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        if not MATPLOTLIB_OK:
            lbl = QLabel(
                "📊  Instal matplotlib untuk menampilkan chart:\n"
                "pip install matplotlib"
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(
                "color: #9AA5AE; font-size: 12px; "
                "background: #F7F5F0; border-radius: 10px; padding: 24px;"
            )
            layout.addWidget(lbl)
            return

        self._fig = Figure(facecolor=C_BG, tight_layout={"pad": 1.4})
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setStyleSheet(f"background-color: {C_BG}; border-radius: 8px;")
        layout.addWidget(self._canvas)
        self._setup_axes()

    def _setup_axes(self):
        self._fig.clear()
        self._ax1 = self._fig.add_subplot(111)
        self._ax2 = self._ax1.twinx()
        self._style_axes()
        self._canvas.draw()

    def _style_axes(self):
        for ax in (self._ax1, self._ax2):
            ax.set_facecolor(C_BG)
            ax.tick_params(colors=C_TEXT, labelsize=8, length=3)
            for spine in ax.spines.values():
                spine.set_color("#EAE6DE")
                spine.set_linewidth(0.8)

        self._ax1.set_xlabel("Waktu (s)", color=C_TEXT, fontsize=8, labelpad=4)
        self._ax1.set_ylabel("Jumlah Orang", color=C_BLUE, fontsize=8, fontweight="semibold")
        self._ax1.tick_params(axis="y", colors=C_BLUE)

        self._ax2.set_ylabel("Slow Ratio", color=C_GOLD, fontsize=8, fontweight="semibold")
        self._ax2.set_ylim(0, 1.05)
        self._ax2.tick_params(axis="y", colors=C_GOLD)

    def add_point(self, t: float, count: float, slow: float):
        if not MATPLOTLIB_OK:
            return
        self._x.append(t)
        self._counts.append(count)
        self._slows.append(slow)
        self._redraw()

    def _redraw(self):
        self._ax1.cla()
        self._ax2.cla()
        self._style_axes()

        x = self._x
        # Count: area biru lembut
        self._ax1.fill_between(x, self._counts, alpha=0.10, color=C_BLUE)
        self._ax1.plot(
            x, self._counts,
            color=C_BLUE, linewidth=2.2, label="Jumlah Orang",
            solid_capstyle="round"
        )

        # Slow ratio: area gold
        self._ax2.fill_between(x, self._slows, alpha=0.10, color=C_GOLD)
        self._ax2.plot(
            x, self._slows,
            color=C_GOLD, linewidth=2.0, linestyle="--",
            label="Slow Ratio", solid_capstyle="round", dash_capstyle="round"
        )

        self._ax1.grid(True, color=C_GRID, linewidth=0.8, linestyle="-")
        self._ax2.set_ylim(0, 1.05)

        lines1, lbl1 = self._ax1.get_legend_handles_labels()
        lines2, lbl2 = self._ax2.get_legend_handles_labels()
        self._ax1.legend(
            lines1 + lines2, lbl1 + lbl2,
            loc="upper left", fontsize=8,
            facecolor="#FAFAF8", edgecolor="#EAE6DE",
            labelcolor="#4A5A66",
            framealpha=0.95,
        )
        self._canvas.draw()

    def clear(self):
        self._x.clear()
        self._counts.clear()
        self._slows.clear()
        if MATPLOTLIB_OK:
            self._setup_axes()