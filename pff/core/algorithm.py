"""
Base Algorithm Interface

Defines the abstract interface that all factorization algorithms must implement.
This enables the pluggable architecture of the PFF framework.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AlgorithmConfig:
    """Configuration for factorization algorithms"""
    backend: str = "aer_simulator"
    shots: int = 1024
    optimization_level: int = 1
    max_iterations: Optional[int] = None
    additional_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}


class FactorizationAlgorithm(ABC):
    """
    Abstract base class for all factorization algorithms.
    
    All algorithms (quantum or classical) must inherit from this class
    and implement the factor() method.
    """
    
    def __init__(self, config: Optional[AlgorithmConfig] = None):
        """
        Initialize the algorithm.
        
        Args:
            config: Algorithm configuration parameters
        """
        self.config = config or AlgorithmConfig()
        self._name = self.__class__.__name__
        
    @property
    def name(self) -> str:
        """Return the algorithm name"""
        return self._name
    
    @abstractmethod
    def factor(self, N: int) -> List[int]:
        """
        Factor a composite integer N into its prime factors.
        
        Args:
            N: The composite integer to factor (must be > 1)
            
        Returns:
            List of prime factors. For a semiprime N = p * q, returns [p, q]
            
        Raises:
            ValueError: If N < 2 or N is prime
            RuntimeError: If factorization fails
        """
        pass
    
    @abstractmethod
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Get metadata about the algorithm.
        
        Returns:
            Dictionary containing:
                - name: Algorithm name
                - type: 'quantum' or 'classical'
                - backend: Backend being used
                - version: Algorithm version
                - parameters: Current configuration
        """
        pass
    
    def validate_input(self, N: int) -> None:
        """
        Validate input for factorization.
        
        Args:
            N: Integer to validate
            
        Raises:
            ValueError: If N is invalid for factorization
        """
        if N < 2:
            raise ValueError(f"N must be >= 2, got {N}")
        if N == 2:
            raise ValueError("N=2 is prime, cannot factor")
        if self._is_prime(N):
            raise ValueError(f"N={N} is prime, cannot factor")
    
    @staticmethod
    def _is_prime(n: int) -> bool:
        """Simple primality test"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def verify_factors(self, N: int, factors: List[int]) -> bool:
        """
        Verify that the factors are correct.
        
        Args:
            N: Original number
            factors: List of factors
            
        Returns:
            True if factors are valid and their product equals N
        """
        if not factors:
            return False
        
        # Check product
        product = 1
        for f in factors:
            product *= f
        
        if product != N:
            return False
        
        # Check all factors are prime
        for f in factors:
            if not self._is_prime(f):
                return False
        
        return True
    
    def __str__(self) -> str:
        return f"{self.name}(backend={self.config.backend})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(config={self.config})"
