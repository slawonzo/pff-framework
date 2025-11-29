"""
Result Data Structures

Defines data classes for storing benchmark results and PFF calculations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class FactorizationResult:
    """Result of a single factorization attempt"""
    N: int  # Input number
    factors: List[int]  # Prime factors found
    time_seconds: float  # Time taken
    success: bool  # Whether factorization succeeded
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """
    Result of a benchmark run for a specific integer size.
    
    Contains timing statistics and PFF calculation.
    """
    s: int  # Binary size of integers
    algorithm: str  # Algorithm name
    trials: int  # Number of trials performed
    successful_trials: int  # Number of successful factorizations
    
    # Timing statistics (in seconds)
    avg_time: float  # Average time per factorization
    min_time: float  # Minimum time observed
    max_time: float  # Maximum time observed
    std_time: float  # Standard deviation of times
    median_time: float  # Median time
    
    # PFF metric
    pff: float  # Prime Factorization Frequency
    
    # Additional data
    timestamp: datetime = field(default_factory=datetime.now)
    backend: str = "unknown"
    individual_results: List[FactorizationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "s": self.s,
            "algorithm": self.algorithm,
            "trials": self.trials,
            "successful_trials": self.successful_trials,
            "avg_time": self.avg_time,
            "min_time": self.min_time,
            "max_time": self.max_time,
            "std_time": self.std_time,
            "median_time": self.median_time,
            "pff": self.pff,
            "timestamp": self.timestamp.isoformat(),
            "backend": self.backend,
            "metadata": self.metadata,
            "success_rate": self.successful_trials / self.trials if self.trials > 0 else 0.0
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    def summary(self) -> str:
        """Return a human-readable summary"""
        success_rate = (self.successful_trials / self.trials * 100) if self.trials > 0 else 0
        return f"""
PFF Benchmark Results
=====================
Integer Size (s):        {self.s} bits
Algorithm:               {self.algorithm}
Backend:                 {self.backend}
Trials:                  {self.trials}
Successful:              {self.successful_trials} ({success_rate:.1f}%)

Timing Statistics:
------------------
Average Time (Ts):       {self.avg_time:.6f} s
Min Time:                {self.min_time:.6f} s
Max Time:                {self.max_time:.6f} s
Std Deviation:           {self.std_time:.6f} s
Median Time:             {self.median_time:.6f} s

PFF Metric:
-----------
PFF(s={self.s}):         {self.pff:,.0f} factorizations/year

Interpretation: This system could theoretically perform {self.pff:,.0f} 
factorizations of {self.s}-bit integers per year.
        """.strip()


@dataclass
class PFFResult:
    """
    Simple PFF calculation result.
    
    Used for quick PFF calculations from known time-to-solution.
    """
    s: int  # Integer size
    time_per_run: float  # Time per factorization (seconds)
    pff: float  # PFF score
    
    def __str__(self) -> str:
        return f"PFF({self.s}-bit) = {self.pff:,.0f} (Ts = {self.time_per_run:.6f}s)"


@dataclass
class ScalingAnalysisResult:
    """
    Result of a scaling analysis across multiple integer sizes.
    """
    algorithm: str
    sizes: List[int]  # List of s values tested
    results: Dict[int, BenchmarkResult]  # s -> BenchmarkResult mapping
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_pff_series(self) -> Dict[int, float]:
        """Get PFF values for each size"""
        return {s: result.pff for s, result in self.results.items()}
    
    def get_timing_series(self) -> Dict[int, float]:
        """Get average timing for each size"""
        return {s: result.avg_time for s, result in self.results.items()}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "algorithm": self.algorithm,
            "sizes": self.sizes,
            "pff_series": self.get_pff_series(),
            "timing_series": self.get_timing_series(),
            "timestamp": self.timestamp.isoformat(),
            "results": {s: r.to_dict() for s, r in self.results.items()}
        }
    
    def summary(self) -> str:
        """Return summary of scaling analysis"""
        lines = [
            "Scaling Analysis Results",
            "=" * 60,
            f"Algorithm: {self.algorithm}",
            f"Sizes tested: {', '.join(map(str, self.sizes))} bits",
            "",
            "Size (bits) | Avg Time (s) | PFF (per year)",
            "-" * 60
        ]
        
        for s in self.sizes:
            result = self.results[s]
            lines.append(f"{s:11d} | {result.avg_time:12.6f} | {result.pff:15,.0f}")
        
        return "\n".join(lines)
