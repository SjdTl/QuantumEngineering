### Full implementation: Not yet complete

import random

# Constants
R = "r"
G = "g"
B = "b"
Y = "y"
R1 = "r1"
G1 = "g1"
B1 = "b1"
Y1 = "y1"
R2 = "r2"
G2 = "g2"
B2 = "b2"
Y2 = "y2"

# Player and pawn designation: also constant
PLAYERS = [Y,R,G,B]
PAWNS = [[Y1,Y2],[R1,R2],[G1,G2],[B1,B2]]

# Order of play:
# yellow: 0
# red: 1
# green: 2
# blue: 3

# Current player
cur = 0

# These will call the functions in quantum_circuits.py
# ---------------------
# I'm guessing based on the following you assume that the quantum_circuits.py contains functions
# This is not true
# It contains a class
# Therefore start with initializing the circuit by: circuit = circuit()
# And change the circuit by just selecting a method: circuit.new_pawn() (this does not return anything)
# And when measuring do the following measurement = circuit.measure()
# ---------------------
def new_pawn():
    return

def switch():
    return

def move():
    return

def capture():
    return

def measure():
    return

# Initialize the board
board = [None]*32

# Two start spots for every player. Order: Y-R-G-B
in_start = [2,2,2,2]
# Two finish spots for every player. Order: Y-R-G-B
in_finish = [[0,0],
            [0,0],
            [0,0],
            [0,0]]

# Respective starting and finishing positions. Order: Y-R-G-B
start_pos = [0,8,16,24]

# Numerical flags to determine which function to call. 
# Flags: split {0,1}, first {0,1}, finish {0,1,2}
flags = [0]*3

## Game loop
while True:
    # Update player
    cur = (cur + 1) % 4

    print(f"Player turn: {PLAYERS[cur]}")

    # Prompt for choice: classical or quantum move
    choice = input("Choose move (0 for classical; 1 for quantum): ")
    while True:
        if choice != '0' and choice != '1':
            choice = input("Enter 0 or 1: ")
        else:
            flags[0] = int(choice)
            break

    v1 = random.randint(1, 7)
    v2 = random.randint(1, 7)
    
    # Throw dice
    if flags[0] == 1:
        values = [v1,v2] # Values can be identical
    else:
        values = [v1,v1]
    print(f"Results: {values}")

    # Calculate movement options given the values
    available = [i for i, x in enumerate(board) if x["Player"] == PLAYERS[cur]]
    if in_start[cur] != 0 and 6 in values and board[start_pos[cur]]["Player"] != PLAYERS[cur]:
        available.append(-1)
    options = []
    targets_list = []
    for ava in available:
        occupation = [0]*2
        targets = [None]*2
        if ava == -1:
            value = 0
            while True:
                target = (start_pos[cur] + value) % 32
                if board[target] != None and board[target]["Player"] != PLAYERS[cur]:
                    if value < 31:
                        value += 1
                    else:
                        occupation = [1,1] # !!! THIS NEEDS TO BE CHANGED BECAUSE OF FINISH MECHANICS !!!
                elif board[target] != None and board[target]["Player"] == PLAYERS[cur]:
                    occupation = [1,1]
                    break
                else:
                    targets = [target,target]
                    break

        for i in range(len(values)):
            while True:
                target = (ava + values[i]) % 32
                if board[target] != None and board[target]["Player"] != PLAYERS[cur]:
                    if values[i] < 31:
                        values[i] += 1
                    else:
                        occupation = [1,1] # !!! THIS NEEDS TO BE CHANGED BECAUSE OF FINISH MECHANICS !!!
                elif board[target] != None and board[target]["Player"] == PLAYERS[cur]:
                    occupation[i] = 1
                    targets[i] = target
                    break
                else:
                    targets[i] = target
                    break
        if occupation != [1,1]:
            options.append(str(ava)) # String because it needs to be compared to player input later, before the input is converted to an integer
            targets_list.append(targets)

    # Prompt for choice of pawn to move       
    from_pos = input(f"Choose starting position from the following: {options}: ")
    while True:
        if from_pos not in options:
            from_pos = input(f"Choose from {available}: ")
        else:
            from_pos = int(from_pos)
            break


# From this point downwards, the code is not up to date.
# ----------------------------------------------------------------------------------------------------------


    if from_pos != -1:
        flags[1] = 0
        # Remove pawn from start
        board[from_pos] = None
    else:
        flags[1] = 1
        values = [1]

    # Place pawn at destination
    for i in range(len(values)):
        if from_pos+values[i] < 32:
            flags[2] = 0
            board[from_pos+values[i]] = {"Pawn": "TheOne"}
        elif from_pos+values[i] > 33:
            flags[2] = 0
            board[66-(from_pos+values[i])] = {"Pawn": "TheOne"}
        else:
            flags[2] += 1




            


"""
Types of moves:
Non-split first
Split first
Non-split inter
Split inter
Non-split capture: code later
Split capture: code later
Non-split finish
Split finish
"""







    


