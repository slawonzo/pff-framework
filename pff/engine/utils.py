"""
Utility functions for number generation and verification.

Provides functions to generate random composite integers and semiprimes
for benchmarking purposes.
"""

import random
from typing import List, Tuple
import math


def is_prime(n: int) -> bool:
    """
    Check if a number is prime using trial division.
    
    Args:
        n: Number to check
        
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Check odd divisors up to sqrt(n)
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    
    return True


def generate_prime(bits: int) -> int:
    """
    Generate a random prime number of specified bit length.
    
    Args:
        bits: Desired bit length of the prime
        
    Returns:
        A random prime number of the specified bit length
    """
    if bits < 2:
        raise ValueError("Bit length must be at least 2")
    
    min_val = 2 ** (bits - 1)
    max_val = 2 ** bits - 1
    
    max_attempts = 10000
    for _ in range(max_attempts):
        candidate = random.randint(min_val, max_val)
        if candidate % 2 == 0:
            candidate += 1
        
        if is_prime(candidate):
            return candidate
    
    raise RuntimeError(f"Could not generate {bits}-bit prime after {max_attempts} attempts")


def generate_semiprime(s: int) -> Tuple[int, int, int]:
    """
    Generate a random semiprime (product of two primes) of size s bits.
    
    A semiprime N = p * q where p and q are prime numbers.
    
    Args:
        s: Target bit length of the semiprime
        
    Returns:
        Tuple of (N, p, q) where N = p * q
        
    Raises:
        ValueError: If s < 4 (minimum for meaningful semiprimes)
    """
    if s < 4:
        raise ValueError("Semiprime size must be at least 4 bits")
    
    # For a semiprime of s bits, we need p and q such that:
    # 2^(s-1) <= p * q < 2^s
    # A good approach: make p and q roughly equal in size (balanced semiprime)
    
    bits_p = s // 2
    
    max_attempts = 1000
    for _ in range(max_attempts):
        p = generate_prime(bits_p)
        
        # Try q with size s - bits_p or s - bits_p + 1 to ensure we cover the range
        # For small s, we might need slightly larger q to reach s bits
        bits_q_options = [s - bits_p]
        # Only add larger option if it doesn't make q larger than p (roughly) 
        # or if necessary. Actually just trying both is fine.
        if s - bits_p + 1 < s: 
             bits_q_options.append(s - bits_p + 1)
             
        bits_q = random.choice(bits_q_options)
        try:
            q = generate_prime(bits_q)
        except RuntimeError:
            continue
        
        # Ensure p != q
        if q == p:
            continue
        
        N = p * q
        
        # Check if N has the correct bit length
        if N.bit_length() == s:
            return N, p, q
    
    raise RuntimeError(f"Could not generate {s}-bit semiprime after {max_attempts} attempts")


def generate_random_composite(s: int, semiprime: bool = True) -> int:
    """
    Generate a random composite integer of size s bits.
    
    Args:
        s: Bit length of the composite integer
        semiprime: If True, generate a semiprime (product of two primes)
                  If False, generate any composite number
        
    Returns:
        Random composite integer of s bits
    """
    if semiprime:
        N, _, _ = generate_semiprime(s)
        return N
    else:
        # Generate any composite number
        min_val = 2 ** (s - 1)
        max_val = 2 ** s - 1
        
        max_attempts = 1000
        for _ in range(max_attempts):
            N = random.randint(min_val, max_val)
            if not is_prime(N) and N > 1:
                return N
        
        raise RuntimeError(f"Could not generate {s}-bit composite after {max_attempts} attempts")


def verify_semiprime(N: int, p: int, q: int) -> bool:
    """
    Verify that N = p * q and both p and q are prime.
    
    Args:
        N: The semiprime
        p: First factor
        q: Second factor
        
    Returns:
        True if N is a valid semiprime with factors p and q
    """
    if p * q != N:
        return False
    
    if not is_prime(p) or not is_prime(q):
        return False
    
    return True


def get_bit_length(N: int) -> int:
    """
    Get the bit length of an integer.
    
    Args:
        N: Integer
        
    Returns:
        Number of bits needed to represent N
    """
    return N.bit_length()


def format_number(N: int) -> str:
    """
    Format a number with thousand separators for readability.
    
    Args:
        N: Number to format
        
    Returns:
        Formatted string
    """
    return f"{N:,}"
