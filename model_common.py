"""Shared validation and costs for inventory planning results."""

import math
from dataclasses import dataclass
from numbers import Real


def validate_number(name: str, value: float, *, positive: bool = False) -> None:
    """Reject non-real, non-finite and out-of-domain scalar inputs."""
    if (
        isinstance(value, bool)
        or not isinstance(value, Real)
        or not math.isfinite(value)
        or (value <= 0 if positive else value < 0)
    ):
        bound = "positive" if positive else "non-negative"
        raise ValueError(f"{name} must be a finite, {bound} number.")


@dataclass(frozen=True)
class CostBreakdown:
    """Costs over the result's stated horizon, in the caller's currency.

    Purchase cost is zero for dynamic models, whose inputs do not include prices.
    """

    purchase: float = 0.0
    ordering: float = 0.0
    holding: float = 0.0
    shortage: float = 0.0

    @property
    def relevant_cost(self) -> float:
        return self.ordering + self.holding + self.shortage

    @property
    def total_cost(self) -> float:
        return self.purchase + self.relevant_cost
