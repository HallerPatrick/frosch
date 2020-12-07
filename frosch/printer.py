"""

    frosch - Better runtime errors

    Patrick Haller
    betterthannothing.blog
    patrickhaller40@googlemail.com

    License MIT

"""

import inspect
import executing


def fprint(*args):
    """Pretty Debug Printing """
    current_frame = inspect.currentframe().f_back

    n = executing.Source.executing(current_frame).node

