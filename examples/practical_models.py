"""Run from the project root: python -m examples.practical_models."""

from dynamic_models import DLSInput, DynamicLotSizing
from inventory_models import BasicEOQ, DiscountEOQ, IncrementalDiscountEOQ
from model_common import OrderConstraints


def main():
    inputs = dict(price=10, demand_rate=1000, ordering_cost=50, holding_rate=0.2)
    basic = BasicEOQ(**inputs)
    constrained = basic.solve(
        OrderConstraints(min_quantity=250, max_quantity=400, order_multiple=48)
    )
    print(f"Continuous EOQ: {basic.solve().order_quantity:.2f}")
    print(
        f"Pack order: {constrained.order_quantity:.0f}; total cost: {constrained.total_cost:.2f}"
    )
    for cls in [DiscountEOQ, IncrementalDiscountEOQ]:
        result = cls(**inputs, discount_rates={100: 0.1, 200: 0.2}).solve()
        print(
            f"{cls.__name__}: Q={result.order_quantity:.2f}, unit price={result.unit_price:.2f}, total={result.total_cost:.2f}"
        )
    data = DLSInput(
        [10, 20, 30], [100, 20, 100], [1, 2, 1], initial_inventory=10, lead_time=1
    )
    for method in ["wagner-whitin", "silver-meal"]:
        plan = DynamicLotSizing(data).solve(method)
        print(
            f"{method}: releases={plan.order_quantities}, receipts={plan.receipt_quantities}, total={plan.total_cost:.2f}"
        )


if __name__ == "__main__":
    main()
