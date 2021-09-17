"""

    frosch - Better runtime errors

    Patrick Haller
    patrickhaller40@googlemail.com

    License MIT

"""

import sys
import traceback

from types import TracebackType
from typing import Optional, Type

from .config_manager import ConfigManager
from .notifier import notify_os
from .parser import MissingStacktraceError, ParsedException
from .writer import ConsoleWriter


DEBUG = False

ETType = Optional[Type[BaseException]]
EType = Optional[BaseException]


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


def print_exception(exception: Exception):
    """Pretty print the exception and traceback to stdout"""
    config_manager = ConfigManager.default()

    hook_loader = config_manager.initialize_datatype_hook_loader()

    # Do we even need exception as param?
    error_type, error_message, _ = sys.exc_info()
    parsed_exception = ParsedException(
        exception.__traceback__, error_type, error_message
    )
    console_writer = ConsoleWriter(config_manager.theme, sys.stdout, hook_loader)
    console_writer.write_exception(parsed_exception)


def pytrace_excepthook(
    error_type: ETType, error_message: EType, traceback_: TracebackType
):
    """New excepthook to overwrite sys.excepthook with a safe fallback"""

    if DEBUG:
        _pytrace_excepthook(error_type, error_message, traceback_)

    try:
        _pytrace_excepthook(error_type, error_message, traceback_)
    except Exception:  # pylint: disable=W0703
        sys.stderr.write(
            "".join(traceback.format_exception(error_type, error_message, traceback_))
        )
        sys.exit(1)


def _pytrace_excepthook(
    error_type: ETType, error_message: EType, traceback_: TracebackType
):
    """New excepthook to overwrite sys.excepthook"""
    configs = pytrace_excepthook.configs
    hook_loader = configs.initialize_datatype_hook_loader()

    try:
        parsed_exception = ParsedException(traceback_, error_type, error_message)
    except MissingStacktraceError:
        sys.stderr.write(
            "".join(traceback.format_exception(error_type, error_message, traceback_))
        )
        sys.exit(1)

    # Write down
    console_writer = ConsoleWriter(configs.theme, sys.stderr, hook_loader)
    console_writer.write_exception(parsed_exception)

    if configs.has_notifier():
        notify_os(configs.title, configs.message)

    # We always dealing with runtime errors, so always return 1
    sys.exit(1)
