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
        last_line = find_next_parseable_statment(last_stack, traceback_)
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

def find_next_parseable_statment(stack: FrameSummary, traceback_: traceback) -> str:
    """If we handling multiline statements we have to look both ways (up and down)
    to find the whole statement. We therefore incrementally go up and down the
    lines and add them to the current line while the single line is not parseable

    Note:
        This is not working on all cases, e.g if multiline statement
        contains lines, which are "parsable" on their own
        x = (
            # This line is parsable on its own
            1 +
            "String"
        )

    """
    source_lines = inspect.getsourcelines(traceback_)[0]

    current_lines = [source_lines[stack.lineno].strip()]

    current_line_before = stack.lineno - 1
    current_line_after = stack.lineno + 1

    found_parseable_line_before = False
    found_parseable_line_after = False

    while True:

        # Check line before
        if current_line_before >= 0:
            if is_parsable(source_lines[current_line_before]):
                found_parseable_line_before = True
            else:
                current_lines.insert(0, source_lines[current_line_before].strip())
                current_line_before -= 1
        else:
            found_parseable_line_before = True

        # Check line after
        if not current_line_after >= len(source_lines):

            if is_parsable(source_lines[current_line_after]):
                found_parseable_line_after = True
            else:
                current_lines.append(source_lines[current_line_after].strip())
                current_line_after += 1
        else:
            found_parseable_line_after = True

        # If both are parsable return
        if found_parseable_line_after and found_parseable_line_before:
            parsable_line = " ".join(current_lines)
            if is_parsable(parsable_line):
                return parsable_line
            raise ParseError("Could not parse mutiline statement: {}".format(parsable_line))

def is_parsable(line: str) -> bool:
    """Test if a line of python is parsable or not"""
    try:
        ast.parse(line.strip())
    except SyntaxError:
        return False
    return True

def retrieve_post_mortem_stack_infos(traceback_):
    """Retrieve post mortem all local and global
    variables of given traceback"""

    base_debugger = Bdb()
    stack, i = base_debugger.get_stack(None, traceback_)

    # Get global and local vals
    locals_ = stack[i][0].f_locals
    globals_ = stack[i][0].f_globals
    return locals_, globals_
