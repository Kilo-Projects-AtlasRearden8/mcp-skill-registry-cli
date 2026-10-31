from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from typing import Any

DEFAULT_PAYLOAD = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "mcp-skill-registry", "version": "0.1.0"},
    },
}


@dataclass
class TestResult:
    skill_id: str
    ok: bool
    returncode: int | None
    stdout: str
    stderr: str
    error: str | None
    duration_ms: float

    def summary(self) -> str:
        if self.error:
            return f"ERROR: {self.error}"
        status = "PASS" if self.ok else "FAIL"
        return f"{status} (exit {self.returncode}, {self.duration_ms:.0f} ms)"


def test_skill(
    skill: dict[str, Any],
    timeout: float = 10.0,
    stdin_payload: dict[str, Any] | None = None,
) -> TestResult:
    skill_id = str(skill.get("id", "unknown"))
    command = list(skill.get("command", [])) + list(skill.get("args", []))
    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in skill.get("env", {}).items()})
    payload = DEFAULT_PAYLOAD if stdin_payload is None else stdin_payload
    stdin_text = json.dumps(payload) + "\n"
    start = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        duration_ms = (time.monotonic() - start) * 1000
        return TestResult(
            skill_id=skill_id,
            ok=completed.returncode == 0,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            error=None,
            duration_ms=duration_ms,
        )
    except FileNotFoundError as exc:
        duration_ms = (time.monotonic() - start) * 1000
        return TestResult(skill_id, False, None, "", "", f"command not found: {command[0] if command else '(empty)'}", duration_ms)
    except subprocess.TimeoutExpired as exc:
        duration_ms = (time.monotonic() - start) * 1000
        return TestResult(
            skill_id,
            False,
            None,
            exc.stdout or "",
            exc.stderr or "",
            f"timed out after {timeout:.0f} seconds",
            duration_ms,
        )
    except OSError as exc:
        duration_ms = (time.monotonic() - start) * 1000
        return TestResult(skill_id, False, None, "", "", str(exc), duration_ms)
