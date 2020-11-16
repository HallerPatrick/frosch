from unittest import TestCase

import pytest

from frosch.config_manager import ConfigManager, ThemeNotExistsError

class TestConfigManager(TestCase):

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