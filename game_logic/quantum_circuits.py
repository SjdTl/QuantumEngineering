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
import qiskit


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
    # Measurement basis constants
    Z_BASIS = "Z"  # {|0>, |1>}, |1> means occupied
    Q_BASIS = "Q"  # {|+q>, |-q>}, |-q> means occupied
    X_BASIS = "X"  # {|+>, |->}, |-> means occupied
    T_BASIS = "T"  # {|+t>, |-t>}, |-t> means occupied

    # Mapping of which player gets measured in which basis based on trigger
    MEASUREMENT_BASIS = {
        ("Red", 1): {"Red": Z_BASIS, "Green": Q_BASIS, "Blue": X_BASIS, "Purple": T_BASIS},
        ("Red", 2): {"Red": Z_BASIS, "Purple": Q_BASIS, "Blue": X_BASIS, "Green": T_BASIS},
        ("Blue", 1): {"Blue": Z_BASIS, "Purple": Q_BASIS, "Red": X_BASIS, "Green": T_BASIS},
        ("Blue", 2): {"Blue": Z_BASIS, "Green": Q_BASIS, "Red": X_BASIS, "Purple": T_BASIS},
        ("Green", 1): {"Green": Z_BASIS, "Red": Q_BASIS, "Purple": X_BASIS, "Blue": T_BASIS},
        ("Green", 2): {"Green": Z_BASIS, "Blue": Q_BASIS, "Purple": X_BASIS, "Red": T_BASIS},
        ("Purple", 1): {"Purple": Z_BASIS, "Blue": Q_BASIS, "Green": X_BASIS, "Red": T_BASIS},
        ("Purple", 2): {"Purple": Z_BASIS, "Red": Q_BASIS, "Green": X_BASIS, "Blue": T_BASIS}
    }

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
        
        # Create superposition with controlled-H
        self.qcircuit.ch(move_from[0], move_to[0])
        # Swap the original state to second target position
        self.qcircuit.swap(move_from[0], move_to[1])
        # Add CX between superposition states
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

    def _apply_measurement_basis(self, qubit: int, basis: str):
        """Apply the appropriate measurement basis transformation gates"""
        if basis == self.Q_BASIS:
            # |+q> = cos(pi/8)|0> + sin(pi/8)|1>
            # |-q> = cos(3pi/8)|0> - sin(3pi/8)|1>
            theta = np.pi/4  # Rotation angle for Q basis
            self.qcircuit.ry(theta, qubit)
        elif basis == self.X_BASIS:
            # |+> = (|0> + |1>)/sqrt(2)
            # |-> = (|0> - |1>)/sqrt(2)
            self.qcircuit.h(qubit)
        elif basis == self.T_BASIS:
            # |+t> = cos(3pi/8)|0> + sin(3pi/8)|1>
            # |-t> = cos(pi/8)|0> - sin(pi/8)|1>
            theta = 3*np.pi/4  # Rotation angle for T basis
            self.qcircuit.ry(theta, qubit)
        # Z basis (default) requires no transformation

    def trigger_measurement(self, trigger_color: str, trigger_pawn: int, occupied_positions: dict):
        """
        Trigger measurement of all qubits based on the triggering pawn
        
        Parameters
        ----------
        trigger_color : str
            Color of the pawn triggering the measurement
        trigger_pawn : int
            Which pawn of the color triggered the measurement (1 or 2)
        occupied_positions : dict
            Dictionary mapping positions to their occupying pawn's color
        
        Returns
        -------
        positions : list
            List of positions where pawns were measured
        filtered_data : dict
            Dictionary of measurement outcomes and their probabilities
        nr_of_qubits_used : int
            Number of qubits used in the measurement
        """
        # Get measurement basis mapping for this trigger
        basis_mapping = self.MEASUREMENT_BASIS[(trigger_color, trigger_pawn)]
        
        # Apply appropriate basis transformation for each occupied position
        for pos, color in occupied_positions.items():
            basis = basis_mapping.get(color, self.Z_BASIS)
            self._apply_measurement_basis(pos, basis)
        
        # Measure all qubits with out_internal_measure=True to get all required return values
        return self.measure(out_internal_measure=True)

    def measure(self, backend = FakeSherbrooke(), optimization_level=2, simulator = True, out_internal_measure=False, shots=1024, efficient = False):
        """Measure the circuit"""
        # Get list of active qubits (qubits with gates applied)
        active_qubits = self._get_active_qubits()
        
        # Debug prints
        print("\n=== Debug Info Before Measurement ===")
        print(f"Active qubits: {active_qubits}")
        print("Original circuit:")
        print(self.qcircuit)
        
        try:
            if efficient == False:
                filtered_data = self._internal_measure(backend=backend, optimization_level=optimization_level, simulator=simulator, shots=shots)
                nr_of_qubits_used = len(active_qubits)
            else:
                filtered_data, nr_of_qubits_used = self._internal_efficient_simulation(backend=backend, optimization_level=optimization_level, shots=shots)
        except Exception as e:
            print(f"\nMeasurement failed with error: {str(e)}")
            print("Falling back to efficient simulation...")
            try:
                filtered_data, nr_of_qubits_used = self._internal_efficient_simulation(backend=backend, optimization_level=optimization_level, shots=shots)
            except Exception as e:
                print(f"Efficient simulation also failed: {str(e)}")
                # Emergency fallback: return current occupied positions
                occupied = self._get_occupied_positions()
                filtered_data = {1.0: occupied} if occupied else {1.0: [0]}
                nr_of_qubits_used = len(occupied) if occupied else 1

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
        
    def _internal_measure(self, backend = FakeSherbrooke(), optimization_level=2, simulator = True, shots = 1024):
        """See circuit.measure() for documentation"""
        
        # Get active qubits
        active_qubits = self._get_active_qubits()
        
        # Create a reduced circuit with only active qubits
        n_qubits = len(active_qubits)
        reduced_circuit = QuantumCircuit(n_qubits, n_qubits)
        
        # Create mapping from original qubit indices to new indices
        qubit_map = {old: new for new, old in enumerate(active_qubits)}
        
        # Copy gates, mapping to new qubit indices
        for gate in self.qcircuit.data:
            # Get new qubit indices for this gate
            new_qargs = [qubit_map[q._index] for q in gate[1]]
            # Skip gates that don't affect active qubits
            if all(idx is not None for idx in new_qargs):
                reduced_circuit.append(gate[0], new_qargs)
        
        # Add measurements for all qubits in reduced circuit
        reduced_circuit.measure_all()
        
        # Transpile and run the reduced circuit
        pm = generate_preset_pass_manager(backend=backend, optimization_level=optimization_level)
        isa_circuit = pm.run(reduced_circuit)
        
        if simulator == False:
            sampler = Sampler(mode = backend)
        else:
            sampler = Sampler(mode = AerSimulator())

        job = sampler.run(pubs=[isa_circuit], shots=shots)
        result = job.result()[0]
        out_with_freq = result.data.meas.get_counts()

        # Filter results and map back to original qubit indices
        filter = 5  # with a shot of 1000, so if P < 0.5% the measurement is removed
        filtered_data = {}
        
        for bitstring, value in out_with_freq.items():
            if value >= filter:
                # Convert bitstring to original qubit indices
                original_positions = []
                for new_idx, bit in enumerate(bitstring[::-1]):
                    if bit == '1':
                        original_positions.append(active_qubits[new_idx])
                filtered_data[value/shots] = original_positions

        return filtered_data
    
    def _internal_efficient_simulation(self, backend = FakeSherbrooke(), optimization_level=2, shots = 1024):
        """Simulate the circuit in a more efficient way by removing idle wires"""
        def count_gates(qc: QuantumCircuit):
            gate_count = {qubit: 0 for qubit in qc.qubits}
            for gate in qc.data:
                for qubit in gate[1]:
                    gate_count[qubit] += 1
            return gate_count

        def remove_idle_wires(qc: QuantumCircuit):
            # Count gate usage for each qubit
            gate_count = count_gates(qc)

            # Identify active qubits
            active_qubits = [qubit for qubit, count in gate_count.items() if count > 0]
            if not active_qubits:  # If no active qubits, return minimal circuit
                qc_out = QuantumCircuit(1)
                return qc_out, [0]

            # Create a new circuit with only active qubits
            qc_out = QuantumCircuit(len(active_qubits))

            # Map old qubits to new qubits
            qubit_map = {qubit: i for i, qubit in enumerate(active_qubits)}

            # Copy instructions while updating qubit indices
            for instruction, qargs, cargs in qc.data:
                new_qargs = [qubit_map[q] for q in qargs if q in qubit_map]
                if new_qargs:  # Only add instruction if it affects active qubits
                    qc_out.append(instruction, new_qargs)

            return qc_out, [q._index for q in active_qubits]
        
        try:
            backend = GenericBackend(self.N)
            transpiled_qc = transpile(self.qcircuit, backend)
            qc, active_qubits = remove_idle_wires(transpiled_qc)
            
            # Add measurements
            qc.measure_all()
            
            # Run simulation
            sampler = Sampler(mode=AerSimulator())
            job = sampler.run(pubs=[qc], shots=shots)
            result = job.result()[0]
            counts = result.data.meas.get_counts()
            
            # Map results back to original qubit indices
            results = {}
            filter_threshold = 5  # Minimum count threshold (with shots=1024, this is ~0.5%)
            for bitstring, count in counts.items():
                if count >= filter_threshold:
                    mapped_positions = [active_qubits[i] for i, bit in enumerate(bitstring[::-1]) if bit == '1']
                    results[count/shots] = mapped_positions
            
            if not results:  # If no results pass the threshold
                results = {1.0: []}
            
            return results, len(active_qubits)
            
        except Exception as e:
            print(f"Efficient simulation failed: {str(e)}")
            # Emergency fallback
            occupied = self._get_occupied_positions()
            return {1.0: occupied} if occupied else {1.0: []}, len(occupied) if occupied else 1
    
    def _reset(self):
        self.qcircuit = QuantumCircuit(self.N)
    
    def _return_circuit(self):
        return self.qcircuit

    def _get_active_qubits(self):
        """
        Returns a list of qubit indices that have gates applied to them
        """
        active_qubits = set()
        for instruction in self.qcircuit.data:
            for qubit in instruction[1]:
                active_qubits.add(qubit._index)
        return sorted(list(active_qubits))

    def _get_occupied_positions(self):
        """
        Returns a list of positions that have X gates applied (representing pawns)
        """
        occupied = []
        for i in range(self.N):
            for gate in self.qcircuit.data:
                if (gate[0].name == 'x' and 
                    isinstance(gate[1][0], qiskit.circuit.Qubit) and 
                    gate[1][0]._index == i):
                    occupied.append(i)
                    break
        return occupied

if __name__ == "__main__":
    qc = circuit(N=100)
    qc.new_pawn([0,1])
    qc.move([0],[2, 3]) # move green 0 -> 2 & 3\\ 
    qc.merge_move([2], [3,4], [4])
    qc.draw(mpl_open=True)
    qc.measure(efficient=True)

    
