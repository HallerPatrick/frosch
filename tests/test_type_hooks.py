import contextlib
import unittest
from unittest.mock import Mock, patch
import sys

from frosch.type_hooks import HookLoader
from frosch.parser import Variable


@contextlib.contextmanager
def mock_module(module_name):
    """Inject a numpy mock to avoid import errors"""
    numpy_mock = Mock()
    numpy_mock.name = module_name
    sys.modules[module_name] = numpy_mock
    yield numpy_mock
    del sys.modules[module_name]


class TestLoader(unittest.TestCase):
    def test_lazy_load_hooks_numpy(self):
        with mock_module("numpy"):
            hook_loader = HookLoader()
            hook_loader._lazy_load_hooks("hook_numpy")
            self.assertEqual(len(hook_loader._hooks), 2)

    def test_lazy_load_hooks_pytorch(self):
        with mock_module("torch"):
            hook_loader = HookLoader()
            hook_loader._lazy_load_hooks("hook_torch")
            self.assertEqual(len(hook_loader._hooks), 1)

    def test_lazy_load_numpy_hooks_from_variable(self):
        class ndarray:
            pass

        nd_array = ndarray()
        var = Variable("nd_array", 2, nd_array)

        with patch("frosch.type_hooks.HookLoader._lazy_load_hooks") as lazy_hook_mock:
            hook_loader = HookLoader()
            hook_loader.lazy_load_hooks_from_variable(var)
            lazy_hook_mock.assert_called_once_with("hook_numpy")

    def test_lazy_load_torch_hooks_from_variable(self):
        class Tensor:
            pass

        _tensor = Tensor()
        var = Variable("tens", 2, _tensor)

        with patch("frosch.type_hooks.HookLoader._lazy_load_hooks") as lazy_hook_mock:
            hook_loader = HookLoader()
            hook_loader.lazy_load_hooks_from_variable(var)
            lazy_hook_mock.assert_called_once_with("hook_torch")
