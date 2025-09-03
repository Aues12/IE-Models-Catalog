# Wave 2: Core EOQ tests, parametrized across models with readable IDs
# Tests invalid parameters

import pytest

from inventory_models import BasicEOQ, EPQ, DiscountEOQ, BackorderEOQ

# --- Constructor validation, shared via parametrization ---------------------

@pytest.mark.parametrize("model_class, invalid_params", [
    (BasicEOQ, dict(price=0, demand_rate=1000, ordering_cost=30)),
    (BasicEOQ, dict(price=10, demand_rate=-1, ordering_cost=30)),
    (BasicEOQ, dict(price=10, demand_rate=1000, ordering_cost=-5)),
    (BasicEOQ, dict(price=10, demand_rate=1000, ordering_cost=30, holding_rate=-0.2)),
    (EPQ, dict(price=10, demand_rate=500, ordering_cost=30, holding_rate=0.25, production_rate=400)),  # P<=D
    (DiscountEOQ, dict(price=15, demand_rate=1000, ordering_cost=40, holding_rate=0.25, discount_rates={})),
    (BackorderEOQ, dict(price=9, demand_rate=800, ordering_cost=25, holding_rate=0.2, shortage_cost=0)),
], ids=[
    "BasicEOQ | price=0",
    "BasicEOQ | demand<0",
    "BasicEOQ | ordering_cost<0",
    "BasicEOQ | holding_rate<0",
    "EPQ | prod_rate<=demand",
    "DiscountEOQ | no tiers",
    "BackorderEOQ | shortage_cost<=0",
])

def test_constructor_validation(model_class, invalid_params):
    with pytest.raises(Exception):
        model_class(**invalid_params)
