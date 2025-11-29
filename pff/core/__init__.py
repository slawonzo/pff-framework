"""
Core module for PFF Framework

Contains base classes and interfaces for the framework.
"""

from pff.core.algorithm import FactorizationAlgorithm
from pff.core.result import BenchmarkResult, PFFResult

__all__ = ["FactorizationAlgorithm", "BenchmarkResult", "PFFResult"]
