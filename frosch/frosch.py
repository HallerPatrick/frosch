"""

    frosch - Better runtime errors

    Patrick Haller
    betterthannothing.blog
    patrickhaller40@googlemail.com

    License MIT

"""

import ast
import linecache
import sys
import traceback
from bdb import Bdb
import builtins
from contextlib import contextmanager
from collections import ChainMap
from types import TracebackType
from typing import List

from asttokens.util import Token
from colorama import deinit, init
from stack_data import Source

from .config_manager import ConfigManager
from .notifier import notify_os
from .writer import ConsoleWriter, Variable


class ParseError(Exception):
    """Thrown in crashing line cannot be parsed with ast.parse"""

@contextmanager
def support_windows_colors():
    """Only for windows terminal"""
    init()
    yield
    deinit()

def hook(**kwargs):
    """Initialize configurations for frosch and set hook"""
    if kwargs:
        config_manager = ConfigManager.default().from_kwargs(**kwargs)
    else:
        config_manager = ConfigManager.default()

    pytrace_excepthook.configs = config_manager
    _hook()

def _hook():
    """Overwrite sys.excepthook"""
    # Don't want global vars
    sys.excepthook = pytrace_excepthook

def pytrace_excepthook(error_type: type, error_message: TypeError, traceback_: TracebackType=None):
    """New excepthook to overwrite sys.excepthook"""
    configs = pytrace_excepthook.configs

    # Get last stack where crash occured
    last_stack = traceback.extract_tb(traceback_)[-1]

    # Get the source of the last stack
    source = Source(last_stack.filename, linecache.getlines(last_stack.filename))

    # Extract all relevant parts
    tokens = extrace_statement_from_source(source, last_stack)

    # Format into one line
    line = extract_source_code(tokens)

    # Parse to get all names
    names = parse_error_line(line)

    # Retrieve locals and globals from the dead
    locals_, globals_ = retrieve_post_mortem_stack_infos(traceback_)

    # Get all variables and values
    variables = debug_variables(names, locals_, globals_)

    # Write down
    with support_windows_colors():
        console_writer = ConsoleWriter(configs.theme)
        console_writer.write_traceback(
            "".join(traceback.format_exception(error_type, error_message, traceback_))
        )
        console_writer.write_last_line(last_stack.lineno, line)
        console_writer.write_debug_tree(variables)
        console_writer.write_newline()

    if configs.has_notifier():
        notify_os(configs.title, configs.message)

def extrace_statement_from_source(source: Source, last_stack) -> List[List[Token]]:
    """Get frame infos and get code pieces (from stack_data) by line
    of crash """
    pieces = source.pieces
    tokens = source.tokens_by_lineno

    statement_piece_tokens = []
    for piece in pieces:
        if last_stack.lineno in list(piece):
            for line in list(piece):
                statement_piece_tokens.append(tokens[line])

    return statement_piece_tokens

def extract_source_code(tokens: List[List[Token]]) -> str:
    """Get all strings of the tokens and flatten into on list"""
    statement_line = []
    for line_tokens in tokens:
        for token in line_tokens:
            string = token.string
            if not string.strip() == "":
                statement_line.append(string.strip())

    return " ".join(statement_line)

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


def parse_error_line(line: str) -> List[Variable]:
    """Parse a line of python code and extract all (variable) names from it"""
    variables = []
    try:
        # If we handling multilines this will not be parsed
        tree = ast.parse(line)

    except IndentationError as error:
        # Case of trying to parse a piece of a statement, like a for loop header
        # Try again with a pass stament
        tree = ast.parse(line + "pass")

    except SyntaxError as error:
        if error.args[0] == "unexpected EOF while parsing":
            try:
                tree = ast.parse(line + "pass")
            except SyntaxError as syntax_error:
                raise ParseError("Could not parse line: {}".format(line)) from syntax_error
        else:
            raise ParseError("Could not parse line: {}".format(line)) from error

    for node in ast.walk(tree):
        # For now just try to do it with names
        if isinstance(node, ast.Name):
            variables.append(Variable(node.id, node.col_offset))
    return variables

def retrieve_post_mortem_stack_infos(traceback_: TracebackType):
    """Retrieve post mortem all local and global
    variables of given traceback"""

    base_debugger = Bdb()
    stack, i = base_debugger.get_stack(None, traceback_)

    # Get global and local vals
    locals_ = stack[i][0].f_locals
    globals_ = stack[i][0].f_globals
    return locals_, globals_
