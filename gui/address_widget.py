from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from geopy.geocoders import Nominatim

class AddressWidget(QWidget):
    def __init__(self, coordinates):
        super().__init__()
        self.coordinates = coordinates

        self.location = None
        self.address_layout = QVBoxLayout()

        self.street_label = QLabel()
        self.town_label = QLabel()
        self.state_label = QLabel()
        self.country_label = QLabel()

        self.address_layout.addWidget(self.street_label)
        self.address_layout.addWidget(self.town_label)
        self.address_layout.addWidget(self.state_label)
        self.address_layout.addWidget(self.country_label)

        self.setLayout(self.address_layout)

        self.update_address(self.coordinates)

    def update_address(self, coordinates):
        self.coordinates = coordinates

        geolocator = Nominatim(user_agent="akku-simulator")
        self.location = geolocator.reverse(self.coordinates)
        try:
            self.street_label.setText(f"{self.location.raw["address"]["road"]} {self.location.raw["address"].get("house_number") if self.location.raw["address"].get("house_number") else ""}")
        except:
            try:
                self.street_label.setText(f"{self.location.raw["address"]["name"]}")
            except:
                self.street_label.setText("")
        try:
            self.town_label.setText(f"{self.location.raw["address"]["postcode"]} {self.location.raw["address"]["town"]}")
        except:
            try:
                self.town_label.setText(f"{self.location.raw["address"]["postcode"]} {self.location.raw["address"]["village"]}")
            except:
                self.street_label.setText()
        try:
            self.state_label.setText(f"{self.location.raw["address"]["state"]}")
        except:
            self.state_label.setText("")
        try:
            self.country_label.setText(f"{self.location.raw["address"]["country"]}")
        except:
            self.country_label.setText("")
