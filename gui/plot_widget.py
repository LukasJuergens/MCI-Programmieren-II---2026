from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(250)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_data(self, y_values, x_values=None, title="Plot", x_label="x", y_label="y"):
        self.figure.clear()

        axes = self.figure.add_subplot(111)
        axes.set_ylabel(y_label)
        axes.grid(True)
        if x_values == None:
            axes.plot(y_values)
            axes.set_xticks([])
        else:
            axes.plot( x_values, y_values)
            axes.set_xlabel(x_label)
        self.figure.tight_layout()
        self.figure.subplots_adjust(bottom=0.2)
        self.canvas.draw()