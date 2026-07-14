from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_data(self, y_values, x_values=None, title="Plot", x_label="x", y_label="y"):
        self.figure.clear()

        axes = self.figure.add_subplot(111)
        axes.plot(y_values)
        axes.set_ylabel(y_label)
        axes.grid(True)
        if x_values == None:
            axes.set_xticks([])
        self.canvas.draw()