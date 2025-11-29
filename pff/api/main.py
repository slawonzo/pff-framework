"""
FastAPI Application - Main Entry Point

Provides REST API endpoints for the PFF Framework.

Endpoints:
- POST /calculate-pff: Calculate PFF for a specific integer size
- POST /scaling-analysis: Run scaling analysis across multiple sizes
- GET /algorithms: List available algorithms
- GET /health: Health check

To run:
    uvicorn pff.api.main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List

from pff.api.models import (
    CalculatePFFRequest,
    PFFResponse,
    ScalingAnalysisRequest,
    ScalingAnalysisResponse,
    AlgorithmInfo,
    HealthResponse,
    ErrorResponse
)
from pff.engine.benchmark import run_benchmark, scaling_analysis
from pff.engine.algorithms.classical import ClassicalFactorization
from pff.core.algorithm import AlgorithmConfig
from pff import __version__

# Check if Qiskit is available
try:
    from pff.engine.algorithms.shors import ShorsAlgorithm
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="PFF Framework API",
    description="Prime Factorization Frequency (PFF) Benchmarking API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_algorithm(algorithm_name: str, backend: str):
    """
    Get algorithm instance by name.
    
    Args:
        algorithm_name: Name of the algorithm ('classical' or 'shors')
        backend: Backend to use
        
    Returns:
        Algorithm instance
        
    Raises:
        HTTPException: If algorithm not found or not available
    """
    algorithm_name = algorithm_name.lower()
    
    if algorithm_name == "classical":
        config = AlgorithmConfig(backend=backend)
        return ClassicalFactorization(config)
    
    elif algorithm_name == "shors":
        if not QISKIT_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Shor's algorithm requires Qiskit. Install with: pip install qiskit qiskit-aer"
            )
        config = AlgorithmConfig(backend=backend)
        return ShorsAlgorithm(config)
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown algorithm: {algorithm_name}. Available: 'classical', 'shors'"
        )


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "PFF Framework API",
        "version": __version__,
        "description": "Prime Factorization Frequency Benchmarking API",
        "docs": "/docs",
        "endpoints": {
            "calculate_pff": "POST /calculate-pff",
            "scaling_analysis": "POST /scaling-analysis",
            "algorithms": "GET /algorithms",
            "health": "GET /health"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint.
    
    Returns system status and availability of components.
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(),
        qiskit_available=QISKIT_AVAILABLE
    )


@app.get("/algorithms", response_model=List[AlgorithmInfo], tags=["Algorithms"])
async def list_algorithms():
    """
    List all available factorization algorithms.
    
    Returns information about each algorithm including supported backends.
    """
    algorithms = [
        AlgorithmInfo(
            name="Classical Factorization",
            type="classical",
            description="Classical factorization using trial division and Pollard's rho",
            supported_backends=["cpu"]
        )
    ]
    
    if QISKIT_AVAILABLE:
        algorithms.append(
            AlgorithmInfo(
                name="Shor's Algorithm",
                type="quantum",
                description="Quantum factorization using Shor's algorithm on Qiskit",
                supported_backends=["aer_simulator", "ibm_quantum"]
            )
        )
    
    return algorithms


@app.post("/calculate-pff", response_model=PFFResponse, tags=["Benchmarking"])
async def calculate_pff_endpoint(request: CalculatePFFRequest):
    """
    Calculate PFF for a specific integer size.
    
    Runs a benchmark with the specified parameters and returns
    timing statistics and the PFF metric.
    
    Args:
        request: PFF calculation parameters
        
    Returns:
        PFF calculation results
        
    Raises:
        HTTPException: If calculation fails
    """
    try:
        # Get algorithm instance
        algorithm = get_algorithm(request.algorithm, request.backend)
        
        # Run benchmark
        result = run_benchmark(
            s=request.s,
            algorithm=algorithm,
            trials=request.trials,
            semiprime=request.semiprime,
            verbose=False
        )
        
        # Convert to response model
        return PFFResponse(
            s=result.s,
            algorithm=result.algorithm,
            backend=result.backend,
            trials=result.trials,
            successful_trials=result.successful_trials,
            avg_time=result.avg_time,
            min_time=result.min_time,
            max_time=result.max_time,
            std_time=result.std_time,
            median_time=result.median_time,
            pff=result.pff,
            timestamp=result.timestamp,
            success_rate=result.successful_trials / result.trials
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark failed: {str(e)}")


@app.post("/scaling-analysis", response_model=ScalingAnalysisResponse, tags=["Benchmarking"])
async def scaling_analysis_endpoint(request: ScalingAnalysisRequest):
    """
    Perform scaling analysis across multiple integer sizes.
    
    Tests the algorithm with different integer sizes to understand
    how performance scales with problem size.
    
    Args:
        request: Scaling analysis parameters
        
    Returns:
        Scaling analysis results
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Get algorithm instance
        algorithm = get_algorithm(request.algorithm, request.backend)
        
        # Run scaling analysis
        result = scaling_analysis(
            algorithm=algorithm,
            sizes=request.sizes,
            trials=request.trials,
            verbose=False
        )
        
        # Convert to response model (convert int keys to strings for JSON)
        return ScalingAnalysisResponse(
            algorithm=result.algorithm,
            sizes=result.sizes,
            pff_series={str(k): v for k, v in result.get_pff_series().items()},
            timing_series={str(k): v for k, v in result.get_timing_series().items()},
            timestamp=result.timestamp
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scaling analysis failed: {str(e)}")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return ErrorResponse(
        error=exc.detail,
        detail=None,
        timestamp=datetime.now()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
