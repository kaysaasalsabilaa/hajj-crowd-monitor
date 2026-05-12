import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QMessageBox,
)
from PyQt6.QtCore import Qt
from app.styles import APP_STYLE
from app.worker import PipelineWorker
from app.widgets.input_panel import InputPanel
from app.widgets.results_panel import ResultsPanel
from app.widgets.status_bar import StatusBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hajj Crowd Monitor v4")
        self.setMinimumSize(1100, 700)
        self.resize(1400, 860)
        self.setStyleSheet(APP_STYLE)

        self._worker: PipelineWorker | None = None
        self._project_root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self._output_dir = os.path.join(self._project_root, "outputs")
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)

        # Input panel
        self._input = InputPanel()
        self._input.run_requested.connect(self._on_run)
        self._input.stop_requested.connect(self._on_stop)

        # koordinat dan nama lokasi 
        self._input._lat_spin.valueChanged.connect(self._sync_location_to_map)
        self._input._lon_spin.valueChanged.connect(self._sync_location_to_map)
        self._input._loc_name.textChanged.connect(self._sync_location_to_map)

        splitter.addWidget(self._input)

        # Results dan Status bar
        right = QWidget()
        right.setObjectName("content_area")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self._results = ResultsPanel()

        self._results.point_selected.connect(self._on_map_point_selected)

        rl.addWidget(self._results, 1)
        self._status = StatusBar()
        rl.addWidget(self._status)

        splitter.addWidget(right)
        splitter.setSizes([320, 1080])
        root.addWidget(splitter)

        self._sync_location_to_map()

    def _sync_location_to_map(self):
        lat = self._input._lat_spin.value()
        lon = self._input._lon_spin.value()
        name = self._input._loc_name.text().strip()
        self._results.set_location(lat, lon, name)

    def _on_map_point_selected(self, point_id: str):
        pass

    def _on_run(self, params: dict):
        video_path = params.get("video_path", "")
        if not os.path.exists(video_path):
            QMessageBox.warning(
                self, "File Tidak Ditemukan",
                "File video tidak ditemukan.\nSilakan pilih video yang valid."
            )
            return

        model_path = os.path.join(self._project_root, "best.pt")
        self._status.clear()
        self._status.set_state("RUNNING")
        self._status.append_log(
            f"▶ Memulai analisis: {params.get('video_name')}\n"
            f"  Lokasi : {params.get('location_name')} "
            f"({params.get('lat'):.4f}, {params.get('lon'):.4f})"
        )
        self._input.set_running(True)

        params["project_root"] = self._project_root
        params["model_path"] = model_path
        params["output_dir"] = self._output_dir

        self._worker = PipelineWorker(params, parent=self)
        self._worker.log_message.connect(self._status.append_log)
        self._worker.progress.connect(self._status.set_progress)
        self._worker.window_result.connect(self._results.update_with_window)
        self._worker.pipeline_finished.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_stop(self):
        if self._worker and self._worker.isRunning():
            self._status.set_state("STOPPING")
            self._status.append_log("Permintaan stop - menunggu frame selesai...")
            self._worker.request_stop()
            self._input.set_running(False)

    def _on_done(self, result: dict):
        stopped = result.get("stopped_by_user", False)
        state = "CANCELLED" if stopped else "DONE"
        self._status.set_state(state)
        self._status.set_progress(100)
        self._input.set_running(False)
        self._results.set_output_paths(result)
        n = len(result.get("window_rows", []))
        f = result.get("frame_count", 0)
        self._status.append_log(
            f"\n{'─'*46}\n"
            f"{'✅' if not stopped else '🛑'} Pipeline "
            f"{'selesai' if not stopped else 'dihentikan'}\n"
            f"  Frame diproses   : {f}\n"
            f"  Window dihasilkan: {n}\n"
            f"  Output tersimpan : outputs/"
        )

    def _on_error(self, msg: str):
        self._status.set_state("ERROR")
        self._input.set_running(False)
        self._status.append_error(msg)
        self._status.append_log("\nℹ Pastikan model tersedia dan video tidak rusak.")

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.request_stop()
            self._worker.wait(3000)
        event.accept()