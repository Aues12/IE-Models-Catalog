from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class DLSInput:
    demand: List[float]
    ordering_cost: float
    holding_cost: float
    initial_inventory: float = 0.0

@dataclass
class DLSResult:
    order_quantities: List[float]
    total_cost: float
    order_periods: List[int]


class DynamicLotSizing:
    def __init__(self, data: DLSInput):
        self.data = data
        self._validate_parameters()

    def _validate_parameters(self):
        if not self.data.demand:
            raise ValueError("Demand list cannot be empty.")

        if self.data.ordering_cost < 0:
            raise ValueError("Ordering cost cannot be negative.")

        if self.data.holding_cost < 0:
            raise ValueError("Holding cost cannot be negative.")

        if any(demand < 0 for demand in self.data.demand):
            raise ValueError("Demand values cannot be negative.")

    # ------------------ Main Solver ------------------------------
    def solve(self, method: str = "wagner-whitin") -> DLSResult:
        if method == "wagner-whitin":
            return self._solve_wagner_whitin()
        elif method == "silver-meal":
            return self._solve_silver_meal()
        else:
            raise ValueError(f"Unknown method: {method}")
        

    # ------------------ Wagner-Whitin Algorithm ------------------
    def _compute_cost_matrix(self):
        demand = self.data.demand
        K = self.data.ordering_cost
        h = self.data.holding_cost

        T = len(demand)
        # Generate the cost matrix C(i, j)
        C = np.zeros((T, T))

        for i in range(T):
            for j in range(i, T):
                ordering = K
                holding = 0

                for k in range(i+1, j+1):
                    holding += demand[k] * (k - i) * h

                C[i, j] = ordering + holding

        return C
    
    def _solve_wagner_whitin(self) -> DLSResult:

        demand = self.data.demand
        T = len(demand)

        # Precompute cost of ordering at i and covering up to j
        # Cost Matrix C[i, j]
        cost_matrix = self._compute_cost_matrix()

        # F[t] = minimum cost up to period t, to satisfy demand
        # DP Vector Array
        min_cost_up_to: List[float] = [0] * (T + 1)

        # prev[t] = best starting period for the last order covering up to t
        best_starts_list: List[int] = [0] * (T + 1)

        # ---------- Forward DP ----------
        for t in range(1, T + 1):
            best_cost = float("inf")
            best_start = 0

            # Try all possible order starting points i
            for start in range(1, t + 1):
                cost_if_start_here = (
                    min_cost_up_to[start - 1] +
                    cost_matrix[start - 1][t - 1]
                ) # F[t] = F[i-1] + C[i, t]

                if cost_if_start_here < best_cost:
                    best_cost = cost_if_start_here
                    best_start = start

            min_cost_up_to[t] = best_cost
            best_starts_list[t] = best_start

        # ---------- Backtracking ----------
        order_periods = []
        t = T

        while t > 0:
            last_start = best_starts_list[t]
            order_periods.append(last_start)
            t = last_start - 1

        order_periods.reverse()

        # ---------- Compute order quantities ----------
        order_quantities: List[float] = [0] * T

        for idx, last_start in enumerate(order_periods):
            start_idx = last_start - 1

            if idx + 1 < len(order_periods):
                next_start = order_periods[idx + 1]
                end_idx = next_start - 2
            else:
                end_idx = T - 1

            total_demand = sum(demand[start_idx:end_idx + 1])
            order_quantities[start_idx] = total_demand

        return DLSResult(
            order_quantities=order_quantities,
            total_cost=min_cost_up_to[T],
            order_periods=order_periods
        )
    
    # ------------------ Silver-Meal Heuristic ------------------
    def _solve_silver_meal(self) -> DLSResult:
        """
        Silver-Meal heuristic for dynamic lot sizing.

        Returns a feasible (not necessarily optimal) ordering plan
        based on average cost minimization.
        """
        demand = self.data.demand
        K = self.data.ordering_cost
        h = self.data.holding_cost

        T = len(demand)

        order_quantities: List[float] = [0.0] * T
        order_periods: List[int] = []

        t = 0

        while t < T:
            n = 1
            prev_avg_cost = float("inf")

            while True:
                total_cost = K

                # holding cost
                for k in range(1, n):
                    if t + k >= T:
                        break
                    total_cost += demand[t + k] * k * h

                avg_cost = total_cost / n

                if avg_cost > prev_avg_cost:
                    break

                prev_avg_cost = avg_cost
                n += 1

                if t + n > T:
                    break

            n_opt = n - 1

            qty = sum(demand[t : t + n_opt])

            order_quantities[t] = qty
            order_periods.append(t + 1)

            t = t + n_opt
            
        # --- Compute cost ---
        inventory = 0.0
        total_cost = 0.0

        for t in range(T):
            order = order_quantities[t]

            if order > 0:
                total_cost += K

            inventory += order
            inventory -= demand[t]

            # holding cost applies to leftover inventory
            if inventory > 0:
                total_cost += inventory * h

        return DLSResult(
            order_quantities=order_quantities,
            total_cost=total_cost,
            order_periods=order_periods
        )
    
    
