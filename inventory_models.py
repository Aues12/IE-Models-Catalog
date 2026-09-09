import math
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

from model_common import CostBreakdown, validate_number


@dataclass(frozen=True)
class EOQResult:
    """Continuous-quantity optimum; costs and cycle time use one demand period."""

    order_quantity: float
    unit_price: float
    cycle_time: float
    max_inventory: float
    max_backorder: float
    costs: CostBreakdown

    @property
    def total_cost(self) -> float:
        return self.costs.total_cost


class BasicEOQ:
    """
    A class to represent the Economic Order Quantity (EOQ) model.
    Basic version of the EOQ Model.
    """

    def __init__(
        self,
        price: float,  # the price of the product
        demand_rate: float,  # annual or period demand (D)
        ordering_cost: float,  # setup cost (S)
        holding_rate: float = 0.25,  # holding cost percentage
        lead_time=None,  # lead time parameter (L)
    ):
        """
        Initializes an EOQ model.
        Can represent various inventory management scenarios.

        Core Parameters:
        * price (float): The price of the product
        * demand_rate (float): Annual or period demand for the product.
        * ordering_cost (float): Cost of placing one order.
        * holding_rate (float): Holding cost percentage. Is multiplied with unit cost to find the holding cost.
        * lead_time (float): Lead time for reorder point calculation.

        """
        for name, value in (
            ("price", price),
            ("demand_rate", demand_rate),
            ("ordering_cost", ordering_cost),
            ("holding_rate", holding_rate),
        ):
            validate_number(name, value, positive=True)
        if lead_time is not None:
            validate_number("lead_time", lead_time)

        self.price = price
        self.demand_rate = demand_rate
        self.ordering_cost = ordering_cost
        self.holding_rate = holding_rate

        self.lead_time = lead_time
        self.eoq_value = None

    @property
    def holding_cost(self) -> float:
        return self.price * self.holding_rate

    def _unit_price(self, quantity: float) -> float:
        return self.price

    def _stock_limits(self, quantity: float) -> tuple[float, float]:
        return quantity, 0.0

    def calculate_costs(self, quantity: float) -> CostBreakdown:
        """Return purchase, ordering, holding and shortage costs per demand period."""
        validate_number("quantity", quantity, positive=True)
        price = self._unit_price(quantity)
        maximum, backlog = self._stock_limits(quantity)
        # Backorders and on-hand stock each occupy a fraction of the cycle.
        if backlog:
            average_inventory = maximum**2 / (2 * quantity)
            shortage = self.shortage_cost * backlog**2 / (2 * quantity)
        else:
            average_inventory = maximum / 2
            shortage = 0.0
        return CostBreakdown(
            purchase=self.demand_rate * price,
            ordering=self.demand_rate * self.ordering_cost / quantity,
            holding=average_inventory * price * self.holding_rate,
            shortage=shortage,
        )

    def solve(self) -> EOQResult:
        """Return the optimum and a common, structured cost breakdown.

        Quantities are continuous. Cycle time is in demand periods, not days.
        Total cost includes purchase cost for all EOQ-family models.
        """
        quantity = self.calculate_eoq()
        maximum, backlog = self._stock_limits(quantity)
        return EOQResult(
            order_quantity=quantity,
            unit_price=self._unit_price(quantity),
            cycle_time=quantity / self.demand_rate,
            max_inventory=maximum,
            max_backorder=backlog,
            costs=self.calculate_costs(quantity),
        )

    def calculate_eoq(self, analysis_mode: bool = False):
        """
        Calculates the Economic Order Quantity (EOQ) for a given set of parameters.

        Args:
            demand_rate (float): The annual demand for the product.
            ordering_cost (float): The cost of placing one order.
            holding_cost (float): The annual cost of holding one unit in inventory.
            analysis_mode (bool): If True, prints detailed calculation steps. Defaults to False.

        Returns:
            float: The Economic Order Quantity (EOQ).
        """
        D = self.demand_rate
        H = self.holding_cost
        S = self.ordering_cost

        eoq = math.sqrt(2 * D * S / H)

        self.eoq_value = eoq  # Store EOQ value for later use

        if analysis_mode:
            print("--- EOQ Calculation Analysis ---")
            print(f"Demand Rate (D): {D}")
            print(f"Ordering Cost (S): {S}")
            print(f"Holding Cost (H): {H}")
            print(f"Formula: math.sqrt(2 * {D} * {S} / {H})")
            print(f"Economic Order Quantity (EOQ): {eoq}")
            print("-----------------------------------")

        return eoq

    def calculate_reorder_point(
        self,
        lead_time,
        safety_stock: float = 0,
        days_of_operation: int = 365,
    ):
        """
        Calculates the Reorder Point (ROP).

        ROP is the inventory level at which a new order should be placed.

        The formula used is:

        ROP = (Daily Demand * Lead Time) + Safety Stock

        where Daily Demand = Annual Demand / Days of Operation.

        Args:
            lead_time: The time (in days) between placing an order and receiving it.
            safety_stock: Extra stock to prevent stockouts. Defaults to 0.
            days_of_operation: The number of operating days in a year. Defaults to 365.

        Returns:
            The reorder point in units.
        """
        validate_number("lead_time", lead_time)
        validate_number("safety_stock", safety_stock)
        validate_number("days_of_operation", days_of_operation, positive=True)
        self.lead_time = lead_time
        return self.demand_rate / days_of_operation * lead_time + safety_stock

    def inventory_level(
        self, t, analysis_mode: bool = False, *, days_of_operation: float = 365
    ):
        """Return stock at elapsed operating days within a repeating cycle."""
        validate_number("days_of_operation", days_of_operation, positive=True)
        t = np.asarray(t, dtype=float)
        if not np.all(np.isfinite(t)) or np.any(t < 0):
            raise ValueError("t must contain finite, non-negative times.")
        t = t / days_of_operation
        D = self.demand_rate
        Q = self.calculate_eoq()
        T = Q / D
        if analysis_mode:
            print("--- Inventory Level Calculation Analysis ---")
            print(f"Demand Rate (D): {D}")
            print(f"Economic Order Quantity (Q): {Q}")
            print(f"Cycle Time (T) (days): {T * days_of_operation}")
            print(f"Time (t) (days): {t * days_of_operation}")
            print(f"Inventory Level at time t: {Q - D * (t % T)}")
        return Q - D * (t % T)

    def graph(self, renderer: str = "plotly"):
        # X is for days
        X = np.arange(1, 366, 1)
        Y = self.inventory_level(X)

        if renderer == "matplotlib":
            plt.title("Inventory Level Over Time")
            plt.plot(X, Y)
            plt.xlabel("Days")
            plt.ylabel("Inventory Level")
            plt.grid()
            plt.show()

        if renderer == "plotly":
            my_graph = px.line(
                x=X,
                y=Y,
                title="Inventory Level Over Time",
                labels={"x": "Days", "y": "Inventory Level"},
            )
            my_graph.show()


class EPQ(BasicEOQ):
    """
    A class to represent the Economic Production Quantity (EPQ) model.

    An EOQ Model that takes gradual production vs. stock quantity relationship into account.
    """

    def __init__(
        self,
        price: float,  # the price of the product
        demand_rate: float,  # annual or period demand (D)
        ordering_cost: float,  # setup cost (S)
        production_rate: float,  # production rate parameter (P)
        holding_rate: float = 0.25,  # holding cost percentage
        lead_time=None,
    ):

        # Calls - Basic EOQ - parent class
        super().__init__(
            price=price,
            demand_rate=demand_rate,
            ordering_cost=ordering_cost,
            holding_rate=holding_rate,
            lead_time=lead_time,
        )

        validate_number("production_rate", production_rate, positive=True)
        if production_rate <= demand_rate:
            raise ValueError("Production rate must be greater than demand rate.")

        self.production_rate = production_rate

    def _stock_limits(self, quantity: float) -> tuple[float, float]:
        return quantity * (1 - self.demand_rate / self.production_rate), 0.0

    def calculate_eoq(self, analysis_mode: bool = False):
        """
        Calculates the Economic Production Quantity (EPQ) for a given set of parameters.

        Args:
            demand_rate (float): The annual demand for the product.
            ordering_cost (float): The cost of placing one order.
            holding_cost (float): The annual cost of holding one unit in inventory.
            production_rate (float): The annual production rate for the product.
            analysis_mode (bool): If True, prints detailed calculation steps. Defaults to False.

        Returns:
            float: The Economic Production Quantity (EPQ).
        """

        if analysis_mode:
            print("--- EPQ Calculation Analysis ---")

        if self.production_rate <= self.demand_rate:
            raise ValueError(
                "Production rate (P) must be greater than demand rate (D)."
            )

        D = self.demand_rate
        H = self.holding_cost
        S = self.ordering_cost
        P = self.production_rate

        epq = math.sqrt((2 * D * S / H) * (P / (P - D)))
        self.eoq_value = epq

        if analysis_mode:
            print(f"Demand Rate (D): {D}")
            print(f"Ordering Cost (S): {S}")
            print(f"Holding Cost (H): {H}")
            print(f"Production Rate (P): {P}")
            print(f"Formula: math.sqrt((2 * {D} * {S} / {H}) * ({P} / ({P} - {D})))")
            print(f"Economic Production Quantity (EPQ): {epq}")
            print("-----------------------------------")

        return epq

    def inventory_level(
        self, t, analysis_mode: bool = False, *, days_of_operation: float = 365
    ):
        """Return stock at elapsed operating days within a repeating cycle."""
        validate_number("days_of_operation", days_of_operation, positive=True)
        t = np.asarray(t, dtype=float)
        if not np.all(np.isfinite(t)) or np.any(t < 0):
            raise ValueError("t must contain finite, non-negative times.")
        t = t / days_of_operation
        D = self.demand_rate
        P = self.production_rate
        Q = self.calculate_eoq()
        T = Q / D
        mod_t = t % T
        production_end = Q / P
        max_inventory = Q * (1 - D / P)
        # Generates arrays with truth values for production and depletion phases
        production_phase = mod_t <= production_end
        depletion_phase = mod_t > production_end

        inventory = production_phase * ((P - D) * mod_t) + depletion_phase * (
            max_inventory - D * (mod_t - production_end)
        )

        if analysis_mode:
            print("--- Inventory Level Calculation Analysis ---")
            print(f"Demand Rate (D): {D}")
            print(f"Production Rate (P): {P}")
            print(f"Economic Order Quantity (Q): {Q}")
            print(f"Cycle Time (T) (days): {T * days_of_operation}")
            print(f"Time (t) (days): {t * days_of_operation}")
            print(f"Max Inventory Level: {max_inventory}")
            print(f"Inventory Level at time t: {inventory}")

        return inventory


class DiscountEOQ(BasicEOQ):
    """
    A class to represent the Economic Order Quantity (EOQ) model with quantity discounts.

    Takes bulk discount prices into account.
    """

    def __init__(
        self,
        price: float,  # the base price of the product
        demand_rate: float,  # annual or period demand (D)
        ordering_cost: float,  # setup cost (S)
        holding_rate: float = 0.25,  # holding cost percentage
        lead_time=None,  # lead time parameter (L)
        discount_rates=None,  # discount rates as a dictionary {min_quantity: discount_rate}
    ):

        super().__init__(
            price=price,
            demand_rate=demand_rate,
            ordering_cost=ordering_cost,
            holding_rate=holding_rate,
            lead_time=lead_time,
        )

        if not isinstance(discount_rates, dict) or not discount_rates:
            raise ValueError("discount_rates must be a non-empty dictionary.")

        normalized_discounts = {0: 0.0, **discount_rates}
        for threshold, rate in normalized_discounts.items():
            validate_number("discount threshold", threshold)
            validate_number("discount rate", rate)
            if rate >= 1:
                raise ValueError("Discount rates must be less than 1.")
        tiers = sorted(normalized_discounts.items())
        if any(right[1] < left[1] for left, right in zip(tiers, tiers[1:])):
            raise ValueError("Discount rates must not decrease as quantity increases.")
        self.discount_rates = normalized_discounts
        self.sorted_discounts = tiers

    def _unit_price(self, quantity: float) -> float:
        rate = next(
            rate
            for minimum, rate in reversed(self.sorted_discounts)
            if quantity >= minimum
        )
        return self.price * (1 - rate)

    def calculate_total_cost(self, quantity, price):
        """
        Calculates the total annual inventory cost for a given quantity and price.
        Total Cost = Purchase Cost + Ordering Cost + Holding Cost
        """
        validate_number("quantity", quantity, positive=True)
        validate_number("price", price, positive=True)
        return (
            self.demand_rate * price
            + self.demand_rate / quantity * self.ordering_cost
            + quantity / 2 * price * self.holding_rate
        )

    def calculate_eoq(self, analysis_mode=False):
        """
        Calculates the optimal order quantity considering quantity discounts.
        """
        best_order_quantity = None
        min_total_cost = float("inf")
        best_unit_price = None

        quantity_breaks = [d[0] for d in self.sorted_discounts]
        if analysis_mode:
            print("Quantity Breaks: ", quantity_breaks)

        # Iterate through each discount tier
        for i in range(len(self.sorted_discounts)):
            if analysis_mode:
                print("\n")
                print("Initiating step ", i + 1, " of ", len(self.sorted_discounts))

            # Min Quantity is the discount price break
            min_qty, discount_rate = self.sorted_discounts[i]
            if analysis_mode:
                print("minimum quantity: ", min_qty, "discount rate: ", discount_rate)

            # Calculate the Discounted Price for this tier
            discounted_price = self.price * (1 - discount_rate)
            if analysis_mode:
                print("discounted price: ", discounted_price)

            # Determine the Upper Bound for the current quantity range
            # Continuous tiers are [minimum, next minimum).
            max_qty = float("inf")
            if i + 1 < len(quantity_breaks):
                max_qty = quantity_breaks[i + 1]

            # Calculate holding cost for the current price
            H = discounted_price * self.holding_rate
            # Calculate EOQ for the current price
            candidate_eoq = math.sqrt((2 * self.demand_rate * self.ordering_cost) / H)
            if analysis_mode:
                print("candidate eoq", i + 1, ": ", candidate_eoq)

            # With nondecreasing discounts, an optimum beyond this tier
            # is dominated by a candidate at a later price tier.
            order_quantity = max(candidate_eoq, min_qty)
            if order_quantity >= max_qty:
                continue

            if analysis_mode:
                print("order quantity: ", order_quantity)

            # Calculate total cost for this valid order quantity
            total_cost = self.calculate_total_cost(order_quantity, discounted_price)

            if analysis_mode:
                print("total cost: ", total_cost)

            if total_cost < min_total_cost:
                min_total_cost = total_cost
                best_order_quantity = order_quantity
                best_unit_price = discounted_price
                if analysis_mode:
                    print("Updated the minimum total cost")
            else:
                if analysis_mode:
                    print("Didn't updated the minimum total cost")

        self.eoq_value = best_order_quantity

        if analysis_mode:
            print()
            print("Best Order Quantity: ", best_order_quantity)
            print("Minimum Total Cost: ", min_total_cost)
            print("Unit Price at Best Order Quantity: ", best_unit_price)

        return best_order_quantity


class BackorderEOQ(BasicEOQ):
    """A class to represent the Economic Order Quantity (EOQ) model with planned shortages (backordering).

    Takes shortage cost into account."""

    def __init__(
        self,
        price,
        demand_rate,
        ordering_cost,
        shortage_cost,
        holding_rate=0.25,
        lead_time=None,
    ):

        # Inherits from BasicEOQ
        super().__init__(price, demand_rate, ordering_cost, holding_rate, lead_time)

        validate_number("shortage_cost", shortage_cost, positive=True)

        self.shortage_cost = (
            shortage_cost  # P: shortage/backorder cost per unit per year
        )

    def _stock_limits(self, quantity: float) -> tuple[float, float]:
        holding = self.price * self.holding_rate
        return (
            quantity * self.shortage_cost / (holding + self.shortage_cost),
            quantity * holding / (holding + self.shortage_cost),
        )

    def calculate_eoq(self, analysis_mode=False):
        """Calculates EOQ with planned shortages (backordering)

        Returns Economical Order Quantiity (Q*)."""

        D, S, H, P = (
            self.demand_rate,
            self.ordering_cost,
            self.holding_cost,
            self.shortage_cost,
        )
        Q_opt = math.sqrt((2 * D * S * (H + P)) / (H * P))
        self.eoq_value = Q_opt

        return Q_opt

    def calculate_cycle_metrics(self):
        """Returns:

        * Optimal quantity Q*,
        * Max inventory,
        * Max backorder,
        * and Annual Total Cost."""

        D, S, H, P = (
            self.demand_rate,
            self.ordering_cost,
            self.holding_cost,
            self.shortage_cost,
        )
        Q = self.calculate_eoq()
        max_inventory = (P / (H + P)) * Q
        max_backorder = (H / (H + P)) * Q
        total_cost = (
            (D * S / Q)
            + (H * max_inventory**2 / (2 * Q))
            + (P * max_backorder**2 / (2 * Q))
        )
        return {
            "Q_opt": Q,
            "S_max": max_inventory,
            "B_max": max_backorder,
            "TotalCost": total_cost,
        }

    def inventory_level(
        self, t, analysis_mode: bool = False, *, days_of_operation: float = 365
    ):
        """Return stock at elapsed operating days within a repeating cycle."""
        validate_number("days_of_operation", days_of_operation, positive=True)
        t = np.asarray(t, dtype=float)
        if not np.all(np.isfinite(t)) or np.any(t < 0):
            raise ValueError("t must contain finite, non-negative times.")
        t = t / days_of_operation
        D = self.demand_rate
        Q = self.calculate_eoq()
        H = self.holding_cost
        P = self.shortage_cost
        T = Q / D
        max_inventory = (P / (H + P)) * Q
        max_backorder = (H / (H + P)) * Q

        mod_t = t % T
        inventory_end = max_inventory / D

        # Generates arrays with truth values for inventory and backorder phases
        inventory_phase = mod_t <= inventory_end
        backorder_phase = mod_t > inventory_end

        inventory = inventory_phase * (max_inventory - D * mod_t) + backorder_phase * (
            -D * (mod_t - inventory_end)
        )

        if analysis_mode:
            print("--- Inventory Level Calculation Analysis ---")
            print(f"Demand Rate (D): {D}")
            print(f"Economic Order Quantity (Q): {Q}")
            print(f"Cycle Time (T) (days): {T * days_of_operation}")
            print(f"Time (t) (days): {t * days_of_operation}")
            print(f"Max Inventory Level: {max_inventory}")
            print(f"Max Backorder Level: {max_backorder}")
            print(f"Inventory Level at time t: {inventory}")

        return inventory
