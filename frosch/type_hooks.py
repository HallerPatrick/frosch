"""

    frosch - Better runtime errors

    Patrick Haller
    betterthannothing.blog
    patrickhaller40@googlemail.com

    License MIT

    Supply some custom hooks for several datatypes of variables are going to
    be displayed in stream. If hook exists replace the displayed string, with
    a hook returns

"""

from collections.abc import Callable
import importlib
from typing import Any, Dict, Optional

from .dt_hooks import hooks
from .parser import Variable

T = Any

type_to_module = {
    "ndarray": "numpy"
}  
class HookLoader:

    def __init__(self):
        self._hooks = {}

    def _lazy_load_hooks(self, module) -> Dict[type, Callable]:
        """Because we don't know what variables are actually used and to avoid import
        errors, we load modules which contains the imported libraries e.g numpy lazy
        and than get the hook functions"""

        import os
        # module = importlib.import_module(module, "frosch.dt_hooks")
        from .dt_hooks import numpy_hooks
        module = importlib.import_module(".numpy_hooks", package="frosch.dt_hooks")
        self._hooks.update(module.hooks)

    def lazy_load_hooks_from_variable(self, variable: Variable):
        module_name = type_to_module[variable.type.__qualname__]
        module = ".hook_{}".format(module_name)
        self._lazy_load_hooks(module)

    @classmethod
    def with_hooks(cls, hooks: dict):
        loader = cls()
        loader._hooks = hooks
        return loader

    def run_hook(self, variable: Variable) -> str:
        if not variable.type in self._hooks:
            self.lazy_load_hooks_from_variable(variable)
        
        if variable.type in self._hooks:
            return self._hooks[variable.type](variable.value)
        
        return variable.tree_str()
