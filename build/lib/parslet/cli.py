from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
import sys


def load_workflow_module(path: str) -> ModuleType:
    """Load a workflow script as a Python module from ``path``.

    Parameters
    ----------
    path: str
        Filesystem path to the workflow script.

    Returns
    -------
    ModuleType
        The loaded Python module.
    """
    wf_path = Path(path).resolve()
    spec = spec_from_file_location(wf_path.stem, wf_path)
    if spec and spec.loader:
        module = module_from_spec(spec)
        sys.modules[wf_path.stem] = module
        spec.loader.exec_module(module)
        return module
    raise ImportError(f"Cannot load workflow module from {path}")
