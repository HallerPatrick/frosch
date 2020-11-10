import sys

import unittest
from unittest import TestCase
from unittest.mock import Mock, patch

import pytest

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
                self.assertEqual(variable.value, "Hello")

            if variable.name == "y":
                self.assertEqual(variable.value, 3)

    def test_parse_error_lines_single_line_simple(self):
        line = "x"
        result = frosch.parse_error_line(line)
        expected_result = [frosch.Variable("x", 0)]
        self.assertListEqual(result, expected_result)

    def test_parse_error_lines_single_line_variables_and_constants(self):
        line = "x = y + 2 + z"
        result = frosch.parse_error_line(line)
        expected_result = [
            frosch.Variable("x", 0),
            frosch.Variable("y", 4),
            frosch.Variable("z", 12)
            ]
        self.assertCountEqual(result, expected_result)


    def test_parse_error_line_multiline_throw_error(self):
        line = "x = ( y"

        with pytest.raises(frosch.ParseError):
            frosch.parse_error_line(line)

    def test_get_whole_expression(self):

        with patch("inspect.getsourcelines") as getsourcelines_mock:
            getsourcelines_mock.return_value = (
                [
                    "x = (y",
                    "+ 1",
                    "+ z)"
                ], 0
            )
            stack_mock = Mock()
            stack_mock.line = "x = (y"
            stack_mock.lineno = 1

            result = frosch.get_whole_expression(stack_mock, None)
            expected_result = "x = (y + 1 + z)"
            self.assertEqual(result, expected_result)


    def test_get_whole_expression_syntax_error(self):

        with patch("inspect.getsourcelines") as getsourcelines_mock:
            getsourcelines_mock.return_value = (
                [
                    "x = (y",
                    "+ 1",
                ], 0
            )
            stack_mock = Mock()
            stack_mock.line = "x = (y"
            stack_mock.lineno = 1
            with pytest.raises(SyntaxError):
                frosch.get_whole_expression(stack_mock, None)

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

