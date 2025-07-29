import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Dict

PLUGIN_FOLDER = Path(__file__).parent

_loaded_plugins: Dict[str, ModuleType] = {}


def load_plugins() -> Dict[str, ModuleType]:
    """Load plugin modules from the plugins folder."""
    for path in PLUGIN_FOLDER.glob("*.py"):
        if path.name == "__init__.py" or path.name == "loader.py":
            continue
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[path.stem] = module
            spec.loader.exec_module(module)
            _loaded_plugins[path.stem] = module
    return _loaded_plugins
