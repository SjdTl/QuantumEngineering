from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt
import sys
import os
from main import Main  # Assuming Main is in a separate module as in your original code

dir_path = os.path.dirname(os.path.realpath(__file__))

stylesheet = """
QWidget {
    background-color: #333; /* Light blue background */
}

QPushButton {
    background-color: #4682B4; /* Steel blue for buttons */
    color: white;
    font-size: 20px;
    border-radius: 15px;
    padding: 10px;
}

QPushButton:hover {
    background-color: #5A9BD4;
}

QPushButton:pressed {
    background-color: #4169E1;
}
"""

class StartScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_window = None  # Placeholder for Main window
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Quantum 'Mens erger je niet'")
        self.setFixedSize(800, 600)
        self.setStyleSheet(stylesheet)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Background Image
        background_label = QLabel(central_widget)
        pixmap = QPixmap(os.path.join(dir_path, "a"))
        background_label.setPixmap(pixmap)
        background_label.setGeometry(0, 0, 800, 600)
        background_label.setScaledContents(True)

        # Title Label
        title = QLabel("Quantum 'Mens erger je niet'", central_widget)
        title.setGeometry(0, 30, 800, 100)
        title.setStyleSheet("color: white; font-size: 48px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        # Play Button with Pawn
        play_button = QPushButton("PLAY", central_widget)
        play_button.setGeometry(300, 180, 250, 60)
        play_button.clicked.connect(lambda _, b = False: self.play(b))

        play_pawn = QPushButton(central_widget)
        play_pawn.setIcon(QIcon(os.path.join(dir_path, "UI figures", "red_pawn.svg")))
        play_pawn.setFixedSize(60, 60)
        play_pawn.setIconSize(play_pawn.size())
        play_pawn.setGeometry(230, 180, 60, 60)

        # Help Button with Pawn
        debug_button = QPushButton("PLAY (DEBUG)", central_widget)
        debug_button.clicked.connect(lambda _, b=True : self.play(b))

        debug_button.setGeometry(300, 260, 250, 60)

        debug_pawn = QPushButton(central_widget)
        debug_pawn.setIcon(QIcon(os.path.join(dir_path, "UI figures", "blue_pawn.svg")))
        debug_pawn.setFixedSize(60, 60)
        debug_pawn.setIconSize(debug_pawn.size())
        debug_pawn.setGeometry(230, 260, 60, 60)

        # Options Button with Pawn
        tutorial_button = QPushButton("TUTORIAL", central_widget)
        tutorial_button.setGeometry(300, 340, 250, 60)

        tutorial_pawn = QPushButton(central_widget)
        tutorial_pawn.setIcon(QIcon(os.path.join(dir_path, "UI figures", "green_pawn.svg")))
        tutorial_pawn.setFixedSize(60, 60)
        tutorial_pawn.setIconSize(tutorial_pawn.size())
        tutorial_pawn.setGeometry(230, 340, 60, 60)

    def play(self, debug = False):
        self.close()  # Close the Start screen
        self.main_window = Main(debug=debug)  # Create instance of Main window
        self.main_window.show()  # Show Main window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    start_screen = StartScreen()
    start_screen.show()
    sys.exit(app.exec_())
