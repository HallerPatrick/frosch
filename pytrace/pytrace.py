from bdb import Bdb
import bdb
import traceback
import sys
import pdb


from colorama import init

from .parser import OutputParser
from .analyzer import retrieve_post_mortem_stack_infos

def hook():
    init()
    sys.excepthook = pytrace_excepthook

def _flush(message):
    sys.stderr.write(message + "\n")
    sys.stderr.flush()

def pytrace_excepthook(error_type, error_message, tb=None):

    traceback_entries = traceback.extract_tb(tb)

    locals, globals = retrieve_post_mortem_stack_infos(tb)

    op = OutputParser()

    handle_stacktrace(traceback_entries, op)

    last_stack = traceback_entries[-1]

    parse_error_line(last_stack.line, locals, globals)


def parse_error_line(line, locals, globals):
    # TODO: Lets parse this correctly with 
    # Python parser or ASt? 
    eval(line, globals, locals)


def handle_stacktrace(traceback_entries, op):
    _flush("Traceback (most recent call last):")
    for entry in traceback_entries:
        _flush(op.format_traceback(entry))

    _flush("")

    _flush(traceback_entries[-1]._line)

    # _flush(op.format_error(error_type, error_message, traceback_entries[-1]))
    

