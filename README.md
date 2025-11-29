# PFF Framework: Prime Factorization Frequency Calculator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

The **Prime Factorization Frequency (PFF) Framework** is a comprehensive benchmarking tool designed to empirically measure the computational efficiency of quantum and classical factorization algorithms. This software serves as the reference implementation for the novel PFF metric proposed in the doctoral dissertation: *"Comparative Analysis of Various Techniques for the Measurement of Quantum System Quality and Size."*

## What is PFF?

The **Prime Factorization Frequency (PFF)** is defined as:

$$PFF(s) = \frac{31,536,000}{T_s}$$

Where:
- **s** = Binary size of the composite integer to be factored
- **T_s** = Average time-to-solution (in seconds) for factoring integers of size s
- **31,536,000** = Number of seconds in a year (365 days)

**Interpretation**: PFF represents how many factorizations of size $s$ could theoretically be performed in one year.

## Key Features

- 🔌 **Pluggable Architecture**: Easy integration of classical and quantum factorization algorithms
- 📊 **Comprehensive Benchmarking**: Automated testing with configurable trials and time constraints
- 🚀 **Multiple Backends**: 
  - Local simulation via Qiskit Aer
  - Real quantum hardware via IBM Quantum Runtime (using `SamplerV2` primitives)
- 📈 **Performance Visualization**: Web-based dashboard for real-time metrics and scaling analysis
- 🧪 **Rigorous Testing**: Built-in validation and verification of factorization results
- 🌐 **API-First Design**: RESTful API for integration with other tools

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                      │
│  - Interactive UI for configuration                          │
│  - Real-time PFF metrics visualization                       │
│  - Scaling charts and performance analysis                   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────────┐
│                   Backend API (FastAPI)                      │
│  - POST /calculate-pff                                       │
│  - GET /algorithms                                           │
│  - GET /results/{id}                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  PFF Engine (Core Framework)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Plugin System                                       │   │
│  │  - Shor's Algorithm (Qiskit)                        │   │
│  │  - Classical Factorization                          │   │
│  │  - [Future: QAOA, Variational Algorithms]          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Benchmarking Engine                                 │   │
│  │  - Random semiprime generation                      │   │
│  │  - High-resolution timing                           │   │
│  │  - Statistical analysis                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
pff-framework/
├── pff/                          # Core framework package
│   ├── core/                     # Framework core
│   │   ├── algorithm.py          # Base algorithm interface
│   │   ├── plugin_manager.py    # Plugin discovery system
│   │   └── result.py            # Result data structures
│   ├── engine/                   # Quantum/Classical engine
│   │   ├── algorithms/          # Algorithm implementations
│   │   │   ├── base.py          # Abstract base class
│   │   │   ├── shors.py         # Shor's algorithm (Qiskit)
│   │   │   └── classical.py     # Classical factorization
│   │   ├── benchmark.py         # Benchmarking logic
│   │   └── utils.py             # Number generation helpers
│   ├── api/                      # FastAPI backend
│   │   ├── main.py              # API entry point
│   │   ├── models.py            # Pydantic models
│   │   └── routes.py            # REST endpoints
│   └── ui/                       # Streamlit frontend
│       └── app.py               # Dashboard
├── tests/                        # Test suite
├── examples/                     # Usage examples
│   ├── basic_example.py         # Simple usage
│   ├── quantum_vs_classical.py  # Comparison benchmark
│   └── quantum_real_backend.py  # Real IBM Quantum hardware example
├── docs/                         # Documentation
├── results/                      # Benchmark results
├── requirements.txt
└── setup.py
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/slawonzo/pff-framework.git
cd pff-framework

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e ".[dev,api,ui]"
```

## Quick Start

### 1. Run a Simple Benchmark

```python
from pff.engine.algorithms.shors import ShorsAlgorithm
from pff.engine.benchmark import run_benchmark

# Create algorithm instance
algorithm = ShorsAlgorithm(backend='aer_simulator')

# Run benchmark for 4-bit integers, 100 trials
results = run_benchmark(s=4, algorithm=algorithm, trials=100)

print(f"PFF Score: {results.pff:,.0f}")
print(f"Average Time: {results.avg_time:.6f}s")
```

### 2. Launch the Web Dashboard

```bash
# Start the FastAPI backend
uvicorn pff.api.main:app --reload

# In another terminal, start the Streamlit UI
streamlit run pff/ui/app.py
```

Navigate to `http://localhost:8501` to access the dashboard.

### 3. Use the REST API

```bash
# Calculate PFF for 6-bit integers using Shor's algorithm
curl -X POST "http://localhost:8000/calculate-pff" \
  -H "Content-Type: application/json" \
  -d '{
    "s": 6,
    "algorithm": "shors",
    "trials": 50
  }'
```

## Usage Examples

### Basic PFF Calculation

```python
from pff.engine.benchmark import calculate_pff

# Calculate PFF for a specific time-to-solution
pff_score = calculate_pff(time_per_run=0.025)  # 25ms per factorization
print(f"PFF: {pff_score:,.0f}")  # Output: PFF: 1,261,440,000
```

### Scaling Analysis

```python
from pff.engine.benchmark import scaling_analysis

# Test multiple integer sizes
results = scaling_analysis(
    algorithm='shors',
    sizes=[4, 6, 8, 10],
    trials=100
)

# Results contain PFF scores for each size
for size, pff in results.items():
    print(f"Size {size}-bit: PFF = {pff:,.0f}")
```

## Contributing

We welcome contributions! This framework is designed to be extensible. See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to add new algorithms
- Plugin development guide
- Testing requirements
- Code style guidelines

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{pff_framework,
  title={PFF Framework: Prime Factorization Frequency Calculator},
  author={slawonzo},
  year={2025},
  url={https://github.com/slawonzo/pff-framework}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [x] Core framework architecture
- [x] Shor's algorithm implementation (Qiskit Aer)
- [x] Classical factorization baseline
- [x] REST API (FastAPI)
- [x] Web dashboard (Streamlit)
- [x] IBM Quantum hardware backend support
- [x] Multi-backend comparison tools
- [ ] QAOA-based factorization
- [ ] Variational quantum algorithms
- [ ] Advanced statistical analysis
- [ ] Distributed benchmarking

## Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Note**: This is a research tool. For production cryptographic applications, use established libraries and consult security experts.
