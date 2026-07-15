from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class GeneralDataWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.average_speed_label = QLabel("")
        self.total_altitude_upwards_label = QLabel("")
        self.total_altitude_downwards_label = QLabel("")
        self.total_distance_label = QLabel("")
        self.maximum_power_label = QLabel("")
        self.total_time_label = QLabel("")

        layout.addWidget(self.average_speed_label)
        layout.addWidget(self.total_altitude_upwards_label)
        layout.addWidget(self.total_altitude_downwards_label)
        layout.addWidget(self.total_distance_label)
        layout.addWidget(self.maximum_power_label)
        layout.addWidget(self.total_time_label)

        self.setLayout(layout)

    def update_labels(self, speed, altitude_up, altitude_down, distance, power, time):
        self.average_speed_label.setText(f"Durchschnittsgeschwindigkeit: {speed}m/s")
        self.total_altitude_upwards_label.setText(f"Höhenmeter Anstieg: {altitude_up}m")
        self.total_altitude_downwards_label.setText(f"Höhenmeter Abstieg: {altitude_down}m")
        self.total_distance_label.setText(f"Gesamtweg zurückgelegt: {distance}m")
        self.maximum_power_label.setText(f"Maximale Leistung: {power}W")
        self.total_time_label.setText(f"Gesamtzeit: {time}")