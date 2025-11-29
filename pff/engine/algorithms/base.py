"""
Base implementation class for factorization algorithms.

Provides common functionality for all algorithm implementations.
"""

from typing import List, Dict, Any
from pff.core.algorithm import FactorizationAlgorithm, AlgorithmConfig


class BaseFactorizationAlgorithm(FactorizationAlgorithm):
    """
    Base implementation providing common utilities for all algorithms.
    
    Concrete algorithm implementations should inherit from this class.
    """
    
    def __init__(self, config: AlgorithmConfig = None, algorithm_type: str = "unknown"):
        """
        Initialize base algorithm.
        
        Args:
            config: Algorithm configuration
            algorithm_type: Type of algorithm ('quantum' or 'classical')
        """
        super().__init__(config)
        self.algorithm_type = algorithm_type
        self._version = "0.1.0"
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Get algorithm metadata.
        
        Returns:
            Dictionary with algorithm information
        """
        return {
            "name": self.name,
            "type": self.algorithm_type,
            "backend": self.config.backend,
            "version": self._version,
            "parameters": {
                "shots": self.config.shots,
                "optimization_level": self.config.optimization_level,
                **self.config.additional_params
            }
        }
    
    def factor(self, N: int) -> List[int]:
        """
        Factor a composite integer (to be implemented by subclasses).
        
        Args:
            N: Integer to factor
            
        Returns:
            List of prime factors
        """
        raise NotImplementedError("Subclass must implement factor() method")
