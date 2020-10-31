import sys

from traceback import FrameSummary
from typing import List

import colorama

from pygments import highlight
from pygments.lexers import Python3Lexer, Python3TracebackLexer
from pygments.formatters import Terminal256Formatter
from pygments.styles.monokai import MonokaiStyle





class Variable:

    def __init__(self, id_, col_offset):
        self.name = id_
        self.col_offset = col_offset
        self._value = None
        self.type = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.type_name == "str":
            self._value = '"{}"'.format(value)
        else:
            self._value = value

    def __str__(self):
        return "{}: {} ({})".format(self.name, self.value, self.col_offset)

    def tree_str(self):
        string = "{}: {} = {}".format(self.name, self.type_name, self.value)
        return highlight(string, Python3Lexer(), Terminal256Formatter(style=MonokaiStyle)).rstrip()

    @property
    def type_name(self):
        if self.type is None:
            return "None"
        return self.type.__name__





class OutputParser:
    """

    We have to parse three types of components we get from the 
    exception hook.

    1. Traceback:
        A list of frames building up the traceback stack.


    """
    def output_traceback(self, tb):
        return highlight(tb, Python3TracebackLexer(), Terminal256Formatter(style=MonokaiStyle))

    @staticmethod
    def offset_vert_lines(offsets):
        line = ""

        current_offset = -1

        # First line
        for offset in offsets:
            new_offset = offset - current_offset -1
            line += (" " * new_offset)
            line += "│"
            current_offset = offset
        
        return line

    def left_bar(self):
        return colorama.Fore.BLUE + "||"

    def render_values(self, names: List[Variable]):
        offsets = list(sorted([x.col_offset for x in names]))
        sorted_values = list(sorted(names, key=lambda val: val.col_offset))
        # del offsets[0]

        num_vars = len(offsets)

        lines = ["    {} ".format(self.left_bar()) for _ in range(len(offsets)+1+len(offsets))]


        current_offset = -1
        processed_vars = 0 
        # First line
        lines[0] += self.offset_vert_lines(offsets)


        unprocessed_values = len(names)
        current_offset = -1 
        # For every line
        i = 1
        for value in reversed(sorted_values):
            # For every value
            for j in range(unprocessed_values):
                new_offset = sorted_values[j].col_offset - current_offset -1
                lines[i] += (" " * (new_offset))
                if j != (unprocessed_values - 1):
                    lines[i] += "│"
                else:
                    lines[i] += "└── {}".format(value.tree_str())

                    # Add spacong row
                    if offsets: 
                        del offsets[-1]

                    i += 1

                    lines[i] += self.offset_vert_lines(offsets)

                current_offset = sorted_values[j].col_offset
            unprocessed_values -= 1
            current_offset = -1
            i += 1
            

        for l in lines:
            print(l)

    def render_last_line(self, lineno, line):
        print()
        print(" {} {} {}".format(lineno, self.left_bar(), highlight(line, Python3Lexer(), Terminal256Formatter(style=MonokaiStyle)).rstrip()))



            



