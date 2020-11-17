import platform
import unittest
from unittest.mock import patch

from frosch import notifier

# @pytest.mark.parametrize("_os", ["Linux", "Darwin", "Windows"])
# def test_all_oses(_os):

#     with patch.object(notifier.os, "system") as system_mock:
#         with patch.object(notifier.platform, "system", return_value=_os.upper()) as plat_mock:
#             with patch.object(
#                 # notifier, "{}_notify".format(_os.lower())
#                 notifier, "linux_notify"
#             ) as notify_mock:
#                 notify_mock.return_value = _os.upper() 
#                 notifier.notify_os("hello", "world")
#                 notify_mock.assert_called_once_with("hello", "world")
#                 system_mock.assert_called_once_with(_os.upper())
class TestNotifier(unittest.TestCase):

    def test_notify_os_no_os(self):
        with patch.object(notifier.os, "system") as system_mock:
            with patch.object(notifier.platform, "system", return_value="TempleOS"):
                notifier.notify_os("hello", "world")
                self.assertFalse(system_mock.called)

    def test_notify_os_darwin_manual(self):
        with patch.object(notifier.os, "system") as system_mock:
            with patch.object(notifier.platform, "system", return_value="Darwin") as plat_mock:
                with patch.object(
                    notifier, "{}_notify".format("darwin")
                ) as notify_mock:
                    notify_mock.return_value = "DARWIN"
                    notifier.notify_os("hello", "world")
                    notify_mock.assert_called_once_with("hello", "world")
                    system_mock.assert_called_once_with("DARWIN")

    def test_notify_os_linux_manual(self):
        with patch.object(notifier.os, "system") as system_mock:
            with patch.object(notifier.platform, "system", return_value="Linux") as plat_mock:
                with patch.object(
                    notifier, "linux_notify"
                ) as notify_mock:
                    notify_mock.return_value = "LINUX"
                    notifier.notify_os("hello", "world")
                    notify_mock.assert_called_once_with("hello", "world")
                    system_mock.assert_called_once_with("LINUX")

    def test_notify_os_windows_manual(self):
        with patch.object(notifier.os, "system") as system_mock:
            with patch.object(notifier.platform, "system", return_value="Windows") as plat_mock:
                with patch.object(
                    notifier, "windows_notify"
                ) as notify_mock:
                    notify_mock.return_value = "WINDOWS"
                    notifier.notify_os("hello", "world")
                    notify_mock.assert_called_once_with("hello", "world")
                    system_mock.assert_called_once_with("WINDOWS")

    @unittest.skipIf(platform.system() != "Darwin", "OS dependent test")
    def test_notify_os_mac(self):
        with patch("os.system") as system_mock:
            notifier.notify_os("Hello", "World")
            expected_result = notifier.darwin_notify("Hello", "World")
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
        result = notifier.darwin_notify("Hello", "World!")
        expected_result = """osascript -e 'display notification "World!" with title "Hello"' """
        self.assertEqual(result, expected_result)

    def test_linux_notify(self):
        result = notifier.linux_notify("Hello", "World!")
        expected_result = """notify-send "Hello" "World!\""""
        self.assertEqual(result, expected_result)

    def test_windows_notify(self):
        result = notifier.windows_notify("Hello", "World!")
        expected_result = """powershell -command "$wshell = New-Object -ComObject Wscript.Shell;\
    $wshell.Popup('World!', 64, 'Hello', 0)" """
        self.assertEqual(result, expected_result)
