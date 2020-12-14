import sys

sys.path.append("..")

from frosch.frosch import hook, fprint

from lib import fails


def hello():
    y = "Some String"
    fprint(y)


hello()
