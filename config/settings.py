"""
Configuration loader — reads partner API configuration.

Loads from:
1. config/partners.yaml (if exists)
2. Environment variables (fallback)
"""

import os
from pathlib import Path
from typing import Any
import yaml

_CONFIG: dict[str, Any] | None = None


def _find_config() -> Path | None:
    """Search for partners.yaml in several locations."""
    candidates = [
        Path("config/partners.yaml"),
        Path.home() / ".clarity" / "partners.yaml",
        Path(os.environ.get("CLARITY_CONFIG", "")),
    ]
    for path in candidates:
        if path and path.exists():
            return path
    return None


def load_config() -> dict[str, Any]:
    """Load configuration once, cache it."""
    global _CONFIG
    if _CONFIG is not None:
        return _CONFIG

    config: dict[str, Any] = {
        "actian": {"connection_string": "", "enable_vector_store": True},
        "band": {"api_key": "", "default_room": "clarity-trials", "enable_human_escalation": True},
        "pioneer": {"api_key": "", "base_url": "https://api.pioneer.ai/v1", "enable_inference": True},
        "deepmind": {"api_key": "", "model": "gemini-2.0-pro", "enable_advanced_reasoning": False},
        "guild": {"agent_name": "clarity-trial-architect", "publish_on_evolve": True},
        "replay": {"api_key": "", "capture_demo": True},
    }

    config_path = _find_config()
    if config_path:
        with open(config_path) as f:
            file_config = yaml.safe_load(f) or {}
            for section, values in file_config.items():
                if section in config and isinstance(values, dict):
                    config[section].update(values)

    # Override from environment variables
    env_map = {
        "ACTIAN_CONNECTION": ("actian", "connection_string"),
        "BAND_API_KEY": ("band", "api_key"),
        "PIONEER_API_KEY": ("pioneer", "api_key"),
        "DEEPMIND_API_KEY": ("deepmind", "api_key"),
        "GUILD_AGENT_NAME": ("guild", "agent_name"),
        "REPLAY_API_KEY": ("replay", "api_key"),
    }
    for env_var, (section, key) in env_map.items():
        if os.environ.get(env_var):
            config[section][key] = os.environ[env_var]

    _CONFIG = config
    return config


def get_section(section: str) -> dict[str, Any]:
    """Get a specific config section."""
    return load_config().get(section, {})


def is_enabled(section: str, key: str = "enable") -> bool:
    """Check if a feature is enabled."""
    return load_config().get(section, {}).get(key, True)
