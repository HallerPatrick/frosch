# OS Notifications

Another utility `frosch` provides is that when a current running python program
crasged to send a OS notifcation to you.

## Usage

```python

from frosch import hook

hook(
  theme="vs", # VSCode Theme
  title="I crashed!",
  message="Run Number #1444 is also crashing..."
)
```

This works on MacOS (`osascript`), Linux (`notify-send`) and Windows (`powershell`).
