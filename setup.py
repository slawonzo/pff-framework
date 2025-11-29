"""
PFF Framework: Prime Factorization Frequency Calculator
Setup configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core dependencies
install_requires = [
    "numpy>=1.24.0",
    "qiskit>=0.45.0",
    "qiskit-aer>=0.13.0",
    "qiskit-ibm-runtime>=0.20.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "python-dateutil>=2.8.0",
]

# Optional dependencies for different features
extras_require = {
    "api": [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "python-multipart>=0.0.6",
    ],
    "ui": [
        "streamlit>=1.28.0",
        "plotly>=5.17.0",
        "pandas>=2.1.0",
        "matplotlib>=3.8.0",
    ],
    "dev": [
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "pytest-asyncio>=0.21.0",
        "black>=23.0.0",
        "flake8>=6.1.0",
        "mypy>=1.6.0",
        "isort>=5.12.0",
    ],
    "docs": [
        "sphinx>=7.2.0",
        "sphinx-rtd-theme>=1.3.0",
        "myst-parser>=2.0.0",
    ],
}

# All optional dependencies combined
extras_require["all"] = list(set(sum(extras_require.values(), [])))

setup(
    name="pff-framework",
    version="0.1.0",
    author="Slawomir Folwarski",
    author_email="slawonzo@gmail.com",
    description="Prime Factorization Frequency (PFF) benchmarking framework for quantum and classical algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slawonzo/pff-framework",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "pff=pff.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
