import tkinter as tk
from tkinter import messagebox
import random

class LudoGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Ludo Game")
        self.window.geometry("1200x800")  
        self.debug_dice_active = False  # Track if the dice were set via debug

        
        # Game constants
        self.BOARD_SIZE = 600
        self.CELL_SIZE = 50
        self.TOTAL_SPOTS = 32
        self.SPOTS_PER_SIDE = 8
        
        self.PLAYERS = {
            'red': {
                'start': 24, 
                'pawns': [], 
                'color': '#FF0000',
                'points': 0,
                'quantum_states': {}
            },
            'blue': {
                'start': 0, 
                'pawns': [], 
                'color': '#0000FF',
                'points': 0,
                'quantum_states': {}
            },
            'green': {
                'start': 16, 
                'pawns': [], 
                'color': '#00FF00',
                'points': 0,
                'quantum_states': {}
            },
            'yellow': {
                'start': 8, 
                'pawns': [], 
                'color': '#FFFF00',
                'points': 0,
                'quantum_states': {}
            }
        }
        
        self.current_player = 'red'
        self.dice_value1 = 0
        self.dice_value2 = 0

        self.setup_main_layout()
        self.initialize_pawns()
        
    # ------------------------------------------------------------------
    # Main Layout: Two columns -> Left: Board Canvas, Right: Debug Panel
    # ------------------------------------------------------------------
    def setup_main_layout(self):
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: The main board
        board_frame = tk.Frame(main_frame)
        board_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.canvas = tk.Canvas(board_frame, width=self.BOARD_SIZE, height=self.BOARD_SIZE, bg='white')
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        
        # Right side: Controls (including debug)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.setup_controls(right_frame)
        self.draw_board()
        
    # ----------------------------
    #  Board + Pawn Initialization
    # ----------------------------
    def draw_board(self):
        self.canvas.delete("all")
        
        border = 2
        self.canvas.create_rectangle(
            border, border, 
            self.BOARD_SIZE-border, self.BOARD_SIZE-border, 
            width=border, fill='white'
        )
        
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
        
        # Show how many pawns remain "in home" (not yet placed)
        pawns_in_home = 2 - len([p for p in self.PLAYERS[color]['pawns'] if p != -1])
        
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
            else:  # yellow
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
            if i % 8 == 0:  # Starting positions => quadrant color
                color = self.get_color_for_position(i)
            
            self.canvas.create_oval(
                x - cell_size//2, y - cell_size//2,
                x + cell_size//2, y + cell_size//2,
                fill=color, outline='black'
            )
            self.canvas.create_text(x, y, text=str(i), fill='black', font=('Arial', 10))
    
    def get_path_position(self, position):
        origin_x = self.BOARD_SIZE // 2
        origin_y = self.BOARD_SIZE // 2
        cell = 50
        coords = {
            0:  (origin_x + cell, origin_y - 4*cell),
            1:  (origin_x + cell, origin_y - 3*cell),
            2:  (origin_x + cell, origin_y - 2*cell),
            3:  (origin_x + cell, origin_y - cell),
            4:  (origin_x + 2*cell, origin_y - cell),
            5:  (origin_x + 3*cell, origin_y - cell),
            6:  (origin_x + 4*cell, origin_y - cell),
            7:  (origin_x + 4*cell, origin_y),
            
            8:  (origin_x + 4*cell, origin_y + cell),
            9:  (origin_x + 3*cell, origin_y + cell),
            10: (origin_x + 2*cell, origin_y + cell),
            11: (origin_x + cell,   origin_y + cell),
            12: (origin_x + cell,   origin_y + 2*cell),
            13: (origin_x + cell,   origin_y + 3*cell),
            14: (origin_x + cell,   origin_y + 4*cell),
            15: (origin_x,          origin_y + 4*cell),
            
            16: (origin_x - cell,   origin_y + 4*cell),
            17: (origin_x - cell,   origin_y + 3*cell),
            18: (origin_x - cell,   origin_y + 2*cell),
            19: (origin_x - cell,   origin_y + cell),
            20: (origin_x - 2*cell, origin_y + cell),
            21: (origin_x - 3*cell, origin_y + cell),
            22: (origin_x - 4*cell, origin_y + cell),
            23: (origin_x - 4*cell, origin_y),
            
            24: (origin_x - 4*cell, origin_y - cell),
            25: (origin_x - 3*cell, origin_y - cell),
            26: (origin_x - 2*cell, origin_y - cell),
            27: (origin_x - cell,   origin_y - cell),
            28: (origin_x - cell,   origin_y - 2*cell),
            29: (origin_x - cell,   origin_y - 3*cell),
            30: (origin_x - cell,   origin_y - 4*cell),
            31: (origin_x,          origin_y - 4*cell),
        }
        return coords[position]
    
    def get_color_for_position(self, position):
        colors = {
            0:  '#0000FF',   # Blue
            8:  '#FFFF00',   # Yellow
            16: '#00FF00',   # Green
            24: '#FF0000'    # Red
        }
        return colors.get(position, 'white')
    
    def draw_pawns(self):
        for player, data in self.PLAYERS.items():
            for pawn_id, states in data['quantum_states'].items():
                for state in states:
                    for pos, prob in state.items():
                        if pos != -1:
                            x, y = self.get_path_position(pos)
                            color = self.blend_with_white(data['color'], prob)
                            self.canvas.create_oval(
                                x - 20, y - 20,
                                x + 20, y + 20,
                                fill=color, outline='white', width=2
                            )
    
    def draw_points(self):
        y = 750
        for i, (player, data) in enumerate(self.PLAYERS.items()):
            self.canvas.create_text(
                100 + i*150, y,
                text=f"{player}: {data['points']} pts",
                fill=data['color']
            )
    
    def initialize_pawns(self):
        for color in self.PLAYERS:
            self.PLAYERS[color]['pawns'] = [-1, -1]
            self.PLAYERS[color]['quantum_states'] = {}
    
    # ------------------------------------------
    #  Game Controls (Plus Additional Debug Panel)
    # ------------------------------------------
    def setup_controls(self, parent_frame):
        # Normal Buttons
        roll_btn = tk.Button(parent_frame, text="Roll Dice", command=self.roll_dice)
        roll_btn.pack(pady=5, fill=tk.X)
        
        # Dice Labels
        self.dice_label1 = tk.Label(parent_frame, text="Dice 1: 0")
        self.dice_label1.pack(pady=5)
        self.dice_label2 = tk.Label(parent_frame, text="Dice 2: 0")
        self.dice_label2.pack(pady=5)
        
        # Player Label
        self.player_label = tk.Label(parent_frame, text=f"Current Player: {self.current_player}")
        self.player_label.pack(pady=5)
        
        # Separator
        sep = tk.Frame(parent_frame, height=2, bd=1, relief=tk.SUNKEN)
        sep.pack(fill=tk.X, pady=10)
        
        # ---------- Debug Panel -----------
        debug_label = tk.Label(parent_frame, text="--- Debug Panel ---", fg="red")
        debug_label.pack(pady=5)
        
        # Dice Controls (Spinboxes)
        dice_frame = tk.Frame(parent_frame)
        dice_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(dice_frame, text="Dice 1:").pack(side=tk.LEFT, padx=5)
        self.debug_dice1 = tk.IntVar(value=1)
        tk.Spinbox(dice_frame, from_=1, to=6, textvariable=self.debug_dice1, width=5).pack(side=tk.LEFT, padx=5)
        
        tk.Label(dice_frame, text="Dice 2:").pack(side=tk.LEFT, padx=5)
        self.debug_dice2 = tk.IntVar(value=1)
        tk.Spinbox(dice_frame, from_=1, to=6, textvariable=self.debug_dice2, width=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(dice_frame, text="Set Dice", command=self.debug_set_dice).pack(side=tk.LEFT, padx=10)
        
        # Pawn Placement Controls
        pawn_frame = tk.Frame(parent_frame)
        pawn_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(pawn_frame, text="Color:").pack(side=tk.LEFT, padx=5)
        self.debug_color = tk.StringVar(value='red')
        tk.OptionMenu(pawn_frame, self.debug_color, *self.PLAYERS.keys()).pack(side=tk.LEFT, padx=5)
        
        tk.Label(pawn_frame, text="Position:").pack(side=tk.LEFT, padx=5)
        self.debug_position = tk.IntVar(value=0)
        tk.Spinbox(pawn_frame, from_=0, to=31, textvariable=self.debug_position, width=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(pawn_frame, text="Add Pawn", command=self.debug_add_pawn).pack(side=tk.LEFT, padx=5)
        tk.Button(pawn_frame, text="Remove Pawn", command=self.debug_remove_pawn).pack(side=tk.LEFT, padx=5)
    
    # ------------------------------
    #  Dice Rolling & Move Handling
    # ------------------------------
    def roll_dice(self):
        # 1) Turn off debug mode
        self.debug_dice_active = False
        
        # 2) Always reset dice to 0 before the new roll
        self.dice_value1 = 0
        self.dice_value2 = 0
        self.dice_label1.config(text="Dice 1: 0")
        self.dice_label2.config(text="Dice 2: 0")
        
        # 3) Do the actual roll
        self.dice_value1 = random.randint(1, 6)
        self.dice_value2 = random.randint(1, 6)
        self.dice_label1.config(text=f"Dice 1: {self.dice_value1}")
        self.dice_label2.config(text=f"Dice 2: {self.dice_value2}")
        
        # 4) Continue any “reroll” or “no valid moves” checks
        if self.should_reroll():
            self.roll_dice()
        elif not self.has_valid_moves():
            messagebox.showinfo("No Moves", f"{self.current_player.capitalize()} has no valid moves!")
            self.next_player()
            self.reset_dice_labels()
    
    def reset_dice_labels(self):
        self.dice_value1 = 0
        self.dice_value2 = 0
        self.dice_label1.config(text="Dice 1: 0")
        self.dice_label2.config(text="Dice 2: 0")
    
    def should_reroll(self):
        # Example logic for re-rolling (can be changed)
        current_player = self.PLAYERS[self.current_player]
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
            start_occupied = start_pos in current_player['pawns']
            for states in current_player['quantum_states'].values():
                for state in states:
                    if start_pos in state:
                        start_occupied = True
                        break
            if not start_occupied:
                # Check if opponent's pawn is at start
                for player, data in self.PLAYERS.items():
                    if player != self.current_player:
                        if start_pos in data['pawns']:
                            has_moves = True
                            break
                        for states in data['quantum_states'].values():
                            for state in states:
                                if start_pos in state:
                                    has_moves = True
                                    break
                if not has_moves:
                    has_moves = True
        
        # Check existing pawns
        for pawn_pos in current_player['pawns']:
            if pawn_pos != -1:
                new_pos = (pawn_pos + self.dice_value1) % self.TOTAL_SPOTS
                path_clear = True
                for step in range(1, self.dice_value1 + 1):
                    check_pos = (pawn_pos + step) % self.TOTAL_SPOTS
                    if check_pos == new_pos:
                        continue
                    for _, data in self.PLAYERS.items():
                        if check_pos in data['pawns']:
                            path_clear = False
                            break
                    if not path_clear:
                        break
                
                if path_clear:
                    can_move = True
                    for _, data in self.PLAYERS.items():
                        if new_pos in data['pawns']:
                            if _ == self.current_player:
                                can_move = False
                            break
                    if can_move:
                        has_moves = True
                        break
        
        return has_moves
    
    def on_canvas_click(self, event):
        """All movement logic goes through here (the real board)."""
        # 1) If no dice value is set at all, do nothing.
        if self.dice_value1 == 0 and self.dice_value2 == 0:
            return

        # 2) Decide which players' pawns are "clickable."
        #    - If debug dice are active, *all* pawns are clickable.
        #    - Otherwise, only the current player's pawns are clickable.
        if self.debug_dice_active:
            players_to_check = list(self.PLAYERS.keys())  # all colors
        else:
            players_to_check = [self.current_player]       # only current color

        moved = False

        # 3) Check each relevant player's quantum pawns for a click
        for player_key in players_to_check:
            player_data = self.PLAYERS[player_key]

            for pawn_id, states in player_data['quantum_states'].items():
                for state in states:
                    for pos, prob in state.items():
                        # If there's an actual position for this "part" of the quantum state
                        if pos != -1:
                            x, y = self.get_path_position(pos)
                            # Check if the user clicked within this pawn's circle
                            if (x - 20 <= event.x <= x + 20) and (y - 20 <= event.y <= y + 20):
                                # Create new quantum superposition using dice_value1 and dice_value2
                                pos1 = (pos + self.dice_value1) % self.TOTAL_SPOTS
                                pos2 = (pos + self.dice_value2) % self.TOTAL_SPOTS

                                new_prob1 = prob * 0.5
                                new_prob2 = prob * 0.5

                                new_states = []
                                for s in states:
                                    if pos in s:
                                        # Split into two new positions
                                        new_states.append({pos1: new_prob1})
                                        new_states.append({pos2: new_prob2})
                                    else:
                                        new_states.append(s)

                                player_data['quantum_states'][pawn_id] = new_states

                                pawn_idx = int(pawn_id.split('_')[1])
                                player_data['pawns'][pawn_idx] = pos1

                                # Check quantum capture
                                if self.check_quantum_capture(pos1, player_key) or self.check_quantum_capture(pos2, player_key):
                                    return

                                moved = True
                                break  # Stop looking for more positions
                    if moved:
                        break  # Stop looking for more states
                if moved:
                    break  # Stop looking for more pawn_ids

            if moved:
                break  # Stop looking for more players

        # 4) If something was moved (quantum movement happened)
        if moved:
            # If we are NOT in debug mode, proceed to next player's turn normally
            if not self.debug_dice_active:
                self.next_player()
                self.reset_dice_labels()

            # Redraw board after move
            self.draw_board()
            return

        # 5) If no quantum pawn was moved, try "placing a new pawn" logic (for the current player)
        if not self.debug_dice_active:
            # Normal mode -> only allow the current player to place a new pawn.
            current_player_data = self.PLAYERS[self.current_player]
            if -1 in current_player_data['pawns'] and self.dice_value1 == 6:
                start_pos = current_player_data['start']
                start_x, start_y = self.get_path_position(start_pos)
                if (start_x - 20 <= event.x <= start_x + 20) and (start_y - 20 <= event.y <= start_y + 20):
                    # Check if start is already occupied by the current player or quantum
                    start_occupied = start_pos in current_player_data['pawns']
                    for states in current_player_data['quantum_states'].values():
                        for state in states:
                            if start_pos in state:
                                start_occupied = True
                                break

                    if not start_occupied:
                        # Possibly capture enemy that’s sitting at start_pos
                        for p, data in self.PLAYERS.items():
                            if p != self.current_player and start_pos in data['pawns']:
                                idx = data['pawns'].index(start_pos)
                                data['pawns'][idx] = -1

                        # Place new pawn
                        idx = current_player_data['pawns'].index(-1)
                        current_player_data['pawns'][idx] = start_pos
                        pawn_id = f"pawn_{idx}"
                        current_player_data['quantum_states'][pawn_id] = [{start_pos: 1.0}]

                        # Turn is over if not debug
                        self.next_player()
                        self.reset_dice_labels()
                        self.draw_board()

        else:
            # Might add later
            pass

    
    def next_player(self):
        order = ["red", "blue", "yellow", "green"]
        curr_idx = order.index(self.current_player)
        self.current_player = order[(curr_idx + 1) % len(order)]
        self.player_label.config(text=f"Current Player: {self.current_player}")
    
    def reset_game(self):
        for player in self.PLAYERS:
            self.PLAYERS[player]['pawns'] = []
            self.PLAYERS[player]['points'] = 0
        self.initialize_pawns()
        self.current_player = 'red'
        self.reset_dice_labels()
        self.player_label.config(text=f"Current Player: {self.current_player}")
        self.draw_board()
    
    # ------------------
    #  Debug Panel Logic
    # ------------------
    def debug_set_dice(self):
        """Force dice values from the debug spinboxes."""
        d1 = self.debug_dice1.get()
        d2 = self.debug_dice2.get()
        if 1 <= d1 <= 6 and 1 <= d2 <= 6:
            self.debug_dice_active = True     
            self.dice_value1 = d1
            self.dice_value2 = d2
            self.dice_label1.config(text=f"Dice 1: {self.dice_value1}")
            self.dice_label2.config(text=f"Dice 2: {self.dice_value2}")
        else:
            # silently ignore or show error
            pass
    
    def debug_add_pawn(self):
        """Force a pawn of the chosen color onto the chosen position."""
        color = self.debug_color.get()
        pos = self.debug_position.get()
        if not (0 <= pos < self.TOTAL_SPOTS):
            return
        
        # Attempt to find a free (=-1) pawn slot for that color
        try:
            idx = self.PLAYERS[color]['pawns'].index(-1)
        except ValueError:
            return  # No free pawn slot left for that color
        
        # Place the pawn
        self.PLAYERS[color]['pawns'][idx] = pos
        pawn_id = f"pawn_{idx}"
        self.PLAYERS[color]['quantum_states'][pawn_id] = [{pos: 1.0}]
        
        self.draw_board()
    
    def debug_remove_pawn(self):
        """Force removal of any pawn at the chosen position."""
        color = self.debug_color.get()
        pos = self.debug_position.get()
        
        # Try to find which pawn is at that pos
        try:
            idx = self.PLAYERS[color]['pawns'].index(pos)
        except ValueError:
            return  # There's no pawn of that color at pos
        
        # Remove from classical + quantum
        self.PLAYERS[color]['pawns'][idx] = -1
        del self.PLAYERS[color]['quantum_states'][f"pawn_{idx}"]
        
        self.draw_board()
    
    # -----------------------------------
    #  Capture + Probability Visualization
    # -----------------------------------
    def blend_with_white(self, color, probability):
        # Convert hex color to RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        # Blend
        r = int(r * probability + 255 * (1 - probability))
        g = int(g * probability + 255 * (1 - probability))
        b = int(b * probability + 255 * (1 - probability))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def check_quantum_capture(self, position, moved_color):
        for player, data in self.PLAYERS.items():
            if player != moved_color:  # the color we actually moved
                for states in data['quantum_states'].values():
                    for state in states:
                        if position in state:
                            messagebox.showinfo("Quantum Capture!", "Handle capture logic here.")
                            self.reset_game()
                            return True
        return False

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = LudoGame()
    game.run()
