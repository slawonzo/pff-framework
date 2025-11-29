# PFF Framework - Project Overview

## 🎯 Project Summary

The **PFF (Prime Factorization Frequency) Framework** is a comprehensive benchmarking tool for measuring the computational efficiency of quantum and classical factorization algorithms. It implements the novel PFF metric from the doctoral dissertation on quantum system quality measurement.

### Key Innovation: The PFF Metric

$$PFF(s) = \frac{31,536,000}{T_s}$$

Where:
- **31,536,000** = seconds in one year
- **T_s** = average time-to-solution for factoring s-bit integers
- **s** = binary size of the composite integer

The PFF metric quantifies how many factorizations a system could theoretically perform in one year, providing an intuitive benchmark for algorithm comparison.

## 📁 Project Structure

```
pff-framework/
├── pff/                          # Main package
│   ├── core/                     # Core framework
│   │   ├── algorithm.py          # Base algorithm interface
│   │   └── result.py            # Result data structures
│   ├── engine/                   # Computational engine
│   │   ├── algorithms/          # Algorithm implementations
│   │   │   ├── classical.py     # Classical factorization
│   │   │   └── shors.py         # Shor's algorithm (Qiskit)
│   │   ├── benchmark.py         # Benchmarking logic
│   │   └── utils.py             # Utility functions
│   ├── api/                      # FastAPI REST API
│   │   ├── main.py              # API server
│   │   └── models.py            # Pydantic models
│   └── ui/                       # Streamlit dashboard
│       └── app.py               # Web interface
├── examples/                     # Usage examples
├── tests/                        # Test suite
├── docs/                         # Documentation
└── results/                      # Benchmark results
```

## 🔧 Core Components

### 1. Algorithm Framework (`pff/core/`)

**Purpose**: Provides the plugin architecture for factorization algorithms

**Key Classes**:
- `FactorizationAlgorithm`: Abstract base class for all algorithms
- `AlgorithmConfig`: Configuration data structure
- `BenchmarkResult`: Result data structure with PFF calculation

**Features**:
- Pluggable algorithm system
- Input validation
- Factor verification
- Metadata tracking

### 2. Engine (`pff/engine/`)

**Purpose**: Implements factorization algorithms and benchmarking logic

**Components**:

**a) Algorithms (`pff/engine/algorithms/`)**
- `ClassicalFactorization`: Trial division + Pollard's rho
- `ShorsAlgorithm`: Quantum factorization via Qiskit
  - Supports local simulation (`AerSimulator`)
  - Supports real hardware via IBM Quantum Runtime (`SamplerV2`)
- Extensible for future algorithms (QAOA, variational methods)

**b) Benchmarking (`pff/engine/benchmark.py`)**
- `run_benchmark()`: Execute trials and calculate PFF
- `scaling_analysis()`: Test multiple integer sizes
- `calculate_pff()`: Direct PFF calculation
- Statistical analysis (mean, median, std dev)

**c) Utilities (`pff/engine/utils.py`)**
- `generate_semiprime()`: Create test integers
- `is_prime()`: Primality testing
- Number generation and validation

### 3. REST API (`pff/api/`)

**Purpose**: HTTP interface for programmatic access

**Endpoints**:
- `POST /calculate-pff`: Run benchmark for specific size
- `POST /scaling-analysis`: Multi-size analysis
- `GET /algorithms`: List available algorithms
- `GET /health`: System status

**Technology**: FastAPI with Pydantic validation

### 4. Web Dashboard (`pff/ui/`)

**Purpose**: Interactive visualization and benchmarking

**Features**:
- Real-time benchmark execution
- Interactive parameter configuration
- PFF scaling charts (Plotly)
- Results export (JSON/CSV)
- Algorithm comparison

**Technology**: Streamlit

## 🎓 Alignment with Thesis

The framework directly implements concepts from your doctoral dissertation:

### 1. PFF Metric Implementation
- Exact formula from thesis (31,536,000 / T_s)
- Time-to-solution measurement
- Scaling analysis across integer sizes

### 2. Algorithm Support
- **Shor's Algorithm**: Primary quantum implementation
- **Classical Baseline**: For comparison
- **Extensible**: Ready for QAOA, variational methods

### 3. Benchmarking Methodology
- Random semiprime generation
- Statistical rigor (multiple trials)
- Performance characterization
- Reproducible results

### 4. Quality Measurement
- Success rate tracking
- Error handling and validation
- Backend comparison (simulator vs. hardware)

## 🚀 Usage Patterns

### Pattern 1: Quick PFF Calculation

```python
from pff.engine.algorithms.classical import ClassicalFactorization
from pff.engine.benchmark import run_benchmark

algo = ClassicalFactorization()
result = run_benchmark(s=8, algorithm=algo, trials=100)
print(f"PFF: {result.pff:,.0f}")
```

### Pattern 2: Algorithm Comparison

```python
classical = ClassicalFactorization()
quantum = ShorsAlgorithm()

classical_result = run_benchmark(s=6, algorithm=classical, trials=50)
quantum_result = run_benchmark(s=6, algorithm=quantum, trials=50)

print(f"Classical PFF: {classical_result.pff:,.0f}")
print(f"Quantum PFF: {quantum_result.pff:,.0f}")
```

### Pattern 3: Scaling Analysis

```python
result = scaling_analysis(
    algorithm=ClassicalFactorization(),
    sizes=[4, 6, 8, 10, 12],
    trials=25
)
print(result.summary())
```

### Pattern 4: Web Dashboard

```bash
# Terminal 1: Start API
uvicorn pff.api.main:app --reload

# Terminal 2: Start UI
streamlit run pff/ui/app.py
```

### Pattern 5: Real Quantum Backend

```python
from pff.engine.algorithms.shors import ShorsAlgorithm
from pff.core.algorithm import AlgorithmConfig

# Configure for IBM Quantum
config = AlgorithmConfig(
    backend="ibm_quantum", 
    shots=1024, 
    max_iterations=10
)
algorithm = ShorsAlgorithm(config=config)

# Run factorization on real hardware
result = algorithm.factor(15)
print(f"Factors: {result}")
```

## 📊 Data Flow

```
User Input (s, algorithm, trials)
        ↓
Benchmark Runner
        ↓
Generate Random Semiprimes (s-bit)
        ↓
For each trial:
    ├── Time factorization
    ├── Verify result
    └── Record statistics
        ↓
Calculate Statistics
    ├── Mean, Median, Std Dev
    ├── Min, Max times
    └── Success rate
        ↓
Calculate PFF = 31,536,000 / avg_time
        ↓
Return BenchmarkResult
```

## 🔬 Research Applications

### 1. Quantum System Benchmarking
- Compare simulator vs. real hardware
- Measure noise impact on factorization
- Track improvement over time

### 2. Algorithm Analysis
- Classical vs. quantum performance
- Scaling behavior with integer size
- Resource requirements estimation

### 3. Hardware Comparison
- Different quantum backends
- Various classical systems
- Distributed computing setups

## 🛠️ Extensibility

### Adding New Algorithms

1. Inherit from `BaseFactorizationAlgorithm`
2. Implement `factor(N)` method
3. Add to plugin registry
4. Update API and UI

Example:

```python
class QAOAFactorization(BaseFactorizationAlgorithm):
    def __init__(self, config=None):
        super().__init__(config, algorithm_type="quantum")
        self._name = "QAOA Factorization"
    
    def factor(self, N: int) -> List[int]:
        # QAOA implementation
        pass
```

### Adding New Backends

1. Extend `AlgorithmConfig`
2. Implement backend initialization
3. Update backend selection in UI/API

### Adding New Metrics

1. Extend `BenchmarkResult`
2. Update calculation in `run_benchmark()`
3. Add visualization in dashboard

## 📈 Future Roadmap

### Phase 1: Foundation (v0.1.0) ✅
- [x] Core framework
- [x] Classical algorithms
- [x] Shor's algorithm (simulator)
- [x] REST API
- [x] Web dashboard

### Phase 2: Enhancement (v0.2.0) 🚧
- [x] IBM Quantum hardware support (via Qiskit Runtime)
- [x] Multi-backend comparison (Simulator vs Real)
- [ ] QAOA implementation
- [ ] Advanced statistical analysis
- [ ] Distributed benchmarking

### Phase 3: Production (v1.0.0)
- [ ] Variational quantum algorithms
- [ ] Cloud deployment
- [ ] Result database
- [ ] Historical tracking
- [ ] Automated reporting

## 💡 Key Design Decisions

### 1. Pluggable Architecture
**Why**: Enables easy addition of new algorithms without core changes
**How**: Abstract base class with defined interface

### 2. Separate Engine from UI/API
**Why**: Allows multiple frontend options
**How**: Core logic in `pff/engine/`, separate `api/` and `ui/`

### 3. PFF as Primary Metric
**Why**: Intuitive interpretation (factorizations/year)
**How**: Constant (31.5M seconds) divided by time-to-solution

### 4. Statistical Rigor
**Why**: Reliable benchmarking requires multiple trials
**How**: Mean, median, std dev, success rate tracking

### 5. Result Preservation
**Why**: Enable reproducibility and long-term tracking
**How**: Structured data classes with JSON serialization

## 🎯 Success Metrics

For the framework to be successful:

1. **Accuracy**: PFF calculations match manual computations
2. **Reliability**: High success rates across algorithm types
3. **Usability**: Clear API, good documentation
4. **Extensibility**: Easy to add new algorithms
5. **Performance**: Efficient benchmarking
6. **Research Value**: Supports thesis objectives

## 📚 Documentation Structure

- `README.md`: Overview and features
- `QUICKSTART.md`: Get started in 5 minutes
- `CONTRIBUTING.md`: Development guidelines
- `docs/architecture.md`: Detailed design
- `docs/algorithms.md`: Algorithm documentation
- `docs/api.md`: API reference
- Examples in `examples/` directory

## 🤝 Collaboration Ready

The framework is designed for open collaboration:

- Clear contribution guidelines
- Modular architecture
- Comprehensive tests
- Good documentation
- GitHub-friendly structure

---

**Note**: This is a research tool aligned with doctoral thesis requirements. All benchmarks should be interpreted in appropriate context with consideration for hardware limitations and quantum noise.
