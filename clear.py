from pyteal import *

from pyteal_helpers import program


def contract():
    return Approve()


if __name__ == "__main__":
    print(program.to_teal_app(contract()))
