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


    locals, globals = retrieve_port_mortem_infos(tb)

    op = OutputParser()

    # _flush("Traceback (most recent call last):")
    # for entry in traceback_entries:
    #     _flush(op.format_traceback(entry))

    # _flush("")

    # _flush(traceback_entries[-1]._line)

    # _flush(op.format_error(error_type, error_message, traceback_entries[-1]))
    



