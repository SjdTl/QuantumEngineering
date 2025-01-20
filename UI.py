import os as os
from PyQt5.QtGui import QIcon

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

def button_stylesheet(button, color="transparent", border_color='white', selected = False, pawn = 0, classical = True):
        quantum_transparency = 100
        color_rgba = {
                    'Red': rf"rgba(255, 0, 0, {255 if classical==True else quantum_transparency})",
                    'Blue': rf"rgba(0, 0, 255, {255 if classical==True else quantum_transparency})",
                    'Purple': rf"rgba(128, 0, 128, {255 if classical==True else quantum_transparency})",
                    'Green': rf"rgba(0, 150, 0, {255 if classical==True else quantum_transparency})",
                    None: "transparent",
                    "transparent" : "transparent"
                }


        stylesheet = rf"""
            QPushButton {{
                border-radius: 25px; /* Half of the width/height */
                background-color: {color_rgba[color]};
                border: {6 if selected == True else 2}px {"dashed" if pawn == 0 else ""} solid {border_color};
            }}
            QPushButton:hover {{
                border: 4px solid {border_color};
            }}
            """
        button.setStyleSheet(stylesheet)

def die_stylesheet(color="transparent"):
     return rf"""
            QPushButton {{
                border : 2px solid {color};
            }}
            QPushButton:hover {{
                border : 4px solid {color};
                }}
            """

dir_path = os.path.dirname(os.path.realpath(__file__))
die_cons = [QIcon(((os.path.join(dir_path, "UI figures", str(number) + '.svg')))) for number in range(0,7)]
    