import math

class Economic_Order_Quantity:
    """
    A class to calculate inventory management metrics like
    Economic Order Quantity (EOQ) and Reorder Point (ROP).
    """
    def __init__(
            
        self,
        demand_rate,             # annual or period demand (D)
        ordering_cost,      # setup cost (S)
        holding_cost,       # holding cost per unit per year (H)
        production_rate=None,  # (P) parameter if the model is EPQ
        shortage_cost=None,    # penalty cost if shortages allowed
        discount_scheme=None,  # dict or list for quantity discounts
        lead_time=0,           # reorder point calc

                 ):
        """
        Initializes a EOQ model.
        Can represent various inventory management scenarios.

        Core Parameters:
        * demand_rate (float): Annual or period demand for the product.
        * ordering_cost (float): Cost of placing one order.
        * holding_cost (float): Annual holding cost per unit.

        Optional Parameters (for EOQ variations):
        * production_rate (float): Production rate if using EPQ model.
        * shortage_cost (float): Cost per unit of backordering or stockout.
        * discount_scheme (dict/list): Quantity discount structure.
        * lead_time (float): Lead time for reorder point calculation.

        Stores all input parameters in `self.params` for easy reference and further calculations.

        """
        self.params = locals()
        self.demand_rate = demand_rate
        self.ordering_cost = ordering_cost
        self.holding_cost = holding_cost

    def calculate_eoq(self) -> float:
        """
        Calculates the Economic Order Quantity (EOQ).

        EOQ is the ideal order quantity to minimize inventory costs.

        Returns:
            The Economic Order Quantity.
        """
        if self.holding_cost == 0:
            return float('inf')
        
        return math.sqrt((2 * self.demand_rate * self.ordering_cost) / self.holding_cost)

    def calculate_reorder_point(
        self,
        lead_time: float,
        safety_stock: float = 0,
        days_of_operation: int = 365,
    ) -> float:
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
        if lead_time < 0 or safety_stock < 0:
            raise ValueError("Lead time and safety stock cannot be negative.")
        if days_of_operation <= 0:
            raise ValueError("Days of operation must be a positive number.")

        daily_demand = self.demand_rate / days_of_operation
        reorder_point = (daily_demand * lead_time) + safety_stock
        return reorder_point

if __name__ == "__main__":
    # --- Example Usage ---
    inventory_system = Economic_Order_Quantity(
        demand_rate=1000,   # 1000 units per year
        ordering_cost=50,        # $50 per order
        holding_cost=2.5      # $2.50 per unit per year
    )

    print(f"Demand is {inventory_system.demand_rate} units per year")
    print(f"Ordering cost is {inventory_system.ordering_cost}")
    print(f"Holding cost is {inventory_system.holding_cost}")

    # 1. Calculate Economic Order Quantity
    eoq = inventory_system.calculate_eoq()
    print(f"Economic Order Quantity (EOQ): {eoq:.2f} units")

    # 2. Calculate Reorder Point
    reorder_point = inventory_system.calculate_reorder_point(
        lead_time=7,          # 7-day lead time
        safety_stock=20       # 20 units of safety stock
    )
    print(f"Reorder Point (ROP): {reorder_point:.2f} days")

    # 3. Calculate Reorder Point based on business days (e.g., 252)
    reorder_point_biz_days = inventory_system.calculate_reorder_point(
        lead_time=7, safety_stock=20, days_of_operation=252
    )
    print(f"Reorder Point (ROP) for business days: {reorder_point_biz_days:.2f} days")
