"""
Basic example: Calculate PFF for a single integer size

This example demonstrates how to:
1. Create an algorithm instance
2. Run a basic benchmark
3. Display the PFF result
"""

from pff.engine.algorithms.classical import ClassicalFactorization
from pff.engine.benchmark import run_benchmark

def main():
    print("PFF Framework - Basic Example")
    print("=" * 60)
    
    # Create algorithm instance
    algorithm = ClassicalFactorization()
    print(f"Algorithm: {algorithm.name}")
    print(f"Type: {algorithm.algorithm_type}")
    
    # Set parameters
    s = 8  # 8-bit integers
    trials = 50  # 50 factorization attempts
    
    print(f"\nParameters:")
    print(f"  Integer size: {s} bits")
    print(f"  Trials: {trials}")
    
    # Run benchmark
    print(f"\nRunning benchmark...")
    result = run_benchmark(s=s, algorithm=algorithm, trials=trials, verbose=True)
    
    # Display results
    print(f"\n{result.summary()}")
    
    # Save results to JSON
    with open("pff_result.json", "w") as f:
        f.write(result.to_json())
    print(f"\nResults saved to pff_result.json")

if __name__ == "__main__":
    main()
