import os as os
from PyQt5.QtGui import QIcon

stylesheet  ="""
            QWidget { /* specifies default color scheme in game and winner pop-up */
                background-color: #333; /* Darker background color */
                color: #fff; /* Text color */
            }

            QMenuBar {  /* specifies color scheme of the menu bar at the top of the window (file, debug, moves) */
                background-color: #444; /* Menu bar background color */
                color: #fff; /* Text color */
            }

            QMenuBar::menu:hover { /* specifies color directly surrounding the menu items */
                background-color: #444; /* Menu item background color */
            }
                                
            QMenu { /* specifies color scheme of the drop down menus of the menu items */
                background-color: #555; /* Default background for the menu */
                border: 1px solid #555; /* Border for the menu */
            }

            QMenu::item:hover { /* specifies color scheme when mouse hovering over items */
                background-color: #0066cc; /* Hover effect for menu items */
                color: #fff; /* Text color on hover */
            }

            QMenu::item:pressed { /* specifies color scheme when drop down menu item is pressed */
                background-color: #0066cc; /* Pressed state background */
                color: #fff; /* Text color on press */
            }
                           
            QLabel, QLineEdit { margin : 0px; padding: 0px; } /* specifies margin and padding around text in pop-ups */
            """

def button_stylesheet(button, color="transparent", border_color='white', selected = False, pawn = 0, classical = True):
        """
        Description
        ----------- 
        Specifies color and transparency of a position on the board and border response to:
        1. being occupied
        2. being hovered over
        3. being available for a move


        quantum_transparency: transparency when position is not 100% occupied

        color_rgba: 
            color depends on player occupying position
            not occupied: fully transparent
            100% occupied: fully opaque
            superposition: partially transparent

        stylesheet: 
            specifies default border radius
            implements background color
            if player turn:
                before dice roll: positions occupied by player -> dashed border
                after dice roll: positions available for movement -> thick border
            if hover over position: semi-thick border
        """

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
        """
        Description
        -----------
     
        Specifies visual effects of the dice boxes (bottom left on the screen)


        Border color depends on who's turn it is

        Default border width: 2px
        Border width when hovering over die box: 4px
        """

        return rf"""
            QPushButton {{
                border : 2px solid {color};
            }}
            QPushButton:hover {{
                border : 4px solid {color};
                }}
            """

# Get images of dice to display in the dice boxes
dir_path = os.path.dirname(os.path.realpath(__file__))
die_cons = [QIcon(((os.path.join(dir_path, "UI figures", str(number) + '.svg')))) for number in range(0,7)]
    