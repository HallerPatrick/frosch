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
