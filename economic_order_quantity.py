import math

class Basic_EOQ:
    """
    A class to represent the Economic Order Quantity (EOQ) model.
    Basic version of the EOQ Model.
    """

    def __init__(
        
        self,
        demand_rate: float,         # annual or period demand (D)
        ordering_cost: float,      # setup cost (S)
        holding_cost: float,       # holding cost per unit per year (H) 
        lead_time = None,          # lead time parameter (L)
        holding_cost_per = None    # holding cost percentage
                 ):
        """
        Initializes a EOQ model.
        Can represent various inventory management scenarios.

        Core Parameters:
        * demand_rate (float): Annual or period demand for the product.
        * ordering_cost (float): Cost of placing one order.
        * holding_cost (float): Annual holding cost per unit.
        * holding_cost_per: Holding cost percentage. Is multiplied with unit cost to find the holding cost.

        Optional Parameters (for EOQ variations):
        * production_rate (float): Production rate if using EPQ model.
        * shortage_cost (float): Cost per unit of backordering or stockout.
        * discount_scheme (dict/list): Quantity discount structure.
        * lead_time (float): Lead time for reorder point calculation.

        Stores all input parameters in `self.params` for easy reference and further calculations.

        """
        
        self.demand_rate = demand_rate
        self.ordering_cost = ordering_cost
        self.holding_cost = holding_cost

        self.lead_time = lead_time
        

    def calculate_eoq(self):
        """
        Calculates the Economic Order Quantity (EOQ) for a given set of parameters.

        Args:
            demand_rate (float): The annual demand for the product.
            ordering_cost (float): The cost of placing one order.
            holding_cost (float): The annual cost of holding one unit in inventory.

        Returns:
            float: The Economic Order Quantity (EOQ).
        """
        D = self.demand_rate
        H = self.holding_cost
        S = self.ordering_cost
        

        if D < 0 or S < 0 or H < 0:
            raise ValueError("All input parameters must be non-negative.")
        if H == 0:
            raise ValueError("Holding cost cannot be zero, as it would lead to infinite EOQ.")

        eoq = math.sqrt(2 * D * S / H)
        return eoq

        

    def calculate_reorder_point(
        self,
        lead_time,
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
        if lead_time is not None:
            if lead_time < 0 or safety_stock < 0:
                raise ValueError("Lead time and safety stock cannot be negative.")
            if days_of_operation <= 0:
                raise ValueError("Days of operation must be a positive number.")

            daily_demand = self.demand_rate / days_of_operation
            reorder_point = (daily_demand * lead_time) + safety_stock
            
            return reorder_point
        

class EPQ(Basic_EOQ):
    """
    A class to represent the Economic Production Quantity (EPQ) model.

    An EOQ Model that takes gradual production vs. stock quantity relationship into account.
    """

    def __init__(self,
                demand_rate: float,             # annual or period demand (D)
                ordering_cost: float,      # setup cost (S)
                holding_cost: float,       # holding cost per unit per year (H)
                production_rate: float,     # production rate parameter (P)
                holding_cost_per = None,    # holding cost percentage
                 ):
        
        # Calls - Basic EOQ - parent class
        super().__init__(
            demand_rate,             # annual or period demand (D)
            ordering_cost,      # setup cost (S)
            holding_cost,       # holding cost per unit per year (H)
            holding_cost_per,    # holding cost percentage 
                        )
        
        self.production_rate = production_rate

    
    def calculate_epq(self):
        """
        Calculates the Economic Production Quantity (EPQ) for a given set of parameters.

        Args:
            demand_rate (float): The annual demand for the product.
            ordering_cost (float): The cost of placing one order.
            holding_cost (float): The annual cost of holding one unit in inventory.
            production_rate (float): The annual production rate for the product.

        Returns:
            float: The Economic Production Quantity (EOpQ).
        """

        if self.production_rate <= self.demand_rate:
            raise ValueError("Production rate (P) must be greater than demand rate (D).")

        D = self.demand_rate
        H = self.holding_cost
        S = self.ordering_cost
        P = self.production_rate
        

        if D < 0 or S < 0 or H < 0:
            raise ValueError("All input parameters must be non-negative.")
        if H == 0:
            raise ValueError("Holding cost cannot be zero, as it would lead to infinite EOQ.")

        epq = math.sqrt((2 * D * S / H) * (P / (P - D)))
        return epq


    
