
import sys

sys.path.append("..")

from frosch.frosch import print_exception

try:
    [0, 1][3]
except IndexError as error:
    print_exception(error)
