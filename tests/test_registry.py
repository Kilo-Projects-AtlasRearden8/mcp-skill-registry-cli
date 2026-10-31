import json
import tempfile
import unittest
from pathlib import Path

from mcp_skill_registry.catalog import Catalog
from mcp_skill_registry.errors import SkillError
from mcp_skill_registry.registry import CATALOG_SCHEMA, Registry
from mcp_skill_registry.schema import SchemaValidator
from mcp_skill_registry.tester import test_skill

VALID_SKILL = {
    "id": "echo-skill",
    "name": "Echo Skill",
    "description": "An example skill.",
    "version": "0.1.0",
    "command": ["python"],
    "args": ["-c", "print('hi')"],
    "capabilities": ["echo"],
    "tags": ["example"],
}

INVALID_SKILL = {"name": "No Id"}

DUPLICATE_SKILL = {
    "id": "echo-skill",
    "name": "Duplicate",
    "command": ["python"],
}


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.catalog_path = Path(self.tmpdir) / "catalog.json"
        self.registry = Registry(self.catalog_path)
        self.registry.load()

    def test_add_and_list_skill(self):
        self.registry.add_skill(VALID_SKILL)
        skills = self.registry.list_skills()
        self.assertEqual(len(skills), 1)
        self.assertEqual(skills[0]["id"], "echo-skill")

    def test_get_skill(self):
        self.registry.add_skill(VALID_SKILL)
        skill = self.registry.get_skill("echo-skill")
        self.assertIsNotNone(skill)
        self.assertEqual(skill["name"], "Echo Skill")
        self.assertIsNone(self.registry.get_skill("missing"))

    def test_remove_skill(self):
        self.registry.add_skill(VALID_SKILL)
        removed = self.registry.remove_skill("echo-skill")
        self.assertEqual(removed["id"], "echo-skill")
        self.assertEqual(len(self.registry.list_skills()), 0)
        with self.assertRaises(SkillError):
            self.registry.remove_skill("echo-skill")

    def test_duplicate_id_rejected(self):
        self.registry.add_skill(VALID_SKILL)
        with self.assertRaises(SkillError):
            self.registry.add_skill(DUPLICATE_SKILL)

    def test_invalid_skill_rejected(self):
        with self.assertRaises(SkillError):
            self.registry.add_skill(INVALID_SKILL)

    def test_catalog_roundtrip(self):
        self.registry.add_skill(VALID_SKILL)
        loaded = Catalog.load(self.catalog_path)
        self.assertEqual(len(loaded.skills), 1)
        self.assertEqual(loaded.skills[0]["id"], "echo-skill")

    def test_validate_catalog(self):
        self.registry.add_skill(VALID_SKILL)
        self.assertEqual(self.registry.validate_catalog(), [])

    def test_validate_invalid_catalog(self):
        bad = Catalog.from_dict({"version": 1, "skills": [{"id": 123}]})
        bad.path = self.catalog_path
        bad.save()
        registry = Registry(self.catalog_path)
        registry.load()
        errors = registry.validate_catalog()
        self.assertTrue(any("id" in error for error in errors))


class SchemaValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = SchemaValidator(CATALOG_SCHEMA)

    def test_valid_catalog(self):
        self.assertTrue(self.validator.is_valid({"version": 1, "skills": [VALID_SKILL]}))

    def test_missing_required(self):
        errors = self.validator.validate({"skills": []})
        self.assertTrue(any("version" in error for error in errors))

    def test_wrong_type(self):
        errors = self.validator.validate({"version": "1", "skills": []})
        self.assertTrue(any("version" in error for error in errors))

    def test_additional_properties_rejected(self):
        errors = self.validator.validate(
            {"version": 1, "skills": [], "extra": True}
        )
        self.assertTrue(any("extra" in error for error in errors))

    def test_skill_additional_properties_rejected(self):
        bad_skill = dict(VALID_SKILL, bogus=True)
        errors = self.validator.validate(bad_skill, CATALOG_SCHEMA["properties"]["skills"]["items"])
        self.assertTrue(any("bogus" in error for error in errors))


class TesterTests(unittest.TestCase):
    def test_passing_command(self):
        skill = {
            "id": "ok-skill",
            "command": ["python3"],
            "args": ["-c", "import sys,json;sys.stdin.readline();print(json.dumps({'ok':True}));sys.exit(0)"],
        }
        result = test_skill(skill, timeout=5)
        self.assertTrue(result.ok)
        self.assertEqual(result.returncode, 0)

    def test_failing_command(self):
        skill = {
            "id": "bad-skill",
            "command": ["python3"],
            "args": ["-c", "import sys;sys.exit(3)"],
        }
        result = test_skill(skill, timeout=5)
        self.assertFalse(result.ok)
        self.assertEqual(result.returncode, 3)

    def test_command_not_found(self):
        skill = {"id": "missing-skill", "command": ["this-command-does-not-exist-xyz"]}
        result = test_skill(skill, timeout=5)
        self.assertFalse(result.ok)
        self.assertIsNotNone(result.error)

    def test_timeout(self):
        skill = {"id": "slow-skill", "command": ["python3"], "args": ["-c", "import time;time.sleep(30)"]}
        result = test_skill(skill, timeout=1)
        self.assertFalse(result.ok)
        self.assertIsNotNone(result.error)


if __name__ == "__main__":
    unittest.main()
