from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .catalog import Catalog
from .errors import MCPRegistryError
from .registry import CATALOG_SCHEMA, Registry
from .schema import SchemaValidator
from .tester import DEFAULT_PAYLOAD, test_skill


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-skill-registry",
        description="Register, list, and test MCP agent skills in a local JSON catalog.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    register = sub.add_parser("register", help="Add a skill to a catalog")
    register.add_argument("--catalog", required=True, help="Path to catalog JSON file")
    register.add_argument("--skill", required=True, help="Path to skill JSON file")

    list_cmd = sub.add_parser("list", help="List skills in a catalog")
    list_cmd.add_argument("--catalog", required=True, help="Path to catalog JSON file")

    test_cmd = sub.add_parser("test", help="Test a skill by running its command")
    test_cmd.add_argument("--catalog", required=True, help="Path to catalog JSON file")
    test_cmd.add_argument("--id", required=True, help="Skill id to test")
    test_cmd.add_argument("--timeout", type=float, default=10.0, help="Command timeout in seconds")

    validate = sub.add_parser("validate", help="Validate a catalog against the schema")
    validate.add_argument("--catalog", required=True, help="Path to catalog JSON file")

    return parser


def _load_skill_file(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise MCPRegistryError(f"Skill file {path} must contain a JSON object")
    return data


def cmd_register(args: argparse.Namespace) -> int:
    registry = Registry(args.catalog)
    registry.load()
    skill = _load_skill_file(args.skill)
    registry.add_skill(skill)
    print(f"Registered skill '{skill['id']}' in {args.catalog}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    registry = Registry(args.catalog)
    registry.load()
    skills = registry.list_skills()
    if not skills:
        print("No skills registered.")
        return 0
    print(f"{'ID':<24} {'NAME':<28} {'VERSION':<10} DESCRIPTION")
    print("-" * 80)
    for skill in skills:
        print(
            f"{str(skill.get('id', '')):<24} "
            f"{str(skill.get('name', '')):<28} "
            f"{str(skill.get('version', '')):<10} "
            f"{skill.get('description', '')}"
        )
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    registry = Registry(args.catalog)
    registry.load()
    skill = registry.get_skill(args.id)
    if skill is None:
        print(f"Skill '{args.id}' not found in {args.catalog}", file=sys.stderr)
        return 1
    result = test_skill(skill, timeout=args.timeout, stdin_payload=DEFAULT_PAYLOAD)
    print(f"Testing skill '{result.skill_id}'...")
    print(result.summary())
    if result.stdout:
        print("STDOUT:")
        print(result.stdout.rstrip())
    if result.stderr:
        print("STDERR:")
        print(result.stderr.rstrip())
    return 0 if result.ok else 1


def cmd_validate(args: argparse.Namespace) -> int:
    registry = Registry(args.catalog)
    registry.load()
    errors = registry.validate_catalog()
    if errors:
        print("Catalog is invalid:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Catalog {args.catalog} is valid ({len(registry.list_skills())} skill(s)).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "register":
            return cmd_register(args)
        if args.command == "list":
            return cmd_list(args)
        if args.command == "test":
            return cmd_test(args)
        if args.command == "validate":
            return cmd_validate(args)
    except MCPRegistryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 1
