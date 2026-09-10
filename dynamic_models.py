"""Deterministic lot sizing with period costs and explicit release/receipt timing."""

from dataclasses import dataclass, field
from typing import List

import numpy as np

from model_common import (
    CostBreakdown,
    InfeasiblePlanError,
    validate_count,
    validate_number,
)


@dataclass
class DLSInput:
    demand: List[float]
    ordering_cost: float | List[float]
    holding_cost: float | List[float]
    initial_inventory: float = 0.0
    lead_time: int = 0


@dataclass
class DLSResult:
    order_quantities: List[float]
    total_cost: float
    order_periods: List[int]
    costs: CostBreakdown = field(default_factory=CostBreakdown)
    inventory_levels: List[float] = field(default_factory=list)
    receipt_quantities: List[float] = field(default_factory=list)
    receipt_periods: List[int] = field(default_factory=list)

    @property
    def cost_basis(self) -> dict:
        return {
            "horizon": "planning_horizon",
            "periods": len(self.order_quantities),
            "quantity_unit": "item",
            "currency": "caller_defined",
        }


def _cost_series(name, value, periods):
    """Expand a constant rate or copy a full-horizon series without mutating input."""
    values = list(value) if isinstance(value, (list, tuple)) else [value] * periods
    if len(values) != periods:
        raise ValueError(f"{name} must have one value per demand period.")
    for number in values:
        validate_number(name, number)
    return values


class DynamicLotSizing:
    def __init__(self, data: DLSInput):
        self.data = data
        self._validate_parameters()

    def _validate_parameters(self):
        if not isinstance(self.data.demand, (list, tuple)) or not self.data.demand:
            raise ValueError("Demand must be a non-empty list or tuple.")
        self._ordering = _cost_series(
            "ordering_cost", self.data.ordering_cost, len(self.data.demand)
        )
        self._holding = _cost_series(
            "holding_cost", self.data.holding_cost, len(self.data.demand)
        )
        validate_number("initial_inventory", self.data.initial_inventory)
        self._lead_time = validate_count("lead_time", self.data.lead_time)
        for demand in self.data.demand:
            validate_number("demand", demand)

    def solve(self, method: str = "wagner-whitin") -> DLSResult:
        """Return releases, receipts and costs over the original planning horizon.

        Setup is charged at release; holding at each period end. Orders cannot
        be released before period 1. Initial stock must cover demand before the
        first possible receipt. There are no pre-existing pipeline orders.
        """
        if method not in {"wagner-whitin", "silver-meal"}:
            raise ValueError(f"Unknown method: {method}")
        self._validate_parameters()
        remaining = self.data.initial_inventory
        net_demand = []
        for demand in self.data.demand:
            consumed = min(remaining, demand)
            net_demand.append(demand - consumed)
            remaining -= consumed
        lead = self._lead_time
        if any(q > 0 for q in net_demand[:lead]):
            raise InfeasiblePlanError(
                "Initial inventory cannot cover demand before the first possible receipt; pre-horizon orders are not supported."
            )
        if method == "wagner-whitin":
            receipts = self._solve_wagner_whitin(net_demand)
        else:
            receipts = self._solve_silver_meal(net_demand)
        periods = len(net_demand)
        orders = [0.0] * periods
        for t, quantity in enumerate(receipts):
            if quantity > 0:
                orders[t - lead] = quantity
        inventory = self.data.initial_inventory
        levels = []
        for demand, receipt in zip(self.data.demand, receipts):
            inventory += receipt - demand
            if inventory < 0 and np.isclose(inventory, 0, atol=1e-10, rtol=0):
                inventory = 0.0
            levels.append(inventory)
        costs = CostBreakdown(
            ordering=sum(cost for q, cost in zip(orders, self._ordering) if q > 0),
            holding=sum(stock * cost for stock, cost in zip(levels, self._holding)),
        )
        return DLSResult(
            order_quantities=orders,
            total_cost=costs.total_cost,
            order_periods=[t + 1 for t, q in enumerate(orders) if q > 0],
            costs=costs,
            inventory_levels=levels,
            receipt_quantities=receipts,
            receipt_periods=[t + 1 for t, q in enumerate(receipts) if q > 0],
        )

    def _compute_cost_matrix(self, demand):
        """Cost of receipt i covering i..j, in quadratic time and storage."""
        periods = len(demand)
        costs = np.full((periods, periods), np.inf)
        for i in range(self._lead_time, periods):
            total = self._ordering[i - self._lead_time]
            accumulated_holding = 0.0
            for j in range(i, periods):
                if j > i:
                    accumulated_holding += self._holding[j - 1]
                total += demand[j] * accumulated_holding
                costs[i, j] = total
        return costs

    def _solve_wagner_whitin(self, demand):
        periods = len(demand)
        matrix = self._compute_cost_matrix(demand)
        min_cost = [0.0] * (periods + 1)
        best_start = [None] * (periods + 1)
        for end in range(1, periods + 1):
            if demand[end - 1] == 0:
                min_cost[end] = min_cost[end - 1]
                continue
            min_cost[end] = float("inf")
            for start in range(self._lead_time, end):
                candidate = min_cost[start] + matrix[start, end - 1]
                if candidate < min_cost[end]:
                    min_cost[end] = candidate
                    best_start[end] = start
        receipts = [0.0] * periods
        end = periods
        while end > 0:
            start = best_start[end]
            if start is None:
                end -= 1
            else:
                receipts[start] = sum(demand[start:end])
                end = start
        return receipts

    def _solve_silver_meal(self, demand):
        """Extend a receipt until average setup/holding cost first increases.

        Receipt starts at the next positive net demand. With varying setup costs
        this may miss a cheaper earlier receipt; the policy remains a heuristic.
        """
        periods = len(demand)
        receipts = [0.0] * periods
        t = 0
        while t < periods:
            if demand[t] == 0:
                t += 1
                continue
            total = self._ordering[t - self._lead_time]
            previous_average = total
            accumulated_holding = 0.0
            end = t + 1
            while end < periods:
                accumulated_holding += self._holding[end - 1]
                total += demand[end] * accumulated_holding
                average = total / (end - t + 1)
                if average > previous_average:
                    break
                previous_average = average
                end += 1
            receipts[t] = sum(demand[t:end])
            t = end
        return receipts
