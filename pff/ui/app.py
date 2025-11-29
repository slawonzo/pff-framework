"""
Streamlit Dashboard for PFF Framework

Interactive web interface for running PFF benchmarks and visualizing results.

To run:
    streamlit run pff/ui/app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pff.engine.benchmark import run_benchmark, scaling_analysis, calculate_pff
from pff.engine.algorithms.classical import ClassicalFactorization
from pff.core.algorithm import AlgorithmConfig

# Check if Qiskit is available
try:
    from pff.engine.algorithms.shors import ShorsAlgorithm
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="PFF Framework",
    page_icon="🔢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application"""
    
    # Title
    st.markdown('<div class="main-header">🔢 PFF Framework</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; font-size: 1.2rem; color: #666;">Prime Factorization Frequency Calculator</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    
    # Algorithm selection
    algorithm_options = ["Classical Factorization"]
    if QISKIT_AVAILABLE:
        algorithm_options.append("Shor's Algorithm (Quantum)")
    
    selected_algorithm = st.sidebar.selectbox(
        "Select Algorithm",
        algorithm_options,
        help="Choose the factorization algorithm to benchmark"
    )
    
    # Mode selection
    mode = st.sidebar.radio(
        "Benchmark Mode",
        ["Single Size", "Scaling Analysis"],
        help="Single Size: Test one integer size\nScaling Analysis: Test multiple sizes"
    )
    
    st.sidebar.markdown("---")
    
    # Parameters based on mode
    if mode == "Single Size":
        st.sidebar.subheader("Benchmark Parameters")
        
        s = st.sidebar.slider(
            "Integer Size (s) in bits",
            min_value=4,
            max_value=20,
            value=8,
            step=1,
            help="Binary size of integers to factor"
        )
        
        trials = st.sidebar.number_input(
            "Number of Trials",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            help="How many factorizations to perform"
        )
        
    else:  # Scaling Analysis
        st.sidebar.subheader("Scaling Parameters")
        
        min_size = st.sidebar.slider("Minimum Size (bits)", 4, 16, 4)
        max_size = st.sidebar.slider("Minimum Size (bits)", min_size + 2, 20, 12)
        step_size = st.sidebar.slider("Step Size", 1, 4, 2)
        
        sizes = list(range(min_size, max_size + 1, step_size))
        st.sidebar.write(f"Sizes to test: {sizes}")
        
        trials = st.sidebar.number_input(
            "Trials per Size",
            min_value=10,
            max_value=500,
            value=50,
            step=10
        )
    
    # Backend selection (for quantum algorithms)
    if "Quantum" in selected_algorithm:
        backend = st.sidebar.selectbox(
            "Quantum Backend",
            ["aer_simulator"],  # Add more as implemented
            help="Quantum computing backend"
        )
    else:
        backend = "cpu"
    
    semiprime = st.sidebar.checkbox(
        "Generate Semiprimes Only",
        value=True,
        help="If checked, generates products of two primes; otherwise any composite"
    )
    
    # Run button
    st.sidebar.markdown("---")
    run_button = st.sidebar.button("🚀 Run Benchmark", type="primary", use_container_width=True)
    
    # Information section
    with st.sidebar.expander("ℹ️ About PFF"):
        st.markdown("""
        **Prime Factorization Frequency (PFF)** measures how many factorizations
        a system could perform in one year.
        
        $$PFF(s) = \\frac{31,536,000}{T_s}$$
        
        Where:
        - **31,536,000** = seconds in a year
        - **T_s** = average time per factorization
        - **s** = integer size in bits
        """)
    
    # Main content area
    if run_button:
        # Get algorithm instance
        config = AlgorithmConfig(backend=backend)
        
        if "Classical" in selected_algorithm:
            algorithm = ClassicalFactorization(config)
        else:
            algorithm = ShorsAlgorithm(config)
        
        # Run benchmark
        if mode == "Single Size":
            run_single_benchmark(algorithm, s, trials, semiprime)
        else:
            run_scaling_benchmark(algorithm, sizes, trials, semiprime)
    
    else:
        # Show welcome screen
        show_welcome_screen()


def run_single_benchmark(algorithm, s, trials, semiprime):
    """Run a single benchmark and display results"""
    
    with st.spinner(f"Running benchmark for {s}-bit integers with {trials} trials..."):
        try:
            result = run_benchmark(
                s=s,
                algorithm=algorithm,
                trials=trials,
                semiprime=semiprime,
                verbose=False
            )
            
            # Display results
            st.success("✅ Benchmark completed successfully!")
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "PFF Score",
                    f"{result.pff:,.0f}",
                    help="Factorizations per year"
                )
            
            with col2:
                st.metric(
                    "Avg Time (T_s)",
                    f"{result.avg_time*1000:.3f} ms",
                    help="Average time per factorization"
                )
            
            with col3:
                st.metric(
                    "Success Rate",
                    f"{result.successful_trials/result.trials*100:.1f}%",
                    help="Percentage of successful factorizations"
                )
            
            with col4:
                st.metric(
                    "Trials",
                    f"{result.successful_trials}/{result.trials}",
                    help="Successful / Total trials"
                )
            
            # Detailed statistics
            st.markdown("### 📊 Detailed Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                stats_df = pd.DataFrame({
                    "Metric": ["Average", "Median", "Min", "Max", "Std Dev"],
                    "Time (ms)": [
                        f"{result.avg_time*1000:.6f}",
                        f"{result.median_time*1000:.6f}",
                        f"{result.min_time*1000:.6f}",
                        f"{result.max_time*1000:.6f}",
                        f"{result.std_time*1000:.6f}"
                    ]
                })
                st.table(stats_df)
            
            with col2:
                # Histogram of times
                times_ms = [r.time_seconds * 1000 for r in result.individual_results if r.success]
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=times_ms,
                    nbinsx=30,
                    name="Time Distribution",
                    marker_color='#1f77b4'
                ))
                fig.update_layout(
                    title="Time Distribution",
                    xaxis_title="Time (ms)",
                    yaxis_title="Frequency",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # PFF interpretation
            st.markdown("### 🎯 Interpretation")
            st.info(
                f"This system could theoretically perform **{result.pff:,.0f} factorizations** "
                f"of {s}-bit integers per year using {algorithm.name}."
            )
            
        except Exception as e:
            st.error(f"❌ Benchmark failed: {str(e)}")


def run_scaling_benchmark(algorithm, sizes, trials, semiprime):
    """Run scaling analysis and display results"""
    
    with st.spinner(f"Running scaling analysis for sizes {sizes}..."):
        try:
            result = scaling_analysis(
                algorithm=algorithm,
                sizes=sizes,
                trials=trials,
                semiprime=semiprime,
                verbose=False
            )
            
            st.success("✅ Scaling analysis completed!")
            
            # Prepare data for visualization
            pff_series = result.get_pff_series()
            timing_series = result.get_timing_series()
            
            df = pd.DataFrame({
                "Size (bits)": list(pff_series.keys()),
                "PFF": list(pff_series.values()),
                "Avg Time (ms)": [t * 1000 for t in timing_series.values()]
            })
            
            # Display table
            st.markdown("### 📊 Results Summary")
            st.dataframe(df, use_container_width=True)
            
            # Plots
            col1, col2 = st.columns(2)
            
            with col1:
                # PFF vs Size
                fig1 = go.Figure()
                fig1.add_trace(go.Scatter(
                    x=df["Size (bits)"],
                    y=df["PFF"],
                    mode='lines+markers',
                    name='PFF',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=10)
                ))
                fig1.update_layout(
                    title="PFF Scaling",
                    xaxis_title="Integer Size (bits)",
                    yaxis_title="PFF (factorizations/year)",
                    yaxis_type="log",
                    height=400
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Time vs Size
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=df["Size (bits)"],
                    y=df["Avg Time (ms)"],
                    mode='lines+markers',
                    name='Avg Time',
                    line=dict(color='#ff7f0e', width=3),
                    marker=dict(size=10)
                ))
                fig2.update_layout(
                    title="Time-to-Solution Scaling",
                    xaxis_title="Integer Size (bits)",
                    yaxis_title="Average Time (ms)",
                    yaxis_type="log",
                    height=400
                )
                st.plotly_chart(fig2, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Scaling analysis failed: {str(e)}")


def show_welcome_screen():
    """Display welcome information"""
    
    st.markdown("### 👋 Welcome to the PFF Framework!")
    
    st.markdown("""
    This dashboard allows you to benchmark quantum and classical factorization algorithms
    using the **Prime Factorization Frequency (PFF)** metric.
    
    #### Getting Started:
    1. **Configure** your benchmark in the sidebar
    2. **Select** an algorithm (Classical or Quantum)
    3. **Choose** between single size or scaling analysis
    4. **Run** the benchmark and view results
    
    #### What is PFF?
    
    The PFF metric quantifies computational efficiency for factorization:
    """)
    
    st.latex(r"PFF(s) = \frac{31,536,000}{T_s}")
    
    st.markdown("""
    Where:
    - **31,536,000** = seconds in one year
    - **T_s** = average time to factor an s-bit integer
    - **s** = binary size of the integer
    
    **Higher PFF = Better Performance** 🚀
    """)
    
    # Quick example
    st.markdown("### 📖 Example")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Input:**")
        st.code("""
Integer Size: 8 bits
Avg Time: 0.5 ms (0.0005 s)
        """)
    
    with col2:
        st.markdown("**Output:**")
        example_pff = calculate_pff(0.0005)
        st.code(f"""
PFF(8) = 31,536,000 / 0.0005
       = {example_pff:,.0f} factorizations/year
        """)


if __name__ == "__main__":
    main()
