import sys
import re
from io import StringIO

from contextlib import contextmanager

from unittest import TestCase
from unittest.mock import Mock, patch

import pytest

from frosch import writer
from frosch.type_hooks import HookLoader

class TestVariable(TestCase):


    def test_init_variable(self):
        variable = writer.Variable("some_name", 4)
        self.assertEqual(variable.name, "some_name")
        self.assertEqual(variable.col_offset, 4)
        self.assertIsNone(variable.value)

    def test_set_value_string(self):
        variable = writer.Variable("other_name", 15)
        variable.value = "Hello World"
        self.assertEqual(variable.tree_str(), "other_name: str = 'Hello World'")

    def test_set_value_int(self):
        variable = writer.Variable("other_name", 15)
        variable.value = 42
        self.assertEqual(variable.value, 42)

    def test_tree_str_value_none(self):
        variable = writer.Variable("other_name", 15)
        variable.value = None
        self.assertEqual(variable.tree_str(), "other_name = None")

    def test_tree_str_dict(self):
        variable = writer.Variable("other_name", 15)
        variable.value = {}
        self.assertEqual(variable.tree_str(), "other_name: dict = {}")

    def test_tree_str_type_dict(self):
        variable = writer.Variable("other_name", 15)
        variable.value = dict
        self.assertEqual(variable.tree_str(), "other_name: type = <class 'dict'>")

    def test_str_repr(self):
        variable = writer.Variable("other_name", 15)
        variable.value = 12
        self.assertEqual(str(variable), "Variable('other_name', 15, 12)")


class TestWindowsColorSupport(TestCase):

    def test_support_windows_colors_context_manager(self):
        with patch.object(writer, "init") as init_mock:
            with patch.object(writer, "deinit") as deinit_mock:
                with writer.support_windows_colors():
                    self.assertTrue(init_mock.called)
                    self.assertFalse(deinit_mock.called)
                
                self.assertTrue(deinit_mock.called)

class TestConsoleWriter(TestCase):

    def setUp(self) -> None:
        self.cw = writer.ConsoleWriter("monokai", sys.stderr,HookLoader())

    def test_offset_vert_lines(self):
        offsets = [1, 4, 7]
        line = self.cw.offset_vert_lines(offsets)

        self.assertEqual(line, " │  │  │")

    def test_left_bar(self):
        self.assertEqual(escape_ansi(self.cw.left_bar()), "||")

    def test_construct_debug_tree(self):
        lines = [
            "",
            "",
            "",
            "",
            ""
        ]
        Variable = writer.Variable

        var1 = Variable("y", 0)
        var1.value = "Something"

        var2 = Variable("x", 2)
        var2.value = "Other"
        sorted_values = [var1, var2]

        result = self.cw.construct_debug_tree(lines, sorted_values)
        result = [escape_ansi(l) for l in result]
        expected_result = ['│ │', '│ └── x: str = \'Other\'', '│', '└── y: str = \'Something\'', '']
        self.assertListEqual(result, expected_result)

    def test_write_exception(self):

        self.cw.write_traceback = Mock()
        self.cw.write_last_line = Mock()
        self.cw.write_debug_tree = Mock()
        self.cw.write_newline = Mock()

        parsed_exception = Mock()
        parsed_exception.error_type = "error_type"
        parsed_exception.error_message = "error_message"
        parsed_exception.traceback = "traceback"
        parsed_exception.last_stack = Mock()
        parsed_exception.last_stack.lineno = 42
        parsed_exception.line = "line"
        parsed_exception.variables = "variables"

        with patch("frosch.writer.support_windows_colors") as color_mock:
            self.cw.write_exception(parsed_exception)

            self.assertTrue(color_mock.called)
            self.cw.write_traceback.assert_called_once_with("error_type", "error_message", "traceback")
            self.cw.write_last_line.assert_called_once_with(42, "line")
            self.cw.write_debug_tree.assert_called_once_with("variables")
            self.assertTrue(self.cw.write_newline.called)




# https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

# Using capsys fixture
def test_write_out(capsys):
    cw = writer.ConsoleWriter("monokai", sys.stderr, HookLoader())
    cw._write_out("Hello World")
    captured = capsys.readouterr()
    assert captured.err == "Hello World"

def test_output_traceback_no_formatting_applied(capsys):
    cw = writer.ConsoleWriter("emacs", sys.stderr, HookLoader())
    with patch.object(
        writer.traceback, "format_exception", return_value=["Hello", "\n"]
    ) as format_exception:
        cw.write_traceback("A", "B", "C")
        format_exception.assert_called_once_with("A", "B", "C")
        captured = capsys.readouterr()
        assert captured.err == "Hello\n"

def test_out_traceback_with_format(capsys):
    cw = writer.ConsoleWriter("monokai", sys.stderr, HookLoader())
    tb = "Traceback Value"
    error_message = "Some Error Message"
    error_type = "IndexError"
    with patch.object(
        writer.traceback, "format_exception", return_value=["Some", "traceback"]
    ) as format_mock:
        cw.write_traceback(error_type, error_message, tb)
        format_mock.assert_called_once_with(error_type, error_message, tb)

        captured = capsys.readouterr()
        escaped_tb = escape_ansi(captured.err)
        assert escaped_tb.strip() == "Sometraceback"

def test_render_last_line(capsys):
    cw = writer.ConsoleWriter("vim", sys.stderr, HookLoader())
    cw.write_last_line(42, "x = hello * 'String'")
    captured = capsys.readouterr()
    output = escape_ansi(captured.err).strip()
    assert output == "42 || x = hello * 'String'"

def test_write_debug_tree(capsys):
    Variable = writer.Variable

    var1 = Variable("y", 0)
    var1.value = "Something"

    var2 = Variable("x", 2)
    var2.value = "Other"
    sorted_values = [var1, var2]

    console_writer = writer.ConsoleWriter("monokai", sys.stderr, HookLoader())
    console_writer.left_offset = 1
    console_writer.write_debug_tree(sorted_values)

    capture = capsys.readouterr()
    result = escape_ansi(capture.err)
    expected_result = """   || │ │
   || │ └── x: str = 'Other'
   || │
   || └── y: str = 'Something'
   || \n"""
    assert result == expected_result

def test_write_debug_tree_offset_2(capsys):
    Variable = writer.Variable

    var1 = Variable("y", 0)
    var1.value = "Something"

    var2 = Variable("x", 2)
    var2.value = "Other"
    sorted_values = [var1, var2]

    console_writer = writer.ConsoleWriter("monokai", sys.stderr, HookLoader())
    console_writer.left_offset = 2
    console_writer.write_debug_tree(sorted_values)

    capture = capsys.readouterr()
    result = escape_ansi(capture.err)
    expected_result = """    || │ │
    || │ └── x: str = 'Other'
    || │
    || └── y: str = 'Something'
    || \n"""
    assert result == expected_result
