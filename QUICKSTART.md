# PFF Framework Quick Start Guide

Welcome to the PFF (Prime Factorization Frequency) Framework! This guide will help you get started quickly.

## Installation

### 1. Prerequisites

- Python 3.10 or higher
- pip package manager
- Git (for cloning the repository)

### 2. Clone and Install

```bash
# Clone the repository
git clone https://github.com/slawonzo/pff-framework.git
cd pff-framework

# Install the package
pip install -e .

# Or install with all optional dependencies
pip install -e ".[all]"
```

### 3. Verify Installation

```bash
python -c "import pff; print(pff.__version__)"
```

## Running Your First Benchmark

### Option 1: Python Script

Create a file `my_first_benchmark.py`:

```python
from pff.engine.algorithms.classical import ClassicalFactorization
from pff.engine.benchmark import run_benchmark

# Create algorithm
algorithm = ClassicalFactorization()

# Run benchmark for 8-bit integers
result = run_benchmark(s=8, algorithm=algorithm, trials=50)

# Display results
print(result.summary())
```

Run it:

```bash
python my_first_benchmark.py
```

### Option 2: Interactive Python

```python
>>> from pff.engine.algorithms.classical import ClassicalFactorization
>>> from pff.engine.benchmark import run_benchmark
>>> 
>>> algo = ClassicalFactorization()
>>> result = run_benchmark(s=6, algorithm=algo, trials=20)
>>> 
>>> print(f"PFF Score: {result.pff:,.0f}")
PFF Score: 1,234,567
```

### Option 3: Web Dashboard

Start the backend API:

```bash
uvicorn pff.api.main:app --reload
```

In another terminal, start the UI:

```bash
streamlit run pff/ui/app.py
```

Open your browser to `http://localhost:8501`

## Running on Real Quantum Hardware

To run Shor's algorithm on real IBM Quantum hardware:

1.  **Get your API Token**: Sign up at [quantum.ibm.com](https://quantum.ibm.com/).
2.  **Save your Account**:
    ```bash
    python -c "from qiskit_ibm_runtime import QiskitRuntimeService; QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='YOUR_API_TOKEN')"
    ```
3.  **Run the Example**:
    ```bash
    python examples/quantum_real_backend.py
    ```

This script will:
- Connect to the least busy operational backend.
- Transpile the circuit for the specific device.
- Submit the job using Qiskit Runtime Primitives (`SamplerV2`).
- Provide a link to monitor the job status.

## Understanding Your Results

A typical benchmark result looks like this:

```
PFF Benchmark Results
=====================
Integer Size (s):        8 bits
Algorithm:               Classical Factorization
Backend:                 cpu
Trials:                  50
Successful:              50 (100.0%)

Timing Statistics:
------------------
Average Time (Ts):       0.000125 seconds
Min Time:                0.000098 seconds
Max Time:                0.000201 seconds
Std Deviation:           0.000031 seconds
Median Time:             0.000119 seconds

PFF Metric:
-----------
PFF(s=8):                252,288,000 factorizations/year
```

**Interpretation**: This system could theoretically perform 252,288,000 factorizations of 8-bit integers per year.

## Common Tasks

### 1. Compare Different Integer Sizes

```python
from pff.engine.algorithms.classical import ClassicalFactorization
from pff.engine.benchmark import scaling_analysis

algorithm = ClassicalFactorization()
result = scaling_analysis(
    algorithm=algorithm,
    sizes=[4, 6, 8, 10, 12],
    trials=25
)

print(result.summary())
```

### 2. Test Quantum Algorithm (Requires Qiskit)

First, install Qiskit:

```bash
pip install qiskit qiskit-aer
```

Then:

```python
from pff.engine.algorithms.shors import ShorsAlgorithm
from pff.engine.benchmark import run_benchmark

quantum_algo = ShorsAlgorithm()
result = run_benchmark(s=6, algorithm=quantum_algo, trials=10)
print(result.summary())
```

### 3. Use the REST API

```bash
# Start the API server
uvicorn pff.api.main:app --reload
```

Then make requests:

```bash
# Calculate PFF
curl -X POST "http://localhost:8000/calculate-pff" \
  -H "Content-Type: application/json" \
  -d '{
    "s": 8,
    "algorithm": "classical",
    "trials": 50
  }'

# List available algorithms
curl http://localhost:8000/algorithms

# Health check
curl http://localhost:8000/health
```

### 4. Save Results

```python
import json
from pff.engine.benchmark import run_benchmark
from pff.engine.algorithms.classical import ClassicalFactorization

algorithm = ClassicalFactorization()
result = run_benchmark(s=10, algorithm=algorithm, trials=100)

# Save to JSON
with open("results/my_benchmark.json", "w") as f:
    f.write(result.to_json())

# Save to CSV (custom)
import csv
with open("results/my_benchmark.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Trial", "N", "Time", "Success"])
    for i, r in enumerate(result.individual_results, 1):
        writer.writerow([i, r.N, r.time_seconds, r.success])
```

## Examples

The `examples/` directory contains ready-to-run examples:

```bash
# Basic example
python examples/basic_example.py

# Scaling analysis
python examples/scaling_example.py

# Quantum vs Classical comparison (requires Qiskit)
python examples/quantum_vs_classical.py
```

## Troubleshooting

### Import Errors

If you see import errors, make sure you installed the package:

```bash
pip install -e .
```

### Qiskit Not Found

For quantum algorithms, install Qiskit:

```bash
pip install qiskit qiskit-aer
```

### Slow Performance

For small integers (s < 10), use fewer trials:

```python
result = run_benchmark(s=6, algorithm=algo, trials=10)
```

For large integers (s > 15), classical algorithms may be very slow.

## Next Steps

1. **Read the full README.md** for detailed documentation
2. **Explore examples/** for more use cases
3. **Check docs/** for algorithm details
4. **Contribute!** See CONTRIBUTING.md

## Getting Help

- **Issues**: Open an issue on GitHub
- **Discussions**: Start a discussion for questions
- **Documentation**: See `docs/` folder

Happy factorizing! 🚀
