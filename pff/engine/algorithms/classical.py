"""
Classical Factorization Algorithm

Implements classical integer factorization for baseline comparison.
Uses trial division and Pollard's rho algorithm.
"""

from typing import List, Dict, Any
import math
from pff.core.algorithm import AlgorithmConfig
from pff.engine.algorithms.base import BaseFactorizationAlgorithm


class ClassicalFactorization(BaseFactorizationAlgorithm):
    """
    Classical factorization algorithm using trial division and Pollard's rho.
    
    This serves as a baseline for comparing against quantum algorithms.
    """
    
    def __init__(self, config: AlgorithmConfig = None):
        """Initialize classical factorization algorithm"""
        super().__init__(config, algorithm_type="classical")
        self._name = "Classical Factorization"
    
    def factor(self, N: int) -> List[int]:
        """
        Factor N using classical methods.
        
        Args:
            N: Composite integer to factor
            
        Returns:
            List of two prime factors [p, q] where p * q = N
            
        Raises:
            ValueError: If N is invalid
            RuntimeError: If factorization fails
        """
        self.validate_input(N)
        
        # For small N, use trial division
        if N < 1000000:
            factors = self._trial_division(N)
        else:
            # For larger N, use Pollard's rho
            factors = self._pollards_rho(N)
        
        # Verify the result
        if not self.verify_factors(N, factors):
            raise RuntimeError(f"Failed to factor {N} correctly")
        
        return sorted(factors)
    
    def _trial_division(self, N: int) -> List[int]:
        """
        Factor N using trial division.
        
        Args:
            N: Number to factor
            
        Returns:
            List of prime factors
        """
        factors = []
        
        # Check for factor of 2
        while N % 2 == 0:
            factors.append(2)
            N //= 2
        
        # Check odd factors up to sqrt(N)
        i = 3
        while i * i <= N:
            while N % i == 0:
                factors.append(i)
                N //= i
            i += 2
        
        # If N is still greater than 1, it's a prime factor
        if N > 1:
            factors.append(N)
        
        return factors
    
    def _pollards_rho(self, N: int) -> List[int]:
        """
        Factor N using Pollard's rho algorithm.
        
        Args:
            N: Number to factor
            
        Returns:
            List of prime factors
        """
        if N % 2 == 0:
            return [2] + self._pollards_rho(N // 2)
        
        # Function for Pollard's rho
        def g(x):
            return (x * x + 1) % N
        
        x, y, d = 2, 2, 1
        
        while d == 1:
            x = g(x)
            y = g(g(y))
            d = math.gcd(abs(x - y), N)
        
        if d != N:
            # Found a non-trivial factor
            factor1 = d
            factor2 = N // d
            
            # Recursively factor if needed
            factors = []
            if self._is_prime(factor1):
                factors.append(factor1)
            else:
                factors.extend(self._pollards_rho(factor1))
            
            if self._is_prime(factor2):
                factors.append(factor2)
            else:
                factors.extend(self._pollards_rho(factor2))
            
            return factors
        else:
            # Fallback to trial division
            return self._trial_division(N)
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get algorithm information"""
        info = super().get_algorithm_info()
        info["method"] = "Trial Division / Pollard's Rho"
        return info
