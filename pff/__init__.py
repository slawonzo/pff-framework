"""
PFF Framework - Prime Factorization Frequency Calculator

A comprehensive framework for benchmarking quantum and classical 
factorization algorithms using the PFF metric.
"""

__version__ = "0.1.0"
__author__ = "Slawomir Folwarski"

from pff.core.algorithm import FactorizationAlgorithm
from pff.core.result import BenchmarkResult, PFFResult
from pff.engine.benchmark import run_benchmark, calculate_pff, scaling_analysis

__all__ = [
    "FactorizationAlgorithm",
    "BenchmarkResult",
    "PFFResult",
    "run_benchmark",
    "calculate_pff",
    "scaling_analysis",
]
