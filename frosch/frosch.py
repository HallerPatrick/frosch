"""

    frosch - Better runtime errors

    Patrick Haller
    betterthannothing.blog
    patrickhaller40@googlemail.com

    License MIT

"""

import ast
import sys
import traceback
from traceback import FrameSummary
from bdb import Bdb
import builtins
from contextlib import contextmanager
from collections import ChainMap
import inspect
from typing import List

from colorama import deinit, init

from .writer import ConsoleWriter, Variable

class ParseError(Exception):
    """Thrown in crashing line cannot be parsed with ast.parse"""

@contextmanager
def support_windows_colors():
    """Only for windows terminal"""
    init()
    yield
    deinit()

def hook():
    """Overwrite sys.excepthook and make sure windows color work too"""
    sys.excepthook = pytrace_excepthook

def pytrace_excepthook(error_type: type, error_message: TypeError, traceback_: traceback=None):
    """New excepthook to overwrite sys.excepthook"""

    traceback_entries = traceback.extract_tb(traceback_)
    formatted_tb = traceback.format_exception(error_type, error_message, traceback_)

    locals_, globals_ = retrieve_post_mortem_stack_infos(traceback_)

    last_stack = traceback_entries[-1]
    last_line = last_stack.line

    try:
        names = parse_error_line(last_line)
    except ParseError:
        # Try to collect multiline expression
        last_line = get_whole_expression(last_stack, traceback_)
        names = parse_error_line(last_line)

    variables = debug_variables(names, locals_, globals_)

    with support_windows_colors():
        console_writer = ConsoleWriter()
        console_writer.output_traceback("".join(formatted_tb))
        console_writer.render_last_line(last_stack.lineno, last_line)
        console_writer.write_debug_tree(variables)
        console_writer.write_newline()

def debug_variables(variables: List[Variable], locals_: dict, globals_: dict) -> List[Variable]:
    """Evaluate for every given variable the value and type"""
    chainmap = ChainMap(locals_, globals_, vars(builtins))
    for var in variables:
        try:
            value = chainmap[var.name]
            var.value = value
        except KeyError:
            pass
    return variables


def parse_error_line(line: str):
    """Parse a line of python code and extract all (variable) names from it"""
    variables = []
    try:
        # If we handling multilines this will not be parsed
        tree = ast.parse(line)
    except SyntaxError as error:
        raise ParseError("Could not parse line: {}".format(line)) from error

    for node in ast.walk(tree):
        # For now just try to do it with names
        if isinstance(node, ast.Name):
            variables.append(Variable(node.id, node.col_offset))
    return variables


def get_whole_expression(stack: FrameSummary, traceback_: traceback) -> str:
    """Try to search the following lines to get a whole parsable expression"""
    source_lines = inspect.getsourcelines(traceback_)[0]

    current_lines = [stack.line]
    current_line_no = stack.lineno

    parsed = False

    while not parsed:
        try:
            current_lines.append(source_lines[current_line_no].strip())
        except IndexError as error:
            # Reached EOF
            # This should never happen, as this means there is a
            # SyntaxError in the python file, which would be caught
            # way early, but still...

            # What is the correct way to handle a failure in frosch?
            # Is there a way to let the original excepthook handle
            # from this point?
            raise SyntaxError("SyntaxError in line:{}".format(stack.lineno)) from error

        whole_line = "".join(current_lines)

        try:
            ast.parse(whole_line)
            parsed = True
        except SyntaxError:
            current_line_no += 1

    return " ".join(current_lines)


def retrieve_post_mortem_stack_infos(traceback_):
    """Retrieve post mortem all local and global
    variables of given traceback"""

    base_debugger = Bdb()
    stack, i = base_debugger.get_stack(None, traceback_)

    # Get global and local vals
    locals_ = stack[i][0].f_locals
    globals_ = stack[i][0].f_globals
    return locals_, globals_
