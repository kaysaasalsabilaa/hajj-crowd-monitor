from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QFrame, QLineEdit,
    QSizePolicy, QApplication,
)
from PyQt6.QtCore import Qt, pyqtSlot, QUrl, QTimer
from PyQt6.QtGui import QFont

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebChannel import QWebChannel
    from PyQt6.QtCore import QObject, pyqtSignal as Signal
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False


MAP_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #f0ede6; font-family: 'Segoe UI', sans-serif; }
  #map { width: 100%; height: 100vh; }
  #crosshair {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none; z-index: 1000;
    font-size: 32px; opacity: 0.7;
  }
  #hint {
    position: absolute; bottom: 20px; left: 50%;
    transform: translateX(-50%);
    background: rgba(26,46,59,0.92); color: #e8e6e0;
    padding: 8px 18px; border-radius: 20px;
    font-size: 12px; z-index: 1000;
    pointer-events: none; white-space: nowrap;
    border: 1px solid #c9a84c;
  }
  .leaflet-marker-icon { transition: transform 0.15s ease; }
</style>
</head>
<body>
<div id="map"></div>
<div id="hint">🖱️ Klik pada peta untuk memilih lokasi pengamatan</div>
<script>
var map = L.map('map', {
  center: [21.4225, 39.8262],
  zoom: 14,
  zoomControl: true
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19,
}).addTo(map);

// Marker custom
var pinIcon = L.divIcon({
  html: '<div style="font-size:32px;line-height:1;transform:translateY(-100%);">📍</div>',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  className: '',
});

var marker = null;
var selectedLat = null;
var selectedLon = null;
var bridge = null;

// Setup QWebChannel
new QWebChannel(qt.webChannelTransport, function(channel) {
  bridge = channel.objects.bridge;
});

map.on('click', function(e) {
  var lat = e.latlng.lat.toFixed(6);
  var lon = e.latlng.lng.toFixed(6);
  selectedLat = parseFloat(lat);
  selectedLon = parseFloat(lon);

  if (marker) { map.removeLayer(marker); }
  marker = L.marker([selectedLat, selectedLon], {icon: pinIcon}).addTo(map);
  marker.bindPopup(
    '<b>Lokasi Dipilih</b><br>' +
    'Lat: ' + lat + '<br>Lon: ' + lon,
    {closeButton: false}
  ).openPopup();

  if (bridge) {
    bridge.locationSelected(selectedLat, selectedLon);
  }

  document.getElementById('hint').innerHTML =
    '✅ Lat: ' + lat + '  |  Lon: ' + lon + '  &nbsp;(klik lagi untuk ubah)';
});
</script>
</body>
</html>"""


if WEB_ENGINE_AVAILABLE:
    from PyQt6.QtCore import QObject, pyqtSignal as Signal

    class MapBridge(QObject):
        location_selected = Signal(float, float)

        @pyqtSlot(float, float)
        def locationSelected(self, lat: float, lon: float):
            self.location_selected.emit(lat, lon)

class MapPickerDialog(QDialog):
    """
    Dialog peta interaktif.
    Jika QWebEngineView tersedia → Leaflet.js di dalam app.
    Jika tidak → fallback ke form input manual koordinat.
    Returns: (lat: float, lon: float) or (None, None)
    """

    def __init__(self, initial_lat=21.4225, initial_lon=39.8262, parent=None):
        super().__init__(parent)
        self.setObjectName("map_dialog")
        self.setWindowTitle("Pilih Lokasi Pengamatan")
        self.setMinimumSize(800, 580)
        self.resize(960, 640)

        self._lat = initial_lat
        self._lon = initial_lon
        self._confirmed_lat = None
        self._confirmed_lon = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # toolbar
        toolbar = QWidget()
        toolbar.setObjectName("map_toolbar")
        tb_lay = QHBoxLayout(toolbar)
        tb_lay.setContentsMargins(16, 10, 16, 10)
        tb_lay.setSpacing(12)

        instr = QLabel("🗺️  Klik titik pada peta untuk memilih lokasi pengamatan jamaah")
        instr.setObjectName("map_instruction")
        tb_lay.addWidget(instr)
        tb_lay.addStretch()

        self._coord_display = QLabel("Belum ada lokasi dipilih")
        self._coord_display.setObjectName("map_coord_display")
        self._coord_display.setMinimumWidth(250)
        self._coord_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tb_lay.addWidget(self._coord_display)

        layout.addWidget(toolbar)

        if WEB_ENGINE_AVAILABLE:
            self._build_web_map(layout)
        else:
            self._build_fallback_form(layout)

        # button
        btn_bar = QWidget()
        btn_bar.setStyleSheet(
            "background: #f5f3ee; border-top: 1px solid #e0dcd4;"
        )
        bb_lay = QHBoxLayout(btn_bar)
        bb_lay.setContentsMargins(16, 10, 16, 10)
        bb_lay.setSpacing(10)

        tip = QLabel("💡 Lokasi dipilih akan langsung mengisi form koordinat")
        tip.setStyleSheet("color: #8a8070; font-size: 11px;")
        bb_lay.addWidget(tip)
        bb_lay.addStretch()

        self._confirm_btn = QPushButton("✓  Konfirmasi Lokasi")
        self._confirm_btn.setObjectName("btn_map_confirm")
        self._confirm_btn.setEnabled(False)
        self._confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._confirm_btn.clicked.connect(self._on_confirm)

        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("btn_map_cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        bb_lay.addWidget(cancel_btn)
        bb_lay.addWidget(self._confirm_btn)
        layout.addWidget(btn_bar)

    def _build_web_map(self, parent_layout):
        """Render peta Leaflet via QWebEngineView."""
        self._view = QWebEngineView()
        self._channel = QWebChannel()
        self._bridge = MapBridge()
        self._channel.registerObject("bridge", self._bridge)
        self._view.page().setWebChannel(self._channel)
        self._bridge.location_selected.connect(self._on_location_selected)
        self._view.setHtml(MAP_HTML, QUrl("qrc:///"))
        parent_layout.addWidget(self._view, 1)

    def _build_fallback_form(self, parent_layout):
        """Fallback: form koordinat manual jika WebEngine tidak tersedia."""
        fallback = QWidget()
        fallback.setStyleSheet("background-color: #f5f4f0;")
        fl = QVBoxLayout(fallback)
        fl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.setSpacing(16)

        icon = QLabel("🗺️")
        icon.setStyleSheet("font-size: 56px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        notice = QLabel(
            "Peta interaktif memerlukan PyQt6-WebEngine.\n"
            "Silakan install dengan:\n"
            "pip install PyQt6-WebEngine\n\n"
            "Untuk sekarang, masukkan koordinat secara manual:"
        )
        notice.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notice.setStyleSheet("color: #5a4a2a; font-size: 12px; line-height: 1.6;")

        coord_widget = QWidget()
        coord_widget.setMaximumWidth(360)
        cw_lay = QVBoxLayout(coord_widget)
        cw_lay.setSpacing(10)

        lat_row = QHBoxLayout()
        lat_lbl = QLabel("Latitude:")
        lat_lbl.setFixedWidth(80)
        lat_lbl.setStyleSheet("color: #1a2e3b; font-weight: 600;")
        self._lat_edit = QLineEdit(str(self._lat))
        self._lat_edit.setStyleSheet(
            "background: #ffffff; border: 1px solid #d4cfc4; border-radius: 7px;"
            "padding: 8px; color: #1a2e3b;"
        )
        self._lat_edit.textChanged.connect(self._on_manual_coords_changed)
        lat_row.addWidget(lat_lbl)
        lat_row.addWidget(self._lat_edit)
        cw_lay.addLayout(lat_row)

        lon_row = QHBoxLayout()
        lon_lbl = QLabel("Longitude:")
        lon_lbl.setFixedWidth(80)
        lon_lbl.setStyleSheet("color: #1a2e3b; font-weight: 600;")
        self._lon_edit = QLineEdit(str(self._lon))
        self._lon_edit.setStyleSheet(
            "background: #ffffff; border: 1px solid #d4cfc4; border-radius: 7px;"
            "padding: 8px; color: #1a2e3b;"
        )
        self._lon_edit.textChanged.connect(self._on_manual_coords_changed)
        lon_row.addWidget(lon_lbl)
        lon_row.addWidget(self._lon_edit)
        cw_lay.addLayout(lon_row)

        fl.addWidget(icon)
        fl.addWidget(notice)
        fl.addWidget(coord_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(fallback, 1)

        self._on_location_selected(self._lat, self._lon)

    def _on_manual_coords_changed(self):
        try:
            lat = float(self._lat_edit.text())
            lon = float(self._lon_edit.text())
            self._on_location_selected(lat, lon)
        except (ValueError, AttributeError):
            pass

    @pyqtSlot(float, float)
    def _on_location_selected(self, lat: float, lon: float):
        self._lat = lat
        self._lon = lon
        self._coord_display.setText(f"📍  {lat:.6f},  {lon:.6f}")
        self._confirm_btn.setEnabled(True)

    def _on_confirm(self):
        self._confirmed_lat = self._lat
        self._confirmed_lon = self._lon
        self.accept()

    def get_result(self):
        """Return (lat, lon) atau (None, None) jika dibatalkan."""
        return self._confirmed_lat, self._confirmed_lon