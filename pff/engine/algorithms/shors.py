"""
Shor's Algorithm Implementation using IBM Qiskit

Implements quantum integer factorization using Shor's algorithm.
This implementation features:
- Hybrid execution support:
  - Local simulation via Qiskit Aer
  - Real quantum hardware via IBM Quantum Runtime (SamplerV2)
- Modular exponentiation using unitary gates
- Automatic circuit transpilation and optimization
- Detailed circuit statistics logging
"""

from typing import List, Dict, Any, Optional
import math
from fractions import Fraction
import numpy as np

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit_aer import AerSimulator
    from qiskit.circuit.library import QFT
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

from pff.core.algorithm import AlgorithmConfig
from pff.engine.algorithms.base import BaseFactorizationAlgorithm


class ShorsAlgorithm(BaseFactorizationAlgorithm):
    """
    Shor's algorithm for quantum integer factorization.
    
    This implementation uses IBM Qiskit and supports both
    simulator and real quantum hardware backends.
    
    Key Features:
    - Uses Qiskit Runtime Primitives (SamplerV2) for real hardware
    - Falls back to standard backend.run() for local simulators
    - Implements proper modular exponentiation U|y> = |ay mod N>
    """
    
    def __init__(self, config: AlgorithmConfig = None, backend: str = "aer_simulator"):
        """
        Initialize Shor's algorithm.
        
        Args:
            config: Algorithm configuration
            backend: Qiskit backend to use ('aer_simulator', 'ibm_quantum', etc.)
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for Shor's algorithm. Install with: pip install qiskit qiskit-aer")
        
        if config is None:
            config = AlgorithmConfig(backend=backend)
        
        super().__init__(config, algorithm_type="quantum")
        self._name = "Shor's Algorithm (Qiskit)"
        self.backend = self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the Qiskit backend"""
        if self.config.backend == "aer_simulator":
            return AerSimulator()
        elif self.config.backend == "ibm_quantum" or self.config.backend.startswith("ibm_"):
            try:
                from qiskit_ibm_runtime import QiskitRuntimeService
                service = QiskitRuntimeService()
                
                if self.config.backend == "ibm_quantum":
                    # Find least busy real backend
                    print("  Searching for least busy operational backend (this may take a moment)...")
                    backend = service.least_busy(operational=True, simulator=False)
                    print(f"  Found backend: {backend.name}")
                    return backend
                else:
                    # Use specific backend
                    return service.backend(self.config.backend)
            except ImportError:
                raise ImportError("qiskit-ibm-runtime is required for IBM Quantum backends. Install with: pip install qiskit-ibm-runtime")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize IBM Quantum backend: {e}")
        else:
            # For real hardware, users will need to configure IBMQ
            raise NotImplementedError(
                f"Backend {self.config.backend} not yet implemented. "
                "Currently only 'aer_simulator' and 'ibm_quantum' are supported."
            )
    
    def factor(self, N: int) -> List[int]:
        """
        Factor N using Shor's algorithm.
        
        Args:
            N: Composite integer to factor (must be odd and N > 2)
            
        Returns:
            List of two prime factors [p, q] where p * q = N
            
        Raises:
            ValueError: If N is invalid
            RuntimeError: If factorization fails after max attempts
        """
        self.validate_input(N)
        
        # Handle even numbers
        if N % 2 == 0:
            return [2, N // 2]
        
        # Check if N is a perfect power (N = a^b)
        power_factor = self._check_perfect_power(N)
        if power_factor is not None:
            return [power_factor, N // power_factor]
        
        # Main Shor's algorithm loop
        max_attempts = self.config.max_iterations or 10
        print(f"Starting factorization with max_attempts={max_attempts}")
        for attempt in range(max_attempts):
            print(f"Attempt {attempt + 1}/{max_attempts}")
            # Choose random a coprime to N
            a = self._choose_random_a(N)
            
            # Classical GCD check
            gcd = math.gcd(a, N)
            if gcd > 1:
                # Lucky case: a shares a factor with N
                return [gcd, N // gcd]
            
            # Quantum part: Find period r of f(x) = a^x mod N
            r = self._find_period_quantum(a, N)
            
            if r is None or r % 2 != 0:
                continue  # Try again
            
            # Classical post-processing
            factor = self._extract_factors_from_period(a, r, N)
            
            if factor is not None:
                factors = [factor, N // factor]
                if self.verify_factors(N, factors):
                    return sorted(factors)
        
        raise RuntimeError(f"Failed to factor {N} after {max_attempts} attempts")
    
    def _choose_random_a(self, N: int) -> int:
        """Choose a random integer a where 1 < a < N and gcd(a, N) = 1"""
        import random
        max_tries = 100
        for _ in range(max_tries):
            a = random.randint(2, N - 1)
            if math.gcd(a, N) == 1:
                return a
        raise RuntimeError(f"Could not find suitable 'a' for N={N}")
    
    def _check_perfect_power(self, N: int) -> Optional[int]:
        """Check if N = a^b for some a, b > 1"""
        for b in range(2, int(math.log2(N)) + 1):
            a = int(round(N ** (1.0 / b)))
            if a ** b == N:
                return a
        return None
    
    def _find_period_quantum(self, a: int, N: int) -> Optional[int]:
        """
        Find the period r of the function f(x) = a^x mod N using quantum circuit.
        
        This is the core quantum subroutine of Shor's algorithm.
        """
        from qiskit import transpile
        
        # Number of qubits needed
        n_count = 2 * N.bit_length()  # Counting qubits
        
        # Build the quantum circuit
        print(f"  Building circuit for N={N}, a={a}...")
        circuit = self._build_shor_circuit(a, N, n_count)
        
        # Transpile for the backend
        print("  Transpiling...")
        transpiled_circuit = transpile(circuit, self.backend)
        
        # Calculate active qubits (qubits that actually have gates applied)
        active_qubits = set()
        for instruction in transpiled_circuit.data:
            for qubit in instruction.qubits:
                active_qubits.add(qubit)
        n_active = len(active_qubits)
        
        # Log circuit statistics
        print(f"  [Circuit Statistics]")
        print(f"    - Device Size: {transpiled_circuit.num_qubits} qubits")
        print(f"    - Active Qubits: {n_active} qubits")
        print(f"    - Depth: {transpiled_circuit.depth()}")
        print(f"    - Gate Counts: {transpiled_circuit.count_ops()}")
        print(f"    - Shots: {self.config.shots}")
        
        # Execute on backend
        print("  Running simulation...")
        
        counts = {}
        
        # Check if using IBM Quantum Runtime
        is_ibm_backend = False
        try:
            from qiskit_ibm_runtime import IBMBackend
            if isinstance(self.backend, IBMBackend):
                is_ibm_backend = True
        except ImportError:
            pass
            
        if is_ibm_backend:
            from qiskit_ibm_runtime import SamplerV2 as Sampler
            
            # Use SamplerV2 for IBM Quantum backends
            sampler = Sampler(mode=self.backend)
            job = sampler.run([transpiled_circuit], shots=self.config.shots)
            
            print(f"  Job submitted! Job ID: {job.job_id()}")
            print(f"  View status at: https://quantum.ibm.com/jobs/{job.job_id()}")
            print("  Waiting for results (this may take a while due to queue)...")
            
            result = job.result()
            
            # Extract counts from SamplerV2 result
            # result[0].data.classical contains the counts for the 'classical' register
            counts = result[0].data.classical.get_counts()
            
        else:
            # Legacy/Aer execution
            job = self.backend.run(transpiled_circuit, shots=self.config.shots)
            result = job.result()
            counts = result.get_counts()
        
        # Get the most frequent measurement
        if not counts:
            return None
        
        measured_phase = int(max(counts, key=counts.get), 2)
        
        # Convert phase to period using continued fractions
        r = self._phase_to_period(measured_phase, n_count, N, a)
        
        return r
    
    def _find_period_classical(self, a: int, N: int) -> Optional[int]:
        """
        Classical period finding for small N.
        Finds the smallest r > 0 such that a^r ≡ 1 (mod N).
        """
        if math.gcd(a, N) != 1:
            return None
        
        r = 1
        current = a % N
        max_period = N  # Period must be < N
        
        while r < max_period:
            if current == 1:
                return r
            current = (current * a) % N
            r += 1
        
        return None
    
    def _build_shor_circuit(self, a: int, N: int, n_count: int) -> QuantumCircuit:
        """
        Build the quantum circuit for Shor's algorithm.
        
        Args:
            a: Base for modular exponentiation
            N: Number to factor
            n_count: Number of counting qubits
            
        Returns:
            Quantum circuit implementing Shor's algorithm
        """
        # Create quantum registers
        counting_qubits = QuantumRegister(n_count, 'counting')
        auxiliary_qubits = QuantumRegister(N.bit_length(), 'auxiliary')
        classical_bits = ClassicalRegister(n_count, 'classical')
        
        circuit = QuantumCircuit(counting_qubits, auxiliary_qubits, classical_bits)
        
        # Initialize: |0⟩⊗n |1⟩
        circuit.h(counting_qubits)  # Hadamard on counting qubits
        circuit.x(auxiliary_qubits[0])  # Set auxiliary to |1⟩
        
        # Controlled modular exponentiation: U|y⟩ = |ay mod N⟩
        self._add_modular_exponentiation(circuit, counting_qubits, auxiliary_qubits, a, N)
        
        # Inverse QFT on counting qubits (decompose to get basic gates)
        qft_inverse = QFT(n_count, inverse=True).decompose()
        circuit.append(qft_inverse, counting_qubits)
        
        # Measure counting qubits
        circuit.measure(counting_qubits, classical_bits)
        
        return circuit
    
    def _add_modular_exponentiation(self, circuit, counting_qubits, auxiliary_qubits, a, N):
        """
        Add controlled modular exponentiation gates to the circuit.
        
        This implements controlled U^(2^j) where U|y⟩ = |ay mod N⟩
        using a simplified approach suitable for small N.
        """
        n_count = len(counting_qubits)
        
        # For each counting qubit, apply controlled-U^(2^j) operation
        for j in range(n_count):
            # Calculate a^(2^j) mod N
            power = pow(a, 2**j, N)
            
            # Apply controlled multiplication by power
            # This is a simplified classical-controlled approach
            # For larger N, you'd need proper quantum modular arithmetic
            if power != 1:  # Only apply if not identity
                self._apply_controlled_modular_mult(
                    circuit, 
                    counting_qubits[j], 
                    auxiliary_qubits, 
                    power, 
                    N
                )
    
    def _apply_controlled_modular_mult(self, circuit, control_qubit, target_qubits, multiplier, N):
        """
        Apply controlled modular multiplication by multiplier (mod N).
        
        This uses a unitary matrix approach which is suitable for simulation
        of small N, but not scalable to large N.
        """
        from qiskit.circuit.library import UnitaryGate
        
        num_target_qubits = len(target_qubits)
        dim = 2 ** num_target_qubits
        
        # Create the unitary matrix for U|y> = |(y * multiplier) mod N>
        # Note: We must handle y >= N carefully.
        # Since we start with |1> and multiply by a (coprime to N),
        # we only care about states y < N where gcd(y, N) = 1.
        # For other states, we can just map them to themselves (identity)
        # to ensure unitarity.
        
        matrix = np.zeros((dim, dim), dtype=complex)
        
        for y in range(dim):
            if y < N and math.gcd(y, N) == 1:
                # Valid state in the multiplicative group
                result = (y * multiplier) % N
                matrix[result, y] = 1
            else:
                # Identity for states >= N or not coprime
                # This is a simplification; strictly we need a permutation
                # of all basis states.
                # If y is not in the group generated by 'a' acting on 1,
                # it doesn't matter for the algorithm outcome, but we need a valid unitary.
                
                # Better approach: Just map y -> (y * multiplier) % N is not necessarily
                # a permutation if we include y >= N.
                
                # Let's use a simpler approach:
                # The map y -> (y * multiplier) % N is a permutation on the set
                # {y | 0 <= y < N, gcd(y, N) = 1}.
                # We need to extend this to a permutation on {0, ..., 2^n - 1}.
                
                # If we just map y -> y for "invalid" states, we might have collisions
                # if (y * multiplier) % N maps to an "invalid" state (impossible if y < N)
                # or if an "invalid" state maps to something.
                
                # Since 'multiplier' is coprime to N, the map y -> (y * multiplier) % N
                # is a bijection on Z_N*.
                
                if y < N:
                     # If gcd(y, N) != 1, we can still multiply?
                     # If gcd(y, N) != 1, then gcd(y*multiplier, N) != 1.
                     # So it maps non-coprimes to non-coprimes.
                     # But is it 1-to-1? Yes, if multiplier is coprime to N.
                     result = (y * multiplier) % N
                     matrix[result, y] = 1
                else:
                    # For y >= N, just map to itself
                    matrix[y, y] = 1

        # Create the controlled gate
        # UnitaryGate(matrix).control(1)
        u_gate = UnitaryGate(matrix, label=f"*{multiplier} mod {N}")
        cu_gate = u_gate.control(1)
        
        # Apply to circuit
        circuit.append(cu_gate, [control_qubit] + list(target_qubits))
    
    def _phase_to_period(self, phase: int, n_count: int, N: int, a: int) -> Optional[int]:
        """
        Convert measured phase to period using continued fractions.
        
        Args:
            phase: Measured phase value
            n_count: Number of counting qubits
            N: Number being factored
            a: Base used in modular exponentiation
            
        Returns:
            Period r, or None if not found
        """
        if phase == 0:
            return None
        
        # Convert to fraction
        frac = Fraction(phase, 2 ** n_count).limit_denominator(N)
        
        r = frac.denominator
        
        # Verify that r is a valid period
        if r > 0 and pow(a, r, N) == 1:
            return r
        
        return None
    
    def _extract_factors_from_period(self, a: int, r: int, N: int) -> Optional[int]:
        """
        Extract factors from the period r.
        
        Args:
            a: Base used in period finding
            r: Period found
            N: Number to factor
            
        Returns:
            A non-trivial factor of N, or None if not found
        """
        if r % 2 != 0:
            return None
        
        # Compute gcd(a^(r/2) ± 1, N)
        x = pow(a, r // 2, N)
        
        factor1 = math.gcd(x - 1, N)
        factor2 = math.gcd(x + 1, N)
        
        for factor in [factor1, factor2]:
            if 1 < factor < N:
                return factor
        
        return None
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get algorithm information"""
        info = super().get_algorithm_info()
        info.update({
            "quantum_framework": "Qiskit",
            "backend_type": self.config.backend,
            "shots": self.config.shots,
        })
        return info
