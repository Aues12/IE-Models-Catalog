"""Validate and translate JSON requests; inventory formulas stay in the library."""

import json
import math
import sys
from dataclasses import asdict
from importlib.resources import files

from jsonschema import Draft202012Validator

from dynamic_models import DLSInput, DynamicLotSizing
from inventory_models import (
    EPQ,
    BackorderEOQ,
    BasicEOQ,
    DiscountEOQ,
    IncrementalDiscountEOQ,
)
from model_common import InfeasiblePlanError, OrderConstraints

PACKAGE = files("ie_models_agent")
CONTRACT = json.loads(PACKAGE.joinpath("contract.json").read_text(encoding="utf-8"))
REQUEST_SCHEMA = json.loads(
    PACKAGE.joinpath("schemas/request.json").read_text(encoding="utf-8")
)
RESPONSE_SCHEMA = json.loads(
    PACKAGE.joinpath("schemas/response.json").read_text(encoding="utf-8")
)
MAX_REQUEST_BYTES = CONTRACT["limits"]["max_request_bytes"]
CLASSES = {
    "basic_eoq": BasicEOQ,
    "epq": EPQ,
    "discount_eoq": DiscountEOQ,
    "incremental_discount_eoq": IncrementalDiscountEOQ,
    "backorder_eoq": BackorderEOQ,
}
ANNUAL_BASIS = {
    "horizon": "year",
    "purchase_included": True,
    "currency": "caller_defined",
}


class NumericalError(ValueError):
    """A calculation cannot be represented as finite, usable JSON numbers."""


def _costs(costs):
    return {
        **asdict(costs),
        "relevant_cost": costs.relevant_cost,
        "total_cost": costs.total_cost,
    }


def _model(params):
    inputs = dict(params["inputs"])
    if params["model"] in {"discount_eoq", "incremental_discount_eoq"}:
        tiers = inputs.pop("discount_tiers")
        thresholds = [tier["minimum_quantity"] for tier in tiers]
        if len(set(thresholds)) != len(thresholds):
            raise ValueError("discount_tiers minimum_quantity values must be unique.")
        inputs["discount_rates"] = {
            tier["minimum_quantity"]: tier["discount_rate"] for tier in tiers
        }
    model = CLASSES[params["model"]](**inputs)
    if not math.isfinite(model.holding_cost) or model.holding_cost <= 0:
        raise NumericalError(
            "Derived holding cost is outside the supported numeric range."
        )
    return model


def _solve_eoq(params):
    constraints = (
        OrderConstraints(**params["constraints"]) if "constraints" in params else None
    )
    result = _model(params).solve(constraints=constraints)
    if not result.order_quantity or result.order_quantity <= 0:
        raise NumericalError("Optimal quantity is outside the supported numeric range.")
    return {
        **asdict(result),
        **({"constraints": asdict(constraints)} if constraints is not None else {}),
        "model": params["model"],
        "costs": _costs(result.costs),
        "total_cost": result.total_cost,
        "cost_basis": dict(ANNUAL_BASIS),
        "guarantee": "exact_under_assumptions",
    }


def _evaluate_eoq(params):
    costs = _model(params).calculate_costs(params["quantity"])
    return {
        "model": params["model"],
        "quantity": params["quantity"],
        "costs": _costs(costs),
        "total_cost": costs.total_cost,
        "cost_basis": dict(ANNUAL_BASIS),
    }


def _reorder_point(params):
    days = params.get("days_of_operation", 365)
    value = _model(params).calculate_reorder_point(
        params["lead_time"], params.get("safety_stock", 0), days
    )
    return {
        "model": params["model"],
        "reorder_point": value,
        "unit": "items",
        "lead_time_days": params["lead_time"],
        "days_of_operation": days,
    }


def _inventory_profile(params):
    days = params.get("days_of_operation", 365)
    inventory = _model(params).inventory_level(
        params["times"],
        days_of_operation=days,
        constraints=OrderConstraints(**params["constraints"])
        if "constraints" in params
        else None,
    )
    return {
        "model": params["model"],
        "times": list(params["times"]),
        "inventory_levels": inventory.tolist(),
        "time_unit": "operating_days",
        "inventory_unit": "items",
        "days_of_operation": days,
    }


def _dynamic_plan(params, method):
    data = DLSInput(
        demand=list(params["demand"]),
        ordering_cost=params["ordering_cost"],
        holding_cost=params["holding_cost"],
        initial_inventory=params.get("initial_inventory", 0),
        lead_time=params.get("lead_time", 0),
    )
    result = DynamicLotSizing(data).solve(method)
    return {
        **asdict(result),
        "method": method,
        "costs": _costs(result.costs),
        "guarantee": "heuristic"
        if method == "silver-meal"
        else "exact_under_assumptions",
        "cost_basis": {
            "horizon": "input_horizon",
            "periods": len(data.demand),
            "period_unit": params.get("period_unit", "period"),
            "purchase_included": False,
            "currency": "caller_defined",
        },
    }


def _compare_dynamic(params):
    plans = [
        _dynamic_plan(params, method) for method in ("wagner-whitin", "silver-meal")
    ]
    reference = plans[0]["total_cost"]
    difference = plans[1]["total_cost"] - reference
    return {
        "plans": plans,
        "reference_method": "wagner-whitin",
        "absolute_cost_gap": difference,
        "relative_cost_gap_percent": difference / reference * 100
        if reference
        else None,
    }


HANDLERS = {
    "list_models": lambda params: {
        "models": CONTRACT["models"],
        "limits": CONTRACT["limits"],
    },
    "solve_eoq": _solve_eoq,
    "evaluate_eoq": _evaluate_eoq,
    "reorder_point": _reorder_point,
    "inventory_profile": _inventory_profile,
    "solve_dynamic": lambda params: _dynamic_plan(
        params, params.get("method", "wagner-whitin")
    ),
    "compare_dynamic": _compare_dynamic,
}


def _error(code, message, error_type="ValueError"):
    return {
        "success": False,
        "message": message,
        "error": {"type": error_type, "code": code, "message": message},
    }


def _validate_request(request):
    # JSON schema numbers do not by themselves exclude Python's NaN/Infinity.
    encoded = json.dumps(request, allow_nan=False)
    if len(encoded.encode("utf-8")) > MAX_REQUEST_BYTES:
        raise ValueError(f"Request exceeds {MAX_REQUEST_BYTES} bytes.")
    if not isinstance(request, dict) or set(request) - {"operation", "params", "meta"}:
        raise ValueError(
            "Request must be an object with only operation, params, and optional meta."
        )
    operation = request.get("operation")
    if not isinstance(operation, str) or operation not in HANDLERS:
        raise ValueError(
            "Unknown operation; use list_models and the operation list in SKILL.yaml."
        )
    if "params" not in request or not isinstance(request["params"], dict):
        raise ValueError("params must be an explicit object.")
    # Select by the validated operation for errors narrower than the outer oneOf.
    variant = next(
        v
        for v in REQUEST_SCHEMA["oneOf"]
        if v["properties"]["operation"]["const"] == operation
    )
    validator = Draft202012Validator({**variant, "$defs": REQUEST_SCHEMA["$defs"]})
    errors = list(validator.iter_errors(request))
    if errors:
        # Avoid echoing potentially large/sensitive caller values in error messages.
        error = errors[0]
        path = ".".join(str(p) for p in error.absolute_path) or "request"
        raise ValueError(
            f"Invalid {path}: {error.validator} constraint failed; consult SKILL.yaml."
        )
    return operation, request["params"]


def run(request: dict) -> dict:
    """Execute a bounded JSON request and return a fresh success/error envelope.

    No files supplied by the caller are read or written. Errors are data; this
    function never exits the process. Caller meta is validated but not echoed.
    """
    try:
        operation, params = _validate_request(request)
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        return _error("INVALID_REQUEST", str(exc))
    try:
        result = HANDLERS[operation](params)
        response = {
            "success": True,
            "message": f"Completed {operation}.",
            "result": result,
            "meta": {
                "operation": operation,
                "contract_version": CONTRACT["contract_version"],
            },
        }
        try:
            serialized = json.dumps(response, allow_nan=False)
        except (ValueError, OverflowError) as exc:
            raise NumericalError(
                "Result contains a non-finite value; rescale the inputs."
            ) from exc
        # Fresh plain JSON values; no caller can mutate shared contract metadata.
        response = json.loads(serialized)
        if not Draft202012Validator(RESPONSE_SCHEMA).is_valid(response):
            raise NumericalError(
                "Result violates the numeric/result contract; inspect input scale."
            )
        return response
    except InfeasiblePlanError as exc:
        return _error("INFEASIBLE_PLAN", str(exc), type(exc).__name__)
    except (NumericalError, ArithmeticError) as exc:
        return _error("NUMERICAL_ERROR", str(exc), type(exc).__name__)
    except (ValueError, TypeError) as exc:
        return _error("INVALID_REQUEST", str(exc), type(exc).__name__)
    except Exception:
        return _error(
            "EXECUTION_ERROR",
            "Unexpected execution failure; report a reproducible request.",
            "RuntimeError",
        )


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object keys are not permitted.")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError("JSON numeric values must be finite.")


def main() -> None:
    """Read one UTF-8 JSON document (at most 1 MiB) and emit one envelope."""
    try:
        raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
        if not raw.strip() or len(raw) > MAX_REQUEST_BYTES:
            raise ValueError("Expected one non-empty JSON request of at most 1 MiB.")
        request = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_invalid_constant,
        )
    except (ValueError, UnicodeError, RecursionError):
        response = _error(
            "INVALID_JSON",
            "Expected one UTF-8 JSON object, at most 1 MiB, without duplicate keys or non-finite numbers.",
        )
        code = 2
    else:
        response = run(request)
        code = (
            0
            if response["success"]
            else (
                1
                if response["error"]["code"] in {"INVALID_REQUEST", "INFEASIBLE_PLAN"}
                else 3
            )
        )
    sys.stdout.write(json.dumps(response, ensure_ascii=True, allow_nan=False) + "\n")
    raise SystemExit(code)
