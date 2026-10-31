# MCP Skill Registry CLI

Local-first Python CLI to register, list, and test MCP agent skills using a JSON catalog with schema validation. No API keys, no accounts, and nothing leaves your machine.

Built and maintained by **Asdale Dynamics, LLC** — beginner-friendly AI education, books, and practical local tools. See dylanasdale.github.io.

## What it does

- **register** — add an MCP agent skill to a local JSON catalog, with schema validation
- **list** — show registered skills (id, name, version, description)
- **test** — run a skill's command locally and report pass/fail, output, and timing
- **validate** — check a catalog file against the JSON schema

No keys, no secrets, no network required.

## Install

```bash
git clone <your-copy-of-this-repo>
cd mcp-skill-registry-cli
pip install -e .
```

Or run without installing:

```bash
python -m mcp_skill_registry --help
```

## Usage

Register a skill:

```bash
mcp-skill-registry register --catalog catalog.json --skill skills/echo_skill.json
```

List skills:

```bash
mcp-skill-registry list --catalog catalog.json
```

Test a skill:

```bash
mcp-skill-registry test --catalog catalog.json --id echo-skill --timeout 10
```

Validate a catalog:

```bash
mcp-skill-registry validate --catalog catalog.json
```

## Skill file format

Each skill is a JSON object:

```json
{
  "id": "echo-skill",
  "name": "Echo Skill",
  "description": "Example MCP skill that echoes input back.",
  "version": "0.1.0",
  "command": ["python3"],
  "args": ["-c", "..."],
  "env": {"MY_VAR": "value"},
  "capabilities": ["echo"],
  "tags": ["example"]
}
```

Required fields: `id`, `name`, `command`. See `schema/catalog.schema.json` for the full catalog schema.

## Tests

```bash
python -m unittest discover -s tests
```

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC.

## Credit

Asdale Dynamics, LLC — beginner-friendly AI education, books, and practical local-first tools.
(dylanasdale.github.io)
