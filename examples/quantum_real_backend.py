"""
Real Quantum Backend Example

This example demonstrates how to run Shor's algorithm on a real IBM Quantum backend.

PREREQUISITES:
1. You must have an IBM Quantum account (https://quantum.ibm.com/).
2. You must have saved your API token locally.
   Run this in your terminal once:
   python -c "from qiskit_ibm_runtime import QiskitRuntimeService; QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='YOUR_API_TOKEN')"

WARNING:
- Real quantum hardware has queues and may take time to return results.
- Real hardware has noise, so results may not be 100% accurate (success rate < 100%).
"""

import time
from pff.engine.algorithms.shors import ShorsAlgorithm
from pff.core.algorithm import AlgorithmConfig
from pff.engine.utils import generate_semiprime

def main():
    print("PFF Framework - Real Quantum Backend Example")
    print("=" * 60)
    
    # Check for IBM Quantum credentials
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
        if not QiskitRuntimeService.saved_accounts():
            print("\n❌ No saved IBM Quantum accounts found!")
            print("Please save your account first using (use your venv python):")
            print("C:/Users/sfolwarski/pff-framework/.venv/Scripts/python.exe -c \"from qiskit_ibm_runtime import QiskitRuntimeService; QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='YOUR_API_TOKEN')\"")
            return
    except ImportError:
        print("\n❌ qiskit-ibm-runtime not installed.")
        return

    print("Initializing Shor's Algorithm with IBM Quantum backend...")
    print("(This will select the least busy operational quantum computer)")
    
    try:
        # Initialize with 'ibm_quantum' to use real hardware
        # You can also specify a specific backend name like 'ibm_brisbane'
        # max_iterations=10 gives a higher chance of success on noisy hardware
        config = AlgorithmConfig(backend="ibm_quantum", shots=1024, max_iterations=10)
        algorithm = ShorsAlgorithm(config=config)
        
        print(f"\nSelected Backend: {algorithm.backend.name}")
        print(f"Qubits available: {algorithm.backend.num_qubits}")
        
        # Parameters
        s = 4  # 4-bit integers (N=15)
        # Note: We use N=15 specifically as it's the standard test case
        N = 15
        print(f"\nTarget Integer: {N} (4 bits)")
        print("Running up to 10 trials (max_iterations=10)...")
        
        start_time = time.time()
        
        try:
            factors = algorithm.factor(N)
            duration = time.time() - start_time
            
            print(f"\n✅ Factorization Successful!")
            print(f"Factors: {factors}")
            print(f"Time taken: {duration:.2f} seconds")
            print(f"Verification: {factors[0]} * {factors[1]} = {factors[0] * factors[1]}")
            
        except Exception as e:
            print(f"\n❌ Factorization Failed: {e}")
            
    except Exception as e:
        print(f"\n❌ Error initializing backend: {e}")
        print("Make sure you have access to IBM Quantum services.")

if __name__ == "__main__":
    main()
