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
from bdb import Bdb
from contextlib import contextmanager
from typing import List

from colorama import deinit, init

from .writer import ConsoleWriter, Variable


@contextmanager
def support_windows_colors():
    """Only for windows terminal"""
    init()
    yield
    deinit()

def hook():
    """Overwrite sys.excepthook and make sure windows color work too"""
    with support_windows_colors():
        sys.excepthook = pytrace_excepthook

def pytrace_excepthook(error_type: type, error_message: TypeError, traceback_: traceback=None):
    """New excepthook to overwrite sys.excepthook"""

    traceback_entries = traceback.extract_tb(traceback_)
    formatted_tb = traceback.format_exception(error_type, error_message, traceback_)

    locals_, globals_ = retrieve_post_mortem_stack_infos(traceback_)

    last_stack = traceback_entries[-1]

    names = parse_error_line(last_stack.line)

    variables = debug_variables(names, locals_, globals_)

    console_writer = ConsoleWriter()
    console_writer.output_traceback("".join(formatted_tb))
    console_writer.render_last_line(last_stack.lineno,last_stack.line)
    console_writer.write_debug_tree(variables)
    console_writer.write_newline()

def debug_variables(variables: List[Variable], locals_: dict, globals_: dict) -> List[Variable]:
    """Evaluate for every given variable the value and type"""
    for var in variables:
        try:
            value = eval(var.name, globals_, locals_)
            var.value = value
        except NameError:
            pass
    return variables


def parse_error_line(line: str):
    """Parse a line of python code and extract all (variable) names from it"""
    variables = []
    tree = ast.parse(line)
    for node in ast.walk(tree):
        # For now just try to do it with names
        if isinstance(node, ast.Name):
            variables.append(Variable(node.id, node.col_offset))
    return variables


def retrieve_post_mortem_stack_infos(traceback_):
    """Retrieve post mortem all local and global
    variables of given traceback"""

    base_debugger = Bdb()
    stack, i = base_debugger.get_stack(None, traceback_)

    # Get global and local vals
    locals_ = stack[i][0].f_locals
    globals_ = stack[i][0].f_globals
    return locals_, globals_
