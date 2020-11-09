import sys

import unittest
from unittest import TestCase
from unittest.mock import Mock

from frosch import frosch



class TestFrosch(TestCase):


    def setUp(self):
        pass


    def test_hook_attached(self):
        _old_excepthook = sys.excepthook
        frosch.hook()
        self.assertEqual(frosch.pytrace_excepthook, sys.excepthook)

        sys.excepthook = _old_excepthook

    def test_debug_variables_none_locals_globals(self):
        variables = [
            frosch.Variable("x", 4),
            frosch.Variable("y", 10)
        ]

        _locals = {}
        _globals = {}

        expected_result = frosch.debug_variables(variables, _locals, _globals)

        for var in expected_result:
            self.assertIsNone(var.value, None)

    def test_debug_variables(self):
        variables = [
            frosch.Variable("x", 4),
            frosch.Variable("y", 10)
        ]

        _locals = {"x": "Hello", "y": 3}
        _globals = {}

        expected_result = frosch.debug_variables(variables, _locals, _globals)

        for variable in expected_result:
            if variable.name == "x":
                self.assertEqual(variable.value, "'Hello'")

            if variable.name == "y":
                self.assertEqual(variable.value, 3)

    @unittest.skip("How to test this?")
    def test_pytrace_excepthook(self):
        _old_excepthook = sys.excepthook

        def custom_hook(error_type, error_message, tb):
            # Mock console writer to check if called correctly
            frosch.ConsoleWriter = Mock()
            frosch.ConsoleWriter.output_traceback = Mock()
            frosch.ConsoleWriter.render_last_line = Mock()
            frosch.ConsoleWriter.write_debug_tree = Mock()
            frosch.ConsoleWriter.write_newlines = Mock()

            frosch.pytrace_excepthook(error_type, error_message, tb)

        sys.excepthook = custom_hook