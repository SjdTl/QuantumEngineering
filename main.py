# CODE IN REPOSITORY
# IMPORT THE STYLESHEETS
from UI import stylesheet, button_stylesheet, die_cons, die_stylesheet

# IMPORT THE QUANTUM CIRCUITS
from game_logic.quantum_circuits import circuit

# LIBRARIES
# application from pyqt
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QComboBox,QPushButton, QLabel, QHBoxLayout,QVBoxLayout, QGridLayout, QMenuBar, QMainWindow, QDialog
import PyQt5.QtWidgets as Qt
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, QTimer

# others
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sys
import os
import numpy as np
import random
from pandas import DataFrame

dir_path = os.path.dirname(os.path.realpath(__file__))

class LoadingPopup(QDialog):
    def __init__(self, header_text : str):
        super().__init__()
        self.setWindowTitle(header_text)
        self.setFixedSize(300, 200)
        layout = QVBoxLayout()
        self.label = QLabel("")
        layout.addWidget(self.label)
        self.setLayout(layout)

class selectDicePopup(QDialog):
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
    # Thought it might be fun to add an animation here
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

class Main(QMainWindow):
    def __init__(self, simulation = True, debug = False):
        self.simulation = simulation
        self.debug = debug

        self.N = 32
        self.circuit = circuit(self.N)

        self.circuitfigure = CircuitFigure()
        self.fig = self.circuit.draw(mpl_open = False, term_draw = False)
        self.circuitfigure.plot(self.fig)
        if debug:
            self.circuitfigure.show()

        super().__init__()
        self.settings()
        self.window()
        self.initUI()
        self.total_turns = 0
        self.next_turn()

    def window(self):
        # Menu bar
        self.menu = QMenuBar(self)
        self.file_menu = self.menu.addMenu("File")
        self.debug_menu = self.menu.addMenu("Debug")
        self.test_moves = self.menu.addMenu("Moves")
        self.setMenuBar(self.menu)
        
        self.reset = Qt.QAction("Reset", self)
        self.reset.setShortcut("Ctrl+R")
        self.reset.triggered.connect(self.reset_app)

        self.measure_button = Qt.QAction("Measure", self)
        self.measure_button.setShortcut("Ctrl+M")
        self.measure_button.triggered.connect(self.measure_action)

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
        self.print_positions_button.setShortcut("Ctrl+Alt+P")

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

        self.file_menu.addAction(self.reset)
        self.file_menu.addAction(self.throw_dice_button)
        self.debug_menu.addAction(self.measure_button)
        self.debug_menu.addAction(self.skip_turn)
        self.debug_menu.addAction(self.select_dice_button)
        self.debug_menu.addAction(self.random_turn_button)
        self.debug_menu.addAction(self.circuit_visibility_button)
        self.debug_menu.addAction(self.position_names_button)
        self.debug_menu.addAction(self.print_positions_button)
        self.debug_menu.addAction(self.print_move_options_button)

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.setStyleSheet(stylesheet)

        grid = QGridLayout()

        self.board_positions = [Qt.QPushButton(rf'{i if self.debug==True else ""}') for i in range(self.N)]

        x=3
        y=0
        for i, pos in enumerate(self.board_positions):
            pos.setFixedSize(50, 50)
            # pos.setStyleSheet(button_stylesheet())
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

        self.colors = ['red', 'green', 'blue', 'purple'] # MUST BE FOUR COLOURS
        self.current_turn = self.colors[-1]
        self.start_position = {
            self.colors[0] : 26,
            self.colors[1] : 2,
            self.colors[2] : 10,
            self.colors[3] : 18
        }

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

        self.final_positions = [Qt.QPushButton(rf'{i if self.debug==True else ""}') for i in range(32,32+8)]
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

        number_of_dice = 2
        self.dice = [Qt.QPushButton() for _ in range(number_of_dice)]
        for i, die in enumerate(self.dice):
            die.setIcon(die_cons[0])
            die.setIconSize(QSize(45,45))
            die.setFixedSize(50,50)
            die.setStyleSheet(die_stylesheet())
            grid.addWidget(die, 9, i)

        self.update_stylesheets()
        # show grid
        central_widget.setLayout(grid)

    def next_turn(self, random_turn = False):
        self.update_drawn_circuit()
        # self.deselect_all_pawns()
        self.update_stylesheets(deselect=True)

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

        if random_turn == True:
            self.throw_dice(random_turn = True)

    def throw_dice(self, debug_throw = False, random_turn = False):
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
            QTimer.singleShot(250, lambda : self.game_logic(random_turn = True))
            # self.game_logic(random_turn=True)
        else:
            self.game_logic()


    def game_logic(self, random_turn = False):
        self.update_stylesheets(deselect=True)
        pawns_on_board = [[position.property("Color"), position.property("Pawn")] for position in self.board_positions]
        pawns_on_spawn = [[position.property("Color"), position.property("Pawn")] for position in self.home_positions]

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
                    # self.board_positions[i].setStyleSheet(button_stylesheet(color=self.current_turn, selected=True))
                    self.board_positions[i].setProperty("Selected", True)
                    self.board_positions[i].clicked.connect(lambda _, b=i: self.move(move_from = b))
                
                for i in new_pawn_options:
                    # self.home_positions[i].setStyleSheet(button_stylesheet(color=self.current_turn, selected=True))
                    self.home_positions[i].setProperty("Selected", True)
                    self.home_positions[i].clicked.connect(lambda _, b = i: self.new_pawn(move_from = b))

                for i in single_move_options:
                    # self.board_positions[i].setStyleSheet(button_stylesheet(color=self.current_turn, selected=True))
                    self.board_positions[i].setProperty("Selected", True)
                    self.board_positions[i].clicked.connect(lambda _, b=i: self.direct_move(move_from = b))
        self.update_stylesheets(deselect=False)

    def find_next_available_spot(self, changing_move, constant_move=None):
            if changing_move == constant_move or constant_move == None:
                constant_move = changing_move

                while self.board_positions[changing_move].property("Color") is not None:
                    changing_move=(changing_move+1)%32
                
            return changing_move
    
    def check_if_moving_in_final_positions(self, move_from, move_to):
        """ Further requirements
        - Have two qubits extra in total for all the 8 possible end positions (since only two are used at the same time, since we always measure after a finish)
        - When you throw 'too much' it is already implemented that you reverse, but not the capturing in reverse
        - Something (I don't know what yet) when a final position is already occupied
        """

        self.final_position_values = {self.colors[0] : [32, 33],
                                      self.colors[1] : [34, 35],
                                      self.colors[2] : [36, 37],
                                      self.colors[3] : [38, 39]}

        start_position = self.start_position[self.current_turn]
        for i, move in enumerate(move_to):
            if (move_from - start_position) % 32 > 16 and (move - start_position) % 32 < 16: #this might not be the most general solution, but since the maximum movement is 6 this will work
                spare_moves = (move - start_position + 1) % 32 
                if spare_moves == 1 or spare_moves == 3:
                    move_to[i] = self.final_position_values[self.current_turn][0]                 
                elif spare_moves == 2:
                    move_to[i] = self.final_position_values[self.current_turn][1]
                else: 
                    move_to[i] = (start_position-1) % 32 - (spare_moves - 4)
                    # REQUIRES SOME EXTRA LOGIC SINCE IF MOVE_TO[i] == move_from the program will crash
        return move_to

    def direct_move(self, move_from, to_next_turn = True):
        move_to = [(move_from + self.die_throws[0]) % 32]
        captives = [pos for pos in move_to if self.board_positions[pos].property("Color") != None]
        normal_move = [pos for pos in move_to if self.board_positions[pos].property("Color") is None]
        captive_entanglement = [[i for i in range(0,32)
                                if self.board_positions[i].property("Color") == self.board_positions[move].property("Color")
                                and self.board_positions[i].property("Pawn") == self.board_positions[move].property("Pawn")
                                and move != i] for move in captives]
        capture_move = list(map(lambda move: self.find_next_available_spot(move, None), captives))
        
        move_to = normal_move + capture_move
        move_to = self.check_if_moving_in_final_positions(move_from, move_to)

        for prop in ["Color", "Pawn"]:
            self.board_positions[move_to[0]].setProperty(prop, self.board_positions[move_from].property(prop))
            self.board_positions[move_from].setProperty(prop, None)
        
        # self.board_positions[move_to[0]].setStyleSheet(button_stylesheet(color=self.current_turn))
        # self.board_positions[move_from].setStyleSheet(button_stylesheet(color=None))

        if all(move < 32 for move in move_to):
            self.circuit.switch([move_from], move_to)
        else:
            print("Move to final qubits and measure")
        if captives:
            self.circuit.capture(capture_move, captives, captive_entanglement[0])
        if to_next_turn:
            self.next_turn()

    def move(self, move_from, to_next_turn = True):
        move_to = [(move_from + self.die_throws[0]) % 32, (move_from + self.die_throws[1]) % 32]
        captives = [pos for pos in move_to if self.board_positions[pos].property("Color") != None]
        normal_move = [pos for pos in move_to if self.board_positions[pos].property("Color") is None]
        captive_entanglement = [[i for i in range(0,32)
                                if self.board_positions[i].property("Color") == self.board_positions[move].property("Color")
                                and self.board_positions[i].property("Pawn") == self.board_positions[move].property("Pawn")
                                and move != i] for move in captives]
        capture_move = list(map(lambda move: self.find_next_available_spot(move, None), captives))
        
        if len(captives) != 0:
            capture_move[0] = self.find_next_available_spot(changing_move=capture_move[0], constant_move=(normal_move[0] if len(captives) == 1 else capture_move[1]))

        move_to = normal_move + capture_move
        move_to = self.check_if_moving_in_final_positions(move_from, move_to)

        self.circuit.move(move_from = [move_from], move_to = move_to)

        for i in range(len(captives)):
            self.circuit.capture(capturer=[capture_move[i]], captive = [captives[i]], captive_entanglement=captive_entanglement[i])         

        for prop in ["Color", "Pawn"]:
            self.board_positions[move_to[0]].setProperty(prop, self.board_positions[move_from].property(prop))
            self.board_positions[move_to[1]].setProperty(prop, self.board_positions[move_from].property(prop))
            self.board_positions[move_from].setProperty(prop, None)
        
        # self.board_positions[move_to[0]].setStyleSheet(button_stylesheet(color=self.current_turn))
        # self.board_positions[move_to[1]].setStyleSheet(button_stylesheet(color=self.current_turn))
        # self.board_positions[move_from].setStyleSheet(button_stylesheet(color=None))

        if to_next_turn: 
            self.next_turn()

    def new_pawn(self, move_from, optional_move_to = None, to_next_turn = True):
        move_to_original = self.start_position[self.current_turn] if optional_move_to == None else optional_move_to
        move_to = self.find_next_available_spot(move_to_original)
        captive_entanglement = [i for i in range(0,32)
                                if self.board_positions[i].property("Color") == self.board_positions[move_to_original].property("Color")
                                and self.board_positions[i].property("Pawn") == self.board_positions[move_to_original].property("Pawn")
                                and move_to_original != i]
        
        for prop in ["Color", "Pawn"]:
            self.board_positions[move_to].setProperty(prop, self.home_positions[move_from].property(prop))
            self.home_positions[move_from].setProperty(prop, None)

        # self.board_positions[move_to].setStyleSheet(button_stylesheet(color=self.current_turn))
        # self.home_positions[move_from].setStyleSheet(button_stylesheet(border_color=self.current_turn))

        self.circuit.new_pawn([move_to])

        if move_to != move_to_original:
            self.circuit.capture([move_to], [move_to_original], captive_entanglement)

        if to_next_turn:
            self.next_turn()

    def measure_action(self):
        measure_popup = MeasurePopup()
        measure_popup.show()
        positions, out_with_freq, nr_of_qubits_used = self.circuit.measure(out_internal_measure=True, efficient = True)
        print(nr_of_qubits_used)
        print(out_with_freq)
        print(positions)
        for pos in range(0,len(self.board_positions)):
            if pos not in positions:
                for prop in ["Color", "Pawn"]:
                    self.board_positions[pos].setProperty(prop, None)
                # self.board_positions[pos].setStyleSheet(button_stylesheet())

        measure_popup.close()
        self.next_turn()



    # def deselect_all_pawns(self):
    #     for position in self.board_positions + self.home_positions:
    #         position.setStyleSheet(button_stylesheet(color=position.property("Color")))
    #         try:
    #             position.clicked.disconnect()
    #         except TypeError:
    #             pass

    def update_stylesheets(self, deselect = True):
        print(deselect)
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
            button_stylesheet(pos, color = pos_color, pawn = pos_pawn, selected=select)
        for i, pos in enumerate(self.final_positions):
            pos_color = pos.property('Color')
            pos_pawn = pos.property("Pawn")
            button_stylesheet(pos, color = pos_color, pawn=pos_pawn, border_color=self.colors[int(np.floor(i/2))])


    def settings(self):
        self.setWindowTitle("Testing")
        self.setGeometry(250,250,600,500)



    def update_drawn_circuit(self):
        self.fig = self.circuit.draw(mpl_open = False, term_draw = False, show_idle_wires=False)
        self.circuitfigure.plot(self.fig)

    def circuit_visibility(self):
        if self.circuitfigure.isVisible():
            self.circuitfigure.close()
            self.circuit_visibility_button.setText("Open circuit")
        else:
            self.circuitfigure.show()
            self.circuit_visibility_button.setText("Close circuit")

    def show_position_names(self):
        show = self.home_positions[0].text() == "" # If show=True add the integers values, otherwise remove

        self.position_names_button.setText("Remove position names" if show==True else "Show position names")
        for positions in [self.home_positions, self.board_positions, self.final_positions]:
                for i, pos in enumerate(positions):
                    pos.setText(rf'{str(i) if show==True else ""}')

    def reset_app(self):
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

        self.update_stylesheets(deselect=True)
        
        self.throw_dice_button.setEnabled(False)
        self.select_dice_button.setEnabled(False)
        self.random_turn_button.setEnabled(False)
        
        self.next_turn()

    def print_positions(self):
        pawns_on_board = [[position.property("Color"), position.property("Pawn")] for position in self.board_positions]
        pawns_on_spawn = [[position.property("Color"), position.property("Pawn")] for position in self.home_positions]
        print(DataFrame(pawns_on_board, columns = ['Color','Pawn number']).T.fillna('   ').replace({np.NaN: '   '}))
        print(DataFrame(pawns_on_spawn, columns = ['Color','Pawn number']).T.fillna('   ').replace({np.NaN: '   '}))
        print("--------------------")

    def print_all_options(self):
        option_names = ["superposition_move_options", "new_pawn_options", "single_move_options"]
        for i in range(0,3):
            print(option_names[i], self.all_options[i])
        print("--------------------")


    # ------------------------------------------------------------
    # Preprogrammed positions
    # ------------------------------------------------------------

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
        
        self.game_logic()
        
    def add_all_pawns_on_board(self, position = 0):
        self.reset_app()
        for i, color in enumerate(self.colors):
            self.current_turn = color
            self.new_pawn(i*2, optional_move_to=(self.start_position[color] + int(32*position))%32, to_next_turn=False)
        self.current_turn = self.colors[-1]
        self.next_turn()
    
if __name__ in "__main__":
    app = QApplication(sys.argv)
    main = Main(debug=True)
    main.show()
    app.exec_()