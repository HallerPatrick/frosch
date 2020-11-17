import sys

import unittest
from unittest import TestCase
from unittest.mock import Mock, patch, PropertyMock

import pytest

from frosch import frosch



class TestFrosch(TestCase):

    def test_hook_attached(self):
        _old_excepthook = sys.excepthook
        frosch.hook()
        self.assertEqual(frosch.pytrace_excepthook, sys.excepthook)
        self.assertIsNotNone(sys.excepthook.configs)
        sys.excepthook = _old_excepthook

    def test_hook_attached_with_args(self):
        _old_excepthook = sys.excepthook
        frosch.hook(theme="vim")
        self.assertEqual(frosch.pytrace_excepthook, sys.excepthook)
        self.assertIsNotNone(sys.excepthook.configs)
        self.assertEqual(type(sys.excepthook.configs.theme).__name__, "StyleMeta")

        sys.excepthook = _old_excepthook

    @unittest.skip("How to test this?")
    def test_pytrace_excepthook(self):
        _old_excepthook = sys.excepthook

        def custom_hook(error_type, error_message, tb):
            # Mock console writer to check if called correctly
            frosch.ConsoleWriter = Mock()
            frosch.ConsoleWriter.write_traceback = Mock()
            frosch.ConsoleWriter.write_last_line = Mock()
            frosch.ConsoleWriter.write_debug_tree = Mock()
            frosch.ConsoleWriter.write_newlines = Mock()

            frosch.pytrace_excepthook(error_type, error_message, tb)

        sys.excepthook = custom_hook

