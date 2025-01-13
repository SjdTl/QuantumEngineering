from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QComboBox,QPushButton, QLabel, QHBoxLayout,QVBoxLayout, QGridLayout, QMenuBar, QMainWindow, QDialog
import PyQt5.QtWidgets as Qt
import sys

import os

import matplotlib.pyplot as plt
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
        self.setStyleSheet(stylesheet)

        grid = QGridLayout()

        N_dots = 32
        self.dots = [Qt.QPushButton("CLICK") for _ in range(N_dots)]
        for dot, i in zip(self.dots, range(N_dots)):
            dot.setFixedSize(50, 50)
            dot.setStyleSheet(
            """
            QPushButton {
                border-radius: 25px; /* Half of the width/height */
                border: 2px solid white;
            }
            QPushButton:hover {
                border : 4px solid white;
                }
            """)
            grid.addWidget(dot, 0, i)

        # show grid
        central_widget.setLayout(grid)

        
    def settings(self):
        self.setWindowTitle("Testing")
        self.setGeometry(250,250,600,500)
    
    def button_events(self):
        1==1
        # self.dot1.clicked.connect()

    def reset_app(self):
        self.input_box.clear()
        self.output_box.clear()

def start():
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    app.exec_()
    
if __name__ in "__main__":
    start()