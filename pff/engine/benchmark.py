"""
Benchmarking Engine for PFF Framework

Implements the core benchmarking logic including:
- PFF calculation
- Time-to-solution measurement
- Statistical analysis
- Scaling analysis
"""

import time
import statistics
from typing import List, Dict, Optional
from datetime import datetime

from pff.core.algorithm import FactorizationAlgorithm
from pff.core.result import BenchmarkResult, PFFResult, FactorizationResult, ScalingAnalysisResult
from pff.engine.utils import generate_random_composite

# Constants
SECONDS_PER_YEAR = 31_536_000  # 365 days * 24 hours * 60 minutes * 60 seconds


def calculate_pff(time_per_run: float, s: Optional[int] = None) -> float:
    """
    Calculate the Prime Factorization Frequency (PFF) metric.
    
    PFF(s) = 31,536,000 / T_s
    
    Where:
        - 31,536,000 = seconds in a year (365 days)
        - T_s = average time-to-solution for size s
    
    Args:
        time_per_run: Average time per factorization in seconds
        s: Optional integer size (for reference only)
        
    Returns:
        PFF score (factorizations per year)
        
    Raises:
        ValueError: If time_per_run <= 0
    """
    if time_per_run <= 0:
        raise ValueError(f"time_per_run must be positive, got {time_per_run}")
    
    pff = SECONDS_PER_YEAR / time_per_run
    
    return pff


def run_benchmark(
    s: int,
    algorithm: FactorizationAlgorithm,
    trials: int = 100,
    semiprime: bool = True,
    verbose: bool = False
) -> BenchmarkResult:
    """
    Run a benchmark for factoring integers of size s bits.
    
    This function:
    1. Generates 'trials' random composite integers of size s
    2. Times how long it takes to factor each one
    3. Calculates statistics and the PFF metric
    
    Args:
        s: Binary size of integers to factor
        algorithm: Factorization algorithm instance
        trials: Number of factorization attempts
        semiprime: If True, generate semiprimes; else any composite
        verbose: If True, print progress
        
    Returns:
        BenchmarkResult containing timing statistics and PFF score
        
    Raises:
        ValueError: If parameters are invalid
    """
    if s < 2:
        raise ValueError(f"Integer size s must be >= 2, got {s}")
    if trials < 1:
        raise ValueError(f"Number of trials must be >= 1, got {trials}")
    
    print(f"\n{'='*60}")
    print(f"Starting PFF Benchmark")
    print(f"{'='*60}")
    print(f"Integer Size (s):     {s} bits")
    print(f"Algorithm:            {algorithm.name}")
    print(f"Backend:              {algorithm.config.backend}")
    print(f"Trials:               {trials}")
    print(f"Number Type:          {'Semiprime' if semiprime else 'Composite'}")
    print(f"{'='*60}\n")
    
    times: List[float] = []
    individual_results: List[FactorizationResult] = []
    successful = 0
    
    for trial in range(trials):
        if verbose and (trial + 1) % 10 == 0:
            print(f"Progress: {trial + 1}/{trials} trials completed...")
        
        # Generate random composite integer
        N = generate_random_composite(s, semiprime=semiprime)
        
        # Time the factorization
        start_time = time.perf_counter()
        
        try:
            factors = algorithm.factor(N)
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            
            # Verify result
            success = algorithm.verify_factors(N, factors)
            
            if success:
                times.append(elapsed)
                successful += 1
            
            # Store individual result
            individual_results.append(FactorizationResult(
                N=N,
                factors=factors,
                time_seconds=elapsed,
                success=success,
                metadata={"trial": trial + 1}
            ))
            
        except Exception as e:
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            
            individual_results.append(FactorizationResult(
                N=N,
                factors=[],
                time_seconds=elapsed,
                success=False,
                error_message=str(e),
                metadata={"trial": trial + 1}
            ))
    
    # Calculate statistics
    if not times:
        raise RuntimeError("No successful factorizations completed")
    
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    median_time = statistics.median(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0.0
    
    # Calculate PFF
    pff = calculate_pff(avg_time, s)
    
    # Create result
    result = BenchmarkResult(
        s=s,
        algorithm=algorithm.name,
        trials=trials,
        successful_trials=successful,
        avg_time=avg_time,
        min_time=min_time,
        max_time=max_time,
        std_time=std_time,
        median_time=median_time,
        pff=pff,
        timestamp=datetime.now(),
        backend=algorithm.config.backend,
        individual_results=individual_results,
        metadata={
            "semiprime": semiprime,
            "algorithm_info": algorithm.get_algorithm_info()
        }
    )
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Benchmark Complete!")
    print(f"{'='*60}")
    print(f"Successful Trials:    {successful}/{trials} ({successful/trials*100:.1f}%)")
    print(f"Average Time (T_s):   {avg_time:.6f} seconds")
    print(f"Min Time:             {min_time:.6f} seconds")
    print(f"Max Time:             {max_time:.6f} seconds")
    print(f"Std Deviation:        {std_time:.6f} seconds")
    print(f"\n{'='*60}")
    print(f"PFF({s}-bit) = {pff:,.0f} factorizations/year")
    print(f"{'='*60}\n")
    
    return result


def scaling_analysis(
    algorithm: FactorizationAlgorithm,
    sizes: List[int],
    trials: int = 100,
    semiprime: bool = True,
    verbose: bool = False
) -> ScalingAnalysisResult:
    """
    Perform scaling analysis across multiple integer sizes.
    
    This runs benchmarks for different values of s to understand
    how the algorithm's performance scales with problem size.
    
    Args:
        algorithm: Factorization algorithm to test
        sizes: List of integer sizes (s values) to test
        trials: Number of trials per size
        semiprime: Whether to use semiprimes
        verbose: Print detailed progress
        
    Returns:
        ScalingAnalysisResult with results for each size
    """
    print(f"\n{'#'*60}")
    print(f"# PFF Scaling Analysis")
    print(f"{'#'*60}")
    print(f"Algorithm: {algorithm.name}")
    print(f"Sizes to test: {sizes}")
    print(f"Trials per size: {trials}")
    print(f"{'#'*60}\n")
    
    results: Dict[int, BenchmarkResult] = {}
    
    for i, s in enumerate(sizes, 1):
        print(f"\n[{i}/{len(sizes)}] Testing size s={s} bits...")
        print(f"{'-'*60}")
        
        result = run_benchmark(
            s=s,
            algorithm=algorithm,
            trials=trials,
            semiprime=semiprime,
            verbose=verbose
        )
        
        results[s] = result
    
    # Create scaling analysis result
    analysis = ScalingAnalysisResult(
        algorithm=algorithm.name,
        sizes=sizes,
        results=results,
        timestamp=datetime.now()
    )
    
    # Print summary
    print(f"\n{'#'*60}")
    print(f"# Scaling Analysis Complete")
    print(f"{'#'*60}\n")
    print(analysis.summary())
    print(f"\n{'#'*60}\n")
    
    return analysis


def quick_pff_estimate(s: int, sample_size: int = 10) -> PFFResult:
    """
    Quick PFF estimation using a small sample.
    
    Useful for rapid testing without full benchmark.
    
    Args:
        s: Integer size in bits
        sample_size: Number of samples (default: 10)
        
    Returns:
        PFFResult with estimated PFF
    """
    from pff.engine.algorithms.classical import ClassicalFactorization
    
    algorithm = ClassicalFactorization()
    result = run_benchmark(s, algorithm, trials=sample_size, verbose=False)
    
    return PFFResult(
        s=s,
        time_per_run=result.avg_time,
        pff=result.pff
    )
