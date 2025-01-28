import numpy as np
from typing import List
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
from qiskit.providers.fake_provider import GenericBackendV2 as GenericBackend
from qiskit_ibm_runtime import SamplerV2 as Sampler 
from qiskit_aer import AerSimulator

import random


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
    qc = circuit()\\
    qc.new_pawn([5,3,29])\\
    qc.measure()

    >>> [3,5,29]
    """
    def __init__(self, N=32):
        self.N = N + 2
        self.qcircuit = QuantumCircuit(self.N)
        self.history = []

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
        if len(move_to) != 0:
            self.qcircuit.x(move_to)

    def switch(self, move_from : List[int], move_to : List[int]):
        """
        Description
        ------------
        Just adds a switch gate between move_from and move_to

        Parameters
        ----------
        move_form : List[int]
            List of one integer: the position to move from
        move_to : List[int]
            List of one integer: the position to move to
        """
        if len(move_from) != 1 or len(move_to) != 1:
            raise ValueError("move must be in the form [int]; a list containing one integer")
        
        self.qcircuit.swap(move_from[0], move_to)

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
        self.qcircuit.cx(move_from[0], move_to[0])
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

    def merge_move(self, move_from : List[int], move_to : List[int], merge_in : List[int]):
        """
        Description
        -----------
        Unused move in which a pawn (P=50%) merges with another pawn (P=50%) to form a superposition (P=75% and P=25%)

        Pawn moves from a position move_from to two positions, but one of these positions is occupied by the same pawn in superposition (namely on position merge_in)
        """
        if len(move_from) != 1:
            raise ValueError("Move_from must be in the from [int]; a list containing one integer")
        if len(move_to) != 2:
            raise ValueError("Move_to must be in the form [int, int]: a list of two integers")
        if len(merge_in) != 1:
            raise ValueError("Merge_in must be in the form [int]: a list containing one integer")
        if merge_in[0] not in move_to:
            raise ValueError("Merge_in position is not in the two move_to positions")
        
        aN = (-2 - np.sqrt(3))*np.sqrt(2 - np.sqrt(3))/2
        bN = -np.sqrt(1/2 - np.sqrt(3)/4)
        cN = (-2 + np.sqrt(3))*np.sqrt(np.sqrt(3) + 2)/2
        dN = np.sqrt(np.sqrt(3)/4 + 1/2)

        U = np.array([
            [1, 0, 0, 0],
            [0, aN, bN, 0],
            [0, cN, dN, 0],
            [0, 0, 0, 1]
        ])

        move_to.remove(merge_in[0])    
    
        self.qcircuit.swap(move_from[0], move_to[0])
        self.qcircuit.unitary(U, [merge_in[0], move_to[0]])

    def measure_basis(self, measure_bases : List[int]):
        for i, measure_basis in enumerate(measure_bases):
            if measure_basis != None:
                if measure_basis == "Z":
                    # Nothing happens
                    pass
                if measure_basis == "X":
                    self.qcircuit.h(i)
                if measure_basis == "Q":
                    theta = np.pi/4  # Rotation angle for Q basis
                    self.qcircuit.ry(theta, i)
                if measure_basis == "T":
                    theta = 3*np.pi/4  # Rotation angle for T basis
                    self.qcircuit.ry(theta, i)
    
    def measure(self, backend = FakeSherbrooke(), optimization_level=2, simulator = True, out_internal_measure=False, shots=1024, efficient = False, service = None):
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
        out_internal_measure : boolean
            Outputs out_with_freq from the self._internal_measure if True. Mostly unused
        
        Returns
        -------
        output : np.array
            Array containing the collapsed bits describing the remaining pawns
        if out_internal_measure == True: out_with_freq : dictionary
            Dictionary containing the measurement outcome in binary with its frequency, see ibm for exact documentation
        
        Notes
        ------
        It seems not necessary to have a backend and a simulator arguments. However, the fakesimulators are describing to which architecture
        the circuit is compiled, while the simulator value makes sure that for the simulation itself a 'perfect' simulation is used,
        namely the AerSimulator(), because the normal fakesimulators can not simulate this many bits

        The simulator returns several hunderds of measurement. Therefore all possible outcomes have a certain frequency connected to them
        This is used as a weight in selecting the final measurement from all the measurements using pseudo-random methods
        Also some results are filtered out to control for errors
        """
        if service is None and simulator == False:
            raise ValueError("If simulator is False, the service must be given")

        if efficient == False or simulator == False:
            filtered_data = self._internal_measure(backend = backend, optimization_level=optimization_level, simulator = simulator, shots = shots, service = service)
            if simulator == False:
                nr_of_qubits_used = self.N
            else:
                nr_of_qubits_used = 127
        else:
            filtered_data, nr_of_qubits_used = self._internal_efficient_simulation(backend = backend, optimization_level=optimization_level, shots = shots)
        
        weights = list(filtered_data.keys())
        positions = list(filtered_data.values())

        if weights:
            chosen_positions = random.choices(positions, weights=weights, k=1)[0]
        else:
            raise ValueError(r"Not a single measurement outcome has a probability P>0.5\% of occuring; there is probably a measurement error")
        if out_internal_measure == False:
            return chosen_positions
        else:
            return chosen_positions, filtered_data, nr_of_qubits_used
    
    def draw(self, mpl_open = True, term_draw = True, show_idle_wires = True):
        """
        Description
        ------------
        Test function that draws the circuit and opens it in matplotlib if mpl_open == True
        Also prints the circuit in the terminal if term_draw == True
        """
        fig = self.qcircuit.draw('mpl', style="iqp-dark", idle_wires=show_idle_wires)
        if mpl_open == True:
            plt.show()
        if term_draw ==True:
            print(self.qcircuit)
        return fig
    
    def save(self):
        self.history.append(self.qcircuit.copy())
    
    def undo(self):
        if len(self.history) != 0:
            self.qcircuit = self.history.pop()
            self.qcircuit = self.history.pop()
        else:
            self.reset()
        
    def _internal_measure(self, backend = FakeSherbrooke(), optimization_level=2, simulator = True, shots = 1024, service = None):
        """See circuit.measure() for documentation"""
        if service is None and simulator == False:
            raise ValueError("If simulator is False, the service must be given")
        if simulator == False:
            backend = service.least_busy(operational=True, simulator=False)

        self.qcircuit.measure_all()

        pm = generate_preset_pass_manager(backend=backend, optimization_level=optimization_level)
        isa_circuit = pm.run(self.qcircuit)
        pub = (isa_circuit)

        if simulator == False:
            sampler = Sampler(mode = backend)
        else:
            sampler = Sampler(mode = AerSimulator())

        job = sampler.run(pubs=[pub], shots = 1024)
        result = job.result()[0]
        out_with_freq = result.data.meas.get_counts()


        filter = 1 # with a shot of 1000, so if P < 0.1% the measurement is removed
        filtered_data = {value/shots : [index for index, char in enumerate(key[::-1]) if char == '1'] for key, value in out_with_freq.items() if value >= filter}

        return filtered_data
    
    def _internal_efficient_simulation(self, backend = FakeSherbrooke(), optimization_level =2, shots = 1024):
        """Simulate the circuit in a more efficient way by removing idle wires"""
        def count_gates(qc: QuantumCircuit):
            gate_count = {qubit: 0 for qubit in qc.qubits}
            for gate in qc.data:
                for qubit in gate.qubits:
                    gate_count[qubit] += 1
            return gate_count

        def remove_idle_wires(qc: QuantumCircuit):
            # Count gate usage for each qubit
            gate_count = count_gates(qc)

            # Identify active qubits
            active_qubits = [qubit for qubit, count in gate_count.items() if count > 0]

            # Create a new circuit with only active qubits
            qc_out = QuantumCircuit(len(active_qubits), len(active_qubits))

            # Map old qubits to new qubits
            qubit_map = {qubit: i for i, qubit in enumerate(active_qubits)}

            # Copy instructions while updating qubit indices
            for instruction, qargs, cargs in qc.data:
                new_qargs = [qubit_map[q] for q in qargs if q in qubit_map]
                qc_out.append(instruction, new_qargs, cargs)

            return qc_out, [active_qubits[i]._index for i in range(len(active_qubits))]
        
        backend = GenericBackend(self.N)
        transpiled_qc = transpile(self.qcircuit, backend)
        qc, active_qubits = remove_idle_wires(transpiled_qc)
        old_qubits = [transpiled_qc.layout.final_index_layout().index(i) for i in active_qubits]

        qc.measure_all()

        pm = generate_preset_pass_manager(backend=backend, optimization_level=optimization_level)
        isa_circuit = pm.run(qc)
        pub = (isa_circuit)

        sampler = Sampler(mode = AerSimulator())

        job = sampler.run(pubs=[pub], shots = shots)
        result = job.result()[0]
        out_with_freq = result.data.meas.get_counts()

        filter = 2 # with a shot of 1000, so if P < 0.2% the measurement is removed
        filtered_data = {value/shots : [old_qubits[index] for index, char in enumerate(key[::-1]) if char == '1'] for key, value in out_with_freq.items() if value >= filter}
        self.qcircuit = QuantumCircuit(self.N)
        return filtered_data, len(active_qubits)
    
    def _reset(self):
        self.qcircuit = QuantumCircuit(self.N)
    
    def _return_circuit(self):
        return self.qcircuit

if __name__ == "__main__":
    qc = circuit(N=100)
    qc.new_pawn([0,1])
    qc.move([0],[2, 3]) # move green 0 -> 2 & 3\\ 
    qc.merge_move([2], [3,4], [4])
    qc.draw(mpl_open=True)
    qc.measure(efficient=True)

    
