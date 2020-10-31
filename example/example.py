import sys
import pdb


sys.path.append("..")

from pytrace.pytrace import hook

hook()

def hello():
    y = "Some String"
    z = [1, 2, "hel"]
    index = 0
    i = "Other string"
    x = y + z[index] + i + 4 + "ROFL"


def num():
    return 3


hello()