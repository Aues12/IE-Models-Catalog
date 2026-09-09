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


class InfeasiblePlanError(ValueError):
    """Valid inputs admit no plan under the requested operational constraints."""


@dataclass(frozen=True)
class OrderConstraints:
    """EOQ bounds in items; optional integer quantities or whole-item pack multiples.

    Bounds are inclusive. A pack multiple already implies an integer quantity.
    These are per-order constraints, not shared inventory or production capacity.
    """

    min_quantity: float = 0.0
    max_quantity: float | None = None
    integer: bool = False
    order_multiple: int | None = None

    def __post_init__(self):
        validate_number("min_quantity", self.min_quantity)
        if self.max_quantity is not None:
            validate_number("max_quantity", self.max_quantity, positive=True)
            if self.max_quantity < self.min_quantity:
                raise ValueError("max_quantity must be at least min_quantity.")
        if not isinstance(self.integer, bool):
            raise ValueError("integer must be a boolean.")
        if self.order_multiple is not None and (
            isinstance(self.order_multiple, bool)
            or not isinstance(self.order_multiple, int)
            or self.order_multiple < 1
        ):
            raise ValueError("order_multiple must be a positive integer.")

    def candidates(self, lower: float, upper: float, optimum: float) -> list[float]:
        """Return convex-tier candidates within [lower, upper) and global bounds."""
        lo = max(lower, self.min_quantity)
        hi = min(
            upper, self.max_quantity if self.max_quantity is not None else math.inf
        )
        if lo > hi or lo >= upper:
            return []
        step = self.order_multiple or (1 if self.integer else None)
        if step:
            first = max(1, math.ceil(lo / step))
            last = math.floor(hi / step) if math.isfinite(hi) else math.inf
            if math.isfinite(upper):
                last = min(last, math.ceil(upper / step) - 1)
            if first > last:
                return []
            indices = {
                max(first, min(last, math.floor(optimum / step))),
                max(first, min(last, math.ceil(optimum / step))),
            }
            return [float(index * step) for index in sorted(indices)]
        quantity = min(max(optimum, lo), hi)
        return [quantity] if 0 < quantity < upper else []
