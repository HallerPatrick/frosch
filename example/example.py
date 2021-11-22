import sys

sys.path.append("..")

from frosch.frosch import hook

from lib import fails


def hello():

    import torch

    hook()

    t = torch.tensor([1])

    t + "String"


if __name__ == "__main__":
    hello()
