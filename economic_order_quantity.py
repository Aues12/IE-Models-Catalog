import math

class Economic_Order_Quantity:
    """
    A class to calculate inventory management metrics like
    Economic Order Quantity (EOQ) and Reorder Point (ROP).
    """
    def __init__(
        self,
        annual_demand: float,
        order_cost: float,
        holding_cost: float,
    ):
        """
        Initializes the Economic_Order_Quantity calculator.

        Args:
            annual_demand: The total annual demand for the product.
            order_cost: The cost to place a single order.
            holding_cost: The cost to hold one unit of inventory for a year.
        """
        if annual_demand < 0 or order_cost < 0 or holding_cost < 0:
            raise ValueError("Inputs cannot be negative.")
        self.annual_demand = annual_demand
        self.order_cost = order_cost
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
        
        return math.sqrt((2 * self.annual_demand * self.order_cost) / self.holding_cost)

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

        daily_demand = self.annual_demand / days_of_operation
        reorder_point = (daily_demand * lead_time) + safety_stock
        return reorder_point

if __name__ == "__main__":
    # --- Example Usage ---
    inventory_system = Economic_Order_Quantity(
        annual_demand=1000,   # 1000 units per year
        order_cost=50,        # $50 per order
        holding_cost=2.5      # $2.50 per unit per year
    )

    # 1. Calculate Economic Order Quantity
    eoq = inventory_system.calculate_eoq()
    print(f"Economic Order Quantity (EOQ): {eoq:.2f} units")

    # 2. Calculate Reorder Point
    reorder_point = inventory_system.calculate_reorder_point(
        lead_time=7,          # 7-day lead time
        safety_stock=20       # 20 units of safety stock
    )
    print(f"Reorder Point (ROP): {reorder_point:.2f} units")

    # 3. Calculate Reorder Point based on business days (e.g., 252)
    reorder_point_biz_days = inventory_system.calculate_reorder_point(
        lead_time=7, safety_stock=20, days_of_operation=252
    )
    print(f"Reorder Point (ROP) for business days: {reorder_point_biz_days:.2f} units")