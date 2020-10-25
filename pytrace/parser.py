from traceback import FrameSummary

import sys

from blessings import Terminal

class OutputParser:
    """

    We have to parse three types of components we get from the 
    exception hook.

    1. Traceback:
        A list of frames building up the traceback stack.


    """

    def __init__(self):
        self.t = Terminal(stream=sys.stderr)

    def format_traceback(self, traceback: FrameSummary):
        filename = traceback.filename
        lineno = self.t.bold(self.t.blue(str(traceback.lineno)))
        orig = self.t.bold(traceback.name)
        line = traceback.line

        return '  File "{}", line {}, in {}\n\t{}'.format(filename, lineno, orig, line)

    def format_error(self, error_type: str, error_message: str, last_traceback: FrameSummary):
        
        error_message = self.t.bold(self.t.white(str(error_message)))
        error_message_line = "error: {}".format(error_message)


        error = [
            error_message_line,
            " {} {}:{}".format(self.t.blue("-->"), last_traceback.filename, last_traceback.lineno),
            *self.format_code_snippet(error_type, error_message, last_traceback),
        ]

        return "\n".join(error)


    def format_code_snippet(self, error_type, error_message, last_traceback):

        offset = len(str(last_traceback.lineno)) * " " + " "

        code_snippet_lines = [
            "{}|".format(offset),
            "{} |\t{}".format(last_traceback.lineno, last_traceback.line),
            "{}|".format(offset)
        ]
        

        return code_snippet_lines


