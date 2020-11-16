"""

    frosch - Better runtime errors

    Patrick Haller
    betterthannothing.blog
    patrickhaller40@googlemail.com

    License MIT

"""
import importlib
import string
from typing import Optional

class ThemeNotExistsError(Exception):
    """Thrown when trying to import a theme from pygments which does not exist"""

class ConfigManager:
    """Used to parse and store configs from various ways of setting"""

    def __init__(self):
        self.message = None
        self.title = None
        self._theme = None

    def set_notifier(self, title: str, message: str):
        """Setter for notifcation message"""
        self.title = title
        self.message = message

    def has_notifier(self):
        """Returns True if message and/or title is set"""
        if self.message or self.title:
            if not self.message:
                self.message = ""
            if not self.title:
                self.title = ""
            return True
        return False

    def from_kwargs(self, **kwargs):
        """Set all given kwargs as attributes, if attr exists"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                self.__setattr__(key, value)
        return self

    @classmethod
    def default(cls):
        """Constructor with default values"""
        _cls = cls()
        _cls.theme = "monokai"
        return _cls

    @property
    def theme(self):
        """Returns theme object of pygments"""
        return self._theme

    @theme.setter
    def theme(self, theme: str):
        """Sets theme object of pygments for given string"""
        self._theme = ConfigManager._get_theme_from_string(theme)

    @staticmethod
    def _get_theme_from_string(theme_string: str):
        """Import the according theme from pygments"""
        pygment_styles_module = "pygments.styles.{}.{}Style".format(
            theme_string, theme_string.capitalize()
        )

        pygment_styles_module = "pygments.styles.{}".format(
            theme_string
        )

        style_class = "{}Style".format(ConfigManager._capitalize_theme(theme_string))

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

        theme = ConfigManager._get_special_themes(theme_string)
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
