"""

    frosch - Better runtime errors

    Patrick Haller
    betterthannothing.blog
    patrickhaller40@googlemail.com

    License MIT

    Supply some custom hooks for several datatypes of variables are going to
    be displayed in stream. If hook exists replace the displayed string, with
    a hook returns

"""

from collections.abc import Callable
from typing import Any, Optional

T = Any

type_map = {

}


def dt_display_dispatcher(value: T) -> Optional[Callable[[T], str]]: # pylint: disable=E1136
    """Check if hook is found else return None"""

    if type(value) in type_map:
        return type_map[type(value)]

    return None
