# Quantum Ludo
## Example game
An example game and a walkthrough of the debug functions can be found [here](https://github.com/SjdTl/QuantumEngineering/blob/main/play.mp4) in this repository.
## Game description
The game Ludo, or more specifically [Mensch ärgere Dich nicht](https://en.wikipedia.org/wiki/Mensch_%C3%A4rgere_Dich_nicht), is a game in which four players have four pawns which must get to their home haven. They each move over the path based on die throws. When two pawns go on top of eachother, the original pawn is captured and gets send back to its original position.

With this quantum implementation, there are two dice which cause the pawns to get into a superposition. The pawns can still capture other pawns, but this is done by quantum entanglement. Only after a measurement it is clear where pawns end up and if they have captured other pawns. Measurements (for all pawns at the same time) happen when a pawn get to their safe haven or if there are more then 20 spots filled in the game.

<img src="https://github.com/SjdTl/QuantumEngineering/blob/main/Figures/board.svg" width="500" height="300" />

## Quantum Element
While the game is playing, a quantum circuit is created in the background. With each move, a perticular quantum gate is appended to the circuit. When a measurement should happen, the circuit is simulated using the AerSimulator or Qiskit or using physical IBM chips.

# Dependencies
- matplotlib==3.10.0
- pandas==2.2.3
- PyQt5==5.15.11
- qiskit==1.3.1
- qiskit-aer==0.15.1

The game will probably run with packages in different versions, but these are the tested ones. The game is tested on both macOS and Windows.

When running on the real quantum chip, an API key should also be inserted in the repository, which can be found [here](https://quantum.ibm.com/)

# Run
For the standard experience, run the code [start_screen.py](https://github.com/SjdTl/QuantumEngineering/blob/main/start_screen.py). 
This should open the following window:

<img src="https://github.com/SjdTl/QuantumEngineering/blob/main/screenshots/start_screen.svg" height="200" />

And after pressing play the board opens and the game can be played.

<img src="https://github.com/SjdTl/QuantumEngineering/blob/main/screenshots/capturing.svg" height = "200" />

# High overview documentation
<img src="https://github.com/SjdTl/QuantumEngineering/blob/main/Figures/coding_flow.svg" height = "700" />
The names in the arrows correspond to functions in the files, except the move arrow. That corresponds to three different functions:
 - Direct_move()
 - Move()
 - New pawn()

# Repository structure
```
QuantumEngineering/
├── README.md         
├── .gitignore         
├── start_screen.py             # Start screen UI and connection to main.py
├── main.py                     # Contains the UI, classical logic and connects it to quantum_circuits.py
├── UI.py                       # Contains mostly stylesheets for the UI 
├── UI figures/                 # Graphics used in the UI
│   ├── 0.svg                   # Graphic of an unthrown die
│   ├── i.svg                   # Graphic of a die throw i
│   └── i_pawn.svg              # Graphic of a side view of a pawn of color i 
├── game_logic/
│   ├── quantum_circuits.py     # Contains a circuit class whose methods update a qiskit circuit based on a pawn move
│   └── test_ui.py              # UI for testing quantum_circuits.py with actual pawns  
├── Figures/                    # Contains figures for the report and documentation
│   ├── general_implementation  # A high overview figure describing how the game operates in the backend
│   └── ...                     # Other documentation figures
└── screenshots/                # Contains the screenshots made of the game using f5
```



