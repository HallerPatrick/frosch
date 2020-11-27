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
from typing import Any, Dict

# from .dt_hooks import hooks
from .parser import Variable

T = Any

# This will probably break/not work if there a types of the same name
type_to_module = {
    "ndarray": "numpy"
}
class HookLoader:
    """HookLoader manages all datatype hooks for display relevant variables in output"""

    def __init__(self):
        self._hooks = {}

    @classmethod
    def with_hooks(cls, hooks: dict):
        """Init HookLoader with predefined hooks"""
        loader = cls()
        loader._hooks = hooks # pylint: disable=W0212
        return loader

    def _lazy_load_hooks(self, module) -> Dict[type, Callable]:
        """Because we don't know what variables are actually used and to avoid import
        errors, we load modules which contains the imported libraries e.g numpy lazy
        and than get the hook functions"""
        try:
            module = importlib.import_module(".dt_hooks.{}".format(module), package="frosch")
        except ImportError:
            return
        self._hooks.update(module.hooks)

    def lazy_load_hooks_from_variable(self, variable: Variable):
        """Get the type of variable and look up if there is a module which contains this type"""

        if variable.value is None:
            return

        try:
            module_name = type_to_module[variable.type.__name__]
        except KeyError:
            return

        module_name = "hook_{}".format(module_name)
        self._lazy_load_hooks(module_name)


    def run_hook(self, variable: Variable) -> str:
        """Check if hook is already imported, else try import"""

        if not variable.type in self._hooks:
            self.lazy_load_hooks_from_variable(variable)

        if variable.type in self._hooks:
            return self._hooks[variable.type](variable.value)

        return variable.tree_str()
