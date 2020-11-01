"""

    frosch - Better runtime errors

    Patrick Haller
    betterthannothing.blog
    patrickhaller40@googlemail.com

    License MIT

"""

import sys
from typing import Any, List

import colorama
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.python import Python3Lexer, Python3TracebackLexer
from pygments.styles.monokai import MonokaiStyle


class Variable:
    """Dataclass for a variable in error throwing line of program"""

    def __init__(self, id_: str, col_offset: int):
        self.name = id_
        self.col_offset = col_offset
        self._value = None
        self.type = None

    @property
    def value(self) -> Any:
        """Value of variable"""
        return self._value

    @value.setter
    def value(self, value):
        """Setter for value"""
        self.type = type(value)

        if self.type_name == "str":
            self._value = '"{}"'.format(value)
        else:
            self._value = value

    def __str__(self):
        """str representation of a Variable object"""
        return "{}: {} ({})".format(self.name, self.value, self.col_offset)

    def tree_str(self):
        """Python>3.8 variable declaration format with types"""
        return "{}: {} = {}".format(self.name, self.type_name, self.value)

    @property
    def type_name(self):
        """Getter for type of variable in string format"""
        if self.type is None:
            return "None"
        return self.type.__name__





class ConsoleWriter:
    """Handles formatting, highlighting and writing to output of error message"""

    def __init__(self):
        self.stderr = sys.stderr
        self.terminal_formater = Terminal256Formatter(style=MonokaiStyle)
        self.python_lexer = Python3Lexer()
        self.python_traceback_lexer = Python3TracebackLexer()

    def output_traceback(self, traceback_):
        """Highlight traceback and write out"""
        self._write_out(highlight(traceback_, self.python_traceback_lexer, self.terminal_formater))

    @staticmethod
    def offset_vert_lines(offsets) -> str:
        """Construct a line with vertical bars for all offsets in offsets"""
        line = ""

        current_offset = -1

        # First line
        for offset in offsets:
            new_offset = offset - current_offset -1
            line += (" " * new_offset)
            line += "│"
            current_offset = offset

        return line

    @staticmethod
    def left_bar() -> str:
        """Bar used on left side of debug tree"""
        return colorama.Fore.BLUE + "||"

    def _write_out(self, message: str):
        """Write to stderr"""
        self.stderr.write(message)
        self.stderr.flush()

    def write_newline(self):
        """Write newline to stderr"""
        self.stderr.write("\n")
        self.stderr.flush()


    def write_debug_tree(self, names: List[Variable]):
        """Sort offsets and values for construction of debug tree"""

        sorted_values = list(sorted(names, key=lambda val: val.col_offset))

        num_variables = len(sorted_values)

        lines = ["    {} ".format(self.left_bar()) for _ in range((2*num_variables) + 1)]


        self.construct_debug_tree(lines, sorted_values)

        for line in lines:
            self._write_out(line)
            self.write_newline()

    def construct_debug_tree(self, lines, sorted_values):
        """Construction of debug tree"""
        current_offset = -1
        offsets = [val.col_offset for val in sorted_values]

        unprocessed_values = len(sorted_values)

        # First line
        lines[0] += self.offset_vert_lines(offsets)

        i = 1
        for value in reversed(sorted_values):
            # For every value
            for j in range(unprocessed_values):
                new_offset = sorted_values[j].col_offset - current_offset -1
                lines[i] += (" " * (new_offset))

                if j != (unprocessed_values - 1):
                    lines[i] += "│"
                else:
                    lines[i] += "└── {}".format(
                        highlight(value.tree_str(), self.python_lexer, self.terminal_formater)
                        .rstrip()
                    )

                    # Add spacong row
                    if offsets:
                        del offsets[-1]
                    i += 1
                    lines[i] += self.offset_vert_lines(offsets)

                current_offset = sorted_values[j].col_offset
            unprocessed_values -= 1
            current_offset = -1
            i += 1

        return lines

    def render_last_line(self, lineno: int, line: str):
        """Write out the line which throws runtime error with highlighting"""
        self.write_newline()
        self._write_out(" {} {} {}\n".format(
            lineno,
            self.left_bar(),
            highlight(line, self.python_lexer, self.terminal_formater).rstrip())
        )
