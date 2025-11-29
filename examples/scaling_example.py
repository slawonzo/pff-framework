"""
Scaling Analysis Example

This example demonstrates how to run a scaling analysis
across multiple integer sizes to understand performance characteristics.
"""

from pff.engine.algorithms.classical import ClassicalFactorization
from pff.engine.benchmark import scaling_analysis

def main():
    print("PFF Framework - Scaling Analysis Example")
    print("=" * 60)
    
    # Create algorithm instance
    algorithm = ClassicalFactorization()
    
    # Define sizes to test
    sizes = [4, 6, 8, 10, 12]
    trials_per_size = 25
    
    print(f"Algorithm: {algorithm.name}")
    print(f"Sizes to test: {sizes}")
    print(f"Trials per size: {trials_per_size}")
    
    # Run scaling analysis
    print("\nStarting scaling analysis...")
    result = scaling_analysis(
        algorithm=algorithm,
        sizes=sizes,
        trials=trials_per_size,
        verbose=True
    )
    
    # Display summary
    print(f"\n{result.summary()}")
    
    # Save to JSON
    import json
    with open("scaling_results.json", "w") as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"\nResults saved to scaling_results.json")

if __name__ == "__main__":
    main()
