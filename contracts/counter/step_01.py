from pyteal import *
from pyteal.ast.bytes import Bytes
from pyteal_helpers import program


def approval():
    # globals
    global_owner = Bytes("owner")  # byteslice
    global_counter = Bytes("counter")  # uint64

    op_increment = Bytes("inc")
    op_decrement = Bytes("dec")

    increment = Seq(
        [
            App.globalPut(global_counter, App.globalGet(global_counter) + Int(1)),
            Approve(),
        ]
    )

    decrement = Seq(
        [
            App.globalPut(global_counter, App.globalGet(global_counter) - Int(1)),
            Approve(),
        ]
    )

    return program.event(
        init=Seq(
            [
                App.globalPut(global_owner, Txn.sender()),
                App.globalPut(global_counter, Int(0)),
                Approve(),
            ]
        ),
        no_op=Cond(
            [Txn.application_args[0] == op_increment, increment],
            [Txn.application_args[0] == op_decrement, decrement],
        ),
    )


def clear():
    return Approve()
