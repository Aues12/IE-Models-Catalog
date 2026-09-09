"""Detect drift among the canonical manifest, schemas, registry and runtime."""

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from ie_models_agent import run
from ie_models_agent.tool import CONTRACT, HANDLERS, REQUEST_SCHEMA, RESPONSE_SCHEMA

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_manifest_and_registry_are_synchronized():
    result = subprocess.run(
        [sys.executable, "scripts/sync_agent_metadata.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert CONTRACT == json.loads((ROOT / "SKILL.yaml").read_text())
    assert set(HANDLERS) == {op["name"] for op in CONTRACT["operations"]}
    registry = json.loads((ROOT / "registry/tool_registry.json").read_text())
    assert set(registry["tools"][0]["operations"]) == set(HANDLERS)
    for model in CONTRACT["models"]:
        assert (ROOT / model["guide"]).is_file()
        assert (ROOT / (model["module"] + ".py")).is_file()
    for interface in CONTRACT["interfaces"]:
        assert (ROOT / interface["entrypoint"]).is_file()


def test_schemas_are_valid_and_all_operation_examples_execute():
    Draft202012Validator.check_schema(REQUEST_SCHEMA)
    Draft202012Validator.check_schema(RESPONSE_SCHEMA)
    for op in CONTRACT["operations"]:
        request = json.loads((ROOT / op["example"]).read_text())
        assert request["operation"] == op["name"]
        Draft202012Validator(REQUEST_SCHEMA).validate(request)
        response = run(request)
        assert response["success"], response
        Draft202012Validator(RESPONSE_SCHEMA).validate(response)


def test_drift_check_fails_without_rewriting_modified_artifacts(tmp_path):
    import shutil

    (tmp_path / "scripts").mkdir()
    shutil.copy(
        ROOT / "scripts/sync_agent_metadata.py",
        tmp_path / "scripts/sync_agent_metadata.py",
    )
    shutil.copy(ROOT / "SKILL.yaml", tmp_path / "SKILL.yaml")
    command = [sys.executable, str(tmp_path / "scripts/sync_agent_metadata.py")]
    subprocess.run(command, check=True, capture_output=True)
    target = tmp_path / "registry/tool_registry.json"
    target.write_text('{"tools": []}\n')
    result = subprocess.run(command + ["--check"], capture_output=True, text=True)
    assert result.returncode == 1
    assert "registry/tool_registry.json" in result.stderr
    assert target.read_text() == '{"tools": []}\n'


def test_declared_limits_match_request_schemas():
    operations = {op["name"]: op for op in CONTRACT["operations"]}
    limits = CONTRACT["limits"]
    for name in ("solve_dynamic", "compare_dynamic"):
        assert (
            operations[name]["params"]["properties"]["demand"]["maxItems"]
            == limits["max_periods"]
        )
    for variant in operations["inventory_profile"]["params"]["oneOf"]:
        assert (
            variant["properties"]["times"]["maxItems"] == limits["max_profile_points"]
        )
    tiers = CONTRACT["schemas"]["input_discount_eoq"]["properties"]["discount_tiers"]
    assert tiers["maxItems"] == limits["max_discount_tiers"]
