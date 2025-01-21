# Quantum Ludo
The game Ludo, or more specifically [Mensch ärgere Dich nicht](https://en.wikipedia.org/wiki/Mensch_%C3%A4rgere_Dich_nicht), is a game in which four players have four pawns which must get to their home haven. They each move over the path based on die throws. When two pawns go on top of eachother, the original pawn is captured and gets send back to its original position.

With this quantum implementation, there are two dice which cause the pawns to get into a superposition. The pawns can still capture other pawns, but this is done by quantum entanglement. Only after a measurement it is clear where pawns end up and if they have captured other pawns. Measurements (for all pawns at the same time) happen when a pawn get to their safe haven or if there are more then 20 spots filled in the game.
![|300](https://github.com/SjdTl/QuantumEngineering/blob/main/positions/board.svg)

## Hardware used
[qiskit ibm](https://www.ibm.com/quantum/qiskit) ([documentation](https://docs.quantum.ibm.com/guides))
with some exercises here [IBM challenge 2024](https://github.com/qiskit-community/ibm-quantum-challenge-2024?tab=readme-ov-file)
