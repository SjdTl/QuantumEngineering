import numpy as np
from typing import List
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
from qiskit_ibm_runtime import SamplerV2 as Sampler 
from qiskit_aer import AerSimulator


class circuit():
    """
    Description
    -----------
    Class containg the quantum circuit that is slowly updated with every move

    ----------
    N : int
        Size of the quantum circuit
    
    Returns
    -------
    new_positions : list[int]
        List of integers with indeces where the pawns remain when calling circuit.measure()

    Example
    -------
    qc = circuit()
    qc.new_pawn([5,3,29])
    qc.measure()

    >>> [3,5,29]
    """
    def __init__(self, N=32):
        self.qcircuit = QuantumCircuit(N)

    def new_pawn(self, move_to : List[int]):
        """
        Description
        -----------
        Add a pawn to position move_to[0] by drawing an X gate in the circuit at qubit move_to[0]

        Parameters
        ----------
        move_to : List[int]
            List of integer(s) : the position to move to

        Raises
        ------
        ValueError
            move_to must be in the form [int]; a list containing one integer

        Example
        -------
        qc = circuit(N=2)\\
        qc.new_pawn([0])\\
        qc.draw()

        >>>      ┌───┐
        >>> q_0: ┤ X ├
        >>>      └───┘
        >>> q_1: ─────
        """

        self.qcircuit.x(move_to)

    def move(self, move_from : List[int], move_to : List[int]):
        """
        Description
        -----------
        Move one pawn (possibly in a superposition) to a superposition, so move_from one position
        and move_to two positions
        
        Parameters
        ----------
        move_form : List[int]
            List of one integer: the position to move from
        move_to : List[int]
            List of two integers: the position to move to
        
        Raises
        ------
        ValueError
            move_from must be in the from [int]; a list containing one integer
        ValueError
            move_to must be in the form [int, int]; a list containing two integers
        
        Examples
        --------
        qc = circuit(N=3) \\
        qc.move([0], [1,2]) \\
        qc.draw()

        >>> q_0: ──■───X──────
        >>>      ┌─┴─┐ │
        >>> q_1: ┤ H ├─┼───■──
        >>>      └───┘ │ ┌─┴─┐
        >>> q_2: ──────X─┤ X ├
                         └───┘
        """
        if len(move_from) != 1:
            raise ValueError("move_from must be in the form [int]; a list containing one integer")
        if len(move_to) != 2:
            raise ValueError("move_to must be in the form [int, int]; a list containing two integers")
        
        self.qcircuit.ch(move_from[0], move_to[0])
        self.qcircuit.swap(move_from[0], move_to[1])
        self.qcircuit.cx(move_to[0], move_to[1])

    def capture(self, capturer : List[int], captive : List[int], captive_entanglement : List[int]):
        """
        Description
        -----------
        Move in which the capturer captures the captive. It is also necessary to provide the pawns with which
        the captive is entangled
        ---ATTENTION---
        THIS DOES NOT MOVE THE PAWN THAT CAPTURES (called capturer), IT ONLY ENTANGLES THE CAPTURER and CAPTURED

        Parameters
        ----------
        capturer : List[int] 
            List of one integer: contains the pawn that captures (called capturer)
        captive : List[int]
            List of one integer: contains the pawn that is captured (called captive)
        captive_entanglement : List[int]
            List of some integers: contains the pawns with which the captive is in superpositions. So all other positions
            that are of the same colour and same pawn as the captive
        
        Raises
        ------
        ValueError
            capturer or captive must be in the from [int]; a list containing one integer
        ValueError
            the captive_entanglement also contains the captive, this should not be the case
            please look at the documentation
        
        Examples
        --------
        qc = circuit(N=6)\\
        qc.new_pawn([0, 1])\\
        qc.move([0],[2, 3]) # move green 0 -> 2 & 3\\ 
        qc.move([1], [4, 5]) # move red 1 -> 4 & 5, but capture green since red actually came on top of 3\\
        qc.capture([4], [3], [2]) # reds 4 captures greens 3 that is connected to 2 \\
        qc.draw()

        >>>                              ┌───┐
        >>> q_0 (initial green):         ┤ X ├─■────────X──────────────────────── |0>
        >>>                              ├───┤ │        │
        >>> q_1 (initial red):           ┤ X ├─┼────■───┼──X───────────────────── |0>
        >>>                              └───┤─┴─┐  │   │  │      ┌───┐     ┌───┐
        >>> q_2 (0.5 green):             ────┤ H ├──┼───┼──┼───■──┤ X ├──■──┤ X ├ 
        >>>                                  └───┘  │   │  │ ┌─┴─┐└───┘┌─┴─┐└───┘ 
        >>> q_3 (0.5 green and captive): ───────────┼───X──┼─┤ X ├─────┤ X ├───── 
        >>>                                       ┌─┴─┐    │ └───┘     └─┬─┘
        >>> q_4 (0.5 red and capturer):  ─────────┤ H ├────┼───■─────────■───────
        >>>                                       └───┘    │ ┌─┴─┐
        >>> q_5 (0.5 red):               ──────────────────X─┤ X ├───────────────
        >>>                                                  └───┘
        """
        if len(capturer) != 1 or len(captive) != 1:
            raise ValueError("capturer or captive must be in the from [int]; a list containing one integer")
        if captive[0] in captive_entanglement:
            raise ValueError("the captive_entanglement also contains the captive, this should not be the case please look at the documentation")
        
        for captive_entangled in captive_entanglement:
            self.qcircuit.x(captive_entangled)
        
        self.qcircuit.mcx(captive_entanglement+capturer, captive[0])
    
        for captive_entangled in captive_entanglement:
            self.qcircuit.x(captive_entangled)

    
    def measure(self, backend = FakeSherbrooke(), optimization_level=2, simulator = True):
        """
        Description
        -----------
        Measures the circuit and returns the remaining positions in an array

        Parameters
        ----------
        circuit : qiskit.QuantumCircuit
            Quantum circuit that describes the positions of the board in qubits and gates
        backend: Fake or real backend
            Backend to which the circuit is transpiled (and run)
        optimization_level: int
            See https://docs.quantum.ibm.com/api/qiskit/transpiler_preset#generate_preset_pass_manager 
        
        Returns
        -------
        output : np.array
            Array containing the collapsed bits describing the remaining pawns
        
        Notes
        ------
        It seems not necessary to have a backend and a simulator arguments. However, the fakesimulators are describing to which architecture
        the circuit is compiled, while the simulator value makes sure that for the simulation itself a 'perfect' simulation is used,
        namely the AerSimulator(), because the normal fakesimulators can not simulate this many bits
        """
        
        out_with_freq = self._internal_measure(backend = backend, optimization_level=optimization_level, simulator = simulator)
        most_freq_out = max(out_with_freq, key=out_with_freq.get)
        new_positions = [index for index, char in enumerate(most_freq_out[::-1]) if char == '1']

        return new_positions
    
    def draw(self, mpl_open = True, term_draw = True):
        """
        Description
        ------------
        Test function that draws the circuit and opens it in matplotlib if mpl_open == True
        Also prints the circuit in the terminal if term_draw == True
        """
        self.qcircuit.draw('mpl')
        if mpl_open == True:
            plt.show()
        if term_draw ==True:
            print(self.qcircuit)

    def _internal_measure(self, backend = FakeSherbrooke(), optimization_level=2, simulator = True):
        """See circuit.measure() for documentation"""

        self.qcircuit.measure_all()

        pm = generate_preset_pass_manager(backend=backend, optimization_level=optimization_level)
        isa_circuit = pm.run(self.qcircuit)
        pub = (isa_circuit)

        if simulator == False:
            sampler = Sampler(mode = backend)
        else:
            sampler = Sampler(mode = AerSimulator())

        job = sampler.run(pubs=[pub])
        result = job.result()[0]
        out_with_freq = result.data.meas.get_counts()

        return out_with_freq


if __name__ == "__main__":
    qc = circuit(N=30)
    qc.new_pawn([0,1])
    qc.move([0],[2, 3]) # move green 0 -> 2 & 3\\ 
    # qc.move([1], [4, 5]) # move red 1 -> 4 & 5, but capture green since red actually came on top of 3\\
    # qc.capture([4], [3], [2]) # reds 4 captures greens 3 that is connected to 2 \\
    qc.draw(mpl_open=False)
    print(qc._internal_measure(optimization_level=3))

    def testing():
        dksjf
    
