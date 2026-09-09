"""Compare dynamic lot-sizing methods on identical, deterministic scenarios.

Run: python -m examples.compare_methods
"""

import argparse
import json
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dynamic_models import DLSInput, DynamicLotSizing

METHODS = ("wagner-whitin", "silver-meal")
COLORS = ("#2563eb", "#ea580c")
SCENARIOS = (
    ("Small example", DLSInput([10, 20, 30], 100, 1)),
    ("Growing demand", DLSInput([10, 20, 30, 40, 50, 60], 100, 1)),
    (
        "Intermittent demand + initial stock",
        DLSInput([15, 0, 60, 10, 0, 80], 100, 1, 35),
    ),
)


def compare():
    """Return inputs and both plans, using Wagner–Whitin as the cost reference."""
    records = []
    for name, data in SCENARIOS:
        solver = DynamicLotSizing(data)
        results = [solver.solve(method) for method in METHODS]
        optimum = results[0].total_cost
        for method, result in zip(METHODS, results):
            difference = result.total_cost - optimum
            # A percentage relative to zero is undefined; retain absolute cost.
            gap = 100 * difference / optimum if optimum else None
            records.append(
                {
                    "scenario": name,
                    "method": method,
                    "demand": data.demand,
                    "initial_inventory": data.initial_inventory,
                    "ordering_cost_per_order": data.ordering_cost,
                    "holding_cost_per_unit_period": data.holding_cost,
                    "order_quantities": result.order_quantities,
                    "order_periods": result.order_periods,
                    "inventory_levels": result.inventory_levels,
                    "order_count": len(result.order_periods),
                    "ordering_cost": result.costs.ordering,
                    "holding_cost": result.costs.holding,
                    "total_cost": result.total_cost,
                    "cost_gap": difference,
                    "cost_gap_percent": gap,
                }
            )
    return records


def make_figure(records):
    titles = ["Cost over each scenario's full horizon"]
    for name, _ in SCENARIOS:
        titles.extend([f"{name}: orders", "End-of-period inventory"])
    fig = make_subplots(
        rows=4,
        cols=2,
        specs=[[{"type": "table", "colspan": 2}, None]] + [[{}, {}] for _ in SCENARIOS],
        row_heights=[0.30, 0.233, 0.233, 0.234],
        vertical_spacing=0.08,
        subplot_titles=titles,
    )
    fig.add_trace(
        go.Table(
            header=dict(
                values=[
                    "Scenario",
                    "Method",
                    "Total",
                    "Ordering",
                    "Holding",
                    "Orders",
                    "Gap (%)",
                ],
                fill_color="#dbeafe",
                align="left",
            ),
            cells=dict(
                values=[
                    [r["scenario"] for r in records],
                    [r["method"] for r in records],
                    *[
                        [f"{r[key]:.2f}" for r in records]
                        for key in ("total_cost", "ordering_cost", "holding_cost")
                    ],
                    [r["order_count"] for r in records],
                    [
                        f"{r['cost_gap_percent']:.2f}"
                        if r["cost_gap_percent"] is not None
                        else "N/A"
                        for r in records
                    ],
                ],
                align="left",
                height=36,
            ),
            columnwidth=[230, 120, 65, 65, 65, 55, 65],
        ),
        row=1,
        col=1,
    )
    for index, (name, data) in enumerate(SCENARIOS, start=2):
        periods = list(range(1, len(data.demand) + 1))
        for method, color in zip(METHODS, COLORS):
            record = next(
                r for r in records if r["scenario"] == name and r["method"] == method
            )
            fig.add_trace(
                go.Bar(
                    x=periods,
                    y=record["order_quantities"],
                    name=method,
                    marker_color=color,
                    legendgroup=method,
                    showlegend=index == 2,
                ),
                row=index,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=periods,
                    y=record["inventory_levels"],
                    name=method,
                    mode="lines+markers",
                    line=dict(color=color),
                    legendgroup=method,
                    showlegend=False,
                ),
                row=index,
                col=2,
            )
        fig.add_trace(
            go.Scatter(
                x=periods,
                y=data.demand,
                name="Demand",
                mode="lines+markers",
                line=dict(color="#475569", dash="dot"),
                legendgroup="demand",
                showlegend=index == 2,
            ),
            row=index,
            col=1,
        )
        for column in (1, 2):
            fig.update_xaxes(
                title_text="Period (1-based)", dtick=1, row=index, col=column
            )
            fig.update_yaxes(
                title_text="Units", rangemode="tozero", row=index, col=column
            )
    fig.update_layout(
        title=dict(
            text="Wagner–Whitin and Silver–Meal | same inputs, different plans", y=0.98
        ),
        template="plotly_white",
        height=1450,
        width=1200,
        barmode="group",
        margin=dict(t=100, b=110),
        legend=dict(orientation="h", y=1.035, x=0),
    )
    fig.add_annotation(
        x=0,
        y=-0.08,
        xref="paper",
        yref="paper",
        showarrow=False,
        xanchor="left",
        text="Synthetic scenarios; costs exclude purchases. Compare methods within each scenario.<br>"
        "Gap = (method cost − Wagner–Whitin cost) / Wagner–Whitin cost. Inventory points are period-end balances.",
    )
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("examples/output"))
    args = parser.parse_args()
    records = compare()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "method_comparison.json"
    html_path = args.output_dir / "method_comparison.html"
    json_path.write_text(
        json.dumps(records, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    make_figure(records).write_html(html_path, include_plotlyjs=True, auto_open=False)
    print(f"{'Scenario':36} {'Method':15} {'Cost':>8} {'Orders':>7} {'Gap':>8}")
    for r in records:
        gap = (
            f"{r['cost_gap_percent']:.2f}%"
            if r["cost_gap_percent"] is not None
            else "N/A"
        )
        print(
            f"{r['scenario']:36} {r['method']:15} {r['total_cost']:8.2f} {r['order_count']:7} {gap:>8}"
        )
    print(f"\nInteractive report: {html_path}\nNumeric results: {json_path}")


if __name__ == "__main__":
    main()
