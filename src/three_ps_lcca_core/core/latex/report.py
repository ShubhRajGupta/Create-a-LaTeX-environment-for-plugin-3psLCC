import os
import json
import re

def read_json_if_exists(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def format_num(val):
    if isinstance(val, (int, float)):
        return f"{val:,.2f}"
    return str(val)

def to_math_text(expr):
    """Converts a formula string into a LaTeX math expression wrapping variables in \\text{}"""
    parts = re.split(r'(\+|-|\s+x\s+|\s+/\s+|\s+)', str(expr))
    out = []
    for p in parts:
        p_strip = p.strip()
        if not p_strip:
            continue
        if p_strip == 'x':
            out.append(r'\times')
        elif p_strip == '/':
            out.append(r'\div')
        elif p_strip in ['+', '-', '=', '(', ')']:
            out.append(p_strip)
        elif p_strip.replace('.','',1).isdigit():
            out.append(p_strip)
        else:
            word = p_strip.replace("_", " ").title()
            out.append(rf"\text{{{word}}}")
    return " ".join(out)

def render_breakdown(title, breakdown):
    if not breakdown:
        return ""
    
    lines = []
    lines.append(rf"\subsubsection{{{title}}}")
    
    formulae = breakdown.get("formulae", {})
    inputs = breakdown.get("inputs", {})
    computed = breakdown.get("computed_values", {})
    
    if formulae:
        for name, formula in formulae.items():
            clean_name = name.replace("_", " ").title()
            
            lines.append(rf" \paragraph{{Calculation for {clean_name}}} ")
            # Plain English
            lines.append(f"The {clean_name} is calculated as: {str(formula).replace('_', ' ')}.")
            
            # Equation
            lines.append(r"\begin{align*}")
            lines.append(rf" \text{{{clean_name}}} &= {to_math_text(formula)} \\")
            
            # Substitute
            substituted = str(formula)
            for k in sorted(inputs.keys(), key=len, reverse=True): 
                if str(k) in substituted:
                    substituted = substituted.replace(str(k), format_num(inputs[k]))
                    
            lines.append(rf" \text{{{clean_name}}} &= {to_math_text(substituted)} \\")
            
            # Final Value
            if name in computed:
                lines.append(rf" \text{{{clean_name}}} &= {format_num(computed[name])} ")
            lines.append(r"\end{align*}")
            
    if inputs:
        lines.append(r"\textbf{Input Values:}")
        lines.append(r"\begin{itemize}")
        for k, v in inputs.items():
            clean_k = k.replace("_", " ").title()
            lines.append(rf"\item {clean_k} = {format_num(v)}")
        lines.append(r"\end{itemize}")
            
    return "\n".join(lines)


def generate_latex_report(input_data, construction_costs, results, output_path=None):
    if not output_path:
        output_path = "LCCA_Report.tex"

    debug_dir = "debug"

    # read debug jsons
    stage_1 = read_json_if_exists(os.path.join(debug_dir, "stage_costs_1-initial_cost_breakdown.json"))
    stage_2 = read_json_if_exists(os.path.join(debug_dir, "stage_costs_2-use_stage_cost_breakdown.json"))
    stage_3 = read_json_if_exists(os.path.join(debug_dir, "stage_costs_3-Reconstruction_breakdown.json"))
    stage_4 = read_json_if_exists(os.path.join(debug_dir, "stage_costs_4-end_of_life_breakdown.json"))

    gp = input_data.get("general_parameters", {})

    tex = []
    tex.append(r"\documentclass{article}")
    tex.append(r"\usepackage[utf8]{inputenc}")
    tex.append(r"\usepackage{geometry}")
    tex.append(r"\geometry{a4paper, margin=1in}")
    tex.append(r"\usepackage{longtable}")
    tex.append(r"\usepackage{amsmath}")
    tex.append(r"\usepackage{booktabs}")
    tex.append(r"\usepackage{hyperref}")
    tex.append(r"\title{Life Cycle Cost Analysis Report}")
    tex.append(r"\author{3psLCCA Engine}")
    tex.append(r"\date{\today}")
    tex.append(r"\begin{document}")
    tex.append(r"\maketitle")
    
    # I. Title Page / General Params
    tex.append(r"\section{Project Parameters}")
    tex.append(r"\begin{longtable}{lc}")
    tex.append(r"\toprule")
    tex.append(r"\textbf{Parameter} & \textbf{Value} \\")
    tex.append(r"\midrule")
    for k in ["service_life_years", "analysis_period_years", "discount_rate_percent", "inflation_rate_percent", "interest_rate_percent", "currency_conversion"]:
        val = gp.get(k, "N/A")
        clean_k = k.replace("_", " ").title()
        tex.append(rf"{clean_k} & {format_num(val)} \\")
    tex.append(r"\bottomrule")
    tex.append(r"\end{longtable}")

    # II. Construction Cost Inputs
    tex.append(r"\section{Construction Cost Inputs}")
    tex.append(r"\begin{longtable}{lc}")
    tex.append(r"\toprule")
    tex.append(r"\textbf{Cost Item} & \textbf{Value} \\")
    tex.append(r"\midrule")
    for k, v in construction_costs.items():
        if isinstance(v, (int, float)):
            clean_k = k.replace("_", " ").title()
            tex.append(rf"{clean_k} & {format_num(v)} \\")
    tex.append(r"\bottomrule")
    tex.append(r"\end{longtable}")

    # III. Calculation Sections
    tex.append(r"\section{Calculation Sections (Stages 1-4)}")
    
    # Stage 1
    tex.append(r"\subsection{Initial Stage}")
    if stage_1:
        tex.append(render_breakdown("Initial Cost Breakdown", stage_1))
    
    # Stage 2
    tex.append(r"\subsection{Use Stage}")
    for section_name, section_data in stage_2.items():
        if isinstance(section_data, dict) and "breakdown" in section_data:
            clean_name = section_name.replace("_", " ").title()
            tex.append(render_breakdown(clean_name, section_data["breakdown"]))

    # Stage 3
    tex.append(r"\subsection{Reconstruction Stage}")
    for section_name, section_data in stage_3.items():
        if section_name.endswith("_breakdown") and isinstance(section_data, dict):
            clean_name = section_name.replace("_breakdown", "").replace("_", " ").title()
            if "formulae" in section_data: 
                tex.append(render_breakdown(clean_name, section_data))
            elif "breakdown" in section_data:
                tex.append(render_breakdown(clean_name, section_data["breakdown"]))

    # Stage 4
    tex.append(r"\subsection{End-of-Life Stage}")
    for section_name, section_data in stage_4.items():
        if section_name.endswith("_breakdown") and isinstance(section_data, dict):
            clean_name = section_name.replace("_breakdown", "").replace("_", " ").title()
            if "formulae" in section_data: 
                tex.append(render_breakdown(clean_name, section_data))
            elif "breakdown" in section_data:
                tex.append(render_breakdown(clean_name, section_data["breakdown"]))

    # IV. Final Summary
    tex.append(r"\section{Summary}")
    tex.append(r"\begin{longtable}{llc}")
    tex.append(r"\toprule")
    tex.append(r"\textbf{Stage} & \textbf{Category} & \textbf{Cost} \\")
    tex.append(r"\midrule")
    
    grand_totals = {"economic": 0, "environmental": 0, "social": 0}

    for stage in ["initial_stage", "use_stage", "reconstruction", "end_of_life"]:
        stage_title = stage.replace("_", " ").title()
        stage_res = results.get(stage, {})
        for cat in ["economic", "environmental", "social"]:
            cat_data = stage_res.get(cat, {})
            cat_total = sum(cat_data.values()) if isinstance(cat_data, dict) else 0
            grand_totals[cat] += cat_total
            tex.append(rf"{stage_title} & {cat.title()} & {format_num(cat_total)} \\")
    
    tex.append(r"\midrule")
    tex.append(r"\textbf{Grand Totals} & & \\")
    tex.append(r"\midrule")
    grand_sum = 0
    for cat, total in grand_totals.items():
         grand_sum += total
         tex.append(rf"& \textbf{{{cat.title()}}} & \textbf{{{format_num(total)}}} \\")
    tex.append(r"\midrule")
    tex.append(rf"& \textbf{{Grand Total}} & \textbf{{{format_num(grand_sum)}}} \\")
    tex.append(r"\bottomrule")
    tex.append(r"\end{longtable}")

    tex.append(r"\end{document}")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex))
