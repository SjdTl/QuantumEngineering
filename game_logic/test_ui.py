from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QComboBox,QPushButton, QLabel, QHBoxLayout,QVBoxLayout, QGridLayout, QMenuBar, QMainWindow, QDialog
import PyQt5.QtWidgets as Qt
from PyQt5 import QtCore
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

def button_stylesheet(color=None, selected = False, opacity = 200):
        if color == None:
            text = "transparent"
        else: 
            text = color
        stylesheet = rf"""
            QPushButton {{
                border-radius: 25px; /* Half of the width/height */
                border: {6 if selected == True else 2}px solid white;
                background-color : {text};
                opacity : {opacity};
            }}
            QPushButton:hover {{
                border : 4px solid white;
                }}
            QPushButton:pressed {{
                border : 6px solid white;
            }}
            """
        return stylesheet

def get_color_and_opacity(button):
    stylesheet = button.styleSheet()
    return (stylesheet.split("background-color : ")[-1]).split(";")[0], float((stylesheet.split("opacity : ")[-1]).split(";")[0])

def copy_buttons(buttons):
    new_buttons = []
    for button in buttons:
        new_button = QPushButton(button.text())
        new_button.setStyleSheet(button.styleSheet())
        new_button.setEnabled(button.isEnabled())
        new_button.setFixedSize(50,50)
        new_buttons.append(new_button)
    
    return new_buttons

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
        self.resize(800, 600)

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

class AllOptions(QDialog):
    def __init__(self, or_buttons, options):
        super().__init__()
        self.setStyleSheet(stylesheet)
        self.setWindowTitle("Other options")
        self.resize(800, 600)

        self.setStyleSheet(stylesheet)

        grid = QGridLayout()

        weights = list(options.keys())
        positions = list(options.values())
        for i in range(len(positions)+1):
            print(i)
            buttons = copy_buttons(or_buttons)
            if i == 0:
                for j in range(len(buttons)):
                    grid.addWidget(buttons[j], i, j+1)
            if i > 0:
                for j in (range(len(buttons))):
                    if j in positions[i-1]:
                        pass
                    else:
                        buttons[j].setStyleSheet(button_stylesheet())
                    grid.addWidget(buttons[j], i, j+1)
                label = QLabel()
                label.setText(str(weights[i-1]))
                grid.addWidget(label, i, 0)
        self.setLayout(grid)

        
class Main(QMainWindow):
    def __init__(self, qcircuit, N=32):
        self.N = N
        self.circuit = qcircuit

        self.circuitfigure = CircuitFigure()
        self.fig = self.circuit.draw(mpl_open = False, term_draw = False)
        self.circuitfigure.plot(self.fig)
        self.circuitfigure.show()

        self.pressed_buttons = []
        self.spressed_buttons = []
        self.pressed_cbuttons = []

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
        self.reset.triggered.connect(self.reset_app)
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
            dot.setStyleSheet(button_stylesheet(color=colours[i]))
            grid.addWidget(dot, 0, i)

        self.measure = Qt.QPushButton("Measure")
        grid.addWidget(self.measure, 0, len(colours)+1)

        self.nrqubits = Qt.QLabel(rf"# qubits used={0}")
        grid.addWidget(self.nrqubits, 0, len(colours)+2)

        # show grid
        central_widget.setLayout(grid)


        
    def settings(self):
        self.setWindowTitle("Testing")
        self.setGeometry(250,250,600,500)
    
    def button_events(self):
        print(self.cdots, self.dots)

        for cbutton in self.cdots:
            cbutton.pressed.connect(lambda b=cbutton: self.cur_pressed_cbuttons(self.cdots.index(b)))

        for button in self.dots:
            button.pressed.connect(lambda b=button: self.cur_pressed_buttons(self.dots.index(b)))
        
        self.measure.clicked.connect(self.measure_action)

    def cur_pressed_cbuttons(self, name):
        if name in self.pressed_cbuttons[:]:
            self.pressed_cbuttons.remove(name)
            self.cdots[name].setStyleSheet(button_stylesheet(color = get_color_and_opacity((self.cdots[name]))[0], selected = False))
        else:
            (self.pressed_cbuttons.append(name))
            self.pressed_cbuttons.sort()
            self.cdots[name].setStyleSheet(button_stylesheet(color = get_color_and_opacity((self.cdots[name]))[0], selected = True))
        self.logic()

    def cur_pressed_buttons(self, name):
        modifiers = Qt.QApplication.keyboardModifiers()
        if (modifiers != QtCore.Qt.ShiftModifier):
            if name in self.pressed_buttons[:]:
                self.pressed_buttons.remove(name)
                self.dots[name].setStyleSheet(button_stylesheet(color = get_color_and_opacity((self.dots[name]))[0], selected = False))
            else:
                (self.pressed_buttons.append(name))
                self.pressed_buttons.sort()
                self.dots[name].setStyleSheet(button_stylesheet(color = get_color_and_opacity((self.dots[name]))[0], selected = True))
        else:
            if name in self.spressed_buttons[:]:
                self.spressed_buttons.remove(name)
                self.dots[name].setStyleSheet(button_stylesheet(color = get_color_and_opacity((self.dots[name]))[0], selected = False))
            else:
                (self.spressed_buttons.append(name))
                self.spressed_buttons.sort()
                self.dots[name].setStyleSheet(button_stylesheet(color = get_color_and_opacity((self.dots[name]))[0], selected = True))
        self.logic()

    def reset_buttons(self):
        for name in self.pressed_cbuttons[:]:
            self.pressed_cbuttons.remove(name)
            self.cdots[name].setStyleSheet(button_stylesheet(color = get_color_and_opacity((self.cdots[name]))[0], selected = False))
        for name in self.pressed_buttons[:]:
            self.pressed_buttons.remove(name)
            self.dots[name].setStyleSheet(button_stylesheet(color = get_color_and_opacity((self.dots[name]))[0], selected = False))
        for name in self.spressed_buttons[:]:
            self.spressed_buttons.remove(name)
            self.dots[name].setStyleSheet(button_stylesheet(color = get_color_and_opacity((self.dots[name]))[0], selected = False))
        print(self.pressed_buttons, self.pressed_cbuttons, self.spressed_buttons)

    def logic(self):
        print(self.pressed_buttons, self.pressed_cbuttons, self.spressed_buttons)

        if len(self.pressed_cbuttons) == 1 and len(self.pressed_buttons) == 1 and len(self.spressed_buttons) == 0:
            # Initialize
            color = get_color_and_opacity(self.cdots[self.pressed_cbuttons[0]])[0]
            self.dots[self.pressed_buttons[0]].setStyleSheet(button_stylesheet(color))
            self.circuit.new_pawn(move_to = self.pressed_buttons)
            self.update_drawn_circuit()
            self.reset_buttons()

        if len(self.pressed_cbuttons) == 0 and len(self.pressed_buttons) == 3 and len(self.spressed_buttons) == 0:
            # Superposition move
            # REWRITE THIS PIECE OF LOGIC SINCE IT IS VERY INEFFICIENT AND HARD TO UNDERSTAND

            no_move = False
            for button_index in self.pressed_buttons:
                current_color, current_opacity = get_color_and_opacity(self.dots[button_index])
                if current_color != 'transparent':
                    move_to = [x for x in self.pressed_buttons if x != button_index]
                    move_from = [button_index]
                    captive_entanglement = []
                    captive = []
                    capturer = []
                    for i in range(len(move_to)):
                        cap_color = get_color_and_opacity(self.dots[move_to[i]])[0]
                        if cap_color != 'transparent':
                            if cap_color != current_color:
                                captive_entanglement = [j for j in range(self.N) if get_color_and_opacity(self.dots[j])[0] == cap_color and move_to[i] != j]
                                captive = [move_to[i]]
                                move_to[i] = move_to[i] + 1
                                capturer = [move_to[i]]
                            else: 
                                self.circuit.merge_move(move_from = move_from, merge_in = [move_to[i]], move_to = move_to)
                                no_move = True
                            break
                    if no_move == False:
                        self.circuit.move(move_from, move_to)
                        if len(captive) != 0:
                            self.circuit.capture(capturer = capturer, captive = captive, captive_entanglement = captive_entanglement)
                    no_move = False
                    
                    for i in move_to:
                        self.dots[i].setStyleSheet(button_stylesheet(color=current_color, opacity = current_opacity/2))
                    for j in move_from:
                        self.dots[j].setStyleSheet(button_stylesheet(color=None))

                    self.reset_buttons()
                    self.update_drawn_circuit()
        
        if len(self.spressed_buttons) == 2 and len(self.pressed_cbuttons) == 0 and len(self.pressed_buttons) == 0:
            self.circuit.switch([self.spressed_buttons[0]], [self.spressed_buttons[1]])
            c0, o0 = get_color_and_opacity(self.dots[self.spressed_buttons[0]])
            c1, o1 = get_color_and_opacity(self.dots[self.spressed_buttons[1]])

            self.dots[self.spressed_buttons[0]].setStyleSheet(button_stylesheet(color=c1, opacity=o1))
            self.dots[self.spressed_buttons[1]].setStyleSheet(button_stylesheet(color=c0, opacity=o0))

            self.reset_buttons()
            self.update_drawn_circuit()



    def measure_action(self):
        positions, out_with_freq, nr_of_qubits_used = self.circuit.measure(out_internal_measure=True, efficient = True)
        self.nrqubits.setText((rf"# qubits used={nr_of_qubits_used}"))
        self.all_options = AllOptions(self.dots, out_with_freq)
        for i in range(self.N):
            if i in positions:
                pass
            else:
                self.dots[i].setStyleSheet(button_stylesheet())

        self.all_options.show()
        self.all_options.exec()
        self.update_drawn_circuit()


    def update_drawn_circuit(self):
        self.fig = self.circuit.draw(mpl_open = False, term_draw = False)
        self.circuitfigure.plot(self.fig)

    def reset_app(self):
        # Show reset confirmation (optional)
        popup = LoadingPopup()
        popup.label.setText("Resetting")
        popup.show()
        # Reset circuit object
        self.circuit._reset()

        # Reset buttons
        for dot in self.dots:
            dot.setStyleSheet(button_stylesheet())
        for cdot in self.cdots:
            cdot.setStyleSheet(button_stylesheet(color=get_color_and_opacity(cdot)[0]))

        # Clear pressed button lists
        self.pressed_buttons.clear()
        self.pressed_cbuttons.clear()

        # Update the drawn circuit
        self.update_drawn_circuit()

        try:
            self.all_options.close()
        except AttributeError:
            1==1
            
            
        popup.close()


def start(circuit, N):
    app = QApplication(sys.argv)
    main = Main(circuit, N)
    main.show()
    app.exec_()
    
if __name__ in "__main__":
    N = 32 # number of qubits(/places)
    qc = circuit(N)
    start(qc, N)