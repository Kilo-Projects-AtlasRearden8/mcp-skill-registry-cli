# STATUS

## What was built

`mcp-skill-registry` — a local-first Python CLI (v0.1.0) to register, list, and test MCP agent skills using a JSON catalog with schema validation. No API keys, no accounts, no network required; nothing leaves your machine.

Built and maintained by Asdale Dynamics, LLC (dylanasdale.github.io) — beginner-friendly AI education, books, and practical local-first tools.

## Project layout

```
pyproject.toml          # package config + console script entry point
README.md               # beginner-friendly usage guide, credits Asdale Dynamics, LLC
LICENSE                 # MIT, Copyright (c) 2026 Asdale Dynamics, LLC
STATUS.md               # this file
catalog.example.json    # empty starter catalog
schema/catalog.schema.json  # catalog JSON schema (human-readable copy)
skills/echo_skill.json        # example MCP skill
src/mcp_skill_registry/ # package
  __init__.py           # __version__
  __main__.py           # python3 -m mcp_skill_registry
  cli.py                # argparse CLI: register, list, test, validate
  catalog.py            # Catalog dataclass, JSON load/save
  registry.py           # Registry: add/list/get/remove/validate skills
  schema.py             # small JSON Schema subset validator
  tester.py             # run a skill command locally, capture output
  errors.py             # exception hierarchy
tests/test_registry.py        # 17 registry/schema/tester tests
```

## How to run it

You need Python 3.9 or newer.

```bash
pip install -e .          # installs the mcp-skill-registry command

mcp-skill-registry register --catalog catalog.json --skill skills/echo_skill.json
mcp-skill-registry list --catalog catalog.json
mcp-skill-registry test --catalog catalog.json --id echo-skill --timeout 10
mcp-skill-registry validate --catalog catalog.json

python3 -m unittest discover -s tests   # run the test suite
```

No install needed alternative: `python3 -m mcp_skill_registry --help`

## Verification results

- `pip install -e .` — success
- `python3 -m unittest discover -s tests` — 17 tests, OK (registry add/list/get/remove, duplicate rejection, schema validation, catalog roundtrip, skill tester pass/fail/not-found/timeout)
- `python3 -m mcp_skill_registry --help` — works
- CLI end-to-end — register, list, validate, and test all succeed against `skills/echo_skill.json`; test reports PASS with echoed JSON-RPC response (exit 0)
- LICENSE line 3 — exactly `Copyright (c) 2026 Asdale Dynamics, LLC`
- README credits Asdale Dynamics, LLC; uses `python3` consistently

## Known gaps

- Example skill uses `python3`; on systems where only `python` is available, update `command` in skill files.
- Tester sends an MCP `initialize` JSON-RPC message by default and checks exit code/output; it does not implement full MCP session negotiation.
- Schema validator covers a subset of JSON Schema (type, required, properties, additionalProperties, items, minLength, minItems, enum, minimum), sufficient for this catalog.
- Tests use stdlib `unittest`; no pytest dependency.
- Not published to PyPI (intentional, local-first).
