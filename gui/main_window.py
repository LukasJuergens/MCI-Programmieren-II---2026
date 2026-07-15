from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QComboBox
from PySide6.QtCore import Qt

from gui.map_widget import MapWidget
from gui.plot_widget import PlotWidget
from gui.address_widget import AddressWidget
from gui.battery_selection_widget import BatterySelectionWidget
from inputDataProcessor import inputDataProcessor
from Battery_Pack import BatteryPack





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
        self.socs = []
        self.voltages = []

        self.battery_pack = None

        self.min_lat = None
        self.max_lat = None
        self.min_lon = None
        self.max_lon = None


        self.bike_type_label = QLabel("Fahrrad:")

        self.bike_type = QComboBox()
        self.bike_type.addItems(["mountainbike", "racebike", "gravelbike"])
        self.bike_type.currentTextChanged.connect(self.get_data) 

        self.road_surface_label = QLabel("Straßenoberfläche:")
        self.road_surface = QComboBox()
        self.road_surface.addItems(["asphalt", "gravel"])   
        self.road_surface.currentTextChanged.connect(self.get_data)
        
        environmentLayout = QHBoxLayout()
        environmentLayout.addWidget(self.bike_type_label)
        environmentLayout.addWidget(self.bike_type)
        environmentLayout.addWidget(self.road_surface_label)
        environmentLayout.addWidget(self.road_surface)
        

        self.battery_selection_widget = BatterySelectionWidget()
        self.battery_selection_widget.battery_combobox.currentTextChanged.connect(self.update_battery)
        self.battery_selection_widget.apply_button.clicked.connect(self.update_battery)

        self.get_data()

        layout = QVBoxLayout()
        centralWidget = QWidget()

        self.map_widget = MapWidget(self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.lat, self.lon)

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setMinimum(1)
        self.time_slider.setMaximum(len(self.lat))
        self.time_slider.setValue(len(self.lat))
        self.time_slider.sliderReleased.connect(self.update_driven_time)

        self.time_display = QLabel(f"Zeit: {self.times[self.time_slider.value()-1]}")

        self.address_widget = AddressWidget(f"{self.lat[self.time_slider.value()-1]}, {self.lon[self.time_slider.value()-1]}")

        self.plot_selection_combobox = QComboBox()
        self.plot_selection_combobox.addItems(["Höhe", "Geschwindigkeit", "Beschleunigung", "Leistung", "Steigung", "Drehmoment", "Motorstrom", "Ladezustand Akku", "Akkuspannung"])
        self.plot_selection_combobox.currentTextChanged.connect(self.update_plot)

        self.plot_widget = PlotWidget()
        self.plot_widget.plot_data(self.elevation)

        self.update_driven_time()
        layout.addLayout(environmentLayout)
        layout.addWidget(self.battery_selection_widget)
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
        self.inputDataProcessor.process(80, 0.5625, 0.6858, 1.5, 200, inputDataProcessor.EnvironmentToFrictionCoefficient(self.bike_type.currentText(), self.road_surface.currentText()))
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
        self.update_battery()



    def update_battery(self):
        cell_capacity = self.battery_selection_widget.cell_capacity_lineedit.text()
        try:
            cell_capacity = float(cell_capacity)
            if(cell_capacity <= 0):
                cell_capacity = 5
        except:
            cell_capacity = 5
        min_battery_capacity, start_capacity = BatteryPack.calculate_min_capacity_Ah(self.inputDataProcessor.currents, cell_capacity)
        batteries = {"LiPo": {0.00: 32.00, 
                                  0.04: 35.87,
                                  0.09: 36.85,
                                  0.13:	37.56,
                                  0.17:	37.87,
                                  0.21:	38.28,
                                  0.26:	38.81,
                                  0.30:	39.05,
                                  0.40:	39.55,
                                  0.52:	40.27,
                                  0.64:	40.70,
                                  0.76:	41.16,
                                  0.88:	41.65,
                                  1.00:	42.00}, 
                                  "NMC": {
                                      0.00: 32.00, 
                                  0.04: 32.61,
                                  0.09: 33.17,
                                  0.13:	33.85,
                                  0.17:	34.24,
                                  0.21:	34.66,
                                  0.26:	35.39,
                                  0.30:	35.65,
                                  0.40:	36.65,
                                  0.52:	37.64,
                                  0.64:	38.91,
                                  0.76:	40.14,
                                  0.88:	41.08,
                                  1.00:	42.00
                        }}
        battery_resistance = {"LiPo": 8, "NMC": 7}
        self.battery_pack = BatteryPack(min_battery_capacity, batteries[self.battery_selection_widget.battery_combobox.currentText()], battery_resistance[self.battery_selection_widget.battery_combobox.currentText()], start_capacity/min_battery_capacity+0.001, 32, 42)
        self.voltages = []
        self.socs = []

        for i in self.inputDataProcessor.currents.fillna(0):
            self.battery_pack.apply_current(-i, 1/3600.0)
            self.voltages.append(self.battery_pack.voltage())
            self.socs.append(self.battery_pack.soc)
        try:
            self.update_plot()
        except: 
            pass

        self.battery_selection_widget.applied_cell_capacity_label.setText(f"Zellkapazität verwendet in Berechnung: {cell_capacity}Ah")
        self.battery_selection_widget.minimum_required_cells_label.setText(f"Minimale Anzahl der Zellen in parallel: {round(min_battery_capacity/cell_capacity)}({min_battery_capacity}Ah)")
        self.battery_selection_widget.minimum_start_soc_label.setText(f"Minimaler State of Charge am anfang: {round(start_capacity/min_battery_capacity, 2)}({round(start_capacity, 2)}Ah)")

    

    def update_driven_time(self):
        self.map_widget.update_map(self.time_slider.value())
        self.update_plot()
        self.address_widget.update_address(f"{self.lat[self.time_slider.value()-1]}, {self.lon[self.time_slider.value()-1]}")
        self.time_display.setText(f"Zeit: {self.times[self.time_slider.value()-1]}")
    


    def update_plot(self):
        data_to_plot = {"Höhe": self.elevation, "Geschwindigkeit": self.speeds, "Beschleunigung": self.accelerations, "Leistung": self.powers, "Steigung": self.inclines, "Drehmoment": self.torques, "Motorstrom": self.currents, "Ladezustand Akku": self.socs, "Akkuspannung": self.voltages}
        y_labels = {"Höhe": "Höhe / m", "Geschwindigkeit": "Geschwindigkeit / m/s", "Beschleunigung": "Beschleunigung / m/s²", "Leistung": "Leistung / W", "Steigung": "Steigung / rad", "Drehmoment": "Drehmoment / Nm", "Motorstrom": "Motorstrom / A", "Ladezustand Akku": "Ladezustand / Ah/Ah", "Akkuspannung": "Akkuspannung / V"}
        self.plot_widget.plot_data(data_to_plot[self.plot_selection_combobox.currentText()][:self.time_slider.value()], [i/60.0 for i in range(self.time_slider.value())], y_label=y_labels[self.plot_selection_combobox.currentText()], x_label="Zeit / min")