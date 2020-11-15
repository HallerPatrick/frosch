# frosch - Runtime Error Debugger

[![PyPI version](https://badge.fury.io/py/frosch.svg)](https://badge.fury.io/py/frosch)
![Codecov](https://img.shields.io/codecov/c/github/HallerPatrick/frosch)

Better runtime error messages 

Are you also constantly seeing the runtime error message the 
python interpreter is giving you?
It lacks some color and more debug information!


Get some good looking error tracebacks and beautifuly formatted
last line with all its last values *before* you crashed the program.

<h1 align="center" style="padding-left: 20px; padding-right: 20px">
  <img src="showcase.png">
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

## Contribution

`frosch` uses [poetry](https://github.com/python-poetry/poetry) for build and dependency
management, so please install beforehand.

### Setup

```bash
$ git clone https://github.com/HallerPatrick/frosch.git
$ poetry install
```

### Run tests

```python
$ python -m pytest tests
```
2 months ago

# Configuration

## Themes

frosch allows to use different themes for styling the output:

| Themes   |          |          |               |             |      |
|----------|----------|----------|---------------|-------------|------|
| abap     | bw       | igor     | native        | rrt         | trac |
| algol    | colorful | inkpot   | paraiso_dark  | sas         | vim  |
| algol_nu | default  | lovelace | paraiso_light | solarized   | vs   |
| arduino  | emacs    | manni    | pastie        | stata_dark  | xcod |
| autumn   | friendly | monokai  | perldoc       | stata_light |      |
| borland  | fruity   | murphy   | rainbow_dash  | tango       |      |

Usage:

```python
from frosch import hook

hook(theme="vim")
````