# MCP Skill Registry CLI

A local-first Python CLI to register, list, and test MCP agent skills using a JSON catalog with schema validation. No API keys, no accounts, and nothing leaves your machine.

Built by **Asdale Dynamics, LLC** — beginner-friendly AI education, books, and practical local tools. Learn more at dylanasdale.github.io.

## What it does

This tool helps you manage a local catalog of MCP (Model Context Protocol) agent skills:

- **register** — add a skill to your local JSON catalog (with schema validation)
- **list** — show every registered skill (id, name, version, description)
- **test** — run a skill's command locally and report pass/fail, output, and timing
- **validate** — check that your catalog file follows the skill schema

Everything runs on your computer. No network, no keys, no secrets.

## Who this is for

This is for anyone getting started with AI agents and MCP — especially beginners who want plain-English, step-by-step tools they can run locally. It's published by Asdale Dynamics, LLC, an Indiana company focused on beginner-friendly AI education, books, and practical tools you can use or share.

## Install

You need Python 3.9 or newer.

Option 1: install the command

```bash
pip install -e .
```

This makes the `mcp-skill-registry` command available.

Option 2: run without installing

```bash
python3 -m mcp_skill_registry --help
```

## Usage

### Register a skill

```bash
mcp-skill-registry register --catalog catalog.json --skill skills/echo_skill.json
```

This reads `skills/echo_skill.json`, checks it against the schema, and adds it to `catalog.json`.

### List your skills

```bash
mcp-skill-registry list --catalog catalog.json
```

You'll see a table with each skill's id, name, version, and description.

### Test a skill

```bash
mcp-skill-registry test --catalog catalog.json --id echo-skill --timeout 10
```

The CLI runs the skill's command locally, sends it a sample JSON-RPC message, and prints whether it passed, its exit code, and any output.

### Validate your catalog

```bash
mcp-skill-registry validate --catalog catalog.json
```

This checks every skill in the catalog against the schema and reports any problems.

## Skill file format

Each skill is a JSON object. Here's the example skill included in this project:

```json
{
  "id": "echo-skill",
  "name": "Echo Skill",
  "description": "Example MCP skill that reads a JSON-RPC message and echoes it back.",
  "version": "0.1.0",
  "command": ["python3"],
  "args": [
    "-c",
    "import sys,json;msg=sys.stdin.readline();print(json.dumps({\"jsonrpc\":\"2.0\",\"id\":1,\"result\":{\"echo\":msg.strip()}}))"
  ],
  "capabilities": ["echo"],
  "tags": ["example"]
}
```

Required fields:

- `id` — a short unique identifier for the skill
- `name` — a human-readable name
- `command` — the program to run (a list, e.g. `["python3"]`)

Optional fields: `description`, `version`, `args`, `env`, `capabilities`, `tags`.

The full catalog schema is in `schema/catalog.schema.json`. An empty starter catalog is in `catalog.example.json`.

## Run the tests

```bash
python3 -m unittest discover -s tests
```

All tests use Python's standard library — nothing extra to install.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC.

## Credit

Asdale Dynamics, LLC — beginner-friendly AI education, books, and practical local-first tools.
(dylanasdale.github.io)
