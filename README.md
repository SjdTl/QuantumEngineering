# Quantum Ludo
## Game description
The game Ludo, or more specifically [Mensch ärgere Dich nicht](https://en.wikipedia.org/wiki/Mensch_%C3%A4rgere_Dich_nicht), is a game in which four players have four pawns which must get to their home haven. They each move over the path based on die throws. When two pawns go on top of eachother, the original pawn is captured and gets send back to its original position.

With this quantum implementation, there are two dice which cause the pawns to get into a superposition. The pawns can still capture other pawns, but this is done by quantum entanglement. Only after a measurement it is clear where pawns end up and if they have captured other pawns. Measurements (for all pawns at the same time) happen when a pawn get to their safe haven or if there are more then 20 spots filled in the game.

<img src="https://github.com/SjdTl/QuantumEngineering/blob/main/positions/board.svg" width="500" height="300" />

## Quantum Element
While the game is playing, a quantum circuit is created in the background. With each move, a perticular quantum gate is appended to the circuit. When a measurement should happen, the circuit is simulated using the AerSimulator or Qiskit or using physical IBM chips.

# Dependencies
- matplotlib==3.10.0
- pandas==2.2.3
- PyQt5==5.15.11
- qiskit==1.3.1
- qiskit-aer==0.15.1
The game will probably run on different versions, but these are the tested ones. The game is both tested on macOS and Windows.

# Run
For the standard experience, run the code [start_screen.py](https://github.com/SjdTl/QuantumEngineering/blob/main/start_screen.py). 
This should open the following window:

<img src="https://github.com/SjdTl/QuantumEngineering/blob/main/screenshots/start_screen.svg" height="200" />

And after pressing play the board opens and the game can be played.

<img src="https://github.com/SjdTl/QuantumEngineering/blob/main/screenshots/capturing.svg" height = "200" />
## Hardware used
[qiskit ibm](https://www.ibm.com/quantum/qiskit) ([documentation](https://docs.quantum.ibm.com/guides))
with some exercises here [IBM challenge 2024](https://github.com/qiskit-community/ibm-quantum-challenge-2024?tab=readme-ov-file)
