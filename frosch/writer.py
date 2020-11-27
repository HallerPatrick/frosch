"""

    frosch - Better runtime errors

    Patrick Haller
    patrickhaller40@googlemail.com

    License MIT

    writer handles are the writing and formating to output stream

"""

from contextlib import contextmanager
import traceback
from typing import List

from colorama import Fore, Style, init, deinit
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.python import Python3Lexer, Python3TracebackLexer

from .parser import ParsedException, Variable
from .type_hooks import HookLoader

class WrongWriteOrder(Exception):
    """Thrown when the correct order of parts to be written to stream is not correct"""

@contextmanager
def support_windows_colors():
    """Only for windows terminal"""
    init()
    yield
    deinit()

class ConsoleWriter:
    """Handles formatting, highlighting and writing to output of error message"""

    def __init__(self, theme, stream, hook_loader: HookLoader):
        self.stream = stream
        self.terminal_formater = Terminal256Formatter(style=theme)
        self.python_lexer = Python3Lexer()
        self.python_traceback_lexer = Python3TracebackLexer()
        self.left_offset = None
        self.hook_loader = hook_loader

    def write_exception(self, parsed_exception: ParsedException):
        """Handles all write methods"""
        # Write down
        with support_windows_colors():
            self.write_traceback(
                parsed_exception.error_type,
                parsed_exception.error_message,
                parsed_exception.traceback
            )
            self.write_last_line(parsed_exception.last_stack.lineno, parsed_exception.line)
            self.write_debug_tree(parsed_exception.variables)
            self.write_newline()

    def write_traceback(self, error_type, error_message, traceback_):
        """Highlight traceback and write out"""
        formatted_exception = "".join(
            traceback.format_exception(error_type, error_message, traceback_)
        )
        self._write_out(
            highlight(formatted_exception, self.python_traceback_lexer, self.terminal_formater)
        )

    @staticmethod
    def offset_vert_lines(offsets: List[int]) -> str:
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
        return Fore.BLUE + "||" + Style.RESET_ALL

    def _write_out(self, message: str):
        """Write to stream"""
        self.stream.write(message)
        self.stream.flush()

    def write_newline(self):
        """Write newline to stderr"""
        self.stream.write("\n")
        self.stream.flush()


    def write_debug_tree(self, names: List[Variable]):
        """Sort offsets and values for construction of debug tree"""

        sorted_values = list(sorted(names, key=lambda val: val.col_offset))

        num_variables = len(sorted_values)
        try:
            line_offset = " " * self.left_offset
        except TypeError as type_error:
            raise WrongWriteOrder("Offset not defined") from type_error

        lines = [
           "  {}{} ".format(line_offset, self.left_bar()) for _ in range((2*num_variables) + 1)
        ]


        self.construct_debug_tree(lines, sorted_values)

        for line in lines:
            self._write_out(line)
            self.write_newline()

    def construct_debug_tree(self, lines: List[int], sorted_values: List[Variable]):
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
                    # Check for datatype hooks and use instead
                    value = self.hook_loader.run_hook(value)

                    lines[i] += "└── {}".format(
                        highlight(value, self.python_lexer, self.terminal_formater).rstrip()
                    )

                    # Add spacing row
                    if offsets:
                        del offsets[-1]
                    i += 1
                    lines[i] += self.offset_vert_lines(offsets)

                current_offset = sorted_values[j].col_offset
            unprocessed_values -= 1
            current_offset = -1
            i += 1

        return lines

    def write_last_line(self, lineno: int, line: str):
        """Write out the line which throws runtime error with highlighting"""
        self.write_newline()
        self.left_offset = len(str(lineno))
        self._write_out(" {} {} {}\n".format(
            lineno,
            self.left_bar(),
            highlight(line, self.python_lexer, self.terminal_formater).rstrip())
        )
