"""Strict, dependency-free configuration validation."""

import json
import re
import sys
from pathlib import Path


class ConfigError(ValueError):
    """A pipeline cannot be safely interpreted as configured."""


def _keys(value, allowed, label):
    if not isinstance(value, dict) or set(value) - allowed:
        raise ConfigError("Invalid or unknown fields in " + label)


def _name(value):
    return isinstance(value, str) and re.fullmatch(
        r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", value
    )


def load_config(path, workspace):
    path, workspace = Path(path), Path(workspace).resolve()
    if not workspace.is_dir():
        raise ConfigError("Workspace must be an existing directory")
    with path.open("rb") as stream:
        data = stream.read(65537)
    if len(data) > 65536:
        raise ConfigError("Configuration exceeds 64 KiB")
    try:
        raw = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ConfigError("Configuration must be valid UTF-8 JSON") from exc
    _keys(raw, {"version", "name", "project_dir", "fail_fast", "stages"}, "pipeline")
    if type(raw.get("version")) is not int or raw["version"] != 1:
        raise ConfigError("version must be 1")
    if not _name(raw.get("name")):
        raise ConfigError(
            "Pipeline name must use letters, numbers, underscores or hyphens"
        )
    relative = raw.get("project_dir")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ConfigError("project_dir must be a nonempty workspace-relative path")
    project = (workspace / relative).resolve()
    if workspace != project and workspace not in project.parents:
        raise ConfigError(
            "project_dir must stay inside the workspace (including symlinks)"
        )
    if not project.is_dir():
        raise ConfigError("project_dir must exist")
    if type(raw.get("fail_fast", True)) is not bool:
        raise ConfigError("fail_fast must be true or false")
    stages = raw.get("stages")
    if not isinstance(stages, list) or not 1 <= len(stages) <= 50:
        raise ConfigError("Supply between 1 and 50 stages")
    validated, known = [], []
    for stage in stages:
        _keys(stage, {"name", "argv", "needs", "timeout_seconds"}, "stage")
        name = stage.get("name")
        if not _name(name) or name in known:
            raise ConfigError("Stage names must be valid and unique")
        argv = stage.get("argv")
        if (
            not isinstance(argv, list)
            or not 1 <= len(argv) <= 100
            or any(
                not isinstance(arg, str) or not arg or len(arg) > 4096 or "\0" in arg
                for arg in argv
            )
        ):
            raise ConfigError(
                "argv must contain 1–100 nonempty strings (no shell command text)"
            )
        timeout = stage.get("timeout_seconds", 120)
        if type(timeout) not in (int, float) or not 0 < timeout <= 3600:
            raise ConfigError(
                "timeout_seconds must be finite, positive and at most 3600"
            )
        needs = stage.get("needs", known[-1:])
        if not isinstance(needs, list) or any(not isinstance(n, str) for n in needs):
            raise ConfigError("needs must be a list of earlier stage names")
        if len(needs) != len(set(needs)) or not set(needs) <= set(known):
            raise ConfigError("Dependencies must be unique and refer to earlier stages")
        validated.append(
            {
                "name": name,
                "argv": [sys.executable if arg == "{python}" else arg for arg in argv],
                "needs": needs,
                "timeout_seconds": timeout,
            }
        )
        known.append(name)
    return {
        "version": 1,
        "name": raw["name"],
        "project_dir": str(project),
        "fail_fast": raw.get("fail_fast", True),
        "stages": validated,
    }
