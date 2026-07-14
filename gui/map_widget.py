import folium
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

class MapWidget(QWidget):
    def __init__(self, min_lat, max_lat, min_lon, max_lon, lat_points, lon_points):
        super().__init__()

        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon

        self.lat_points = lat_points
        self.lon_points = lon_points
        
        self.web_view = QWebEngineView()

        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        self.setLayout(layout)

        self.update_map()

    def update_map(self, points = -1):
        map_view = folium.Map(location=[self.min_lat, self.min_lon], zoom_start=13, tiles="OpenStreetMap")
        map_view.fit_bounds([[[self.min_lat, self.min_lon]], [self.max_lat, self.max_lon]])
        self.draw_on_map(map_view, points)
        html = map_view.get_root().render()

        self.web_view.setHtml(
            html,
            QUrl("https://localhost/")
        )
    
    def draw_on_map(self, map, points):
        folium.PolyLine([[self.lat_points[i], self.lon_points[i]] for i in range(len(self.lat_points[0:points]))]).add_to(map)