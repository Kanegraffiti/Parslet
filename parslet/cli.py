import re
import sys
import tempfile
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
            msg = f"Module '{mod_name}' does not define '{func_name}'."
            raise ImportError(msg)
        # Expose the target callable as ``main`` for CLI expectations
        module.main = getattr(module, func_name)  # type: ignore[attr-defined]
        return module

    wf_path = Path(path).resolve()
    if not wf_path.exists():
        msg = f"Cannot find workflow at '{path}'. Check the path."
        raise ImportError(msg)

    code = wf_path.read_text(encoding="utf-8")
    if re.search(r"@\s*(python_app|bash_app)", code):
        from .compat.parsl_adapter import import_parsl_script

        tmp = tempfile.NamedTemporaryFile(suffix="_parslet.py", delete=False)
        tmp.close()
        import_parsl_script(str(wf_path), tmp.name)
        spec = spec_from_file_location(Path(tmp.name).stem, tmp.name)
        if spec and spec.loader:
            module = module_from_spec(spec)
            sys.modules[Path(tmp.name).stem] = module
            spec.loader.exec_module(module)
            module.__converted_from_parsl__ = True
            module.__original_parsl_path__ = str(wf_path)
            return module
        raise ImportError(
            "Converted Parsl workflow could not be loaded; "
            "please check the source file."
        )

    spec = spec_from_file_location(wf_path.stem, wf_path)
    if spec and spec.loader:
        module = module_from_spec(spec)
        sys.modules[wf_path.stem] = module
        spec.loader.exec_module(module)
        return module
    msg = f"Unable to load workflow from '{path}'. Ensure it is valid Python."
    raise ImportError(msg)
