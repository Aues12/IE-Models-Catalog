"""Agent contract, process boundary, and library-delegation regression checks."""

import copy
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from dynamic_models import DLSInput, DynamicLotSizing
from ie_models_agent import run, tool
from inventory_models import EPQ, BackorderEOQ, BasicEOQ, DiscountEOQ

ROOT = Path(__file__).resolve().parents[1]
BASE = {"price": 10, "demand_rate": 100, "ordering_cost": 5, "holding_rate": 0.2}
MODEL_CASES = [
    ("basic_eoq", BasicEOQ, {}, {}),
    ("epq", EPQ, {"production_rate": 200}, {"production_rate": 200}),
    ("backorder_eoq", BackorderEOQ, {"shortage_cost": 3}, {"shortage_cost": 3}),
    (
        "discount_eoq",
        DiscountEOQ,
        {
            "discount_tiers": [
                {"minimum_quantity": 25.5, "discount_rate": 0.02},
                {"minimum_quantity": 50, "discount_rate": 0.1},
            ]
        },
        {"discount_rates": {25.5: 0.02, 50: 0.1}},
    ),
]


def invoke(raw, cwd=ROOT, env=None):
    return subprocess.run(
        [sys.executable, "-m", "ie_models_agent"],
        input=raw,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=env,
        timeout=20,
    )


@pytest.mark.parametrize("mid,cls,extra,native_extra", MODEL_CASES)
def test_eoq_surfaces_delegate_without_changing_costs(mid, cls, extra, native_extra):
    native = cls(**BASE, **native_extra)
    params = {"model": mid, "inputs": {**BASE, **extra}}
    response = run({"operation": "solve_eoq", "params": params})
    assert response["success"], response
    result = response["result"]
    assert result["order_quantity"] == pytest.approx(native.solve().order_quantity)
    assert result["total_cost"] == pytest.approx(native.solve().total_cost)
    assert result["cost_basis"]["horizon"] == "year"
    evaluated = run({"operation": "evaluate_eoq", "params": {**params, "quantity": 75}})
    assert evaluated["result"]["costs"]["total_cost"] == pytest.approx(
        native.calculate_costs(75).total_cost
    )
    profile = run(
        {
            "operation": "inventory_profile",
            "params": {**params, "times": [0, 10, 20], "days_of_operation": 250},
        }
    )
    assert profile["result"]["inventory_levels"] == pytest.approx(
        native.inventory_level([0, 10, 20], days_of_operation=250)
    )
    rop = run(
        {
            "operation": "reorder_point",
            "params": {**params, "lead_time": 10, "days_of_operation": 250},
        }
    )
    assert rop["result"]["reorder_point"] == 4


@pytest.mark.parametrize("method", ["wagner-whitin", "silver-meal"])
def test_dynamic_initial_stock_and_guarantee(method):
    params = {
        "demand": [15, 0, 60, 10, 0, 80],
        "ordering_cost": 100,
        "holding_cost": 1,
        "initial_inventory": 35,
        "period_unit": "month",
        "method": method,
    }
    result = run({"operation": "solve_dynamic", "params": params})["result"]
    native = DynamicLotSizing(DLSInput(params["demand"], 100, 1, 35)).solve(method)
    assert result["total_cost"] == native.total_cost
    assert result["inventory_levels"] == native.inventory_levels
    assert result["cost_basis"]["period_unit"] == "month"
    assert (result["guarantee"] == "heuristic") == (method == "silver-meal")


@pytest.mark.parametrize("zero", [False, True])
def test_comparison_gap_and_zero_reference(zero):
    result = run(
        {
            "operation": "compare_dynamic",
            "params": {
                "demand": [0] if zero else [10, 20, 30, 40, 50, 60],
                "ordering_cost": 100,
                "holding_cost": 1,
            },
        }
    )["result"]
    assert result["absolute_cost_gap"] == (0 if zero else 10)
    if zero:
        assert result["relative_cost_gap_percent"] is None
    else:
        assert result["relative_cost_gap_percent"] == pytest.approx(1000 / 420)


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"operation": "bad", "params": {}},
        {"operation": "list_models"},
        {"operation": "list_models", "params": [], "meta": {}},
        {"operation": "list_models", "params": {}, "extra": True},
        {"operation": "list_models", "params": {"extra": 1}},
        {"operation": "list_models", "params": {}, "meta": "bad"},
        {"operation": "solve_eoq", "params": {"model": "BasicEOQ", "inputs": BASE}},
        {
            "operation": "solve_eoq",
            "params": {"model": "basic_eoq", "inputs": {**BASE, "lead_time": 1}},
        },
        {
            "operation": "solve_eoq",
            "params": {"model": "epq", "inputs": {**BASE, "production_rate": 50}},
        },
        {
            "operation": "solve_dynamic",
            "params": {"demand": [1] * 121, "ordering_cost": 1, "holding_cost": 1},
        },
        {
            "operation": "solve_dynamic",
            "params": {"demand": [], "ordering_cost": 1, "holding_cost": 1},
        },
        {
            "operation": "inventory_profile",
            "params": {"model": "basic_eoq", "inputs": BASE, "times": [0] * 1001},
        },
    ],
)
def test_bad_requests_are_structured(payload):
    response = run(payload)
    assert not response["success"]
    assert response["error"]["code"] == "INVALID_REQUEST"
    Draft202012Validator(tool.RESPONSE_SCHEMA).validate(response)


@pytest.mark.parametrize(
    "number", [math.nan, math.inf, -math.inf, True, "10", None, -1, 0]
)
def test_invalid_core_numeric_values(number):
    response = run(
        {
            "operation": "solve_eoq",
            "params": {"model": "basic_eoq", "inputs": {**BASE, "price": number}},
        }
    )
    assert not response["success"]
    assert response["error"]["code"] == "INVALID_REQUEST"


@pytest.mark.parametrize(
    "tiers",
    [
        [
            {"minimum_quantity": 1, "discount_rate": 0},
            {"minimum_quantity": 1, "discount_rate": 0.1},
        ],
        [
            {"minimum_quantity": 10, "discount_rate": 0.2},
            {"minimum_quantity": 20, "discount_rate": 0.1},
        ],
        [{"minimum_quantity": 0, "discount_rate": 1}],
        [{"minimum_quantity": 0, "discount_rate": 0, "unexpected": 1}],
    ],
)
def test_discount_cross_field_validation(tiers):
    response = run(
        {
            "operation": "solve_eoq",
            "params": {
                "model": "discount_eoq",
                "inputs": {**BASE, "discount_tiers": tiers},
            },
        }
    )
    assert response["error"]["code"] == "INVALID_REQUEST"


def test_numerical_failure_does_not_emit_nonfinite_success():
    request = {
        "operation": "solve_eoq",
        "params": {
            "model": "basic_eoq",
            "inputs": {**BASE, "price": 1e308, "holding_rate": 1e308},
        },
    }
    response = run(request)
    assert response["error"]["code"] == "NUMERICAL_ERROR"
    json.dumps(response, allow_nan=False)


def test_unexpected_failure_is_contained(monkeypatch):
    def fail(params):
        raise RuntimeError("private diagnostic")

    monkeypatch.setitem(tool.HANDLERS, "solve_eoq", fail)
    response = run(
        {"operation": "solve_eoq", "params": {"model": "basic_eoq", "inputs": BASE}}
    )
    assert response["error"]["code"] == "EXECUTION_ERROR"
    assert "private diagnostic" not in json.dumps(response)


def test_inputs_and_discovery_are_not_mutated():
    request = {
        "operation": "solve_eoq",
        "params": {"model": "basic_eoq", "inputs": BASE},
        "meta": {"id": "private"},
    }
    original = copy.deepcopy(request)
    response = run(request)
    assert request == original
    assert response["meta"] == {"operation": "solve_eoq", "contract_version": 1}
    run({"operation": "list_models", "params": {}})["result"]["models"].clear()
    assert len(run({"operation": "list_models", "params": {}})["result"]["models"]) == 7


@pytest.mark.parametrize(
    "raw,code",
    [
        (b"", 2),
        (b"{", 2),
        (b"\xff", 2),
        (b"{} {}", 2),
        (b'{"operation":"list_models","operation":"solve_eoq","params":{}}', 2),
        (b'{"operation":"list_models","params":{},"meta":{"x":NaN}}', 2),
        (b'{"operation":"list_models","params":{},"meta":{"x":Infinity}}', 2),
        (b" " * 1048577, 2),
        (b"[]", 1),
        (b'{"operation":"unknown","params":{}}', 1),
        (b'{"operation":"list_models","params":{}}', 0),
        (
            b'{"operation":"solve_eoq","params":{"model":"basic_eoq","inputs":{"price":1e308,"demand_rate":100,"ordering_cost":5,"holding_rate":1e308}}}',
            3,
        ),
    ],
    ids=[
        "empty",
        "syntax",
        "encoding",
        "multiple-documents",
        "duplicate-key",
        "nan",
        "infinity",
        "oversized",
        "array",
        "unknown-operation",
        "success",
        "numeric-overflow",
    ],
)
def test_cli_exit_codes_and_single_clean_envelope(raw, code):
    process = invoke(raw)
    assert process.returncode == code, process.stderr
    assert process.stderr == b""
    response = json.loads(process.stdout)
    assert response["success"] == (code == 0)
    assert len(process.stdout.splitlines()) == 1
    Draft202012Validator(tool.RESPONSE_SCHEMA).validate(response)


def test_cli_has_no_plot_imports_or_caller_file_writes(tmp_path):
    environment = {
        **os.environ,
        "PYTHONPATH": str(ROOT),
        "PYTHONDONTWRITEBYTECODE": "1",
        "MPLCONFIGDIR": str(tmp_path / "plot-cache"),
    }
    process = invoke(
        (ROOT / "examples/agent/solve_eoq.json").read_bytes(),
        cwd=tmp_path,
        env=environment,
    )
    assert process.returncode == 0, process.stdout
    assert list(tmp_path.iterdir()) == []
    checked = subprocess.run(
        [
            sys.executable,
            "-c",
            "import ie_models_agent, sys; assert 'matplotlib.pyplot' not in sys.modules; assert 'plotly.express' not in sys.modules",
        ],
        env=environment,
        capture_output=True,
        timeout=20,
    )
    assert checked.returncode == 0, checked.stderr


def test_checkout_script_matches_module_entrypoint(tmp_path):
    raw = (ROOT / "examples/agent/solve_eoq.json").read_bytes()
    result = subprocess.run(
        [sys.executable, str(ROOT / "inventory_agent.py")],
        input=raw,
        cwd=tmp_path,
        capture_output=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == json.loads(invoke(raw).stdout)


def test_optional_defaults_preserve_native_behavior():
    inputs = {"price": 10, "demand_rate": 100, "ordering_cost": 5}
    result = run(
        {"operation": "solve_eoq", "params": {"model": "basic_eoq", "inputs": inputs}}
    )["result"]
    assert result["total_cost"] == BasicEOQ(**inputs).solve().total_cost
    plan = run(
        {
            "operation": "solve_dynamic",
            "params": {"demand": [1], "ordering_cost": 2, "holding_cost": 3},
        }
    )["result"]
    assert plan["method"] == "wagner-whitin"
    assert plan["cost_basis"]["period_unit"] == "period"
    assert plan["inventory_levels"] == [0]
