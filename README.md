# frosch - Runtime Error Debugger

[![PyPI version](https://badge.fury.io/py/frosch.svg)](https://badge.fury.io/py/frosch)
![Codecov](https://img.shields.io/codecov/c/github/HallerPatrick/frosch)
![Pytho_Version](https://img.shields.io/pypi/pyversions/frosch)

Better runtime error messages

Are you also constantly seeing the runtime error message the
python interpreter is giving you?
It lacks some color and more debug information!


Get some good looking error tracebacks and beautifuly formatted
last line with all its last values *before* you crashed the program.

<h1 align="center" style="padding-left: 20px; padding-right: 20px">
  <img src="resources/showcase.png">
</h1>


## Installation

```bash
$ pip install frosch
```

## Usage

Call the hook function at the beginning of your program.

```python

from frosch import hook

hook()

x = 3 + "String"

```

### Print Exceptions

You can also easily print your catched exceptions to stdout

```python

from frosch import print_exception

try:
  x = [0, 1]
  x[3]
except IndexError as error:
  print_exception(error)

```


# Configuration

## Themes

frosch allows to use different themes for styling the output:

| Themes   |          |          |               |             |      |
|----------|----------|----------|---------------|-------------|------|
| abap     | bw       | igor     | native        | rrt         | trac |
| algol    | colorful | inkpot   | paraiso_dark  | sas         | vim  |
| algol_nu | default  | lovelace | paraiso_light | solarized   | vs   |
| arduino  | emacs    | manni    | pastie        | stata_dark  | xcode |
| autumn   | friendly | monokai  | perldoc       | stata_light |      |
| borland  | fruity   | murphy   | rainbow_dash  | tango       |      |

Usage:

```python
from frosch import hook

hook(theme="vim")
````
### Custom Themes

You can also define custom themes by using by subclassing Style (which is just a thin wrapper
around pygments styles). For more information please use the [pygments docs](https://pygments.org/docs/styles/#creating-own-styles).

```python

from frosch import hook
from frosch.style import Style
from frosch.style.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic

class CustomStyle(Style):
    default_style = ""
    styles = {
        Comment:                'italic #888',
        Keyword:                'bold #005',
        Name:                   '#f00',
        Name.Function:          '#0f0',
        Name.Class:             'bold #0f0',
        String:                 'bg:#eee #111'
    }

hook(theme=CustomStyle)

```

## OS Notifications

But wait there is more!

Running longer scripts in the background?

Just add a title and/or message to the hook and it will you give a notification when your program
is crashing.


```python

from frosch import hook

hook(
  theme="vs", # VSCode Theme
  title="I crashed!",
  message="Run Number #1444 is also crashing..."
)
```

This works on MacOS (`osascript`), Linux (`notify-send`) and Windows (`powershell`).



# Contribution

`frosch` uses [poetry](https://github.com/python-poetry/poetry) for build and dependency
management, so please install beforehand.

## Setup

```bash
$ git clone https://github.com/HallerPatrick/frosch.git
$ poetry install
```

## Run tests

```python
$ python -m pytest tests
```
