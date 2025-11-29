"""
Engine module for PFF Framework

Contains factorization algorithms and benchmarking logic.
"""

from pff.engine.benchmark import run_benchmark, calculate_pff, scaling_analysis
from pff.engine.utils import generate_semiprime, generate_random_composite

__all__ = [
    "run_benchmark",
    "calculate_pff",
    "scaling_analysis",
    "generate_semiprime",
    "generate_random_composite",
]
