from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QLabel, QDialog, QLineEdit
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt
import sys
import os
from main import Main 
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtGui import QPainter

dir_path = os.path.dirname(os.path.realpath(__file__))

stylesheet = """
QWidget {
    background-color: #333;
}

QPushButton {
    background-color: #4682B4;
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
QLineEdit {
    background-color: #4682B4;
    color: white;
    font-size: 10px;
    border-radius: 15px;
    padding: 10px;
}
"""
class enterAPI(QDialog):
    """Enter api in window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter API")
        self.setFixedSize(400, 200)
        self.setStyleSheet(stylesheet)

        self.api = QLineEdit(self)
        self.api.setGeometry(50, 50, 300, 30)
        self.api.setEchoMode(QLineEdit.Password)

        self.ok_button = QPushButton("OK", self)
        self.ok_button.setGeometry(150, 100, 100, 40)
        self.ok_button.clicked.connect(self.ok)

    def ok(self):
        self.close()

class StartScreen(QMainWindow):
    def __init__(self):
        self.token = None
        super().__init__()
        self.main_window = None  # Placeholder for Main window
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Quantum 'Mens erger je niet'")
        self.setFixedSize(800, 600)
        self.setStyleSheet(stylesheet)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.service = None
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
        play_button = QPushButton("PLAY (simulator)", central_widget)
        play_button.setGeometry(300, 180, 250, 60)
        play_button.clicked.connect(lambda _, b = True: self.play(simulation=b))

        play_pawn = QPushButton(central_widget)
        play_pawn.setIcon(QIcon(os.path.join(dir_path, "UI figures", "red_pawn.svg")))
        play_pawn.setFixedSize(60, 60)
        play_pawn.setIconSize(play_pawn.size())
        play_pawn.setGeometry(230, 180, 60, 60)

        # Help Button with Pawn
        self.token = None
        self.hardware_button = QPushButton("PLAY (hardware)", central_widget)
        self.hardware_button.clicked.connect(lambda _, b = False: self.play(simulation=b))
        self.hardware_button.setDisabled(True)

        self.hardware_button.setGeometry(300, 260, 250, 60)

        debug_pawn = QPushButton(central_widget)
        debug_pawn.setIcon(QIcon(os.path.join(dir_path, "UI figures", "blue_pawn.svg")))
        debug_pawn.setFixedSize(60, 60)
        debug_pawn.setIconSize(debug_pawn.size())
        debug_pawn.setGeometry(230, 260, 60, 60)

        self.login_button = QPushButton("LOGIN", central_widget)
        self.login_button.setGeometry(300, 420, 250, 60)
        self.login_button.clicked.connect(self.login)


        # Options Button with Pawn
        tutorial_button = QPushButton("TUTORIAL", central_widget)
        tutorial_button.setGeometry(300, 340, 250, 60)

        tutorial_pawn = QPushButton(central_widget)
        tutorial_pawn.setIcon(QIcon(os.path.join(dir_path, "UI figures", "green_pawn.svg")))
        tutorial_pawn.setFixedSize(60, 60)
        tutorial_pawn.setIconSize(tutorial_pawn.size())
        tutorial_pawn.setGeometry(230, 340, 60, 60)
    
    def login(self):
        self.api = enterAPI()
        self.api.exec_()
        self.token = self.api.api.text()
        from qiskit_ibm_runtime import QiskitRuntimeService
 
        QiskitRuntimeService.save_account(
        token=self.token,
        channel="ibm_quantum",
        overwrite=True # `channel` distinguishes between different account types
        )
        self.service = QiskitRuntimeService()
        self.hardware_button.setEnabled(True)
        self.login_button.setDisabled(True)
    
    def play(self, simulation=True, debug = False):
        self.save_as_svg()
        self.close()  # Close the Start screen

        self.main_window = Main(debug=debug, simulation=simulation, service = self.service)  # Create instance of Main window
        self.main_window.show()  # Show Main window

    def save_as_svg(self):
        filename = os.path.join(dir_path, "screenshots", "start_screen.svg")
        # Set up the SVG generator
        svg_generator = QSvgGenerator()
        svg_generator.setFileName(filename)
        svg_generator.setSize(self.size())
        svg_generator.setViewBox(self.rect())
        svg_generator.setTitle("SVG Screenshot")
        svg_generator.setDescription("An SVG rendering of a PyQt window")
        
        # Render the widget onto the SVG generator using QPainter
        painter = QPainter(svg_generator)
        self.render(painter)
        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    start_screen = StartScreen()
    start_screen.show()
    sys.exit(app.exec_())
