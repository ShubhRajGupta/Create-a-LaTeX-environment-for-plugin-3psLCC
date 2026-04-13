# 3psLCCA Engine

3psLCCA is a comprehensive Life Cycle Cost Analysis (LCCA) engine designed for bridge infrastructure. It calculates and structures lifecycle costs across four key stages: **Initial Construction**, **Use (Maintenance)**, **Reconstruction**, and **End-of-Life (Demolition)**.

Designed for transparency, the engine includes a built-in LaTeX report generator that produces detailed, human-readable breakdowns suitable for engineering reviews and formal auditing. 

## Key Features

- **Comprehensive Lifecycle Costing:** Evaluates all four fundamental phases of an infrastructure's life cycle.
- **Automated LaTeX Reports:** Generates `.tex` and `.pdf` reports detailing all formulas, inputs, plain-English explanations, and step-by-step mathematical derivations.
- **Parametric Inputs:** Readily configure discount rates, inflation, reconstruction cycles, and structural maintenance configurations.

## Prerequisites

- **Python 3.8+**
- **LaTeX Distribution:** A working LaTeX compiler (such as TeX Live or MiKTeX) must be installed and available in your system's PATH if you wish to compile the generated `.tex` files into `.pdf`.

## Getting Started

1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd 3psLCCA-core-task
   ```

2. **Run the Example:**
   To verify your setup and see the engine in action, an example script is provided:
   ```bash
   python -m src.examples.from_dict.example
   ```

3. **Check Output:**
   - Calculation results will be printed to your terminal.
   - `LCCA_Report.tex` and the compiled `LCCA_Report.pdf` will be generated in your project root, providing a highly-detailed view of the entire cost breakdown.
   - Detailed JSON data dumps will be placed in the `debug/` directory.

## Usage Guide

You can integrate the core engine directly into your own applications. The primary entry point is `run_full_lcc_analysis()`:

```python
from src.three_ps_lcca_core.core.main import run_full_lcc_analysis

# 1. Define your inputs
project_data = { ... } # Your global parameters & user costs
construction_costs = { ... } # Your initial superstructure/base costs

# 2. Run computation
results = run_full_lcc_analysis(
    input_data=project_data,
    construction_costs=construction_costs,
    latex_report=True,                       # Trigger report generation
    latex_output_path="Analysis_Report.tex"  # Specify custom filename
)

# 3. Access the structured results
print(results["initial_stage"])
print(results["use_stage"])
```

## Contributing
Contributions are always welcome! When developing new features, please ensure that new parameters comply with our internal `ironclad_validator` logic and that you add appropriate test coverage in the `tests/` directory.

## License
Please refer to the [LICENSE](LICENSE) file for details on distribution and copyright.
