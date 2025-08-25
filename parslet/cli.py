import sys
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


def load_workflow_module(path: str) -> ModuleType:
    """Load a workflow script or module reference.

    The ``path`` can either be a filesystem path to a Python file or a
    ``module:func`` reference. In the latter case the referenced callable is
    exposed as ``main`` on the returned module to match the traditional file
    workflow interface.

    Parameters
    ----------
    path: str
        Filesystem path to the workflow script or ``module:func`` reference.

    Returns
    -------
    ModuleType
        The loaded Python module with a ``main`` attribute.
    """

    if ":" in path and not Path(path).exists():
        mod_name, func_name = path.split(":", 1)
        module = import_module(mod_name)
        if not hasattr(module, func_name):
            raise ImportError(f"Module '{mod_name}' has no attribute '{func_name}'")
        # Expose the target callable as ``main`` for CLI expectations
        module.main = getattr(module, func_name)  # type: ignore[attr-defined]
        return module

    wf_path = Path(path).resolve()
    spec = spec_from_file_location(wf_path.stem, wf_path)
    if spec and spec.loader:
        module = module_from_spec(spec)
        sys.modules[wf_path.stem] = module
        spec.loader.exec_module(module)
        return module
    raise ImportError(f"Cannot load workflow module from {path}")
