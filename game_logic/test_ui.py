from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QComboBox,QPushButton, QLabel, QHBoxLayout,QVBoxLayout, QGridLayout, QMenuBar, QMainWindow, QDialog
import PyQt5.QtWidgets as Qt
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os

import matplotlib.pyplot as plt

from quantum_circuits import circuit 

dir_path = os.path.dirname(os.path.realpath(__file__))

stylesheet  ="""
            QWidget {
                background-color: #333; /* Darker background color */
                color: #fff; /* Text color */
            }

            QMenuBar {
                background-color: #444; /* Menu bar background color */
                color: #fff; /* Text color */
            }

            QMenuBar::menu:hover {
                background-color: #444; /* Menu item background color */
            }
                                
            QMenu {
                background-color: #555; /* Default background for the menu */
                border: 1px solid #555; /* Border for the menu */
            }

            QMenu::item:hover {
                background-color: #0066cc; /* Hover effect for menu items */
                color: #fff; /* Text color on hover */
            }

            QMenu::item:pressed {
                background-color: #0066cc; /* Pressed state background */
                color: #fff; /* Text color on press */
            }
                           
            QLabel, QLineEdit { margin : 0px; padding: 0px; }
            """

def button_stylesheet(background_color=None, selected = False):
        if background_color == None:
            text = ""
        else: 
            text = rf"background-color : {background_color};"
        return rf"""
            QPushButton {{
                border-radius: 25px; /* Half of the width/height */
                border: {6 if selected == True else 2}px solid white;
                {text}
            }}
            QPushButton:hover {{
                border : 4px solid white;
                }}
            QPushButton:pressed {{
                border : 6px solid white;
            }}
            """

def get_color(stylesheet):
    # stylesheet = button.styleSheet()
    return (stylesheet.split("background-color : ")[-1]).split(";")[0]

class LoadingPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reset")
        self.setFixedSize(200, 100)
        layout = QVBoxLayout()
        self.label = QLabel("Resetting")
        layout.addWidget(self.label)
        self.setLayout(layout)

class CircuitFigure(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheet)
        self.setWindowTitle("Circuit")
        self.setFixedSize(800, 600)

        self.figure = plt.figure()

        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self, figure):
        self.figure.clear()
        self.figure = figure
        self.canvas.figure = self.figure
        self.canvas.draw()
        
class Main(QMainWindow):
    def __init__(self, qcircuit, N=32):
        self.N = N
        self.circuit = qcircuit

        self.circuitfigure = CircuitFigure()
        self.fig = self.circuit.draw(mpl_open = False, term_draw = False)
        self.circuitfigure.plot(self.fig)
        self.circuitfigure.show()

        super().__init__()
        self.settings()
        self.window()
        self.initUI()
        self.button_events()
        
    def window(self):
        # Menu bar
        self.menu = QMenuBar(self)
        self.file_menu = self.menu.addMenu("File")
        self.setMenuBar(self.menu)
        
        self.reset = Qt.QAction("Reset", self)
        self.reset.setShortcut("Ctrl+R")
        self.file_menu.addAction(self.reset)
        
    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.setStyleSheet(stylesheet)

        grid = QGridLayout()

        self.dots = [Qt.QPushButton("") for _ in range(self.N)]
        for dot, i in zip(self.dots, range(self.N)):
            dot.setFixedSize(50, 50)
            dot.setStyleSheet(button_stylesheet())
            grid.addWidget(dot, 1, i)
        
        colours = ['red', 'green', 'blue', 'yellow']
        self.cdots = [Qt.QPushButton("") for _ in range(len(colours))]
        for dot, i in zip(self.cdots, range(len(colours))):
            dot.setFixedSize(50,50)
            dot.setStyleSheet(button_stylesheet(background_color=colours[i]))
            grid.addWidget(dot, 0, i)

        self.measure = Qt.QPushButton("Measure")
        grid.addWidget(self.measure, 0, len(colours)+1)

        # show grid
        central_widget.setLayout(grid)


        
    def settings(self):
        self.setWindowTitle("Testing")
        self.setGeometry(250,250,600,500)
    
    def button_events(self):
        for cbutton in self.cdots:
            cbutton.pressed.connect(lambda b=cbutton: self.on_cbutton_pressed(b))
            self.cbutton_pressed = True
        self.measure.pressed.connect(self.measure_action)

        for button in self.dots:
            button.clicked.connect(lambda b=button: self.on_button_pressed(b))

    def cur_pressed_buttons(self, button):
        

    def on_button_pressed(self, button):
        if self.cbutton_pressed == False:
            color = get_color(button.styleSheet())
            print('a')

    def on_cbutton_pressed(self, cbutton):
        color = get_color(cbutton.styleSheet())

        cbutton.setStyleSheet(button_stylesheet(rf"{color}", selected = True))

        for button in self.dots:
            button.pressed.connect(lambda b = button: self.new_pawn_action(color, b, cbutton))

    
    def new_pawn_action(self, color, button, cbutton):
        button.setStyleSheet(button_stylesheet(rf"{color}"))
        cbutton.setStyleSheet(button_stylesheet(rf"{color}", selected = False))
        self.circuit.new_pawn(move_to=[self.dots.index(button)])
        self.update_drawn_circuit()
        button.pressed.disconnect()
        cbutton.pressed.disconnect()

    def measure_action(self):
        positions = self.circuit.measure()
        for i in range(self.N):
            for i in positions:
                continue
            else:
                self.dots[i].setStyleSheet(button_stylesheet())
        

        print(positions)

    def update_drawn_circuit(self):
        self.fig = self.circuit.draw(mpl_open = False, term_draw = False)
        self.circuitfigure.plot(self.fig)

    def reset_app(self):
        1==1

def start(circuit, N):
    app = QApplication(sys.argv)
    main = Main(circuit, N)
    main.show()
    app.exec_()
    
if __name__ in "__main__":
    N = 10 # number of qubits(/places)
    qc = circuit(N)
    start(qc, N)