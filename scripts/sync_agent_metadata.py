"""Generate or check registry, schemas, and packaged contract from SKILL.yaml."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def artifacts():
    """Derive integration copies from the canonical JSON-compatible YAML manifest."""
    manifest = json.loads((ROOT / "SKILL.yaml").read_text(encoding="utf-8"))
    operations = manifest["operations"]
    request = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": manifest["schemas"],
        "oneOf": [
            {
                "type": "object",
                "required": ["operation", "params"],
                "additionalProperties": False,
                "properties": {
                    "operation": {"const": op["name"]},
                    "params": op["params"],
                    "meta": {"type": "object"},
                },
            }
            for op in operations
        ],
    }
    response = {
        "$schema": request["$schema"],
        "$defs": manifest["schemas"],
        "oneOf": [
            {
                "type": "object",
                "required": ["success", "message", "result", "meta"],
                "additionalProperties": False,
                "properties": {
                    "success": {"const": True},
                    "message": {"type": "string"},
                    "result": op["returns"],
                    "meta": {
                        "type": "object",
                        "required": ["operation", "contract_version"],
                        "additionalProperties": False,
                        "properties": {
                            "operation": {"const": op["name"]},
                            "contract_version": {"const": manifest["contract_version"]},
                        },
                    },
                },
            }
            for op in operations
        ]
        + [
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["success", "message", "error"],
                "properties": {
                    "success": {"const": False},
                    "message": {"type": "string"},
                    "error": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["type", "code", "message"],
                        "properties": {
                            "type": {"type": "string"},
                            "message": {"type": "string"},
                            "code": {
                                "enum": [
                                    "INVALID_JSON",
                                    "INVALID_REQUEST",
                                    "INFEASIBLE_PLAN",
                                    "NUMERICAL_ERROR",
                                    "EXECUTION_ERROR",
                                ]
                            },
                        },
                    },
                },
            }
        ],
    }
    entry = {
        k: manifest[k]
        for k in ("name", "capability", "status", "interfaces", "contract_version")
    }
    entry.update(
        path=".",
        entrypoint=manifest["interfaces"][0]["entrypoint"],
        transport="stdin_json",
        manifest="SKILL.yaml",
        procedure="USE_TOOL.md",
        operations=[op["name"] for op in operations],
    )
    return {
        "ie_models_agent/contract.json": manifest,
        "ie_models_agent/schemas/request.json": request,
        "ie_models_agent/schemas/response.json": response,
        "registry/tool_registry.json": {"version": "1.0.0", "tools": [entry]},
        "registry/model_registry.json": {
            "version": "1.0.0",
            "models": manifest["models"],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Report drift without writing files."
    )
    args = parser.parse_args()
    stale = []
    for relative, content in artifacts().items():
        path = ROOT / relative
        expected = json.dumps(content, indent=2, ensure_ascii=False) + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    if stale:
        parser.exit(
            1,
            "Metadata drift; run python scripts/sync_agent_metadata.py:\n"
            + "\n".join(stale)
            + "\n",
        )
    print(
        "Agent metadata is consistent." if args.check else "Agent metadata generated."
    )


if __name__ == "__main__":
    main()
