from __future__ import annotations

from pathlib import Path
from typing import Any

from .catalog import Catalog
from .errors import CatalogError, SkillError
from .schema import SchemaValidator

CATALOG_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "MCP Skill Catalog",
    "type": "object",
    "required": ["version", "skills"],
    "properties": {
        "version": {"type": "integer", "minimum": 1},
        "skills": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name", "command"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "name": {"type": "string", "minLength": 1},
                    "description": {"type": "string"},
                    "version": {"type": "string", "minLength": 1},
                    "command": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "args": {"type": "array", "items": {"type": "string"}},
                    "env": {"type": "object", "additionalProperties": {"type": "string"}},
                    "capabilities": {"type": "array", "items": {"type": "string"}},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}

SKILL_SCHEMA = CATALOG_SCHEMA["properties"]["skills"]["items"]


class Registry:
    def __init__(self, catalog_path: str | Path, validator: SchemaValidator | None = None) -> None:
        self.catalog_path = Path(catalog_path)
        self.catalog = Catalog()
        self.validator = validator or SchemaValidator(CATALOG_SCHEMA)
        self._index: dict[str, dict[str, Any]] = {}

    def load(self) -> Catalog:
        self.catalog = Catalog.load(self.catalog_path)
        self._rebuild_index()
        return self.catalog

    def save(self) -> None:
        self.catalog.save(self.catalog_path)

    def _rebuild_index(self) -> None:
        self._index = {}
        for skill in self.catalog.skills:
            skill_id = skill.get("id")
            if isinstance(skill_id, str):
                self._index[skill_id] = skill

    def validate_skill(self, skill: dict[str, Any]) -> list[str]:
        return self.validator.validate(skill, SKILL_SCHEMA)

    def add_skill(self, skill: dict[str, Any]) -> None:
        errors = self.validate_skill(skill)
        if errors:
            raise SkillError("Invalid skill: " + "; ".join(errors))
        skill_id = skill["id"]
        if skill_id in self._index:
            raise SkillError(f"Skill '{skill_id}' is already registered")
        self.catalog.skills.append(dict(skill))
        self._index[skill_id] = self.catalog.skills[-1]
        self.save()

    def list_skills(self) -> list[dict[str, Any]]:
        return list(self.catalog.skills)

    def get_skill(self, skill_id: str) -> dict[str, Any] | None:
        return self._index.get(skill_id)

    def remove_skill(self, skill_id: str) -> dict[str, Any]:
        skill = self._index.get(skill_id)
        if skill is None:
            raise SkillError(f"Skill '{skill_id}' not found")
        self.catalog.skills.remove(skill)
        del self._index[skill_id]
        self.save()
        return skill

    def validate_catalog(self) -> list[str]:
        return self.validator.validate(self.catalog.to_dict())
