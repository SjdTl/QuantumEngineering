from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QComboBox,QPushButton, QLabel, QHBoxLayout,QVBoxLayout, QGridLayout, QMenuBar, QMainWindow, QDialog
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtSvg import QSvgWidget
import PyQt5.QtWidgets as Qt
import sys
from math import pi
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib as mtpl 

import numpy as np
import os
import scienceplots
import sounddevice as sd

import matplotlib.pyplot as plt
dir_path = os.path.dirname(os.path.realpath(__file__))


class LoadingPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reset")
        self.setFixedSize(200, 100)
        layout = QVBoxLayout()
        self.label = QLabel("Resetting")
        layout.addWidget(self.label)
        self.setLayout(layout)

class Main(QMainWindow):
    def __init__(self):
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

        self.dot1 = Qt.QPushButton("O")

        grid = QGridLayout()

        grid.addWidget(self.dot1, 0,0)  

        # show grid
        central_widget.setLayout(grid)

        self.setStyleSheet("""
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

            QPushButton {
                background-color: #66a3ff; /* Lighter background color for buttons */
                color: #333; /* Text color for buttons */
                border: 1px solid #fff; /* White border for buttons */
                border-radius: 5px; /* Rounded corners for buttons */
                padding: 5px 10px; /* Padding for buttons */
            }
                           
            QLabel, QLineEdit { margin : 0px; padding: 0px; }

            QPushButton:hover {
                background-color: #3399ff; /* Lighter background color for buttons on hover */
            }
        """)
        
    def settings(self):
        self.setWindowTitle("Chinese Checkers 1.0")
        self.setGeometry(250,250,600,500)
    
    def button_events(self):
        1==1
        # self.dot1.clicked.connect()

    def reset_app(self):
        self.input_box.clear()
        self.output_box.clear()

    
    
if __name__ in "__main__":
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    app.exec_()