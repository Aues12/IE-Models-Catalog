"""Vary one EOQ input at a time and measure the cost of keeping the old policy.

Run: python -m examples.eoq_sensitivity
"""

import argparse
import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from inventory_models import BasicEOQ

BASELINE = dict(price=50, demand_rate=1200, ordering_cost=75, holding_rate=0.20)
PARAMETERS = {
    "demand_rate": "Annual demand",
    "ordering_cost": "Cost per order",
    "holding_rate": "Annual holding rate",
}
COLORS = ("#2563eb", "#ea580c", "#059669")


def analyze():
    """Reoptimize each scenario and evaluate the baseline quantity under it."""
    baseline = BasicEOQ(**BASELINE).solve()
    records = []
    for parameter in PARAMETERS:
        for multiplier in np.linspace(0.5, 2.0, 31):
            inputs = {**BASELINE, parameter: BASELINE[parameter] * float(multiplier)}
            model = BasicEOQ(**inputs)
            optimum = model.solve()
            fixed_cost = model.calculate_costs(baseline.order_quantity).relevant_cost
            optimal_cost = optimum.costs.relevant_cost
            records.append(
                {
                    "parameter": parameter,
                    "multiplier": float(multiplier),
                    "parameter_value": inputs[parameter],
                    "order_quantity": optimum.order_quantity,
                    "quantity_ratio": optimum.order_quantity / baseline.order_quantity,
                    "optimal_relevant_cost": optimal_cost,
                    "baseline_quantity_relevant_cost": fixed_cost,
                    "extra_cost_percent": 100 * (fixed_cost / optimal_cost - 1),
                }
            )
    return {
        "baseline_inputs": BASELINE,
        "baseline_order_quantity": baseline.order_quantity,
        "baseline_relevant_cost": baseline.costs.relevant_cost,
        "cost_horizon": "one year",
        "cost_components": "ordering + holding; purchase excluded",
        "scenarios": records,
    }


def make_figure(report):
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=[
            "How the optimal order quantity changes",
            "Extra cost of keeping the baseline quantity",
        ],
        horizontal_spacing=0.12,
    )
    for (parameter, label), color in zip(PARAMETERS.items(), COLORS):
        rows = [r for r in report["scenarios"] if r["parameter"] == parameter]
        for column, key in ((1, "quantity_ratio"), (2, "extra_cost_percent")):
            fig.add_trace(
                go.Scatter(
                    x=[r["multiplier"] for r in rows],
                    y=[r[key] for r in rows],
                    name=label,
                    mode="lines+markers",
                    marker=dict(size=4),
                    line=dict(
                        color=color,
                        dash="dot" if parameter == "ordering_cost" else "solid",
                    ),
                    legendgroup=parameter,
                    showlegend=column == 1,
                    hovertemplate="Input multiplier: %{x:.2f}<br>Value: %{y:.3f}<extra>%{fullData.name}</extra>",
                ),
                row=1,
                col=column,
            )
    fig.add_hline(y=1, line_dash="dash", line_color="#94a3b8", row=1, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8", row=1, col=2)
    fig.update_xaxes(title_text="Input / baseline input", ticksuffix="×")
    fig.update_yaxes(title_text="Optimal quantity / baseline quantity", row=1, col=1)
    fig.update_yaxes(
        title_text="Extra annual ordering + holding cost (%)", row=1, col=2
    )
    fig.update_layout(
        title=dict(
            text=f"EOQ sensitivity | baseline quantity {report['baseline_order_quantity']:.2f} units",
            y=0.97,
        ),
        template="plotly_white",
        height=650,
        width=1200,
        margin=dict(t=130, b=150),
        legend=dict(orientation="h", y=1.19, x=0),
    )
    fig.add_annotation(
        x=0,
        y=-0.32,
        xref="paper",
        yref="paper",
        showarrow=False,
        xanchor="left",
        text="One input changes at a time; price stays at 50. Costs cover one year and exclude purchases.<br>"
        "Demand and ordering-cost quantity curves overlap. All three percentage cost-penalty curves overlap.<br>"
        "Toggle series in the legend to inspect them. These deterministic scenarios do not estimate uncertainty.",
    )
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("examples/output"))
    args = parser.parse_args()
    report = analyze()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "eoq_sensitivity.json"
    html_path = args.output_dir / "eoq_sensitivity.html"
    json_path.write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    make_figure(report).write_html(html_path, include_plotlyjs=True, auto_open=False)
    print(
        f"Baseline: Q={report['baseline_order_quantity']:.2f}; annual ordering + holding={report['baseline_relevant_cost']:.2f}"
    )
    print(
        f"{'Changed input':20} {'Multiplier':>10} {'Optimal Q':>12} {'Old-policy penalty':>20}"
    )
    for row in report["scenarios"]:
        if row["multiplier"] in (0.5, 1.0, 2.0):
            print(
                f"{PARAMETERS[row['parameter']]:20} {row['multiplier']:9.1f}x {row['order_quantity']:12.2f} {row['extra_cost_percent']:19.2f}%"
            )
    print(f"\nInteractive report: {html_path}\nNumeric results: {json_path}")


if __name__ == "__main__":
    main()
