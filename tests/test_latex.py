import os
import unittest
from src.three_ps_lcca_core.core.main import run_full_lcc_analysis
from src.examples.from_dict.Input_global import Input_global

life_cycle_construction_cost_breakdown = {
    "initial_construction_cost": 12843979.44,
    "initial_carbon_emissions_cost": 2065434.91,
    "superstructure_construction_cost": 9356038.92,
    "total_scrap_value": 2164095.02,
}

class TestLatexReport(unittest.TestCase):
    def test_latex_report_generation(self):
        output_file = "Test_LCCA_Report.tex"
        
        # Remove file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
            
        results = run_full_lcc_analysis(
            Input_global, 
            life_cycle_construction_cost_breakdown, 
            latex_report=True,
            latex_output_path=output_file
        )
        
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn(r"\documentclass{article}", content)
        self.assertIn(r"\section{Project Parameters}", content)
        self.assertIn(r"\section{Calculation Sections (Stages 1-4)}", content)
        self.assertIn(r"Initial Cost Breakdown", content)
        
        # Clean up
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == '__main__':
    unittest.main()
