import sys
sys.path.append("..")

from frosch.frosch import hook

from lib import fails


def hello():
    hook(theme="vs")

    y = "Some String"
    z = [1, 2, "hel"]
    index = 0
    i = "Other string"
    fails()


hello()