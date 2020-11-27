"""

    frosch - Better runtime errors

    Patrick Haller
    betterthannothing.blog
    patrickhaller40@googlemail.com

    License MIT

"""
import ast
from bdb import Bdb
import builtins
import linecache
import traceback

from collections import ChainMap
from types import TracebackType
from typing import Any, List

from asttokens.util import Token
from stack_data import Source
from yapf.yapflib.yapf_api import FormatCode

class ParseError(Exception):
    """Thrown in crashing line cannot be parsed with ast.parse"""

class Variable:
    """Dataclass for a variable in error throwing line of program"""

    def __init__(self, id_: str, col_offset: int, value: Any = None):
        self.name = id_
        self.col_offset = col_offset
        self.value = value

    def __repr__(self):
        """str representation of a Variable object"""
        return "Variable({!r}, {}, {!r})".format(self.name, self.col_offset, self.value)

    def __eq__(self, other: "Variable"):
        """Mainly for testing purpose"""
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        """We don't care for unique hashes"""
        return hash((self.name, self.col_offset, self.value))

    @property
    def type(self):
        """Property for the type of a value"""
        return type(self.value)

    def tree_str(self):
        """Python>3.8 variable declaration format with types"""
        if self.value is None:
            return "{} = None".format(self.name)
        return "{}: {} = {!r}".format(self.name, type(self.value).__qualname__, self.value)

class ParsedException():
    """Handling all data relevant to parsing and formatting the received exception raising"""
    def __init__(self, traceback_: TracebackType, error_type, error_message):
        self.traceback = traceback_
        self.error_type = error_type
        self.error_message = error_message

        # Get last stack where crash occuredtrace
        self.last_stack = traceback.extract_tb(traceback_)[-1]

        self.line = self._get_source_line()
        self.variables = self._get_variables()

    def _get_source_line(self):
        """Get source line which causes the program to crash it also gets formatted into one line
        """
        tokens = self._extract_tokens_from_stack()

        # Format into one line
        line = extract_source_code(tokens)
        line = format_line(line)
        return line.strip()

    def _get_variables(self):
        """Get a list of variable objects holding all vars contained in the source line"""
        return self._get_vars_from_tb()


    def _extract_tokens_from_stack(self):
        """Load file of stack and get the relevant tokens from statement"""
        # Get the source of the last stack
        source = Source(self.last_stack.filename, linecache.getlines(self.last_stack.filename))

        # Extract all relevant parts
        tokens = extrace_statement_from_source(source, self.last_stack)
        return tokens

    def _get_vars_from_tb(self) -> List[Variable]:
        """Extract all variables from a line and a given traceback"""

        # Parse to get all names
        names = parse_error_line(self.line)

        # Retrieve locals and globals from the dead
        locals_, globals_ = retrieve_post_mortem_stack_infos(self.traceback)

        # Get all variables and values
        variables = debug_variables(names, locals_, globals_)

        return variables

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

def format_line(line: str) -> str:
    """Try format a source code line"""

    formatted_line = line
    try:
        # If we handling multilines this will not be parsed
        formatted_line, _ =  FormatCode(line)

    except IndentationError as error:
        # Case of trying to parse a piece of a statement, like a for loop header
        # Try again with a pass stament
        formatted_line, _ = FormatCode(line + "pass")
        formatted_line = formatted_line.replace("pass", "")

    except SyntaxError as error:
        if error.args[0] == "unexpected EOF while parsing":
            try:
                formatted_line, _ = FormatCode(line + "pass")
                formatted_line = formatted_line.replace("pass", "")
            except SyntaxError as syntax_error:
                raise ParseError("Could not parse line: {}".format(line)) from syntax_error
        else:
            raise ParseError("Could not parse line: {}".format(line)) from error

    return formatted_line.strip()

def retrieve_post_mortem_stack_infos(traceback_: TracebackType):
    """Retrieve post mortem all local and global
    variables of given traceback"""

    base_debugger = Bdb()
    stack, i = base_debugger.get_stack(None, traceback_)

    # Get global and local vals
    locals_ = stack[i][0].f_locals
    globals_ = stack[i][0].f_globals
    return locals_, globals_
