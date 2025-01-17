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

def button_stylesheet(color="transparent", border_color='white', selected = False):
        stylesheet = rf"""
            QPushButton {{
                border-radius: 25px; /* Half of the width/height */
                background-color : {color if color != None else 'transparent'};
                border : {6 if selected == True else 2}px solid {border_color};
            }}
            QPushButton:hover {{
                border : 4px solid {border_color};
                }}
            """
        return stylesheet

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
    