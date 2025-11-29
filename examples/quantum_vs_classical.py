"""
Quantum vs Classical Comparison

This example compares Shor's algorithm (quantum) with
classical factorization on the same set of integers.

Note: Requires Qiskit to be installed.
"""

from pff.engine.algorithms.classical import ClassicalFactorization
from pff.engine.benchmark import run_benchmark

# Try to import Shor's algorithm
try:
    from pff.engine.algorithms.shors import ShorsAlgorithm
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Warning: Qiskit not available. Install with: pip install qiskit qiskit-aer")

def main():
    print("PFF Framework - Quantum vs Classical Comparison")
    print("=" * 60)
    
    # Parameters
    s = 4  # 4-bit integers (runs in ~1s on simulator)
    trials = 5
    
    print(f"Integer size: {s} bits")
    print(f"Trials: {trials}\n")
    
    # Classical benchmark
    print("Running CLASSICAL benchmark...")
    classical_algo = ClassicalFactorization()
    classical_result = run_benchmark(
        s=s,
        algorithm=classical_algo,
        trials=trials,
        verbose=False
    )
    
    # Quantum benchmark (if available)
    if QISKIT_AVAILABLE:
        print("\nRunning QUANTUM benchmark (Shor's algorithm)...")
        quantum_algo = ShorsAlgorithm()
        quantum_result = run_benchmark(
            s=s,
            algorithm=quantum_algo,
            trials=trials,
            verbose=False
        )
    
        # Comparison
        print(f"\n{'='*60}")
        print("COMPARISON RESULTS")
        print(f"{'='*60}")
        print(f"\n{'Metric':<30} {'Classical':<20} {'Quantum (Shor)':<20}")
        print(f"{'-'*70}")
        print(f"{'Average Time (ms)':<30} {classical_result.avg_time*1000:>18.6f}  {quantum_result.avg_time*1000:>18.6f}")
        print(f"{'PFF Score':<30} {classical_result.pff:>18,.0f}  {quantum_result.pff:>18,.0f}")
        print(f"{'Success Rate':<30} {classical_result.successful_trials/classical_result.trials*100:>17.1f}%  {quantum_result.successful_trials/quantum_result.trials*100:>17.1f}%")
        
        # Speedup
        speedup = classical_result.avg_time / quantum_result.avg_time
        print(f"\nQuantum Speedup: {speedup:.2f}x")
    
    else:
        print(f"\n{classical_result.summary()}")
        print("\n⚠️ Quantum comparison not available (Qiskit not installed)")

if __name__ == "__main__":
    main()
