# Contributing to PFF Framework

Thank you for your interest in contributing to the PFF Framework! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/slawonzo/pff-framework.git
   cd pff-framework
   ```
3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/` for new features
- `bugfix/` for bug fixes
- `docs/` for documentation
- `refactor/` for code refactoring

### 2. Make Changes

- Write clean, readable code
- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Write tests for new functionality

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pff --cov-report=html

# Run specific test file
pytest tests/test_benchmark.py
```

### 4. Format Code

```bash
# Format with black
black pff/ tests/ examples/

# Sort imports
isort pff/ tests/ examples/

# Check with flake8
flake8 pff/ tests/ examples/
```

### 5. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add support for custom backends"
```

Follow conventional commits:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `test:` adding tests
- `refactor:` code refactoring
- `style:` formatting changes
- `chore:` maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Adding New Algorithms

To add a new factorization algorithm:

1. **Create algorithm file** in `pff/engine/algorithms/`:

```python
from pff.engine.algorithms.base import BaseFactorizationAlgorithm
from pff.core.algorithm import AlgorithmConfig

class MyNewAlgorithm(BaseFactorizationAlgorithm):
    def __init__(self, config: AlgorithmConfig = None):
        super().__init__(config, algorithm_type="quantum")  # or "classical"
        self._name = "My New Algorithm"
    
    def factor(self, N: int) -> List[int]:
        """Implement factorization logic here"""
        self.validate_input(N)
        # Your algorithm implementation
        factors = ...
        
        if not self.verify_factors(N, factors):
            raise RuntimeError(f"Factorization failed for {N}")
        
        return factors
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        info = super().get_algorithm_info()
        info["custom_field"] = "value"
        return info
```

2. **Add tests** in `tests/test_algorithms/`:

```python
def test_my_new_algorithm():
    algorithm = MyNewAlgorithm()
    factors = algorithm.factor(15)
    assert sorted(factors) == [3, 5]
```

3. **Update documentation** in `docs/algorithms.md`

4. **Add to API** in `pff/api/main.py` if needed

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the structure of the main package
- Name test files with `test_` prefix
- Name test functions with `test_` prefix

Example test:

```python
import pytest
from pff.engine.algorithms.classical import ClassicalFactorization

def test_classical_factorization_basic():
    """Test basic factorization"""
    algo = ClassicalFactorization()
    factors = algo.factor(15)
    assert sorted(factors) == [3, 5]

def test_classical_factorization_invalid_input():
    """Test invalid input handling"""
    algo = ClassicalFactorization()
    with pytest.raises(ValueError):
        algo.factor(1)
```

### Test Coverage

- Aim for >80% code coverage
- Test both success and failure cases
- Test edge cases
- Use parametrized tests for multiple inputs

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def my_function(arg1: int, arg2: str) -> bool:
    """
    Brief description of function.
    
    More detailed description if needed.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When this happens
        RuntimeError: When that happens
    """
    pass
```

### Adding Documentation

- Update README.md for major features
- Add examples in `examples/`
- Update `docs/` for detailed documentation

## Code Style

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names

### Imports

Group imports in this order:
1. Standard library
2. Third-party packages
3. Local modules

```python
import os
import sys
from typing import List, Dict

import numpy as np
from qiskit import QuantumCircuit

from pff.core.algorithm import FactorizationAlgorithm
from pff.engine.utils import generate_semiprime
```

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted (black, isort)
- [ ] No linting errors (flake8)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (for significant changes)

### PR Description

Include in your PR description:
- **What**: Brief description of changes
- **Why**: Reason for changes
- **How**: Implementation approach
- **Testing**: How you tested the changes
- **Breaking Changes**: Any breaking changes

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Contact maintainers for other inquiries

Thank you for contributing! 🙏
