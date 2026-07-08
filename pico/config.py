"""Project-local configuration helpers."""

import os
import re
from pathlib import Path


ENV_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_env_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("export "):
        line = line[len("export "):].strip()
    if "=" not in line:
        raise ValueError(f"invalid .env line: {line}")
    name, value = line.split("=", 1)
    name = name.strip()
    if not ENV_KEY_PATTERN.match(name):
        raise ValueError(f"invalid .env variable name: {name}")
    return name, _strip_quotes(value)


def find_project_env(start):
    current = Path(start).resolve()
    if current.is_file():
        current = current.parent
    for path in (current, *current.parents):
        env_path = path / ".env"
        if env_path.exists():
            return env_path
    return None


def _load_env_file(env_path, override=True):
    loaded = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_env_line(line)
        if parsed is None:
            continue
        name, value = parsed
        loaded[name] = value
        if override or name not in os.environ:
            os.environ[name] = value
    return loaded


def load_project_env(start, override=True):
    env_path = find_project_env(start)
    if env_path is None:
        return {}
    return _load_env_file(env_path, override=override)


def find_pico_project_root():
    """Return the pico install/source tree that owns provider .env configuration."""
    current = Path(__file__).resolve().parent
    for path in (current, *current.parents):
        pyproject = path / "pyproject.toml"
        if not pyproject.exists():
            continue
        try:
            text = pyproject.read_text(encoding="utf-8")
        except OSError:
            continue
        if 'name = "pico"' in text:
            return path
    return None


def load_pico_env(override=True):
    """Load provider configuration from pico's own project root, not --cwd workspace."""
    root = find_pico_project_root()
    if root is None:
        return {}
    env_path = root / ".env"
    if not env_path.exists():
        return {}
    return _load_env_file(env_path, override=override)


def provider_env(name, legacy_names=(), default=""):
    for env_name in (name, *legacy_names):
        value = os.environ.get(env_name)
        if value:
            return value
    return default
