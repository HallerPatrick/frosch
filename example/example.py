import sys
import pdb


sys.path.append("..")

from pytrace.pytrace import hook

hook()

def hello():
    y = "Some String"
    z = 3
    i = "Other string"
    x = y +  z + i


hello()