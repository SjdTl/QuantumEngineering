import tkinter as tk
from tkinter import messagebox
import random

class LudoGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Ludo Game")
        self.window.geometry("800x800")
        
        # Game constants
        self.BOARD_SIZE = 600
        self.CELL_SIZE = 40
        self.TOTAL_SPOTS = 32
        self.SPOTS_PER_SIDE = 8
        
        # Player colors and starting positions - original positions
        self.PLAYERS = {
            'red': {
                'start': 0, 
                'pawns': [], 
                'color': '#FF0000',
                'points': 0,
                'quantum_states': {}  # Will store {pawn_id: [{position: prob}, {position: prob}]}
            },
            'blue': {'start': 8, 'pawns': [], 'color': '#0000FF', 'points': 0, 'quantum_states': {}},
            'green': {'start': 16, 'pawns': [], 'color': '#00FF00', 'points': 0, 'quantum_states': {}},
            'yellow': {'start': 24, 'pawns': [], 'color': '#FFFF00', 'points': 0, 'quantum_states': {}}
        }
        
        self.current_player = 'red'
        self.dice_value1 = 0
        self.dice_value2 = 0
        self.selected_pawn = None
        
        self.setup_board()
        self.setup_controls()
        self.initialize_pawns()
        
    def setup_board(self):
        self.canvas = tk.Canvas(self.window, width=self.BOARD_SIZE, height=self.BOARD_SIZE, bg='white')
        self.canvas.pack(pady=20)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.draw_board()
        
    def draw_board(self):
        self.canvas.delete("all")
        
        border = 2
        self.canvas.create_rectangle(border, border, 
                                   self.BOARD_SIZE-border, self.BOARD_SIZE-border, 
                                   width=border, fill='white')
        
        quadrant_size = self.BOARD_SIZE // 2
        
        self.draw_home_base('red', 0, 0)
        self.draw_home_base('blue', quadrant_size, 0)
        self.draw_home_base('green', 0, quadrant_size)
        self.draw_home_base('yellow', quadrant_size, quadrant_size)
        
        self.draw_paths()
        self.draw_pawns()
        self.draw_points()
    
    def draw_home_base(self, color, x, y):
        size = self.BOARD_SIZE // 2 - 20
        padding = 10
        
        self.canvas.create_rectangle(x+padding, y+padding, 
                                   x+size+padding, y+size+padding, 
                                   fill=self.PLAYERS[color]['color'])
        
        # Get number of pawns in home (not yet in play)
        pawns_in_home = 2 - len([p for p in self.PLAYERS[color]['pawns'] if p != -1])
        
        # Draw pawn indicators in the corners based on color
        if pawns_in_home > 0:
            if color == 'red':  
                start_x = x + padding + 30
                start_y = y + padding + 30
            elif color == 'blue': 
                start_x = x + size - 100
                start_y = y + padding + 30
            elif color == 'green':
                start_x = x + padding + 30
                start_y = y + size - 70
            else:  
                start_x = x + size - 100
                start_y = y + size - 70
            
            for i in range(pawns_in_home):
                circle_x = start_x + (i * 50)  
                
                self.canvas.create_oval(circle_x, start_y,
                                      circle_x + 40, start_y + 40,
                                      fill='white',
                                      outline='black',
                                      width=2)
                
                self.canvas.create_oval(circle_x + 5, start_y + 5,
                                      circle_x + 35, start_y + 35,
                                      fill=self.PLAYERS[color]['color'],
                                      outline='white',
                                      width=2)
    
    def draw_paths(self):
        cell_size = 40  
        
        for i in range(32):
            x, y = self.get_path_position(i)
            color = 'white'
            if i % 8 == 0:  # Starting positions
                color = self.get_color_for_position(i)
            self.canvas.create_rectangle(x-cell_size//2, y-cell_size//2,
                                      x+cell_size//2, y+cell_size//2,
                                      fill=color, outline='black')
    
    def get_path_position(self, position):
        cell_size = 40
        square_size = cell_size * 8
        
        center_x = self.BOARD_SIZE // 2 - square_size // 2
        center_y = self.BOARD_SIZE // 2 - square_size // 2
        
        if position < 8:  # Top row
            return (center_x + position * cell_size, center_y)
        elif position < 16:  # Right column
            return (center_x + square_size, center_y + (position-8) * cell_size)
        elif position < 24:  # Bottom row
            return (center_x + square_size - (position-16) * cell_size, center_y + square_size)
        else:  # Left column
            return (center_x, center_y + square_size - (position-24) * cell_size)
    
    def get_color_for_position(self, position):
        colors = {
            0: '#FF0000',   # Rouge
            8: '#0000FF',   # Bleu
            16: '#00FF00',  # Vert 
            24: '#FFFF00'   # Jaune 
        }
        return colors.get(position, 'white')
    
    def draw_pawns(self):
        for player, data in self.PLAYERS.items():
            # Draw each quantum state separately
            for pawn_id, states in data['quantum_states'].items():
                for state in states:
                    for pos, prob in state.items():
                        if pos != -1:
                            x, y = self.get_path_position(pos)
                            fill_color = self.blend_with_white(data['color'], prob)
                            # Draw slightly smaller pawns for superpositions
                            size = 15 if len(states) > 1 else 15
                            self.canvas.create_oval(x-size, y-size, x+size, y+size,
                                                 fill=fill_color,
                                                 outline='white',
                                                 width=2)
    
    def draw_points(self):
        y = 750
        for player, data in self.PLAYERS.items():
            self.canvas.create_text(100 + list(self.PLAYERS.keys()).index(player) * 150,
                                  y, text=f"{player}: {data['points']} points",
                                  fill=data['color'])
    
    def initialize_pawns(self):
        for color in self.PLAYERS:
            # Initialize with -1 to indicate pawns not in play
            self.PLAYERS[color]['pawns'] = [-1, -1]
            # Initialize empty quantum states dictionary
            self.PLAYERS[color]['quantum_states'] = {}
    
    def setup_controls(self):
        self.controls_frame = tk.Frame(self.window)
        self.controls_frame.pack(pady=20)
        
        self.roll_button = tk.Button(self.controls_frame, text="Roll Dice", command=self.roll_dice)
        self.roll_button.pack(side=tk.LEFT, padx=10)
        
        self.dice_label1 = tk.Label(self.controls_frame, text="Dice 1: 0")
        self.dice_label1.pack(side=tk.LEFT, padx=10)
        
        self.dice_label2 = tk.Label(self.controls_frame, text="Dice 2: 0")
        self.dice_label2.pack(side=tk.LEFT, padx=10)
        
        self.player_label = tk.Label(self.controls_frame, text=f"Current Player: {self.current_player}")
        self.player_label.pack(side=tk.LEFT, padx=10)
    
    def roll_dice(self):
        if self.dice_value1 == 0 and self.dice_value2 == 0:
            self.dice_value1 = random.randint(1, 6)
            self.dice_value2 = random.randint(1, 6)
            self.dice_label1.config(text=f"Dice 1: {self.dice_value1}")
            self.dice_label2.config(text=f"Dice 2: {self.dice_value2}")
            
            # Check for reroll condition
            if self.should_reroll():
                self.roll_dice()  # Reroll if needed
            elif not self.has_valid_moves():
                messagebox.showinfo("No Moves", f"{self.current_player.capitalize()} has no valid moves!")
                self.next_player()
                self.dice_value1 = 0
                self.dice_value2 = 0
                self.dice_label1.config(text="Dice 1: 0")
                self.dice_label2.config(text="Dice 2: 0")
    
    def should_reroll(self):
        current_player = self.PLAYERS[self.current_player]
        # Check if only one pawn is in play and both dice are the same
        if len([p for p in current_player['pawns'] if p != -1]) == 1:
            if self.dice_value1 == self.dice_value2:
                pawn_pos = next(p for p in current_player['pawns'] if p != -1)
                new_pos1 = (pawn_pos + self.dice_value1) % self.TOTAL_SPOTS
                new_pos2 = (pawn_pos + self.dice_value2) % self.TOTAL_SPOTS
                if new_pos1 == new_pos2:
                    return True
        return False
    
    def has_valid_moves(self):
        current_player = self.PLAYERS[self.current_player]
        has_moves = False
        
        # Check if player can put a new pawn in play with a 6
        if self.dice_value1 == 6 and -1 in current_player['pawns']:
            start_pos = current_player['start']
            # Check if own pawn is not at start (both classical and quantum states)
            start_occupied = False
            # Check classical positions
            if start_pos in current_player['pawns']:
                start_occupied = True
            # Check quantum positions
            for states in current_player['quantum_states'].values():
                for state in states:
                    if start_pos in state:
                        start_occupied = True
                        break
            
            if not start_occupied:  # Only proceed if start is not occupied
                # Check if opponent's pawn is at start
                for player, data in self.PLAYERS.items():
                    if player != self.current_player:
                        if start_pos in data['pawns']:
                            has_moves = True  # Can capture opponent's pawn
                            break
                        # Check quantum states
                        for states in data['quantum_states'].values():
                            for state in states:
                                if start_pos in state:
                                    has_moves = True
                                    break
                # If no pawns (classical or quantum) are at start, allow placing new pawn
                if not has_moves:
                    has_moves = True
        
        # check if any existing pawns can move
        for pawn_pos in current_player['pawns']:
            if pawn_pos != -1:  # check pawns that are in play
                new_pos = (pawn_pos + self.dice_value1) % self.TOTAL_SPOTS
                
                # Check if path is blocked by any pawns
                path_clear = True
                for step in range(1, self.dice_value1 + 1):
                    check_pos = (pawn_pos + step) % self.TOTAL_SPOTS
                    if check_pos == new_pos:  # Allow landing on opponent's pawn to capture
                        continue
                    for player, data in self.PLAYERS.items():
                        if check_pos in data['pawns']:
                            path_clear = False
                            break
                    if not path_clear:
                        break
                
                if path_clear:
                    # Check if destination is free or has opponent's pawn
                    can_move = True
                    for player, data in self.PLAYERS.items():
                        if new_pos in data['pawns']:
                            if player == self.current_player:
                                can_move = False  # Can't capture own pawn
                            break
                    if can_move:
                        has_moves = True
                        break
        
        return has_moves
    
    def on_canvas_click(self, event):
        if self.dice_value1 == 0 and self.dice_value2 == 0:
            return
            
        current_player = self.PLAYERS[self.current_player]
        
        # First try to move existing pawns (including superpositions)
        moved = False
        for pawn_id, states in current_player['quantum_states'].items():
            for state in states:
                for pos, prob in state.items():
                    if pos != -1:  # Check each position in superposition
                        x, y = self.get_path_position(pos)
                        if (x-20 <= event.x <= x+20) and (y-20 <= event.y <= y+20):
                            # Create new quantum superposition based on both dice
                            pos1 = (pos + self.dice_value1) % self.TOTAL_SPOTS
                            pos2 = (pos + self.dice_value2) % self.TOTAL_SPOTS
                            
                            # Update probabilities - divide existing probability
                            new_prob1 = prob * 0.5
                            new_prob2 = prob * 0.5
                            
                            # Update the quantum state for this specific position
                            new_states = []
                            for s in states:
                                if pos in s:  # This is the state we're updating
                                    new_states.append({pos1: new_prob1})
                                    new_states.append({pos2: new_prob2})
                                else:  # Keep other states unchanged
                                    new_states.append(s)
                            
                            current_player['quantum_states'][pawn_id] = new_states
                            
                            # Update classical position for tracking
                            pawn_idx = int(pawn_id.split('_')[1])
                            current_player['pawns'][pawn_idx] = pos1
                            
                            # Check for quantum capture
                            if self.check_quantum_capture(pos1) or self.check_quantum_capture(pos2):
                                return  # Game is reset in check_quantum_capture if capture occurs
                            
                            moved = True
                            break
                    if moved:
                        break
                if moved:
                    break
        
        if moved:
            self.next_player()
            self.dice_value1 = 0
            self.dice_value2 = 0
            self.dice_label1.config(text="Dice 1: 0")
            self.dice_label2.config(text="Dice 2: 0")
            self.draw_board()
            return

        # Handle new pawn placement 
        # If no existing pawn was clicked and we have a 6, try to place new pawn
        if -1 in current_player['pawns'] and self.dice_value1 == 6:
            start_x, start_y = self.get_path_position(current_player['start'])
            if (start_x-20 <= event.x <= start_x+20) and (start_y-20 <= event.y <= start_y+20):
                # Check if start position is occupied by any pawn (classical or quantum)
                start_occupied = False
                if current_player['start'] in current_player['pawns']:
                    start_occupied = True
                for states in current_player['quantum_states'].values():
                    for state in states:
                        if current_player['start'] in state:
                            start_occupied = True
                            break
                
                if not start_occupied:
                    # Check for opponent's pawn to capture
                    for player, data in self.PLAYERS.items():
                        if player != self.current_player and current_player['start'] in data['pawns']:
                            # Capture opponent's pawn
                            idx = data['pawns'].index(current_player['start'])
                            data['pawns'][idx] = -1  # Return to start
                    
                    # Put new pawn in play - CLASSICAL PLACEMENT
                    idx = current_player['pawns'].index(-1)
                    current_player['pawns'][idx] = current_player['start']
                    
                    # Initialize quantum state for this pawn
                    pawn_id = f"pawn_{idx}"
                    current_player['quantum_states'][pawn_id] = [{current_player['start']: 1.0}]
                    
                    self.next_player()
                    self.dice_value1 = 0
                    self.dice_value2 = 0
                    self.dice_label1.config(text="Dice 1: 0")
                    self.dice_label2.config(text="Dice 2: 0")
                    self.draw_board()
    
    def next_player(self):
        players = list(self.PLAYERS.keys())
        current_index = players.index(self.current_player)
        self.current_player = players[(current_index + 1) % len(players)]
        self.player_label.config(text=f"Current Player: {self.current_player}")
    
    def reset_game(self):
        for player in self.PLAYERS:
            self.PLAYERS[player]['pawns'] = []
            self.PLAYERS[player]['points'] = 0
        self.initialize_pawns()
        self.current_player = 'red'
        self.dice_value1 = 0
        self.dice_value2 = 0
        self.dice_label1.config(text="Dice 1: 0")
        self.dice_label2.config(text="Dice 2: 0")
        self.player_label.config(text=f"Current Player: {self.current_player}")
        self.draw_board()
    
    def run(self):
        self.window.mainloop()

    def blend_with_white(self, color, probability):
        # Convert hex color to RGB values
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Blend with white based on probability
        r = int(r * probability + 255 * (1 - probability))
        g = int(g * probability + 255 * (1 - probability))
        b = int(b * probability + 255 * (1 - probability))
        
        return f'#{r:02x}{g:02x}{b:02x}'

    def check_quantum_capture(self, position):
        for player, data in self.PLAYERS.items():
            if player != self.current_player:
                for states in data['quantum_states'].values():
                    for state in states:
                        if position in state:
                            messagebox.showinfo("Quantum Capture!", "Do some stuff here") #TODO: add quantum capture logic (Full-Full capture and Half-Half capture)
                            self.reset_game()
                            return True
        return False

if __name__ == "__main__":
    game = LudoGame()
    game.run()
