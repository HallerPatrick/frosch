"""

    frosch - Better runtime errors

    Patrick Haller
    patrickhaller40@googlemail.com

    License MIT

"""

import torch


def display_torch_tensor(tensor: torch.Tensor) -> str:
    """In most cases more usefull to get the dimensions of a tensor, than its values"""
    return str(tensor.size())


hooks = {torch.Tensor: display_torch_tensor}
