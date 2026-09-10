# Architecture at a glance

[Project home](../README.md) · [Learn the models](models/README.md) · [Use Python](API_REFERENCE.md) · [Use the agent interface](../USE_TOOL.md) · [Modify the repository](../AGENTS.md)

IE Models Catalog is both an educational industrial-engineering catalog and a
Python library for deterministic inventory decisions. It connects formulas to
assumptions, worked examples and independently checked implementations. You can
learn why a policy works, calculate a plan, and inspect its costs.

The EOQ family chooses repeating order quantities: basic replenishment, gradual
production (EPQ), quantity discounts and planned backorders. Dynamic lot sizing
plans across a finite sequence of known demands. Wagner–Whitin finds an optimum
under its assumptions; Silver–Meal is a heuristic that can choose a costlier plan.
The [model catalog](models/README.md) explains which problem each model addresses.

This page is a shared orientation for people and agents, not a second technical
specification. Follow the linked references for exact behavior and maintenance rules.

## One library, two ways to use it

```text
                      Mathematical models
                              │
                        Python library
                         /           \
                Python users      Agent adapter ← JSON requests
                                      │
                                 JSON results

                 Machine-readable contract
                         /           \
                 JSON Schemas      Registries
                  validation       discovery
```

The **library owns the mathematics**: formulas, optimization algorithms, stock
balances and cost accounting. Python users call it directly. Its meaning does
not depend on a particular agent platform.

The **adapter translates bounded agent requests** into public library calls and
returns structured results or errors. “Agent-ready” means the existing capability
can be discovered and called through an explicit interface. It does not mean a
second solver or an autonomous planning system has been added.

The **contract defines the machine-readable interface**: which operations exist,
what inputs and outputs mean, and what limits apply. **JSON Schemas validate
structure** at that boundary. **Registries provide discovery metadata**, helping
an integration find the tool and its models. A registry describes what is available;
it does not execute a model or decide its mathematical behavior.

These are related responsibilities, not interchangeable names. Schemas and
registries are derived from the contract so they can remain consistent with it.

## What makes an answer trustworthy?

| Layer | Question it answers | What it does not establish |
| --- | --- | --- |
| JSON Schema | Does the request or response have the expected structure? | Whether the model's domain assumptions hold |
| Domain validation | Are values and their relationships admissible for this model? | Whether the implementation computes the correct optimum |
| Independent numerical tests | Does the implementation agree with independently calculated or enumerated results? | A universal proof or suitability for every business situation |

An exact result is exact only within its model assumptions. A heuristic remains
a heuristic even when it matches an optimum in an example. A successful JSON
response means the computation completed; it does not establish that the chosen
model fits the caller's business. Units, cost horizons and included cost components
must agree before results can be compared. See [shared conventions](models/conventions.md).

## From concepts to implementation

Once the relationships above are clear, these are the places to look:

| Concept | Responsibility | Implementation / reference |
| --- | --- | --- |
| Mathematical models | Formulas, profiles and planning algorithms | [Static models](../inventory_models.py), [dynamic models](../dynamic_models.py), [model guides](models/README.md) |
| Shared domain structures | Numeric validation, constraints and cost records | [model_common.py](../model_common.py); model result types stay with their implementations |
| Public Python entrypoint | Access to the same model classes | [ie_models_catalog](../ie_models_catalog/__init__.py), [API contract](API_CONTRACT.md) |
| Agent boundary | Validate, translate, dispatch and serialize | [Adapter](../ie_models_agent/tool.py), [calling procedure](../USE_TOOL.md) |
| Machine-readable contract | Canonical operation/model metadata and schemas | [SKILL.yaml](../SKILL.yaml) |
| Derived validation and discovery | Schema resources and integration metadata | [Schemas](../ie_models_agent/schemas/), [registries](../registry/) |

`SKILL.yaml` is the canonical machine-readable contract, not an installed assistant
skill. Its generated copies are maintained by [sync_agent_metadata.py](../scripts/sync_agent_metadata.py).
The ownership and generation rules belong in [contract management](../standards/CONTRACTS.md).
You do not need that procedure to calculate an EOQ or call an agent operation.

## Choose the next level

- **Understand:** [model catalog](models/README.md) for decisions and assumptions;
  [shared conventions](models/conventions.md) for units and domain terminology.
- **Use Python:** [quick start](../README.md#quick-start), then
  [API reference](API_REFERENCE.md) and [examples](../examples/README.md).
- **Use an agent/tool:** [calling procedure](../USE_TOOL.md), then its operation
  examples and the contract when exact fields are needed.
- **Modify:** [maintenance guide](../AGENTS.md) routes the task to implementation,
  standards, tests and release procedures.

People and agents share this meaning layer. After understanding it, an agent loads
additional context for its current task rather than every maintenance document.
When a local decision raises architectural uncertainty, return here and to the
[architectural rules](../standards/ARCHITECTURE.md) before continuing.
Meaning is persistent; task context is disposable. The goal is enough grounded
context to make the change correctly, not simply the fewest files read.
