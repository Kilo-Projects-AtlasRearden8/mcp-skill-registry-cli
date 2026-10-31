from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Catalog:
    version: int = 1
    skills: list[dict[str, Any]] = field(default_factory=list)
    path: Path | None = None

    @classmethod
    def load(cls, path: str | Path) -> "Catalog":
        catalog_path = Path(path)
        if not catalog_path.exists():
            return cls(path=catalog_path)
        with open(catalog_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise CatalogError(f"Catalog {catalog_path} must contain a JSON object")
        return cls(
            version=int(data.get("version", 1)),
            skills=list(data.get("skills", [])),
            path=catalog_path,
        )

    def save(self, path: str | Path | None = None) -> None:
        target = Path(path) if path is not None else self.path
        if target is None:
            raise CatalogError("No catalog path to save to")
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2)
            handle.write("\n")

    def to_dict(self) -> dict[str, Any]:
        return {"version": self.version, "skills": self.skills}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Catalog":
        return cls(version=int(data.get("version", 1)), skills=list(data.get("skills", [])))
