from unittest import TestCase

import pytest

from frosch.config_manager import ConfigManager, ThemeNotExistsError
from frosch.style import Style
from frosch.style.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic

class TestConfigManager(TestCase):

    def test_set_notifier(self):
        config_manager = ConfigManager()
        config_manager.set_notifier("hello", "world")
        self.assertEqual(config_manager.title, "hello")
        self.assertEqual(config_manager.message, "world")

    def test_has_notifcation_only_title(self):
        config_manager = ConfigManager()
        config_manager.set_notifier("hello", None)
        self.assertTrue(config_manager.has_notifier())

    def test_has_notifcation_only_message(self):
        config_manager = ConfigManager()
        config_manager.set_notifier(None, "message")
        self.assertTrue(config_manager.has_notifier())

    def test_has_notifcation_no_notification(self):
        config_manager = ConfigManager()
        config_manager.set_notifier(None, None)
        self.assertFalse(config_manager.has_notifier())

    def test_capitalize_theme(self):
        """Most testing done with testing _get_theme_from_string"""
        ConfigManager._get_theme_from_string("vs")

    def test__get_theme_from_string_not_found(self):
        with pytest.raises(ThemeNotExistsError):
            ConfigManager._get_theme_from_string("not existing")

    def test__get_theme_from_string(self):
        themes = [
            "abap",
            "algol",
            "algol_nu",
            "arduino",
            "autumn",
            "borland",
            "bw",
            "colorful",
            "default",
            "emacs",
            "friendly",
            "fruity",
            "igor",
            "inkpot",
            "lovelace",
            "manni",
            "monokai",
            "murphy",
            "native",
            "paraiso_dark",
            "paraiso_light",
            "pastie",
            "perldoc",
            "rainbow_dash",
            "rrt",
            "sas",
            "solarized",
            "stata_dark",
            "stata_light",
            "tango",
            "trac",
            "vim",
            "vs",
            "xcode"
        ]
        for theme in themes:
            ConfigManager().theme = theme

    def test_use_custom_theme(self):
        class YourStyle(Style):
            default_style = ""
            styles = {
                Comment:                'italic #888',
                Keyword:                'bold #005',
                Name:                   '#f00',
                Name.Function:          '#0f0',
                Name.Class:             'bold #0f0',
                String:                 'bg:#eee #111'
            }
        config_manager = ConfigManager()
        config_manager.theme = YourStyle

        self.assertEqual(type(config_manager.theme), type(YourStyle))

    def test_initialize_datatype_hook_loader_no_hooks(self):
        config_manager = ConfigManager()
        hook_loader = config_manager.initialize_datatype_hook_loader()
        self.assertDictEqual(hook_loader._hooks, {})

    def test_initialize_datatype_hook_loader_with_hooks(self):
        config_manager = ConfigManager()
        hooks = {list: lambda x: x}
        config_manager.dt_hooks = hooks
        hook_loader = config_manager.initialize_datatype_hook_loader()
        self.assertDictEqual(hook_loader._hooks, hooks)
