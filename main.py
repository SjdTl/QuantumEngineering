# CODE IN REPOSITORY
# IMPORT THE STYLESHEETS
from UI import stylesheet, button_stylesheet, die_cons, die_stylesheet

# IMPORT THE QUANTUM CIRCUITS
from game_logic.quantum_circuits import circuit

# LIBRARIES
# application from pyqt
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QComboBox,QPushButton, QLabel, QHBoxLayout,QVBoxLayout, QGridLayout, QMenuBar, QMainWindow, QDialog, QProgressBar
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QIcon
import PyQt5.QtCore as Qtc
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtGui import QPainter

# others
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import sys
import os
import numpy as np
import random
from pandas import DataFrame
import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.style.use('dark_background') 
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class BellTestPlot(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(stylesheet)

        # Create and configure the Matplotlib canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Use a layout to add widgets to the QDialog
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Data initialization
        self.xdata = []
        self.ydata = []
        self._plot_ref = None

        # Initialize the plot
        self.update_plot(0, 0)

    def update_plot(self, x, y):
        """Update the plot with new data."""
        self.xdata.append(x)
        self.ydata.append(y)
        
        if self._plot_ref is None:
            # Create the line plot initially
            self._plot_ref, = self.canvas.axes.plot(self.xdata, self.ydata, '-o', label="Data")
            self.canvas.axes.set_xlabel("Number of measurements")
            self.canvas.axes.set_ylabel("Bell violation")

            self.canvas.axes.legend()
        else:
            # Update the existing line plot
            self._plot_ref.set_data(self.xdata, self.ydata)
        
        # Adjust axes to fit the new data
        self.canvas.axes.relim()
        self.canvas.axes.autoscale_view()
        self.canvas.draw()

class LoadingPopup(QDialog):
    """
    Description
    -----------
    General class for a popup window with some text

    Parameters
    ----------
    header_text : str
        Text displayed as header name

    Examples
    --------
    popup = LoadingPopup(header_text = "Loading")
    popup.label.setText(rf"Loading")
    popup.exec_()

    >>> Creates a popup with as header_text "Loading" and text inside the popup "Loading"
    """
    def __init__(self, header_text : str):
        super().__init__()
        self.setWindowTitle(header_text)
        self.setFixedSize(300, 200)
        layout = QVBoxLayout()
        self.label = QLabel("")
        layout.addWidget(self.label)
        self.setLayout(layout)

class WinPopup(QDialog):
    """
    Description
    -----------
    Popup window for when a player wins. Contains the pawn of the player who won and a text saying who won

    Parameters
    ----------
    color : str
        Color of who won

    Examples
    --------
    popup = WinPopup('red)
    popup.exec_()
    """
    def __init__(self, color: str):
        super().__init__()
        self.setWindowTitle(rf"{color} has won")
        self.setFixedSize(300, 200)

        # Directly use QWidget as the dialog's content
        central_widget = QWidget(self)

        # Create a label for the popup
        self.label = QLabel(rf"{color} has won", central_widget)
        self.label.setAlignment(Qtc.Qt.AlignCenter)  # This should work now
        self.label.setGeometry(50, 20, 200, 30)

        # Set the stylesheet
        self.setStyleSheet(stylesheet)

        # Create a button with the pawn icon
        winner = QPushButton(central_widget)
        winner.setIcon(QIcon(os.path.join(dir_path, "UI figures", rf"{color}_pawn.svg")))
        winner.setFixedSize(100, 100)
        winner.setIconSize(winner.size())
        winner.setGeometry(100, 50, 100, 100)

    

class selectDicePopup(QDialog):
    """
    Description
    -----------
    Debug popup window in which the user can select the two die throws.
    When calling the exec_() method, the dice selected are stored in the attribute `dice_selected`.

    Methods
    ----------
    __init__ : Define the layout of the popup: 6 dice next to eachother
    selected_die : Method to store the selected die in the attribute `dice_selected` after clicking on a die

    Examples
    --------
    throw_menu = selectDicePopup()
    if throw_menu.exec_() == QDialog.Accepted:
        die_throws = throw_menu.dice_selected
    print(die_throws)

    >>> [1, 2] # after selecting die 1 and 2
    """
    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheet)
        self.setWindowTitle("Select dice")
        self.setFixedSize(600,300)
        grid = QGridLayout()
        self.select_dice = [Qt.QPushButton("") for _ in range(0,6)]
        for i, die in enumerate(self.select_dice):
            die.setIcon(die_cons[i+1])
            die.setIconSize(QSize(45,45))
            die.setFixedSize(50,50)
            die.setStyleSheet(die_stylesheet())
            die.clicked.connect(lambda _, b=i: self.selected_die(throw=b+1))
            grid.addWidget(die, 0, i)
        self.setLayout(grid)

        self.dice_selected = []
    
    def selected_die(self, throw):
        self.dice_selected.append(throw)

        if len(self.dice_selected)==2:
            print(self.dice_selected)
            self.accept()

class MeasurePopup(QDialog):
    """Popup during measurement"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheet)
        self.setWindowTitle("Measuring")
        self.setFixedSize(600,300)
        self.label= QLabel("MEASURING.......")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

class CircuitFigure(QDialog):
    """
    Description
    -----------
    General class for a popup window with a matplotlib figure. The figure can be updated with another figure
    by calling the method `plot` with the new figure as argument
    
    Methods
    ----------
    __init__ : Define the layout of the popup: a matplotlib figure
    plot : Method to update the canvas with a new figure
    
    Examples
    --------
    circuit = circuit(32)
    circuitfigure = CircuitFigure()
    fig = circuit.draw(mpl_open = False, term_draw = False)
    circuitfigure.plot(self.fig)
    circuitfigure.show()
    """
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
        plt.close()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.updateGeometry()

class Main(QMainWindow):
    """Main class for the game: UI and classical game logic"""
    def __init__(self, simulation = True, debug = False, service = None):
        """
        Description
        -----------
        Initialize the main class for the game: start up the UI, settings and quantum circuit

        Parameters
        ----------
        simulation : Boolean
            If True, the quantum circuit is simulated using AerSimulator(). If False, the quantum circuit is run on a real quantum computer
        debug : Boolean
            If True, the game is in debug mode. This is not very different from normal mode, except that some debug features are already enabled, but can be toggled on and off
        """
        self.simulation = simulation
        self.debug = debug
        self.service = service


        self.N = 32
        self.circuit = circuit(self.N)
        self.history = []

        self.circuitfigure = CircuitFigure()
        self.fig = self.circuit.draw(mpl_open = False, term_draw = False)
        self.circuitfigure.plot(self.fig)
        if debug:
            self.circuitfigure.show()

        super().__init__()
        self.setWindowTitle("Quantum Ludo")
        self.setGeometry(250,250,600,500)
        self.initUI()
        self.window()
        self.total_turns = 0
        self.next_turn()

    def window(self):
        """Creates the top left menu bar containg some file options (undo, screenshot, reset), debug options (measure, selecting dice, autoplay) and some standard moves for testing"""
        # Menu bar
        self.menu = QMenuBar(self)
        self.file_menu = self.menu.addMenu("File")
        self.debug_menu = self.menu.addMenu("Debug")
        self.test_moves = self.menu.addMenu("Moves")
        self.special_measure = self.menu.addMenu("Special measures")
        self.setMenuBar(self.menu)
        
        self.reset = Qt.QAction("Reset", self)
        self.reset.setShortcut("Ctrl+R")
        self.reset.triggered.connect(self.reset_app)

        self.force_standard_basis_button = Qt.QAction("Set measurement basis to be dependent on pawn", self)
        self.force_standard_basis_button.triggered.connect(lambda: self.force_standard_basis())
        self.force_global_standard_basis = True

        self.screenshot = Qt.QAction("Screenshot", self)
        self.screenshot.setShortcut("f5")
        self.screenshot.triggered.connect(self.save_as_svg)

        self.undo_button = Qt.QAction("Undo", self)
        self.undo_button.setShortcut("Ctrl+Z")
        self.undo_button.triggered.connect(self.undo)

        self.measure_button = Qt.QAction("Measure", self)
        self.measure_button.setShortcut("Ctrl+M")
        self.measure_button.triggered.connect(lambda: self.measure_action(standard_basis=True))

        self.skip_turn = Qt.QAction("Skip turn", self)
        self.skip_turn.setShortcut("Ctrl+S")
        self.skip_turn.triggered.connect(self.next_turn)

        self.throw_dice_button = Qt.QAction("Throw dice", self)
        self.throw_dice_button.setShortcut("Ctrl+D")
        self.throw_dice_button.triggered.connect(self.throw_dice)
        self.throw_dice_button.setEnabled(False)

        self.select_dice_button = Qt.QAction("Select dice", self)
        self.select_dice_button.setShortcut("Ctrl+P")
        self.select_dice_button.triggered.connect(lambda: self.throw_dice(debug_throw=True))
        self.select_dice_button.setEnabled(False)

        self.random_turn_button = Qt.QAction("Random move", self)
        self.random_turn_button.setShortcut("Ctrl+Alt+R")
        self.random_turn_button.triggered.connect(lambda: self.next_turn(random_turn=True))
        self.random_turn_button.setEnabled(False)

        self.print_positions_button = Qt.QAction("Print positions", self)
        self.print_positions_button.triggered.connect(self.print_positions)

        self.print_move_options_button = Qt.QAction("Print move options", self)
        self.print_move_options_button.triggered.connect(self.print_all_options)

        self.circuit_visibility_button = Qt.QAction("Show circuit", self)
        if self.debug:
            self.circuit_visibility_button.setText("Close circuit")
        self.circuit_visibility_button.setShortcut("Ctrl+C")
        self.circuit_visibility_button.triggered.connect(self.circuit_visibility)

        self.position_names_button = Qt.QAction("Show position names", self)
        if self.debug:
            self.position_names_button.setText("Remove position names")
        self.position_names_button.triggered.connect(self.show_position_names)

        self.qc_captures_button = self.test_moves.addMenu("QC captures")

        capture_types = ['normal']
        self.qc_capture_buttons = [Qt.QAction(capture_type) for capture_type in capture_types]
        for button, capture_type in zip(self.qc_capture_buttons, capture_types):
            button.triggered.connect(lambda _, b = capture_type: self.start_in_quantum_classical_capture(type_cap = b))
            self.qc_captures_button.addAction(button)

        self.qq_captures_button = self.test_moves.addMenu("QQ captures")
        capture_types = ['normal', 'double_jump', 'triple_jump', 'jump_over_own_pawn', 'jump_over_third_color', 'double_capture', 'jump_over_own_pawn2']
        self.qq_capture_buttons = [Qt.QAction(capture_type) for capture_type in capture_types]
        for button, capture_type in zip(self.qq_capture_buttons, capture_types):
            button.triggered.connect(lambda _, b = capture_type: self.start_in_quantum_quantum_capture(type_cap = b))
            self.qq_captures_button.addAction(button)

        self.cc_captures_button = self.test_moves.addMenu("CC captures")
        capture_types = ['normal', 'new_pawn_capture']
        self.cc_capture_buttons = [Qt.QAction(capture_type) for capture_type in capture_types]
        for button, capture_type in zip(self.cc_capture_buttons, capture_types):
            button.triggered.connect(lambda _, b = capture_type: self.start_in_classical_classical_capture(type_cap = b))
            self.cc_captures_button.addAction(button)

        self.cq_captures_button = self.test_moves.addMenu("CQ captures")
        capture_types = ['normal', 'double_jump', 'new_pawn_capture', 'new_pawn_double_jump']
        self.cq_capture_buttons = [Qt.QAction(capture_type) for capture_type in capture_types]
        for button, capture_type in zip(self.cq_capture_buttons, capture_types):
            button.triggered.connect(lambda _, b = capture_type: self.start_in_classical_quantum_capture(type_cap = b))
            self.cq_captures_button.addAction(button)

        self.all_pawns_button = self.test_moves.addMenu("Add one pawn per color")
        positions = [0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95]
        self.all_pawns_buttons = [Qt.QAction(str(position)) for position in positions]
        for button, position in zip(self.all_pawns_buttons, positions):
            button.triggered.connect(lambda _, b = position: self.add_all_pawns_on_board(position = b))
            self.all_pawns_button.addAction(button)

        self.finish_positions_button = self.test_moves.addMenu("Finish positions")
        finish_types = ['single_move', 'single_capture_finish', 'single_from_super', 'single_win', 'super_move', 'super_win', 'double_super', 'super_cap', 'double_super_win_cap']
        self.finish_position_buttons = [Qt.QAction(finish_type) for finish_type in finish_types]
        for button, finish_type in zip(self.finish_position_buttons, finish_types):
            button.triggered.connect(lambda _, b = finish_type: self.start_in_finish_positions(fin_type = b))
            self.finish_positions_button.addAction(button)

        self.bell_test_button = Qt.QAction("Bell test", self)
        self.bell_test_button.triggered.connect(self.bell_test)

        trigger_options = [(self.colors[0],    0), (self.colors[0],    1), (self.colors[1],   0), (self.colors[1],   1), (self.colors[2],  0), (self.colors[2],  1), (self.colors[3], 0), (self.colors[3], 1)]
        measure_buttons = [Qt.QAction(rf"{c}, pawn {p}", self) for (c, p) in trigger_options]
        for smeasure_button, trigger_option in zip(measure_buttons, trigger_options):
            smeasure_button.triggered.connect(lambda _, b = trigger_option: self.measure_action(trigger=b))
            self.special_measure.addAction(smeasure_button)

        self.keep_circuit_open = Qt.QAction("Keep circuit open", self)
        self.keep_circuit_open.triggered.connect(self.keep_circuit_open_action)
        self.execpopup_measure = False
        self.special_measure.addAction(self.keep_circuit_open)

        self.file_menu.addAction(self.reset)
        self.file_menu.addAction(self.undo_button)
        self.file_menu.addAction(self.throw_dice_button)
        self.file_menu.addAction(self.screenshot)
        self.file_menu.addAction(self.force_standard_basis_button)
        self.debug_menu.addAction(self.measure_button)
        self.debug_menu.addAction(self.skip_turn)
        self.debug_menu.addAction(self.select_dice_button)
        self.debug_menu.addAction(self.random_turn_button)
        self.debug_menu.addAction(self.circuit_visibility_button)
        self.debug_menu.addAction(self.position_names_button)
        self.debug_menu.addAction(self.print_positions_button)
        self.debug_menu.addAction(self.print_move_options_button)
        self.test_moves.addAction(self.bell_test_button)

    def initUI(self):
        """
        Description
        -----------
        Build the board, the dice, the progress bar and the pawns in the home and final positions
        
        Created widgets
        ----------------
        self.board_positions : list of QPushButtons
            List of buttons representing the positions (0-32) on the board
        self.home_positions : list of QPushButtons
            List of buttons representing the home positions (0-8) of the pawns
        self.final_positions : list of QPushButtons
            List of buttons representing the final positions (0-8) of the pawns
        self.dice : list of QPushButtons
            List of buttons representing the two dice
        
        Note
        ----
        The position buttons all have three properties: "Color", "Pawn" and "Selected", which represent:
            - "Color": the color of the pawn at that position. None if no pawn is present
            - "Pawn": the number (0 or 1) of the pawn at that position. None if no pawn is present
            - "Selected": a boolean indicating if the pawn is at a position where it can be moved
        This code does not style the buttons. This is done in the method `update_stylesheets` using these three properties
        The game logic also uses these same properties to determine the possible moves

        Example
        --------
        # The second red pawn is present at position 2 on the board
        self.board_positions[2].setProperty("Color", self.colors[0])
        self.board_positions[2].setProperty("Pawn", 1)
        self.board_positions[2].setProperty("Selected", False)
        """
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.setStyleSheet(stylesheet)

        grid = QGridLayout()

        # ----------------
        # Create the board
        # ----------------
        self.board_positions = [Qt.QPushButton(rf'{i if self.debug==True else ""}') for i in range(self.N)]

        x=3
        y=0
        for i, pos in enumerate(self.board_positions):
            pos.setFixedSize(50, 50)
            pos.setProperty("Color", None)
            pos.setProperty("Pawn", None)
            pos.setProperty("Selected", False)

            grid.addWidget(pos, y, x)
            if (0 <= i < 2) or (5 <= i < 8) or (26 <= i < 29):
                x += 1
            if (10 <= i < 13) or (16 <= i < 18) or (21 <= i < 24):
                x -= 1
            if (2 <= i < 5) or (8 <= i < 10) or (13 <= i < 16):
                y += 1
            if (18 <= i < 21) or (24 <= i < 26) or (29 <= i <= 31):  # 29 <= i <= 31 is valid
                y -= 1

        # ---------------------------------------------------------------------------------------------------------------------
        # Initialize the colours and the position that they occupy after going out of the home position (after throwing a 6)
        # ---------------------------------------------------------------------------------------------------------------------
        self.colors = ['Red', 'Green', 'Blue', 'Purple'] # MUST BE FOUR COLOURS
        self.measure_basis_dict = {
            (self.colors[0],    0): {self.colors[0]:    "Z", self.colors[1]:  "Q", self.colors[2]:   "X", self.colors[3]: "T"},
            (self.colors[0],    1): {self.colors[0]:    "Z", self.colors[3]: "Q", self.colors[2]:   "X", self.colors[1]:  "T"},
            (self.colors[2],   0): {self.colors[2]:   "Z", self.colors[3]: "Q", self.colors[0]:    "X", self.colors[1]:  "T"},
            (self.colors[2],   1): {self.colors[2]:   "Z", self.colors[1]:  "Q", self.colors[0]:    "X", self.colors[3]: "T"},
            (self.colors[1],  0): {self.colors[1]:  "Z", self.colors[0]:    "Q", self.colors[3]: "X", self.colors[2]:   "T"},
            (self.colors[1],  1): {self.colors[1]:  "Z", self.colors[2]:   "Q", self.colors[3]: "X", self.colors[0]:    "T"},
            (self.colors[3], 0): {self.colors[3]: "Z", self.colors[2]:   "Q", self.colors[1]:  "X", self.colors[0]:    "T"},
            (self.colors[3], 1): {self.colors[3]: "Z", self.colors[0]:    "Q", self.colors[1]:  "X", self.colors[2]:   "T"}
        }
        self.current_turn = self.colors[-1]
        self.start_position = {
            self.colors[0] : 26,
            self.colors[1] : 2,
            self.colors[2] : 10,
            self.colors[3] : 18
        }

        # -------------------------
        # Create the home positions
        # -------------------------
        self.home_positions = [Qt.QPushButton(rf'{i if self.debug==True else ""}') for i in range(8)]
        for i, pos in enumerate(self.home_positions):
            current_color = self.colors[int(np.floor(i/2))]
            pos.setFixedSize(50,50)
            # pos.setStyleSheet(button_stylesheet(color = current_color))
            pos.setProperty("Color", current_color)
            pos.setProperty("Selected", False)


            if i == 0: grid.addWidget(pos, 1, 0), pos.setProperty("Pawn", 0)
            if i == 1: grid.addWidget(pos, 0, 1), pos.setProperty("Pawn", 1)
            if i == 2: grid.addWidget(pos, 0, 7), pos.setProperty("Pawn", 0)
            if i == 3: grid.addWidget(pos, 1, 8), pos.setProperty("Pawn", 1)
            if i == 4: grid.addWidget(pos, 7, 8), pos.setProperty("Pawn", 0)
            if i == 5: grid.addWidget(pos, 8, 7), pos.setProperty("Pawn", 1)
            if i == 6: grid.addWidget(pos, 8, 1), pos.setProperty("Pawn", 0)
            if i == 7: grid.addWidget(pos, 7, 0), pos.setProperty("Pawn", 1)

        # ---------------------------
        # Create the final positions
        # ---------------------------
        self.final_positions = [Qt.QPushButton(rf'{i if self.debug==True else ""}') for i in range(8)]
        for i, pos in enumerate(self.final_positions):
            current_color = self.colors[int(np.floor(i/2))]
            pos.setFixedSize(50,50)
            # pos.setStyleSheet(button_stylesheet(border_color = current_color))
            pos.setProperty("Color", None)
            pos.setProperty("Pawn", None)
            pos.setProperty("Selected", False)

            if i == 0: grid.addWidget(pos, 4, 1)
            if i == 1: grid.addWidget(pos, 4, 2)
            if i == 2: grid.addWidget(pos, 1, 4)
            if i == 3: grid.addWidget(pos, 2, 4)
            if i == 4: grid.addWidget(pos, 4, 7)
            if i == 5: grid.addWidget(pos, 4, 6)
            if i == 6: grid.addWidget(pos, 7, 4)
            if i == 7: grid.addWidget(pos, 6, 4)

        # ---------------
        # Create the dice
        # ---------------
        number_of_dice = 2
        self.dice = [Qt.QPushButton() for _ in range(number_of_dice)]
        for i, die in enumerate(self.dice):
            die.setIcon(die_cons[0])
            die.setIconSize(QSize(45, 45))
            die.setFixedSize(50, 50)
            die.setStyleSheet(die_stylesheet())
            grid.addWidget(die, 9, i)

        self.update_stylesheets() # Style the buttons


        # Add the progress bar to the layout
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 20)
        grid.addWidget(self.progress_bar, 9, 2, 1, 2)  # next to the dice

        central_widget.setLayout(grid)

    def next_turn(self, random_turn = False):
        """
        Description
        -----------
        Method to switch to the next turn. This method is called after a player has made a move.
        - Redraw the circuit
        - Update stylesheets
        - Potentially measure the circuit (if therre are more than 20 pawns on the board)
        - Save the game
        - Give turn to the next color
        - Go to the throw_dice method
        """
        self.update_drawn_circuit()
        self.update_stylesheets(deselect=True)
        occupied_positions_count = sum(1 for pos in self.board_positions if pos.property("Color") is not None)
        if occupied_positions_count >= 20:
            QTimer.singleShot(500, lambda : self.measure_action(next_turn=False, standard_basis=True))
            return  # Exit the method after measuring
        self.save()

        if random_turn == False:
            self.total_turns += 1
            self.current_turn = self.colors[(self.colors.index(self.current_turn)+1)%4]
            for die in self.dice:
                die.clicked.connect(self.throw_dice)
                die.setStyleSheet(die_stylesheet(self.current_turn))
                die.setIcon(die_cons[0])
                
        self.throw_dice_button.setEnabled(True)
        self.select_dice_button.setEnabled(True)
        self.random_turn_button.setEnabled(True)

        self.update_progress_bar()

        if random_turn == True:
            self.throw_dice(random_turn = True)
        

    def throw_dice(self, debug_throw = False, random_turn = False):
        """Throw dice (randomly if debug_throw is False, otherwise let the user select the dice) and move on to the game logic"""
        if debug_throw:
            throw_menu = selectDicePopup()
            if throw_menu.exec_() == QDialog.Accepted:
                self.die_throws = throw_menu.dice_selected
        else: 
            ar = [1,2,3,4,5,6]
            self.die_throws = [random.choice(ar), random.choice(ar)]

            if self.debug and self.total_turns == 2:
                self.die_throws = [6,random.choice(ar)] #guarantee a six

        for i, die in enumerate(self.dice):
            die.setIcon(die_cons[self.die_throws[i]])
            die.setIconSize(QSize(45,45))

        for button in self.dice:
            button.clicked.disconnect(self.throw_dice)
        self.throw_dice_button.setEnabled(False)
        self.select_dice_button.setEnabled(False)
        self.random_turn_button.setEnabled(False)

        if random_turn:
            # Wait 250 ms before starting the game logic after a random turn.
            # This is more clear for the player to see what happens
            QTimer.singleShot(250, lambda : self.game_logic(random_turn = True)) 
        else:
            self.game_logic()


    def game_logic(self, random_turn = False):
        """
        Description
        -----------
        Game logic to determine the possible moves for the current player and make the buttons clickable for the player to make a move
        - Determine the possible moves, which can be three possible types:
            - superposition move: move a pawn into a superposition (for example: |100⟩ -> |010⟩ + |001⟩)
            - new pawn move: move a pawn from the home position to the board (|0⟩ -> |1⟩)
            - single move: move a pawn from one position to another (for example: q1 SWAP q2)
        - Make the buttons clickable for the player to make a move or select one randomly if random_turn == True
        """
        # --------------------
        # Find pawn properties
        # --------------------
        self.update_stylesheets(deselect=True)
        pawns_on_board = [[position.property("Color"), position.property("Pawn")] for position in self.board_positions]
        pawns_on_spawn = [[position.property("Color"), position.property("Pawn")] for position in self.home_positions]

        
        # -------------------
        # Find possible moves
        # -------------------

        superposition_move_options = [i for i in range(len(pawns_on_board))
                                    if pawns_on_board[i][0] == self.current_turn 
                                    and ((pawns_on_board[(i+self.die_throws[0])%32][0] is None or pawns_on_board[(i+self.die_throws[0])%32][0] != self.current_turn)
                                    and (pawns_on_board[(i+self.die_throws[1])%32][0] is None or pawns_on_board[(i+self.die_throws[1])%32][0] != self.current_turn))
                                    and self.die_throws[0] != self.die_throws[1]]

        new_pawn_options = [i for i in range(len(pawns_on_spawn))
                            if pawns_on_spawn[i][0] == self.current_turn
                            and pawns_on_board[self.start_position[self.current_turn]][0] != self.current_turn
                            and 6 in self.die_throws]

        single_move_options = [i for i in range(len(pawns_on_board))
                                if pawns_on_board[i][0] == self.current_turn
                                and (pawns_on_board[(i+self.die_throws[0])%32][0] is None or pawns_on_board[(i+self.die_throws[0])%32][0] != self.current_turn)
                                and self.die_throws[0] == self.die_throws[1]]
        
        all_options = [superposition_move_options, new_pawn_options, single_move_options]
        self.all_options = all_options

        # ------------------------------------------------
        # Make buttons clickable or select a move randomly
        # ------------------------------------------------

        if all(len(option) == 0 for option in all_options):
            if random_turn == False:
                popup = LoadingPopup(header_text = "No options")
                popup.label.setText(rf"No options for {self.current_turn}")
                popup.exec_()
            self.next_turn()
        else: 
            if random_turn:
                options = [
                    None if len(superposition_move_options) == 0 else lambda: self.move(move_from=random.choice(superposition_move_options)),
                    None if len(new_pawn_options) == 0 else lambda: self.new_pawn(move_from=random.choice(new_pawn_options)),
                    None if len(single_move_options) == 0 else lambda: self.direct_move(move_from=random.choice(single_move_options)),
                ]
                # Filter out `None` values
                options = [option for option in options if option is not None]
                random.choice(options)()
            else: 
                for i in superposition_move_options:
                    self.board_positions[i].setProperty("Selected", True)
                    self.board_positions[i].clicked.connect(lambda _, b=i: self.move(move_from = b))
                for i in new_pawn_options:
                    self.home_positions[i].setProperty("Selected", True)
                    self.home_positions[i].clicked.connect(lambda _, b = i: self.new_pawn(move_from = b))
                for i in single_move_options:
                    self.board_positions[i].setProperty("Selected", True)
                    self.board_positions[i].clicked.connect(lambda _, b=i: self.direct_move(move_from = b))
        self.update_stylesheets(deselect=False)

    def find_next_available_spot(self, changing_move, constant_move=None):
        """
        Test if the position to move to is occupied (this happens for example when capturing a pawn)
        If this is the case, find the next possible position to move to
        When moving the pawn into a superposition, the pawn can overlap with itself.
        To find the next possible position in this case provide the two arguments
        """
        while (self.board_positions[changing_move].property("Color") is not None 
            or (constant_move is not None and changing_move == constant_move)):
            changing_move = (changing_move + 1) % 32
        return changing_move
    
    def check_if_moving_in_final_positions(self, move_from, move_to):
        """Check if the move_to position is beyond the final_position for a color on a board. If so, move to the final position"""
        start_position = self.start_position[self.current_turn]
        for i, move in enumerate(move_to):
            if (move_from - start_position) % 32 > 16 and (move - start_position) % 32 < 16: #this might not be the most general solution, but since the maximum movement is 6 this will work
                move_to[i] = self.current_turn
        return move_to

    def direct_move(self, move_from, to_next_turn = True):
        """Move a pawn from one position to another and potentially capture another pawn"""
        move_to = [(move_from + self.die_throws[0]) % 32]
        captives = [pos for pos in move_to if self.board_positions[pos].property("Color") != None]
        normal_move = [pos for pos in move_to if self.board_positions[pos].property("Color") is None]
        captive_entanglement = [[i for i in range(0,32)
                                if self.board_positions[i].property("Color") == self.board_positions[move].property("Color")
                                and self.board_positions[i].property("Pawn") == self.board_positions[move].property("Pawn")
                                and move != i] for move in captives]
        capture_move = list(map(lambda move: self.find_next_available_spot(move, None), captives))
        
        normal_move = self.check_if_moving_in_final_positions(move_from, normal_move)
        capture_move = self.check_if_moving_in_final_positions(move_from, capture_move)
        move_to = normal_move + capture_move

        final_pos : int

        if self.current_turn in move_to:
            for prop in ["Color", "Pawn"]:
                pawn = self.board_positions[move_from].property("Pawn")
                final_pos = self.colors.index(self.current_turn) * 2 + pawn
                self.final_positions[final_pos].setProperty(prop, self.board_positions[move_from].property(prop))
                self.board_positions[move_from].setProperty(prop, None)
            move_to = [self.N] 
            capture_move = [self.N]
        else:
            for prop in ["Color", "Pawn"]:
                self.board_positions[move_to[0]].setProperty(prop, self.board_positions[move_from].property(prop))
                self.board_positions[move_from].setProperty(prop, None)
        
        self.circuit.switch([move_from], move_to)
        
        if captives:
            self.circuit.capture(capture_move, captives, captive_entanglement[0])
        if to_next_turn:
            if move_to[0] < 32:
                self.next_turn()
            else:
                self.update_stylesheets(deselect=True)
                self.measure_action(final_position = final_pos)

    def move(self, move_from, to_next_turn = True):
        """Move a pawn from one position to two others (in a superposition) and potentially capture another or two other pawns"""
        move_to = [(move_from + self.die_throws[0]) % 32, (move_from + self.die_throws[1]) % 32]
        move_to.sort()
        captives = [pos for pos in move_to if self.board_positions[pos].property("Color") != None]
        normal_move = [pos for pos in move_to if self.board_positions[pos].property("Color") is None]
        captive_entanglement = [[i for i in range(0,32)
                                if self.board_positions[i].property("Color") == self.board_positions[move].property("Color")
                                and self.board_positions[i].property("Pawn") == self.board_positions[move].property("Pawn")
                                and move != i] for move in captives]
        capture_move = list(map(lambda move: self.find_next_available_spot(move, None), captives))


        if len(captives) != 0:
            capture_move[0] = self.find_next_available_spot(changing_move=capture_move[0], constant_move=(normal_move[0] if len(captives) == 1 else capture_move[1]))

        normal_move = self.check_if_moving_in_final_positions(move_from, normal_move)
        capture_move = self.check_if_moving_in_final_positions(move_from, capture_move)
        
        nr_of_final_positions = sum(1 for pos in normal_move+capture_move if pos == self.current_turn)
        if nr_of_final_positions == 1:
            normal_move = list(map(lambda x: 32 if x == self.current_turn else x, normal_move))
            capture_move = list(map(lambda x: 32 if x == self.current_turn else x, capture_move))
        if nr_of_final_positions == 2:
            if len(normal_move) == 2:
                normal_move = [32, 33]
            elif len(capture_move) == 2:
                capture_move = [32, 33]
            else:
                normal_move = list(map(lambda x: 32 if x == self.current_turn else x, normal_move))
                capture_move = list(map(lambda x: 33 if x == self.current_turn else x, capture_move))
        move_to = normal_move + capture_move
        pawn = self.board_positions[move_from].property("Pawn")
        color = self.board_positions[move_from].property("Color")
        final_pos = self.colors.index(self.current_turn) * 2 + pawn

        self.circuit.move(move_from = [move_from], move_to = move_to)
        for i in range(len(captives)):
            self.circuit.capture(capturer=[capture_move[i]], captive = [captives[i]], captive_entanglement=captive_entanglement[i])   


        board_prop = [pawn, color]

        for i, prop in enumerate(["Pawn", "Color"]):
            if nr_of_final_positions == 0:
                self.board_positions[move_to[0]].setProperty(prop, board_prop[i])
                self.board_positions[move_to[1]].setProperty(prop, board_prop[i])
            if nr_of_final_positions == 1:
                self.final_positions[final_pos].setProperty(prop, board_prop[i])
                for pos in move_to:
                    if pos < 32:
                        self.board_positions[pos].setProperty(prop, self.board_positions[move_from].property(prop))
            if nr_of_final_positions == 2:
                self.final_positions[final_pos].setProperty(prop, board_prop[i])
            self.board_positions[move_from].setProperty(prop, None)
            

        if to_next_turn:
            if nr_of_final_positions == 0:
                self.next_turn()
            else:
                self.update_stylesheets(deselect=True)
                self.measure_action(final_position = final_pos)

    def new_pawn(self, move_from, optional_move_to = None, to_next_turn = True):
        """Move a pawn from the home position to the board and potentially capture another pawn"""
        move_to_original = self.start_position[self.current_turn] if optional_move_to == None else optional_move_to
        move_to = self.find_next_available_spot(move_to_original)
        captive_entanglement = [i for i in range(0,32)
                                if self.board_positions[i].property("Color") == self.board_positions[move_to_original].property("Color")
                                and self.board_positions[i].property("Pawn") == self.board_positions[move_to_original].property("Pawn")
                                and move_to_original != i]
        
        for prop in ["Color", "Pawn"]:
            self.board_positions[move_to].setProperty(prop, self.home_positions[move_from].property(prop))
            self.home_positions[move_from].setProperty(prop, None)

        self.circuit.new_pawn([move_to])

        if move_to != move_to_original:
            self.circuit.capture([move_to], [move_to_original], captive_entanglement)

        if to_next_turn:
            self.next_turn()

    def measure_action(self, final_position = None, next_turn = True, trigger = None, standard_basis = False, bell_test = False):
        """Measure the circuit and update the board accordingly"""
        # Add debug flag to force duplicate pawns
        force_duplicate = False  # For testing duplicate pawn removal
        
        if (trigger != None and self.force_global_standard_basis == True) or self.force_global_standard_basis == False:
            if standard_basis == False:
                if trigger == None:
                    trigger = (self.current_turn, final_position % 2)
                measure_basis = [self.measure_basis_dict[trigger][pos.property("Color")]
                                if pos.property("Color") is not None else None
                                for pos in self.board_positions]
                # measure basis of pawn that finished
                if final_position is not None:
                    # Append same thing twice
                    measure_basis.append([self.measure_basis_dict[trigger][self.current_turn]] * 2)
                else:
                    measure_basis.append([None, None])
                self.circuit.measure_basis(measure_basis)


        # -------
        # Measure
        # -------
        if bell_test == False:
            self.update_drawn_circuit()
            measure_popup = MeasurePopup()
            
            measure_popup.show()
        positions, out_with_freq, nr_of_qubits_used = self.circuit.measure(out_internal_measure=True, efficient = True, simulator = self.simulation, service = self.service)
        
        # Force a duplicate pawn for testing
        if force_duplicate and len(positions) > 0:
            # Add a duplicate pawn at position + 1
            for pos in positions[:]:  # Use slice to avoid modifying while iterating
                if pos < len(self.board_positions) - 1:  # Ensure we don't go out of bounds
                    positions.append((pos + 1) % 32)
                    print(f"DEBUG: Forced duplicate pawn at position {(pos + 1) % 32}")

        if bell_test == False:
            print(nr_of_qubits_used)
            print(out_with_freq)
            print(positions)

        if self.execpopup_measure:
            self.circuitfigure.exec_()

        # ---------------------------------
        # Remove pawns that no longer exist
        # ---------------------------------
        if bell_test == False:
            for pos in range(0,len(self.board_positions)):
                if pos not in positions:
                    for prop in ["Color", "Pawn"]:
                        self.board_positions[pos].setProperty(prop, None)
            if final_position != None:
                if not(32 in positions or 33 in positions):
                    self.final_positions[final_position].setProperty("Color", None)
                    self.final_positions[final_position].setProperty("Pawn", None)

            # If pawn appears in winning position, remove it from other positions
            if final_position is not None and (32 in positions or 33 in positions):
                pawn_num = final_position % 2
                for pos in range(len(self.board_positions)):
                    if (pos in positions and 
                        self.board_positions[pos].property("Color") == self.current_turn and
                        self.board_positions[pos].property("Pawn") == pawn_num):
                        print(f"Removing {self.current_turn} pawn {pawn_num} from position {pos} as it reached winning position")
                        self.board_positions[pos].setProperty("Color", None)
                        self.board_positions[pos].setProperty("Pawn", None)

            # Remove duplicate pawns keeping only the furthest one
            for color in self.colors:
                for pawn in [0, 1]:
                    # Find all positions for this color/pawn combination
                    pawn_positions = []
                    for pos in range(len(self.board_positions)):
                        if (pos in positions and 
                            self.board_positions[pos].property("Color") == color and 
                            self.board_positions[pos].property("Pawn") == pawn):
                            pawn_positions.append(pos)
                    
                    # If there are duplicates, keep only the furthest one
                    if len(pawn_positions) > 1:
                        start_pos = self.start_position[color]
                        furthest_pos = max(pawn_positions, key=lambda x: (x - start_pos) % 32)
                        
                        # Remove all but the furthest position
                        for pos in pawn_positions:
                            if pos != furthest_pos:
                                print(f"Removing duplicate {color} pawn {pawn} at position {pos}, keeping position {furthest_pos}")
                                self.board_positions[pos].setProperty("Color", None)
            
                                self.board_positions[pos].setProperty("Pawn", None)

            # -------------------------------------------------------------------
            # Check if a pawn was captured and put it back into its home position
            # -------------------------------------------------------------------
            pawns = [[pos.property("Color"), pos.property("Pawn")] for pos in self.board_positions + self.final_positions
                    if pos.property("Color") != None]
            all_pawns = [[color, i] for i in [0,1] for color in self.colors]
            pawns_at_spawn = [pawn for pawn in all_pawns if pawn not in pawns]


            pos = self.home_positions
            if [self.colors[0], 0] in pawns_at_spawn: pos[0].setProperty("Pawn", 0), pos[0].setProperty("Color", self.colors[0])
            if [self.colors[0], 1] in pawns_at_spawn: pos[1].setProperty("Pawn", 1), pos[1].setProperty("Color", self.colors[0])
            if [self.colors[1], 0] in pawns_at_spawn: pos[2].setProperty("Pawn", 0), pos[2].setProperty("Color", self.colors[1])
            if [self.colors[1], 1] in pawns_at_spawn: pos[3].setProperty("Pawn", 1), pos[3].setProperty("Color", self.colors[1])
            if [self.colors[2], 0] in pawns_at_spawn: pos[4].setProperty("Pawn", 0), pos[4].setProperty("Color", self.colors[2])
            if [self.colors[2], 1] in pawns_at_spawn: pos[5].setProperty("Pawn", 1), pos[5].setProperty("Color", self.colors[2])
            if [self.colors[3], 0] in pawns_at_spawn: pos[6].setProperty("Pawn", 0), pos[6].setProperty("Color", self.colors[3])
            if [self.colors[3], 1] in pawns_at_spawn: pos[7].setProperty("Pawn", 1), pos[7].setProperty("Color", self.colors[3])

            measure_popup.close()

        new_positions = [p for p in range(len(self.board_positions)) if self.board_positions[p].property("Color") is not None]
        self.circuit._reset()
        self.circuit.new_pawn(new_positions)

        self.progress_bar.setValue(0)
        if self.win() == False or next_turn == False:
            self.next_turn()
        if bell_test == True:
            return positions

    def win(self):
        """Check if a player has won the game. If so, show WinPopup() and reset the game"""
        final_position_colors = [pos.property("Color") for pos in self.final_positions]
        if any(final_position_colors.count(color) == 2 for color in self.colors):
            self.update_stylesheets()
            popup = WinPopup(self.current_turn)
            popup.exec_()
            self.reset_app()
            return True
        else:
            return False

    def update_stylesheets(self, deselect = True):
        """
        Description
        -----------
        Update the stylesheets of the buttons to reflect the current state of the game. This is done using 
        the properties connected to each position.

        Parameters
        ----------
        deselect : boolean
            If true, disconnect all active buttons and set the "Selected" property to False.
        
        Notes
        -----
        For updating the stylesheets more than the three properties are used. The color of the pawns are also determined
        based on being classical or quantum (in a superposition). This is calculated in this function.
        Similarily the border colour also depends on if a button is filled with a pawn.
        """
        for i, pos in enumerate(self.home_positions):
            pos_color = pos.property('Color')
            pos_pawn = pos.property('Pawn')
            if deselect == True:
                try:
                    pos.clicked.disconnect()
                except TypeError:
                    pass
                pos.setProperty('Selected', False)
            select = pos.property('Selected')
            button_stylesheet(pos, color = pos_color, pawn=pos_pawn, border_color=self.colors[int(np.floor(i/2))] if pos_color == None else 'White', selected =select)
        for pos in self.board_positions:
            pos_color = pos.property('Color')
            pos_pawn = pos.property('Pawn')
            if deselect == True:
                try:
                    pos.clicked.disconnect()
                except TypeError:
                    pass
                select = pos.setProperty("Selected", False)
            select = pos.property("Selected")
            classical = len([pos for pos in (self.board_positions) if 
                             pos_pawn == pos.property("Pawn") and pos_color == pos.property("Color")]) == 1
            button_stylesheet(pos, color = pos_color, pawn = pos_pawn, selected=select, classical = classical)
        for i, pos in enumerate(self.final_positions):
            pos_color = pos.property('Color')
            pos_pawn = pos.property("Pawn")
            button_stylesheet(pos, color = pos_color, pawn=pos_pawn, border_color=self.colors[int(np.floor(i/2))])

    def update_drawn_circuit(self):
        self.fig = self.circuit.draw(mpl_open = False, term_draw = False, show_idle_wires=False)
        self.circuitfigure.plot(self.fig)

    def save(self): 
        """Save the current state of the game to the history list and save the circuit to be used by undo()"""
        hp = [[pos.property("Pawn"), pos.property("Color")] for pos in self.home_positions]
        bp = [[pos.property("Pawn"), pos.property("Color")] for pos in self.board_positions]
        fp = [[pos.property("Pawn"), pos.property("Color")] for pos in self.final_positions]
        turn = self.current_turn
        to_save = [hp, bp, fp, turn]
        if len(self.history) == 0 or self.history[-1][0:2] != to_save[0:2]:
            self.history.append(to_save)
            self.circuit.save()
    
    def undo(self):
        """Undo the last move and reset the game to the previous state using the saved history"""
        self.reset_app(next_turn=False)

        if len(self.history) > 1:
            self.circuit.undo()
            positions = self.history.pop()
            positions = self.history.pop()
            
            for i, pos in enumerate(self.home_positions):
                pos.setProperty("Pawn", positions[0][i][0])
                pos.setProperty("Color", positions[0][i][1])
            for i, pos in enumerate(self.board_positions):
                pos.setProperty("Pawn", positions[1][i][0])
                pos.setProperty("Color", positions[1][i][1])
            for i, pos in enumerate(self.final_positions):
                pos.setProperty("Pawn", positions[2][i][0])
                pos.setProperty("Color", positions[2][i][1])
            self.current_turn = positions[3]
            self.next_turn()

    def circuit_visibility(self):
        """Show or hide the circuit figure"""
        if self.circuitfigure.isVisible():
            self.circuitfigure.close()
            self.circuit_visibility_button.setText("Open circuit")
        else:
            self.circuitfigure.show()
            self.circuit_visibility_button.setText("Close circuit")

    def show_position_names(self):
        """Show the position names on the board"""
        show = self.home_positions[0].text() == "" # If show=True add the integers values, otherwise remove

        self.position_names_button.setText("Remove position names" if show==True else "Show position names")
        for positions in [self.home_positions, self.board_positions, self.final_positions]:
                for i, pos in enumerate(positions):
                    pos.setText(rf'{str(i) if show==True else ""}')

    def keep_circuit_open_action(self):
        """Wait for the user to close the measure popup when measuring such that the circuit can be view"""
        if self.keep_circuit_open.text() == "Keep circuit open":
            self.keep_circuit_open.setText("Close circuit")
            self.execpopup_measure = True
        else:
            self.keep_circuit_open.setText("Keep circuit open")
            self.execpopup_measure = False

    def force_standard_basis(self, force_dependency = False):
        if self.force_standard_basis_button.text() == "Set measurement basis to be dependent on pawn" or force_dependency == True:
            self.force_standard_basis_button.setText("Force all measurement in standard basis")
            self.force_global_standard_basis = False
        else:
            self.force_standard_basis_button.setText("Set measurement basis to be dependent on pawn")
            self.force_global_standard_basis = True

    def reset_app(self, next_turn = True):
        """Reset the game to the initial state. This is similar to starting a new game, except that the history is not cleared (e.g. ctrl+z still works)"""
        # Reset the quantum circuit completely
        self.circuit._reset()
        self.update_drawn_circuit()
        
        self.total_turns = 0
        self.current_turn = self.colors[-1]
        
        for die in self.dice:
            die.setIcon(die_cons[0])
            die.setStyleSheet(die_stylesheet())
            try:
                die.clicked.disconnect()
            except TypeError:
                pass
            die.clicked.connect(self.throw_dice)
        
        for pos in self.board_positions:
            pos.setProperty("Color", None)
            pos.setProperty("Pawn", None)
            try:
                pos.clicked.disconnect()
            except TypeError:
                pass
        
        for i, pos in enumerate(self.home_positions):
            current_color = self.colors[int(np.floor(i/2))]
            pos.setProperty("Color", current_color)
            pos.setProperty("Pawn", i % 2)  
            try:
                pos.clicked.disconnect()
            except TypeError:
                pass

        for i, pos in enumerate(self.final_positions):
            pos.setProperty("Color", None)
            pos.setProperty("Pawn", None)  
            try:
                pos.clicked.disconnect()
            except TypeError:
                pass

        self.update_stylesheets(deselect=True)
        
        self.throw_dice_button.setEnabled(False)
        self.select_dice_button.setEnabled(False)
        self.random_turn_button.setEnabled(False)
        
        if next_turn == True:
            self.next_turn()


    def print_positions(self):
        """Print the positions of the pawns on the board and the home positions by displaying the "pawn" and "color" properties of each position"""
        pawns_on_board = [[position.property("Color"), position.property("Pawn")] for position in self.board_positions]
        pawns_on_spawn = [[position.property("Color"), position.property("Pawn")] for position in self.home_positions]
        print(DataFrame(pawns_on_board, columns = ['Color','Pawn number']).T.fillna('   ').replace({np.nan: '   '}))
        print(DataFrame(pawns_on_spawn, columns = ['Color','Pawn number']).T.fillna('   ').replace({np.nan: '   '}))
        print("--------------------")

    def print_all_options(self):
        """Print the possible moves for the current player"""
        option_names = ["superposition_move_options", "new_pawn_options", "single_move_options"]
        for i in range(0,3):
            print(option_names[i], self.all_options[i])
        print("--------------------")

    def save_as_svg(self):
        """Take a screenshot and save as SVG"""
        # Name of file is the time and date
        filename = os.path.join(dir_path, "screenshots", f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.svg")
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

    def update_progress_bar(self):
        """Update progress bar to reflect the number of occupied positions (up to 20)."""
        occupied_positions_count = sum(
            1 for pos in self.board_positions if pos.property("Color") is not None
        )
        # Cap at 20:
        occupied_positions_count = min(occupied_positions_count, 20)
        self.progress_bar.setValue(occupied_positions_count)


    """
    The following methods are not used in the main game, but are used to test the game logic in different scenarios.
    These can be accessed by the "Move" menu in the GUI.
    They are used to test the game logic in different scenarios, such as:
        - Use a quantum pawn to capture a classical pawn
        - Use a quantum pawn to capture a quantum pawn
        - Use a classical pawn to capture a classical pawn
        - Use a classical pawn to capture a quantum pawn
        - Add all pawns to the board 
        - Start just before a pawn reaches its final position
    The functions follow after this comment respectively.
    """
    def start_in_quantum_classical_capture(self, type_cap = 'normal'):
        self.reset_app()
        self.current_turn = self.colors[0]
        self.new_pawn(0, to_next_turn=False)
        self.die_throws = [6,6]
        self.direct_move(26, to_next_turn = False)
        self.current_turn = self.colors[1]
        self.new_pawn(2, to_next_turn= False)
        self.current_turn = self.colors[0]
        self.die_throws = [1,2]
        
        self.dice[0].setIcon(die_cons[self.die_throws[0]])
        self.dice[1].setIcon(die_cons[self.die_throws[1]])
        self.save()
        self.game_logic()

    def start_in_quantum_quantum_capture(self, type_cap = 'normal'):
        self.reset_app()
        self.current_turn = self.colors[0]
        self.new_pawn(0, to_next_turn=False)
        self.die_throws = [6,6]
        self.direct_move(26, to_next_turn = False)
        self.current_turn = self.colors[1]
        self.new_pawn(2, to_next_turn= False)
        self.die_throws = [1,2]
        self.move(2, to_next_turn=False)
        if type_cap == 'triple_jump':
            self.die_throws = [2,3]
            self.move(3, to_next_turn=False)

        if type_cap == 'jump_over_third_color':
            self.current_turn = self.colors[3]
            self.new_pawn(6, to_next_turn=False)
            self.die_throws = [6,6]
            self.direct_move(18, to_next_turn=False)
            self.direct_move(24, to_next_turn=False)
            self.die_throws = [4,4]
            self.direct_move(30, to_next_turn=False)
            self.die_throws = [3,4]
            self.move(2, to_next_turn=False)

        self.current_turn = self.colors[0]

        if type_cap == 'double_jump':
            self.die_throws = [1,3]
        elif type_cap == 'triple_jump':
            self.die_throws = [1,4]
        elif type_cap == 'jump_over_own_pawn':
            self.die_throws = [4,5]
        elif type_cap == 'double_capture':
            self.die_throws = [3,4]
        elif type_cap == 'jump_over_own_pawn2':
            self.new_pawn(1, to_next_turn=False)
            self.die_throws = [5,5]
            self.direct_move(26, to_next_turn=False)
            self.die_throws = [6,6]
            self.direct_move(31, to_next_turn=False)
            self.die_throws = [1,4]
        else:
            self.die_throws = [1,4]

        self.dice[0].setIcon(die_cons[self.die_throws[0]])
        self.dice[1].setIcon(die_cons[self.die_throws[1]])
        self.save()
        self.game_logic()
    
    def start_in_classical_classical_capture(self, type_cap = 'normal'):
        self.reset_app()
        self.current_turn = self.colors[0]
        if type_cap == 'normal':
            self.new_pawn(0, optional_move_to=0, to_next_turn=False)
            self.current_turn = self.colors[1]
            self.new_pawn(2, to_next_turn= False)

            self.current_turn = self.colors[0]
            self.die_throws = [2,2]
        if type_cap == 'new_pawn_capture':
            self.new_pawn(0, optional_move_to=2, to_next_turn=False)
            self.current_turn = self.colors[1]
            self.die_throws = [6,6]

        self.dice[0].setIcon(die_cons[self.die_throws[0]])
        self.dice[1].setIcon(die_cons[self.die_throws[1]])
        self.save()
        self.game_logic()

    def start_in_classical_quantum_capture(self, type_cap = 'normal'):
        self.reset_app()
        self.current_turn=self.colors[0]
        if type_cap == 'normal' or type_cap == 'double_jump':
            self.new_pawn(0, optional_move_to=0, to_next_turn=False)
            self.current_turn = self.colors[1]
            self.new_pawn(2, to_next_turn=False)
            self.die_throws = [1,2]
            self.move(2, to_next_turn=False)
            self.current_turn = self.colors[0]
            if type_cap == 'double_jump':
                self.die_throws = [3,3]
            else:
                self.die_throws = [4,4]
            
        if type_cap == 'new_pawn_capture' or type_cap == 'new_pawn_double_jump':
            self.new_pawn(0, optional_move_to=1, to_next_turn=False)
            if type_cap == 'new_pawn_capture':
                self.die_throws = [1,3]
            if type_cap == 'new_pawn_double_jump':
                self.die_throws = [1,2]
            self.move(1,to_next_turn=False)

            self.current_turn = self.colors[1]
            self.die_throws = [6,6]

        self.dice[0].setIcon(die_cons[self.die_throws[0]])
        self.dice[1].setIcon(die_cons[self.die_throws[1]])
        self.save()
        self.game_logic()
        
    def add_all_pawns_on_board(self, position = 0):
        self.reset_app()
        for i, color in enumerate(self.colors):
            self.current_turn = color
            self.new_pawn(i*2, optional_move_to=(self.start_position[color] + int(32*position))%32, to_next_turn=False)
        self.current_turn = self.colors[-1]
        self.next_turn()

    def start_in_finish_positions(self, fin_type = 'normal'):
        self.reset_app()
        if fin_type == 'single_move':
            self.new_pawn(0, optional_move_to=24, to_next_turn=False)
            self.new_pawn(1, optional_move_to=22, to_next_turn=False)
            self.die_throws = [4,4]
        if fin_type == 'single_capture_finish' or fin_type == 'super_cap':
            self.new_pawn(0,9,False)
            self.current_turn = self.colors[2]
            self.new_pawn(5,7,False)
            if fin_type == 'single_capture_finish':
                self.die_throws = [2,2]
            if fin_type == 'super_cap':
                self.die_throws = [2,5]
        if fin_type == 'single_from_super':
            self.new_pawn(0, 23, False)
            self.die_throws = [1,2]
            self.move(23, False)
            self.die_throws = [5,5]
        if fin_type == 'single_win' or fin_type == 'double_super_win_cap':
            self.final_positions[4].setProperty("Color", self.colors[2])
            self.final_positions[4].setProperty("Pawn", 0)
            self.final_positions[1].setProperty("Color", self.colors[0])
            self.final_positions[1].setProperty("Pawn", 1)
            self.new_pawn(0,23, False)
            self.new_pawn(5, 8, False)
            self.measure_action()
            self.current_turn = self.colors[2]
            if fin_type == 'single_win':
                self.die_throws = [4,4]
            if fin_type == 'double_super_win_cap':
                self.new_pawn(1,9,False)
                self.die_throws = [1,2]
        if fin_type == 'super_move':
            self.new_pawn(0,24,False)
            self.die_throws = [1,2]
        if fin_type == 'super_win' or fin_type == 'double_super':
            self.final_positions[1].setProperty("Color", self.colors[0])
            self.final_positions[1].setProperty("Pawn", 1)
            self.new_pawn(0,24, False)
            self.measure_action()
            self.current_turn = self.colors[0]
            if fin_type == 'super_win':
                self.die_throws = [1,2]
            if fin_type == 'double_super':
                self.die_throws = [4,5]

        self.dice[0].setIcon(die_cons[self.die_throws[0]])
        self.dice[1].setIcon(die_cons[self.die_throws[1]])
        self.save()
        self.game_logic()

    def bell_test(self):
        self.reset_app()
        self.current_turn = self.colors[0]
        self.new_pawn(0,20)
        self.current_turn = self.colors[1]
        self.new_pawn(2,19)
        self.new_pawn(3,23) 
        self.current_turn = self.colors[2]
        self.new_pawn(5,9)
        self.new_pawn(4,8)
        self.current_turn = self.colors[0]
        self.new_pawn(1,25)

        self.update_drawn_circuit()
        self.update_stylesheets(deselect=True)

        self.die_throws = [1,3]
        self.move(20, False)
        QTimer.singleShot(1000, lambda : self.update_drawn_circuit())
        QTimer.singleShot(1000, lambda : self.update_stylesheets())
        self.current_turn = self.colors[2]
        self.die_throws = [2,2]
        QTimer.singleShot(1500, lambda : self.direct_move(19,False))
        QTimer.singleShot(2500, lambda : self.update_drawn_circuit())
        QTimer.singleShot(2500, lambda : self.update_stylesheets())

        if "Set measurement basis to be dependent on pawn":
            self.force_standard_basis()
        QTimer.singleShot(3000, lambda : self._bell_test_internals())
    
    def _bell_test_internals(self):
        def initialize():
            self.reset_app()
            self.current_turn = self.colors[0]
            self.new_pawn(0,20)
            self.current_turn = self.colors[1]
            self.new_pawn(2,19)
            self.new_pawn(3,23) 
            self.current_turn = self.colors[2]
            self.new_pawn(5,9)
            self.new_pawn(4,8)
            self.current_turn = self.colors[0]
            self.new_pawn(1,25)

            self.die_throws = [1,3]
            self.move(20, False)
            self.current_turn = self.colors[2]
            self.die_throws = [2,2]
            self.direct_move(19,False)
            self.update_drawn_circuit()
            self.update_stylesheets(deselect=True)
        def blue_zero_finish():
            self.current_turn = self.colors[2]
            self.die_throws = [2,2]
            self.direct_move(8,False)
            positions = self.measure_action(final_position=4, next_turn=False, bell_test=True)
            if (24 in positions and 23 in positions) or (24 not in positions and 23 not in positions):
                outcomes["XQ"]["total"] += 1
            else:
                outcomes["XQ"]["total"] += -1
            outcomes["XQ"]["amount"] += 1

        def blue_one_finish():
            self.current_turn = self.colors[2]
            self.die_throws = [2,2]
            self.direct_move(9,False)
            positions = self.measure_action(final_position=5, next_turn=False, bell_test=True)

            if (24 in positions and 23 in positions) or (24 not in positions and 23 not in positions):
                outcomes["XT"]["total"] += 1
            else:
                outcomes["XT"]["total"] += -1
            outcomes["XT"]["amount"] += 1
        def red_one_finish():
            self.current_turn = self.colors[0]
            self.die_throws = [1,1]
            self.direct_move(25,False)
            positions = self.measure_action(final_position=1, next_turn=False, bell_test=True)

            if (24 in positions and 23 in positions) or (24 not in positions and 23 not in positions):
                outcomes["ZT"]["total"] += 1
            else:
                outcomes["ZT"]["total"] += -1
            outcomes["ZT"]["amount"] += 1
            
        def red_zero_finish():
            self.current_turn = self.colors[0]
            self.die_throws = [2,2]
            self.direct_move(24,False)
            positions = self.measure_action(final_position=0, next_turn=False, bell_test=True)

            if (23 in positions and 32 in positions) or (23 not in positions and 32 not in positions):
                outcomes["ZQ"]["total"] += 1
            else:
                outcomes["ZQ"]["total"] += -1
            outcomes["ZQ"]["amount"] += 1

        finish_options = [blue_zero_finish, blue_one_finish, red_one_finish, red_zero_finish]
        # randomly select one
        outcomes = {"ZT": {"amount" : 0, "total" : 0}, # Z, T - red 1
                    "ZQ": {"amount" : 0, "total" : 0}, # Z, Q - red 0
                    "XT": {"amount" : 0, "total" : 0}, # X, T - blue 1
                    "XQ": {"amount" : 0, "total" : 0}} # X, Q - blue 0
        bell_test_figure = BellTestPlot()
        bell_test_figure.show()
        
        Ss = []
        for i in range(1,1000):
            finish_options[np.random.randint(0,4)]()
            S = 0
            print(outcomes)

            # Check each value individually and only divide if non-zero
            if outcomes["ZT"]["amount"] != 0:
                S += outcomes["ZT"]["total"] / outcomes["ZT"]["amount"]
            else:
                S += 0

            if outcomes["XQ"]["amount"] != 0:
                S += outcomes["XQ"]['total'] / outcomes["XQ"]['amount']
            else:
                S += 0

            if outcomes["XT"]["amount"] != 0:
                S += outcomes["XT"]['total'] / outcomes["XT"]['amount']
            else:
                S += 0

            if outcomes["ZQ"]["amount"] != 0:
                S -= outcomes["ZQ"]['total'] / outcomes["ZQ"]['amount']
            else:
                S -= 0
            print(S)
            Ss.append(S)
            bell_test_figure.update_plot(y=S, x=i)
            plt.pause(0.1)
            initialize()
            if i % 100 == 0 or i == 1:
                open(os.path.join(dir_path, "game_logic", "Cache", "bell_test_results.txt"), "w").write(str(Ss))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main(debug=True)
    main.show()
    app.exec_()
