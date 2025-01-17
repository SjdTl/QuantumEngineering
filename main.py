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
        for die, i in zip(self.select_dice, range(len(self.select_dice))):
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

        self.circuit_visibility_button = Qt.QAction("Show circuit", self)
        if self.debug:
            self.circuit_visibility_button.setText("Close circuit")
        self.circuit_visibility_button.setShortcut("Ctrl+C")
        self.circuit_visibility_button.triggered.connect(self.circuit_visibility)

        self.position_names_button = Qt.QAction("Show position names", self)
        if self.debug:
            self.position_names_button.setText("Remove position names")
        self.position_names_button.triggered.connect(self.show_position_names)

        self.file_menu.addAction(self.reset)
        self.file_menu.addAction(self.throw_dice_button)
        self.debug_menu.addAction(self.measure_button)
        self.debug_menu.addAction(self.skip_turn)
        self.debug_menu.addAction(self.select_dice_button)
        self.debug_menu.addAction(self.random_turn_button)
        self.debug_menu.addAction(self.circuit_visibility_button)
        self.debug_menu.addAction(self.position_names_button)

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.setStyleSheet(stylesheet)

        grid = QGridLayout()

        self.board_positions = [Qt.QPushButton(rf'{i if self.debug==True else ""}') for i in range(self.N)]

        x=3
        y=0
        for pos, i in zip(self.board_positions, range(self.N)):
            pos.setFixedSize(50, 50)
            pos.setStyleSheet(button_stylesheet())
            pos.setProperty("Color", None)
            pos.setProperty("Pawn", None)

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
        for pos, i in zip(self.home_positions, range(8)):
            current_color = self.colors[int(np.floor(i/2))]
            pos.setFixedSize(50,50)
            pos.setStyleSheet(button_stylesheet(color = current_color))
            pos.setProperty("Color", current_color)


            if i == 0: grid.addWidget(pos, 1, 0), pos.setProperty("Pawn", 0)
            if i == 1: grid.addWidget(pos, 0, 1), pos.setProperty("Pawn", 1)
            if i == 2: grid.addWidget(pos, 0, 7), pos.setProperty("Pawn", 0)
            if i == 3: grid.addWidget(pos, 1, 8), pos.setProperty("Pawn", 1)
            if i == 4: grid.addWidget(pos, 7, 8), pos.setProperty("Pawn", 0)
            if i == 5: grid.addWidget(pos, 8, 7), pos.setProperty("Pawn", 1)
            if i == 6: grid.addWidget(pos, 8, 1), pos.setProperty("Pawn", 0)
            if i == 7: grid.addWidget(pos, 7, 0), pos.setProperty("Pawn", 1)

        self.final_positions = [Qt.QPushButton(rf'{i if self.debug==True else ""}') for i in range(8)]
        for pos, i in zip(self.final_positions, range(8)):
            current_color = self.colors[int(np.floor(i/2))]
            pos.setFixedSize(50,50)
            pos.setStyleSheet(button_stylesheet(border_color = current_color))

            if i == 0: grid.addWidget(pos, 1, 4)
            if i == 1: grid.addWidget(pos, 2, 4)
            if i == 2: grid.addWidget(pos, 4, 7)
            if i == 3: grid.addWidget(pos, 4, 6)
            if i == 4: grid.addWidget(pos, 7, 4)
            if i == 5: grid.addWidget(pos, 6, 4)
            if i == 6: grid.addWidget(pos, 4, 1)
            if i == 7: grid.addWidget(pos, 4, 2)

        number_of_dice = 2
        self.dice = [Qt.QPushButton() for _ in range(number_of_dice)]
        for die,i in zip(self.dice, range(len(self.dice))):
            die.setIcon(die_cons[0])
            die.setIconSize(QSize(45,45))
            die.setFixedSize(50,50)
            die.setStyleSheet(die_stylesheet())
            grid.addWidget(die, 9, i)

        # show grid
        central_widget.setLayout(grid)

    def next_turn(self, random_turn = False):
        self.update_drawn_circuit()
        self.deselect_all_pawns()

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

        for die,i in zip(self.dice, range(len(self.dice))):
            die.setIcon(die_cons[self.die_throws[i]])
            die.setIconSize(QSize(45,45))

        for button in self.dice:
            button.clicked.disconnect(self.throw_dice)
        self.throw_dice_button.setEnabled(False)
        self.select_dice_button.setEnabled(False)
        self.random_turn_button.setEnabled(False)

        if random_turn:
            # QTimer.singleShot(500, self.game_logic(random_turn = True))
            self.game_logic(random_turn=True)
        else:
            self.game_logic()


    def game_logic(self, random_turn = False):
        pawns_on_board = [[position.property("Color"), position.property("Pawn")] for position in self.board_positions]
        pawns_on_spawn = [[position.property("Color"), position.property("Pawn")] for position in self.home_positions]


        superposition_move_options = [i for i in range(len(pawns_on_board))
                                    if pawns_on_board[i][0] == self.current_turn 
                                    and ((pawns_on_board[(i+self.die_throws[0])%32][0] is None or pawns_on_board[(i+self.die_throws[0])%32][0] != self.current_turn)
                                    and (pawns_on_board[(i+self.die_throws[1])%32][0] is None or pawns_on_board[(i+self.die_throws[1])%32][0] != self.current_turn))
                                    and self.die_throws[0] != self.die_throws[1]]

        new_pawn_options = [i for i in range(len(pawns_on_spawn))
                            if pawns_on_spawn[i][0] == self.current_turn
                            and (pawns_on_board[self.start_position[self.current_turn]][0] is None 
                                 or pawns_on_board[self.start_position[self.current_turn]][0] != self.current_turn)
                            and 6 in self.die_throws]

        single_move_options = [i for i in range(len(pawns_on_board))
                                if pawns_on_board[i][0] == self.current_turn
                                and (pawns_on_board[(i+self.die_throws[0])%32][0] is None 
                                     or pawns_on_board[(i+self.die_throws[0])%32][0] != self.current_turn)
                                and self.die_throws[0] == self.die_throws[1]]
        
        if len(superposition_move_options + new_pawn_options + single_move_options) == 0:
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
                    self.board_positions[i].setStyleSheet(button_stylesheet(color=self.current_turn, selected=True))
                    self.board_positions[i].clicked.connect(lambda _, b=i: self.move(move_from = b))
                
                for i in new_pawn_options:
                    self.home_positions[i].setStyleSheet(button_stylesheet(color=self.current_turn, selected=True))
                    self.home_positions[i].clicked.connect(lambda _, b = i: self.new_pawn(move_from = b))

                for i in single_move_options:
                    self.board_positions[i].setStyleSheet(button_stylesheet(color=self.current_turn, selected=True))
                    self.board_positions[i].clicked.connect(lambda _, b=i: self.direct_move(move_from = b))
    
    def direct_move(self, move_from):
        move_to = (move_from + self.die_throws[0]) % 32
        
        # Check for capture
        if self.board_positions[move_to].property("Color") is not None and self.board_positions[move_to].property("Color") != self.current_turn:
            # Find next free position
            next_pos = (move_to + 1) % 32
            while self.board_positions[next_pos].property("Color") is not None:
                next_pos = (next_pos + 1) % 32
            
            # Apply quantum capture
            captured_color = self.board_positions[move_to].property("Color")
            captured_positions = [i for i in range(self.N) 
                                if self.board_positions[i].property("Color") == captured_color 
                                and self.board_positions[i].property("Pawn") == self.board_positions[move_to].property("Pawn")
                                and i != move_to]  # Exclude the capture position
            if captured_positions:  # Only capture if there are entangled positions
                self.circuit.capture([next_pos], [move_to], captured_positions)
            move_to = next_pos

        for prop in ["Color", "Pawn"]:
            self.board_positions[move_to].setProperty(prop, self.board_positions[move_from].property(prop))
            self.board_positions[move_from].setProperty(prop, None)
        
        self.board_positions[move_to].setStyleSheet(button_stylesheet(color=self.current_turn))
        self.board_positions[move_from].setStyleSheet(button_stylesheet(color=None))

        self.circuit.switch([move_from], [move_to])
        self.next_turn()

    def move(self, move_from):
        move_to = [(move_from + self.die_throws[0]) % 32, (move_from + self.die_throws[1]) % 32]

                
        # Check for captures at both destination positions
        captures = [(i, pos) for i, pos in enumerate(move_to) 
                   if self.board_positions[pos].property("Color") is not None 
                   and self.board_positions[pos].property("Color") != self.current_turn]
        
        # Handle captures and find next free positions
        for capture_idx, capture_pos in captures:
            # Find next free position after capture
            next_pos = (capture_pos + 1) % 32
            while (self.board_positions[next_pos].property("Color") is not None or 
                   next_pos in move_to):  # Check if position is already a destination
                next_pos = (next_pos + 1) % 32
            move_to[capture_idx] = next_pos
            
            # Apply quantum capture in circuit
            captured_color = self.board_positions[capture_pos].property("Color")
            captured_positions = [i for i in range(self.N) 
                                if self.board_positions[i].property("Color") == captured_color 
                                and self.board_positions[i].property("Pawn") == self.board_positions[capture_pos].property("Pawn")
                                and i != capture_pos]
            if captured_positions:
                self.circuit.capture([next_pos], [capture_pos], captured_positions)

        if move_to[0] == move_to[1]:
            next_pos = (move_to[1] + 1) % 32
            while self.board_positions[next_pos].property("Color") is not None:
                next_pos = (next_pos + 1) % 32
            move_to[1] = next_pos

        for prop in ["Color", "Pawn"]:
            self.board_positions[move_to[0]].setProperty(prop, self.board_positions[move_from].property(prop))
            self.board_positions[move_to[1]].setProperty(prop, self.board_positions[move_from].property(prop))
            self.board_positions[move_from].setProperty(prop, None)
        
        self.board_positions[move_to[0]].setStyleSheet(button_stylesheet(color=self.current_turn))
        self.board_positions[move_to[1]].setStyleSheet(button_stylesheet(color=self.current_turn))
        self.board_positions[move_from].setStyleSheet(button_stylesheet(color=None))

        self.circuit.move([move_from], move_to)
        self.next_turn()

    def new_pawn(self, move_from):
        move_to = self.start_position[self.current_turn]
        
        for prop in ["Color", "Pawn"]:
            self.board_positions[move_to].setProperty(prop, self.home_positions[move_from].property(prop))
            self.home_positions[move_from].setProperty(prop, None)

        self.board_positions[move_to].setStyleSheet(button_stylesheet(color=self.current_turn))
        self.home_positions[move_from].setStyleSheet(button_stylesheet(border_color=self.current_turn))

        self.circuit.new_pawn([move_to])
        self.next_turn()

    def measure_action(self):
        measure_popup = MeasurePopup()
        measure_popup.show()
        positions, out_with_freq, nr_of_qubits_used = self.circuit.measure(out_internal_measure=True, efficient = True)
        print(positions)
        for pos in range(0,len(self.board_positions)):
            if pos not in positions:
                for prop in ["Color", "Pawn"]:
                    self.board_positions[pos].setProperty(prop, None)
                self.board_positions[pos].setStyleSheet(button_stylesheet())

        measure_popup.close()
        self.next_turn()



    def deselect_all_pawns(self):
        for position in self.board_positions + self.home_positions:
            position.setStyleSheet(button_stylesheet(color=position.property("Color")))
            try:
                position.clicked.disconnect()
            except TypeError:
                pass

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
        if self.home_positions[0].text() == "":
            self.position_names_button.setText("Remove position names")
            for pos,i in zip(self.home_positions, range(len(self.home_positions))):
                pos.setText(str(i))
            for pos,i in zip(self.board_positions, range(len(self.board_positions))):
                pos.setText(str(i))
            for pos,i in zip(self.final_positions, range(len(self.final_positions))):
                pos.setText(str(i))
        else: 
            self.position_names_button.setText("Show position names")
            for pos,i in zip(self.home_positions, range(len(self.home_positions))):
                pos.setText("")
            for pos,i in zip(self.board_positions, range(len(self.board_positions))):
                pos.setText("")
            for pos,i in zip(self.final_positions, range(len(self.final_positions))):
                pos.setText("")

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
            pos.setStyleSheet(button_stylesheet())
            try:
                pos.clicked.disconnect()
            except TypeError:
                pass
        
        
        for i, pos in enumerate(self.home_positions):
            current_color = self.colors[int(np.floor(i/2))]
            pos.setProperty("Color", current_color)
            pos.setProperty("Pawn", i % 2)  
            pos.setStyleSheet(button_stylesheet(color=current_color))
            try:
                pos.clicked.disconnect()
            except TypeError:
                pass
        
        self.throw_dice_button.setEnabled(False)
        self.select_dice_button.setEnabled(False)
        self.random_turn_button.setEnabled(False)
        
        self.next_turn()

    
if __name__ in "__main__":
    app = QApplication(sys.argv)
    main = Main(debug=True)
    main.show()
    app.exec_()