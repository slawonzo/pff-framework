"""
Pydantic Models for API Request/Response

Defines data validation schemas for the REST API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class CalculatePFFRequest(BaseModel):
    """Request model for PFF calculation"""
    s: int = Field(..., ge=2, le=20, description="Binary size of integers to factor")
    algorithm: str = Field(..., description="Algorithm to use: 'shors' or 'classical'")
    trials: int = Field(100, ge=1, le=1000, description="Number of trials to run")
    backend: str = Field("aer_simulator", description="Quantum backend to use")
    semiprime: bool = Field(True, description="Generate semiprimes vs any composite")
    
    class Config:
        json_schema_extra = {
            "example": {
                "s": 6,
                "algorithm": "classical",
                "trials": 50,
                "backend": "aer_simulator",
                "semiprime": True
            }
        }


class PFFResponse(BaseModel):
    """Response model for PFF calculation"""
    s: int
    algorithm: str
    backend: str
    trials: int
    successful_trials: int
    avg_time: float
    min_time: float
    max_time: float
    std_time: float
    median_time: float
    pff: float
    timestamp: datetime
    success_rate: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "s": 6,
                "algorithm": "classical",
                "backend": "aer_simulator",
                "trials": 50,
                "successful_trials": 50,
                "avg_time": 0.000123,
                "min_time": 0.000098,
                "max_time": 0.000201,
                "std_time": 0.000031,
                "median_time": 0.000119,
                "pff": 256410256.41,
                "timestamp": "2025-11-26T12:00:00",
                "success_rate": 1.0
            }
        }


class ScalingAnalysisRequest(BaseModel):
    """Request model for scaling analysis"""
    algorithm: str = Field(..., description="Algorithm to use")
    sizes: List[int] = Field(..., description="List of integer sizes to test")
    trials: int = Field(50, ge=1, le=500, description="Trials per size")
    backend: str = Field("aer_simulator", description="Backend to use")
    
    class Config:
        json_schema_extra = {
            "example": {
                "algorithm": "classical",
                "sizes": [4, 6, 8, 10],
                "trials": 25,
                "backend": "aer_simulator"
            }
        }


class ScalingAnalysisResponse(BaseModel):
    """Response model for scaling analysis"""
    algorithm: str
    sizes: List[int]
    pff_series: Dict[str, float]  # String keys for JSON compatibility
    timing_series: Dict[str, float]
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "algorithm": "classical",
                "sizes": [4, 6, 8],
                "pff_series": {
                    "4": 500000000.0,
                    "6": 250000000.0,
                    "8": 100000000.0
                },
                "timing_series": {
                    "4": 0.000063,
                    "6": 0.000126,
                    "8": 0.000315
                },
                "timestamp": "2025-11-26T12:00:00"
            }
        }


class AlgorithmInfo(BaseModel):
    """Information about an available algorithm"""
    name: str
    type: str  # 'quantum' or 'classical'
    description: str
    supported_backends: List[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    qiskit_available: bool


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
