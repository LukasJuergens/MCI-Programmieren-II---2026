from PySide6.QtWidgets import QWidget, QComboBox, QLineEdit, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

class BatterySelectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        battery_type_label = QLabel("Akkutyp: ")
        self.battery_combobox = QComboBox()
        self.battery_combobox.addItems(["LiPo", "NMC"])

        cell_capacity_label = QLabel("Zellkapazität in Ah")
        self.cell_capacity_lineedit = QLineEdit()

        self.apply_button = QPushButton("Anwenden")

        self.applied_cell_capacity_label = QLabel("Zellkapazität verwendet in Berechnung: 5Ah")
        self.minimum_required_cells_label = QLabel("Minimale Anzahl der Zellen in parallel: 6(30Ah)")
        self.minimum_start_soc_label = QLabel("Minimaler State of Charge am anfang: 1.0(30Ah)")

        input_layout = QHBoxLayout()
        input_layout.addWidget(battery_type_label)
        input_layout.addWidget(self.battery_combobox)
        input_layout.addWidget(cell_capacity_label)
        input_layout.addWidget(self.cell_capacity_lineedit)
        input_layout.addWidget(self.apply_button)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.applied_cell_capacity_label)
        output_layout.addWidget(self.minimum_required_cells_label)
        output_layout.addWidget(self.minimum_start_soc_label)

        layout = QVBoxLayout()

        layout.addLayout(input_layout)
        layout.addLayout(output_layout)

        self.setLayout(layout)