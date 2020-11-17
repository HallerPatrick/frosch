import unittest
from unittest import TestCase
from unittest.mock import Mock, patch

import pytest

from frosch import parser


class TestParser(TestCase):


    def test_debug_variables_none_locals_globals(self):
        variables = [
            parser.Variable("x", 4),
            parser.Variable("y", 10)
        ]

        _locals = {}
        _globals = {}

        expected_result = parser.debug_variables(variables, _locals, _globals)

        for var in expected_result:
            self.assertIsNone(var.value, None)

    def test_debug_variables(self):
        variables = [
            parser.Variable("x", 4),
            parser.Variable("y", 10)
        ]

        _locals = {"x": "Hello", "y": 3}
        _globals = {}

        expected_result = parser.debug_variables(variables, _locals, _globals)

        for variable in expected_result:
            if variable.name == "x":
                self.assertEqual(variable.value, "Hello")

            if variable.name == "y":
                self.assertEqual(variable.value, 3)

    def test_parse_error_lines_single_line_simple(self):
        line = "x"
        result = parser.parse_error_line(line)
        expected_result = [parser.Variable("x", 0)]
        self.assertListEqual(result, expected_result)

    def test_parse_error_lines_single_line_variables_and_constants(self):
        line = "x = y + 2 + z"
        result = parser.parse_error_line(line)
        expected_result = [
            parser.Variable("x", 0),
            parser.Variable("y", 4),
            parser.Variable("z", 12)
            ]
        self.assertCountEqual(result, expected_result)

    def test_parse_error_line_multiline_throw_error(self):
        line = "x = ( y"

        with pytest.raises(parser.ParseError):
            parser.parse_error_line(line)

    def test_parse_error_indentation_case(self):
        line = "for i in range(10):"
        result = parser.parse_error_line(line)
        expected_result = [
            parser.Variable("i", 4),
            parser.Variable("range", 9)
        ]

        self.assertCountEqual(result, expected_result)

    def test_parse_error_indentation_case2(self):
        line = "if(x == 3):"
        result = parser.parse_error_line(line)
        expected_result = [
            parser.Variable("x", 3),
        ]

        self.assertCountEqual(result, expected_result)

    @unittest.skip("Not working yet")
    def test_extract_statement_piece(self):
        """Check if collection of pieces/token from list is working"""
        last_stack_mock = Mock()
        last_stack_mock.lineno = 12
        with patch.object(parser.stack_data, "FrameInfo") as frame_info_mock:
            frame_info_mock.executing = Mock()
            frame_info_mock.executing.source = Mock()
            type(frame_info_mock.executing.source).pieces = PropertyMock(
                return_value=[range(0, 2), range(3, 7), range(11, 12)]
            )
            frame_info_mock.source.tokens_by_lineno = {
                0: None,
                2: None,
                11: "target",
                12: "target2"
            }

            traceback_mock = Mock()

            result = parser.extract_statement_piece(
                traceback_mock, last_stack_mock
                )

            self.assertListEqual(result, ["target", "target2"])

    def test_extract_source_code(self):
        def make_token(val):
            token = Mock()
            token.string = val
            return token 

        tokens = [
            [
                make_token("x"),
                make_token("="),
                make_token("3")
            ]
        ]

        result = parser.extract_source_code(tokens)

        self.assertEqual(result, "x = 3")


    def test_retrieve_post_mortem_stack_infos(self):
        with patch("bdb.Bdb.get_stack") as get_stack_mock:
            stack_mock = Mock()
            stack_mock.f_locals = {"local":"values"}
            stack_mock.f_globals = {"global":"values"}

            stack = [[stack_mock]]
            
            get_stack_mock.return_value = (stack, 0)

            tb_mock = Mock()
            result_locals, result_globals = parser.retrieve_post_mortem_stack_infos(tb_mock)

            get_stack_mock.assert_called_with(None, tb_mock)
            self.assertEqual(stack_mock.f_locals, result_locals)
            self.assertEqual(stack_mock.f_globals, result_globals)
    
    def test_format_line_whitespaces(self):
        line = "x  = { 'key' : 3  }"
        result = parser.format_line(line)
        self.assertEqual(result, "x = {'key': 3}")

    def test_format_line_indentation_error(self):
        line = "for i   in range(0,    10):"
        result = parser.format_line(line)
        self.assertEqual(result, "for i in range(0, 10):")

    def test_format_line_syntax_error(self):
        with pytest.raises(parser.ParseError):
            parser.format_line("x asd ")

class TestParsedException(TestCase):

    def test_parsed_exception_init(self):
        with patch.object(parser.traceback, "extract_tb") as extract_mock:
            with patch.object(parser.ParsedException, "_get_source_line") as source_line_mock:
                with patch.object(parser.ParsedException, "_get_variables") as get_vars_mock:
                    exception = parser.ParsedException("traceback", "error_type", "error_message" )
                    self.assertEqual(exception.traceback, "traceback")
                    self.assertEqual(exception.error_type, "error_type")
                    self.assertEqual(exception.error_message, "error_message")

                    self.assertTrue(extract_mock.called)
                    self.assertTrue(source_line_mock.called)
                    self.assertTrue(get_vars_mock.called)

    def test__get_source_line(self):
        # Mhh a lot of mocking
        with patch.object(parser.traceback, "extract_tb") as extract_mock:
            with patch.object(parser.ParsedException, "_get_variables") as get_vars_mock:

                with patch.object(parser.ParsedException, "_extract_tokens_from_stack") as extract_mock:
                    extract_mock.return_value = "tokens"
                    with patch.object(parser, "extract_source_code") as source_mock:
                        source_mock.return_value = "Line"
                        with patch.object(parser, "format_line") as format_mock:
                            format_mock.return_value = "Formatted Line\n"
                            exception = parser.ParsedException("traceback", "error_type", "error_message" )
                            self.assertEqual(exception.line, "Formatted Line")
                            self.assertTrue(extract_mock.called)
                            source_mock.assert_called_once_with("tokens")
                            format_mock.assert_called_once_with("Line")
                            

