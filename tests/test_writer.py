import sys
import re
from io import StringIO

from contextlib import contextmanager

from unittest import TestCase

import pytest

from frosch import writer

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


class TestConsoleWriter(TestCase):

    def setUp(self) -> None:
        self.cw = writer.ConsoleWriter("monokai")

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


    def test__get_theme_from_string(self):
        themes = [
            "abap",
            "algol",
            "algol_nu",
            "arduino",
            "autumn",
            "borland",
            "bw",
            "colorful",
            "default",
            "emacs",
            "friendly",
            "fruity",
            "igor",
            "inkpot",
            "lovelace",
            "manni",
            "monokai",
            "murphy",
            "native",
            "paraiso_dark",
            "paraiso_light",
            "pastie",
            "perldoc",
            "rainbow_dash",
            "rrt",
            "sas",
            "solarized",
            "stata_dark",
            "stata_light",
            "tango",
            "trac",
            "vim",
            "vs",
            "xcode"
        ]
        for theme in themes:
            writer.ConsoleWriter(theme)

    def test_capitalize_theme(self):
        """Most testing done with testing _get_theme_from_string"""
        writer.ConsoleWriter._get_theme_from_string("vs")

    def test__get_theme_from_string_not_found(self):
        with pytest.raises(writer.ThemeNotExistsError):
            writer.ConsoleWriter._get_theme_from_string("not existing")


# https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

# Using capsys fixture
def test_write_out(capsys):
    cw = writer.ConsoleWriter("monokai")
    cw._write_out("Hello World")
    captured = capsys.readouterr()
    assert captured.err == "Hello World"

def test_output_traceback_no_formatting_applied(capsys):
    cw = writer.ConsoleWriter("monokai")
    cw.output_traceback("Hello")
    captured = capsys.readouterr()
    assert captured.err == "Hello\n"

def test_out_traceback_with_format(capsys):
    cw = writer.ConsoleWriter("monokai")
    tb = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    3 + 'String'
TypeError: unsupported operand type(s) for +: 'int' and 'str'"""
    cw.output_traceback(tb)

    captured = capsys.readouterr()
    escaped_tb = escape_ansi(captured.err)
    assert escaped_tb.strip() == tb.strip()

def test_render_last_line(capsys):
    cw = writer.ConsoleWriter("monokai")
    cw.render_last_line(42, "x = hello * 'String'")
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

    console_writer = writer.ConsoleWriter("monokai")
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

    console_writer = writer.ConsoleWriter("monokai")
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

