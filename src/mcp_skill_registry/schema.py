from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import SchemaError

_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "null": lambda v: v is None,
}


class SchemaValidator:
    def __init__(self, schema: dict[str, Any]) -> None:
        self.schema = schema

    @classmethod
    def from_file(cls, path: str | Path) -> "SchemaValidator":
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise SchemaError(f"Schema in {path} must be a JSON object")
        return cls(data)

    def validate(self, instance: Any, schema: dict[str, Any] | None = None) -> list[str]:
        errors: list[str] = []
        self._check(instance, schema if schema is not None else self.schema, "$root", errors)
        return errors

    def is_valid(self, instance: Any, schema: dict[str, Any] | None = None) -> bool:
        return not self.validate(instance, schema)

    def _check(self, instance: Any, schema: dict[str, Any], path: str, errors: list[str]) -> None:
        if not isinstance(schema, dict):
            return
        expected_type = schema.get("type")
        if expected_type is not None:
            check = _TYPE_CHECKS.get(expected_type)
            if check is None:
                errors.append(f"{path}: unknown type '{expected_type}'")
            elif not check(instance):
                errors.append(f"{path}: expected {expected_type}, got {type(instance).__name__}")
                return
        if isinstance(instance, dict):
            self._check_object(instance, schema, path, errors)
        elif isinstance(instance, list):
            self._check_array(instance, schema, path, errors)
        if "enum" in schema and instance not in schema["enum"]:
            errors.append(f"{path}: value not in enum {schema['enum']}")
        if (
            "minimum" in schema
            and isinstance(instance, (int, float))
            and not isinstance(instance, bool)
            and instance < schema["minimum"]
        ):
            errors.append(f"{path}: value {instance} below minimum {schema['minimum']}")
        if "minLength" in schema and isinstance(instance, str) and len(instance) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength {schema['minLength']}")
        if "minItems" in schema and isinstance(instance, list) and len(instance) < schema["minItems"]:
            errors.append(f"{path}: array fewer than minItems {schema['minItems']}")

    def _check_object(self, instance: dict, schema: dict[str, Any], path: str, errors: list[str]) -> None:
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}.{key}: required property missing")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                self._check(value, properties[key], child_path, errors)
            elif additional is False:
                errors.append(f"{child_path}: additional property not allowed")
            elif isinstance(additional, dict):
                self._check(value, additional, child_path, errors)

    def _check_array(self, instance: list, schema: dict[str, Any], path: str, errors: list[str]) -> None:
        items = schema.get("items")
        if items is not None:
            for index, value in enumerate(instance):
                self._check(value, items, f"{path}[{index}]", errors)
