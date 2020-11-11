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

    def test_find_next_parseable_statement(self):
        with patch("inspect.getsourcelines") as getsourcelines_mock:
            getsourcelines_mock.return_value = (
                [
                    "1+1",
                    "x = (",
                    "1",
                    "+ z)",
                    "2 + 2"
                ], 0
            )
            stack_mock = Mock()
            stack_mock.line = "x = ("
            stack_mock.lineno = 2

            result = frosch.find_next_parseable_statment(stack_mock, None)
            expected_result = "x = ( 1 + z)"
            self.assertEqual(result, expected_result)

    def test_find_next_parseable_statement2(self):
        source_lines = """
import sys
sys.path.append("..")

from frosch.frosch import hook

hook()


def hello():
    y = "Some String"
    z = [1, 2, "hel"]
    index = 0
    i = "Other string"
    x = ( 
        1 + 
        z)


def num():
    return 3


hello()

"""
        with patch("inspect.getsourcelines") as getsourcelines_mock:
            getsourcelines_mock.return_value = (
                source_lines.split("\n")
                , 0
            )
            stack_mock = Mock()
            stack_mock.line = "1 +"
            stack_mock.lineno = 15 

            result = frosch.find_next_parseable_statment(stack_mock, None)
            expected_result = "x = ( 1 + z)"
            self.assertEqual(result, expected_result)

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

            result = frosch.find_next_parseable_statment(stack_mock, None)
            expected_result = "x = (y + 1 + z)"
            self.assertEqual(result, expected_result)

    def test_get_whole_expression2(self):

        with patch("inspect.getsourcelines") as getsourcelines_mock:
            multi_line = [
                    "x = (",
                    "    y + "
                    "z)"
                ]
            getsourcelines_mock.return_value = (
                multi_line, 0
            )
            stack_mock = Mock()
            stack_mock.line = multi_line[0]
            stack_mock.lineno = 1

            result = frosch.find_next_parseable_statment(stack_mock, None)
            expected_result = "x = ( y + z)"
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
            with pytest.raises(frosch.ParseError):
                frosch.find_next_parseable_statment(stack_mock, None)

    def test_is_parsable_true(self):
        result = frosch.is_parsable("x = 3")
        self.assertTrue(result)

    def test_is_parsable_false(self):
        result = frosch.is_parsable("asd3 = (")
        self.assertFalse(result)

    def test_retrieve_post_mortem_stack_infos(self):
        with patch("bdb.Bdb.get_stack") as get_stack_mock:
            stack_mock = Mock()
            stack_mock.f_locals = {"local":"values"}
            stack_mock.f_globals = {"global":"values"}

            stack = [[stack_mock]]
            
            get_stack_mock.return_value = (stack, 0)

            tb_mock = Mock()
            result_locals, result_globals = frosch.retrieve_post_mortem_stack_infos(tb_mock)

            get_stack_mock.assert_called_with(None, tb_mock)
            self.assertEqual(stack_mock.f_locals, result_locals)
            self.assertEqual(stack_mock.f_globals, result_globals)



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

