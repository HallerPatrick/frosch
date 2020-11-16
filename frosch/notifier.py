"""

    frosch - Better runtime errors

    Patrick Haller
    betterthannothing.blog
    patrickhaller40@googlemail.com

    License MIT

"""

import platform
import os

def notify_os(title: str = "Ups", message: str = "Your python program crashed."):
    """Check current OS and run a notification subprocess"""
    current_platform = platform.system()

    if current_platform == "Darwin":
        command = mac_notify(title, message)
    elif current_platform == "Linux":
        command = linux_notify(title, message)
    elif current_platform == "Windows":
        command = windows_notify(title, message)
    else:
        return

    os.system(command)

def mac_notify(title: str, message: str) -> str:
    """Display notification for MacOS systems"""
    command = f'''osascript -e 'display notification "{message}" with title "{title}"' '''
    return command

def linux_notify(title: str, message: str) -> str:
    """Display notification for Linux systems"""
    command = f'''notify-send "{title}" "{message}"'''
    return command

def windows_notify(title: str, message: str) -> str:
    """Display notification for Windows systems"""
    command = f'''powershell -command "$wshell = New-Object -ComObject Wscript.Shell;\
    $wshell.Popup('{message}', 64, '{title}', 0)" '''
    return command
