# frosch - Runtime Error Debugger

[![PyPI version](https://badge.fury.io/py/frosch.svg)](https://badge.fury.io/py/frosch)
![Codecov](https://img.shields.io/codecov/c/github/HallerPatrick/frosch)

Better runtime error messages 

Are you also constantly seeing the runtime error message the 
python interpreter is giving you?
It lacks some color and more debug information!


Get some good looking error tracebacks and beautifuly formatted
last line with all its last values *before* you crashed the program.

<h1 align="center">
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
$ python -m pylint tests
```
2 months ago

# Configuration

## Themes

frosch allows to use different themes for styling the output:
```
abap
algol
algol_nu
arduino
autumn
borland
bw
colorful
default
emacs
friendly
fruity
igor
inkpot
lovelace
manni
monokai
murphy
native
paraiso_dark
paraiso_light
pastie
perldoc
rainbow_dash
rrt
sas
solarized
stata_dark
stata_light
tango
trac
vim
vs
xcode
```