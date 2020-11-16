import platform
import unittest
from unittest.mock import patch

from frosch import notifier

class TestNotifier(unittest.TestCase):

    @unittest.skipIf(platform.system() != "Darwin", "OS dependent test")
    def test_notify_os_mac(self):
        with patch("os.system") as system_mock:
            notifier.notify_os("Hello", "World")
            expected_result = notifier.mac_notify("Hello", "World")
            system_mock.assert_called_once_with(expected_result)

    @unittest.skipIf(platform.system() != "Linux", "OS dependent test")
    def test_notify_os_linux(self):
        with patch("os.system") as system_mock:
            notifier.notify_os("Hello", "World")
            expected_result = notifier.linux_notify("Hello", "World")
            system_mock.assert_called_once_with(expected_result)

    @unittest.skipIf(platform.system() != "Windows", "OS dependent test")
    def test_notify_os_windows(self):
        with patch("os.system") as system_mock:
            notifier.notify_os("Hello", "World")
            expected_result = notifier.windows_notify("Hello", "World")
            system_mock.assert_called_once_with(expected_result)

    def test_mac_notify(self):
        result = notifier.mac_notify("Hello", "World!")
        expected_result = """osascript -e 'display notification "World!" with title "Hello"' """
        self.assertEqual(result, expected_result)

    def test_linux_notify(self):
        result = notifier.linux_notify("Hello", "World!")
        expected_result = """notify-send "Hello" "World!\""""
        self.assertEqual(result, expected_result)

    @unittest.skip("Testing needed")
    def test_windows_notify(self):
        pass
