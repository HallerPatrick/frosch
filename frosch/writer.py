"""

    frosch - Better runtime errors

    Patrick Haller
    betterthannothing.blog
    patrickhaller40@googlemail.com

    License MIT

"""

import importlib
import string
import sys
from typing import Any, List, Optional

import colorama
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.python import Python3Lexer, Python3TracebackLexer
# from pygments.styles.monokai import MonokaiStyle

class WrongWriteOrder(Exception):
    """Thrown when the correct order of parts to be written to stderr is not correct"""

class ThemeNotExistsError(Exception):
    """Thrown when trying to import a theme from pygments which does not exist"""

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

    def tree_str(self):
        """Python>3.8 variable declaration format with types"""
        if self.value is None:
            return "{} = None".format(self.name)
        return "{}: {} = {!r}".format(self.name, type(self.value).__qualname__, self.value)


class ConsoleWriter:
    """Handles formatting, highlighting and writing to output of error message"""

    def __init__(self, theme):
        self.stderr = sys.stderr
        self.terminal_formater = Terminal256Formatter(
            style=ConsoleWriter._get_theme_from_string(theme)
        )
        self.python_lexer = Python3Lexer()
        self.python_traceback_lexer = Python3TracebackLexer()
        self.left_offset = None

    def write_traceback(self, traceback_):
        """Highlight traceback and write out"""
        self._write_out(highlight(traceback_, self.python_traceback_lexer, self.terminal_formater))

    @staticmethod
    def _get_theme_from_string(theme_string: str):
        """Import the according theme from pygments"""
        pygment_styles_module = "pygments.styles.{}.{}Style".format(
            theme_string, theme_string.capitalize()
        )

        pygment_styles_module = "pygments.styles.{}".format(
            theme_string
        )

        style_class = "{}Style".format(ConsoleWriter._capitalize_theme(theme_string))

        try:
            pygment_styles_module = importlib.import_module(pygment_styles_module)
            pygment_style_class = getattr(
                pygment_styles_module,
                style_class
            )
            return pygment_style_class
        except ImportError as import_error:
            raise ThemeNotExistsError("Theme: '{}' does not exists.\nPlease check \
https://github.com/HallerPatrick/frosch#configuration for more infos."
                .format(theme_string)) from import_error
        except AttributeError as attr_error:
            raise ThemeNotExistsError(
                "Could not find style '{}' in module '{}'".format(
                    style_class, pygment_styles_module
                )
            ) from attr_error

    @staticmethod
    def _capitalize_theme(theme_string: str) -> str:
        """Capitalize the theme correctly for import from pygments"""

        # Use this if we only support 3.7 >
        # if theme := ConsoleWriter._get_special_themes(theme_string):
        #    return theme

        theme = ConsoleWriter._get_special_themes(theme_string)
        if theme:
            return theme

        if "_" in theme_string:
            theme_string = theme_string.replace("_", " ")
        theme_string = string.capwords(theme_string)
        return theme_string.replace(" ", "_")

    @staticmethod
    def _get_special_themes(theme_string: str) -> Optional[str]: # pylint: disable=E1136
        """Some theme names cannot be converted programmaticaly
        (or is just to much time to catch all cases), there
        map theme manually"""

        themes = {
            "bw": "BlackWhite",
            "vs": "VisualStudio",
            "inkpot": "InkPot",
            "paraiso_dark": "ParaisoDark",
            "paraiso_light": "ParaisoLight",
            "rainbow_dash": "RainbowDash",
            "solarized": "SolarizedDark", # Just use dark for now
            "stata_dark": "StataDark",
            "stata_light": "StataLight"
        }

        if theme_string in themes:
            return themes[theme_string]
        return None

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
        return colorama.Fore.BLUE + "||" + colorama.Style.RESET_ALL

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

    def write_last_line(self, lineno: int, line: str):
        """Write out the line which throws runtime error with highlighting"""
        self.write_newline()
        self.left_offset = len(str(lineno))
        self._write_out(" {} {} {}\n".format(
            lineno,
            self.left_bar(),
            highlight(line, self.python_lexer, self.terminal_formater).rstrip())
        )
