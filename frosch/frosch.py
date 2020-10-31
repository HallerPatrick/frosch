import ast
from bdb import Bdb
import bdb
import traceback
import sys
import pdb
from typing import List

from contextlib import contextmanager

from colorama import init, deinit

from .parser import OutputParser, Variable
from .analyzer import retrieve_post_mortem_stack_infos


@contextmanager
def support_windows_colors():
    init()
    yield
    deinit()

def hook():
    with support_windows_colors():
        sys.excepthook = pytrace_excepthook

def _flush(message):
    sys.stderr.write(message + "\n")
    sys.stderr.flush()

def pytrace_excepthook(error_type, error_message, tb=None):

    traceback_entries = traceback.extract_tb(tb)
    formatted_tb = traceback.format_exception(error_type, error_message, tb)

    locals_, globals_ = retrieve_post_mortem_stack_infos(tb)

    op = OutputParser()

    # handle_stacktrace(traceback_entries, op)
    print(op.output_traceback("".join(formatted_tb)))

    last_stack = traceback_entries[-1]

    names = parse_error_line(last_stack.line)

    variables = debug_variables(names, locals_, globals_)

    op.render_last_line(last_stack.lineno,last_stack.line)
    op.render_values(variables) 
    print()

def debug_variables(variables: List[Variable], locals_, globals_) -> List[Variable]:
    for var in variables:
        try:
            value = eval(var.name, globals_, locals_)
            var.type = type(value)
            var.value = value
        except NameError:
            pass
    return variables


def parse_error_line(line: str):
    # TODO: Lets parse this correctly with 
    # Python parser or ASt? 
    # eval(line, globals, locals)
    variables = []
    tree = ast.parse(line)
    for node in ast.walk(tree):
        # For now just try to do it with names
        if isinstance(node, ast.Name):
            variables.append(Variable(node.id, node.col_offset))
    return variables


def handle_stacktrace(traceback_entries, op):
    _flush("Traceback (most recent call last):")
    for entry in traceback_entries:
        _flush(op.format_traceback(entry))

    _flush("")

