import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QMessageBox,
)
from PyQt6.QtCore import Qt
from app.styles import STYLE_APLIKASI
from app.worker import PipelineWorker
from app.widgets.input_panel import InputPanel
from app.widgets.results_panel import PanelHasil
from app.widgets.status_bar import StatusBar


class JendelaUtama(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hajj Crowd Monitor v4")
        self.setMinimumSize(800, 500)
        self.resize(1400, 860)
        self.setStyleSheet(STYLE_APLIKASI)

        self._worker: PipelineWorker | None = None
        self._direktori_proyek = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self._direktori_output = os.path.join(self._direktori_proyek, "outputs")
        self._bangun_ui()

    def _bangun_ui(self):
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
        self._input.run_requested.connect(self._on_jalankan)
        self._input.stop_requested.connect(self._on_hentikan)

        # koordinat dan nama lokasi
        self._input._lat_spin.valueChanged.connect(self._sinkron_lokasi_ke_peta)
        self._input._lon_spin.valueChanged.connect(self._sinkron_lokasi_ke_peta)
        self._input._loc_name.textChanged.connect(self._sinkron_lokasi_ke_peta)

        splitter.addWidget(self._input)

        # Results dan Status bar
        right = QWidget()
        right.setObjectName("content_area")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self._results = PanelHasil()
        self._results.point_selected.connect(self._on_titik_peta_dipilih)

        rl.addWidget(self._results, 1)
        self._status = StatusBar()
        rl.addWidget(self._status)

        splitter.addWidget(right)
        splitter.setSizes([320, 1080])
        root.addWidget(splitter)

        self._sinkron_lokasi_ke_peta()

    def _sinkron_lokasi_ke_peta(self):
        lat = self._input._lat_spin.value()
        lon = self._input._lon_spin.value()
        name = self._input._loc_name.text().strip()
        self._results.atur_lokasi(lat, lon, name)

    def _on_titik_peta_dipilih(self, point_id: str):
        pass

    def _on_jalankan(self, params: dict):
        video_path = params.get("video_path", "")
        if not os.path.exists(video_path):
            QMessageBox.warning(
                self, "File Tidak Ditemukan",
                "File video tidak ditemukan.\nSilakan pilih video yang valid."
            )
            return

        model_path = os.path.join(self._direktori_proyek, "best.pt")
        self._status.clear()
        self._status.atur_status("RUNNING")
        self._status.tambah_log(
            f"▶ Memulai analisis: {params.get('video_name')}\n"
            f"  Lokasi : {params.get('location_name')} "
            f"({params.get('lat'):.4f}, {params.get('lon'):.4f})"
        )
        self._input.set_running(True)

        params["project_root"] = self._direktori_proyek
        params["model_path"] = model_path
        params["output_dir"] = self._direktori_output

        self._worker = PipelineWorker(params, parent=self)
        self._worker.log_message.connect(self._status.tambah_log)
        self._worker.progress.connect(self._status.set_progress)
        self._worker.window_result.connect(self._results.perbarui_dengan_window)
        self._worker.pipeline_finished.connect(self._on_selesai)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_hentikan(self):
        if self._worker and self._worker.isRunning():
            self._status.atur_status("STOPPING")
            self._status.tambah_log("Permintaan stop - menunggu frame selesai...")
            self._worker.minta_berhenti()
            self._input.set_running(False)

    def _on_selesai(self, result: dict):
        dihentikan_pengguna = result.get("dihentikan_pengguna", False)
        state = "CANCELLED" if dihentikan_pengguna else "DONE"
        self._status.atur_status(state)
        self._status.set_progress(100)
        self._input.set_running(False)
        self._results.atur_jalur_output(result)
        n = len(result.get("window_rows", []))
        f = result.get("frame_count", 0)
        self._status.tambah_log(
            f"\n{'─'*46}\n"
            f"{'✅' if not dihentikan_pengguna else '🛑'} Pipeline "
            f"{'selesai' if not dihentikan_pengguna else 'dihentikan'}\n"
            f"  Frame diproses   : {f}\n"
            f"  Window dihasilkan: {n}\n"
            f"  Output tersimpan : outputs/"
        )

    def _on_error(self, msg: str):
        self._status.atur_status("ERROR")
        self._input.set_running(False)
        self._status.tambah_error(msg)
        self._status.tambah_log("\nℹ Pastikan model tersedia dan video tidak rusak.")

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.minta_berhenti()
            self._worker.wait(3000)
        event.accept()