"""Load configs/config.yaml. Supports both config["key"] and config.key."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


class _Config(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(name) from e


with open(ROOT / "configs" / "config.yaml") as f:
    config = _Config(yaml.safe_load(f) or {})
