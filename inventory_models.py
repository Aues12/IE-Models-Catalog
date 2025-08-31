import math

class Basic_EOQ:
    """
    A class to represent the Economic Order Quantity (EOQ) model.
    Basic version of the EOQ Model.
    """

    def __init__(
        self,
        price: float,           # the price of the product
        demand_rate: float,     # annual or period demand (D)
        ordering_cost: float,   # setup cost (S)
        holding_rate: float = 0.25, # holding cost percentage
        lead_time = None            # lead time parameter (L)
    ):
        """
        Initializes a EOQ model.
        Can represent various inventory management scenarios.

        Core Parameters:
        * price (float): The price of the product
        * demand_rate (float): Annual or period demand for the product.
        * ordering_cost (float): Cost of placing one order.
        * holding_rate (float): Holding cost percentage. Is multiplied with unit cost to find the holding cost.
        * lead_time (float): Lead time for reorder point calculation.

        """
        # Check parameter boundaries
        if demand_rate <= 0 or ordering_cost < 0 or price <= 0 or holding_rate <= 0:
            raise ValueError("All core parameters (demand_rate, price, holding_rate, ordering_cost) must be positive.")
        
        self.price = price
        self.demand_rate = demand_rate
        self.ordering_cost = ordering_cost
        self.holding_rate = holding_rate
        self.holding_cost = self.price * self.holding_rate

        self.lead_time = lead_time
        

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
        
        if analysis_mode:
            print("--- EOQ Calculation Analysis ---")
            print(f"Demand Rate (D): {D}")
            print(f"Ordering Cost (S): {S}")
            print(f"Holding Cost (H): {H}")

        eoq = math.sqrt(2 * D * S / H)

        if analysis_mode:
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
        self.lead_time = lead_time
        
        if self.lead_time is not None:
            if self.lead_time < 0 or safety_stock < 0:
                raise ValueError("Lead time and safety stock cannot be negative.")
            if days_of_operation <= 0:
                raise ValueError("Days of operation must be a positive number.")

            daily_demand = self.demand_rate / days_of_operation
            reorder_point = (daily_demand * self.lead_time) + safety_stock
            
            return reorder_point
        

class EPQ(Basic_EOQ):
    """
    A class to represent the Economic Production Quantity (EPQ) model.

    An EOQ Model that takes gradual production vs. stock quantity relationship into account.
    """

    def __init__(self,
                price: float,           # the price of the product
                demand_rate: float,     # annual or period demand (D)
                ordering_cost: float,   # setup cost (S)
                production_rate: float,   # production rate parameter (P)
                holding_rate: float = 0.25,     # holding cost percentage
                lead_time = None
                ):
        
        # Calls - Basic EOQ - parent class
        super().__init__(
            price=price,
            demand_rate=demand_rate,
            ordering_cost=ordering_cost,
            holding_rate=holding_rate,
            lead_time=lead_time
                        )
        
        self.production_rate = production_rate

    
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
            raise ValueError("Production rate (P) must be greater than demand rate (D).")

        D = self.demand_rate
        H = self.holding_cost
        S = self.ordering_cost
        P = self.production_rate
        
        if analysis_mode:
            print(f"Demand Rate (D): {D}")
            print(f"Ordering Cost (S): {S}")
            print(f"Holding Cost (H): {H}")
            print(f"Production Rate (P): {P}")

        epq = math.sqrt((2 * D * S / H) * (P / (P - D)))
        
        if analysis_mode:
            print(f"Formula: math.sqrt((2 * {D} * {S} / {H}) * ({P} / ({P} - {D})))")
            print(f"Economic Production Quantity (EPQ): {epq}")
            print("-----------------------------------")

        return epq


class Discount_EOQ(Basic_EOQ):
    
    """
    A class to represent the Economic Order Quantity (EOQ) model with quantity discounts.
    
    Takes bulk discount prices into account. 
    """

    def __init__(self,
                 price: float,           # the base price of the product
                 demand_rate: float,     # annual or period demand (D)
                 ordering_cost: float,   # setup cost (S)
                 holding_rate: float = 0.25,       # holding cost percentage
                 lead_time = None,           # lead time parameter (L)
                 discount_rates = None       # discount rates as a dictionary {min_quantity: discount_rate}
                 ):
        
        super().__init__(
            price=price,
            demand_rate=demand_rate,
            ordering_cost=ordering_cost,
            holding_rate=holding_rate,
            lead_time=lead_time
                         )
        
        if not discount_rates:
            raise ValueError("discount_rates dictionary must be provided.")

        # Add the base price tier (0 quantity, 0% discount)
        if 0 not in discount_rates:
            discount_rates[0] = 0
            
        # Sort the discount tiers by quantity
        self.sorted_discounts = sorted(discount_rates.items())
        self.discount_rates = discount_rates

    def calculate_total_cost(self, quantity, price):
        """
        Calculates the total annual inventory cost for a given quantity and price.
        Total Cost = Purchase Cost + Ordering Cost + Holding Cost
        """
        purchase_cost = self.demand_rate * price
        # Prevent division by zero if quantity is zero
        ordering_cost_component = (self.demand_rate / quantity) * self.ordering_cost if quantity > 0 else 0
        holding_cost_component = (quantity / 2) * (price * self.holding_rate)
        return purchase_cost + ordering_cost_component + holding_cost_component

    def calculate_eoq(self, analysis_mode=True):
        """
        Calculates the optimal order quantity considering quantity discounts.
        """
        best_order_quantity = None
        min_total_cost = float('inf')
        best_unit_price = None

        quantity_breaks = [d[0] for d in self.sorted_discounts]
        print("Quantity Breaks: ", quantity_breaks)

        # Iterate through each discount tier
        for i in range(len(self.sorted_discounts)):
            if analysis_mode:
                print("\n")
                print("Initiating step ", i+1, " of ", len(self.sorted_discounts))

            # Min Quantity is the discount price break
            min_qty, discount_rate = self.sorted_discounts[i]
            if analysis_mode:
                print("minimum quantity: ", min_qty, "discount rate: ", discount_rate)

            # Calculate the Discounted Price for this tier
            discounted_price = self.price * (1 - discount_rate)
            if analysis_mode:
                print("discounted price: ", discounted_price)

            # Determine the Upper Bound for the current quantity range
            # Upper bound is 1 unit less then the next price break
            max_qty = float('inf')
            if i + 1 < len(quantity_breaks):
                max_qty = quantity_breaks[i+1] - 1

            # Calculate holding cost for the current price
            H = discounted_price * self.holding_rate
            if H <= 0:
                # If holding cost is zero or negative, EOQ is infinite or undefined.
                # In a practical sense, we should just consider the boundary.
                candidate_eoq = max_qty
            else:
                candidate_eoq = math.sqrt((2 * self.demand_rate * self.ordering_cost) / H)

            if analysis_mode:
                print("candidate eoq_", i+1, ": ", candidate_eoq)
            
            # Determine the valid order quantity for this tier
            if candidate_eoq > max_qty:
                order_quantity = max_qty
            elif candidate_eoq < min_qty:
                order_quantity = min_qty
            else:
                order_quantity = candidate_eoq

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

        return {
                "best_quantity": best_order_quantity,
                "min_total_cost": min_total_cost,
                "unit_price": best_unit_price
                                                    }

class Backorder_EOQ(Basic_EOQ):
    def __init__(
            self, 
            price, 
            demand_rate, 
            ordering_cost, 
            shortage_cost, 
            holding_rate=0.25, 
            lead_time=None
            ):
        
        # Inherits from Basic_EOQ
        super().__init__(price, 
                         demand_rate, 
                         ordering_cost, 
                         holding_rate, 
                         lead_time)
        
        if shortage_cost <= 0:
            raise ValueError("shortage_cost must be positive.")
        
        self.shortage_cost = shortage_cost  # P: shortage/backorder cost per unit per year

    def calculate_eoq(self, analysis_mode=False):
        """EOQ with planned shortages (backordering); returns Q*."""

        D, S, H, P = self.demand_rate, self.ordering_cost, self.holding_cost, self.shortage_cost
        Q_opt = math.sqrt((2 * D * S * (H + P)) / (H * P))
        if analysis_mode:
            print(f"Q*={Q_opt}")

        return Q_opt

    def calculate_cycle_metrics(self):
        """Return Q*, S_max (max inventory), B_max (max backorder), and annual total cost."""
        D, S, H, P = self.demand_rate, self.ordering_cost, self.holding_cost, self.shortage_cost
        Q = self.calculate_eoq()
        S_max = (P / (H + P)) * Q
        B_max = (H / (H + P)) * Q
        total_cost = (D * S / Q) + (H * S_max**2 / (2 * Q)) + (P * B_max**2 / (2 * Q))
        return {"Q_opt": Q, "S_max": S_max, "B_max": B_max, "TotalCost": total_cost}
