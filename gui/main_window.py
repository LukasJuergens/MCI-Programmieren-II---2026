from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QComboBox
from PySide6.QtCore import Qt
import sys

from gui.map_widget import MapWidget
from gui.plot_widget import PlotWidget
from gui.address_widget import AddressWidget
from inputDataProcessor import inputDataProcessor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_UI()

        self.lat = []
        self.lon = []
        self.elevation = []
        self.times = []
        self.tempratures = []
        self.speeds = []
        self.accelerations = []
        self.torques = []
        self.powers = []
        self.inclines = []
        self.currents = []

        self.min_lat = None
        self.max_lat = None
        self.min_lon = None
        self.max_lon = None

        self.get_data()

        layout = QVBoxLayout()
        centralWidget = QWidget()

        self.map_widget = MapWidget(self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.lat, self.lon)

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setMinimum(1)
        self.time_slider.setMaximum(len(self.lat))
        self.time_slider.setValue(len(self.lat))
        self.time_slider.valueChanged.connect(self.update_driven_time)

        self.time_display = QLabel(f"Zeit: {self.times[self.time_slider.value()-1]}")

        self.address_widget = AddressWidget(f"{self.lat[self.time_slider.value()-1]}, {self.lon[self.time_slider.value()-1]}")

        self.plot_selection_combobox = QComboBox()
        self.plot_selection_combobox.addItems(["Höhe", "Geschwindigkeit", "Beschleunigung", "Leistung", "Steigung", "Drehmoment", "Motorstrom", "Ladezustand Akku"])
        self.plot_selection_combobox.currentTextChanged.connect(self.update_plot)

        self.plot_widget = PlotWidget()
        self.plot_widget.plot_data(self.elevation)

        self.update_driven_time()

        layout.addWidget(self.address_widget)
        layout.addWidget(self.time_display)
        layout.addWidget(self.map_widget)
        layout.addWidget(self.time_slider)
        layout.addWidget(self.plot_selection_combobox)
        layout.addWidget(self.plot_widget)

        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
    
    def init_UI(self):
        self.setWindowTitle("E-Bike Akkusimulation")
        self.setStyleSheet("background-color: white;")
    
    def get_data(self):
        self.inputDataProcessor = inputDataProcessor()
        self.inputDataProcessor.process(80, 0.5625, 0.6858, 1.5, 200)
        self.lat = self.inputDataProcessor.lat.values
        self.lon = self.inputDataProcessor.lon.values
        self.elevation = self.inputDataProcessor.ele.values
        self.times = self.inputDataProcessor.time
        self.tempratures = self.inputDataProcessor.temp.values
        self.speeds = self.inputDataProcessor.speeds.values
        self.accelerations = self.inputDataProcessor.accelerations.values
        self.torques = self.inputDataProcessor.torques.values
        self.powers = self.inputDataProcessor.powers.values
        self.inclines = self.inputDataProcessor.inclines.values
        self.currents = self.inputDataProcessor.currents.values

        self.min_lat = min(self.lat)
        self.max_lat = max(self.lat)
        self.min_lon = min(self.lon)
        self.max_lon = max(self.lon)
    
    def update_driven_time(self):
        self.map_widget.update_map(self.time_slider.value())
        self.update_plot()
        self.address_widget.update_address(f"{self.lat[self.time_slider.value()-1]}, {self.lon[self.time_slider.value()-1]}")
        self.time_display.setText(f"Zeit: {self.times[self.time_slider.value()-1]}")
    
    def update_plot(self):
        data_to_plot = {"Höhe": self.elevation, "Geschwindigkeit": self.speeds, "Beschleunigung": self.accelerations, "Leistung": self.powers, "Steigung": self.inclines, "Drehmoment": self.torques, "Motorstrom": self.currents, "Ladezustand Akku": []}
        self.plot_widget.plot_data(data_to_plot[self.plot_selection_combobox.currentText()][:self.time_slider.value()])