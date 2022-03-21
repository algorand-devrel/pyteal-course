from pyteal import *
from pyteal_helpers import program

def approval():
    global_owner = Bytes("owner")
    global_counter = Bytes("counter")

    return program.event(
        init=Seq(
            App.globalPut(global_counter, Int(0)),
            App.globalPut(global_owner, Txn.sender()),
            Approve()
        ),
        # no_op=,
    )

def clear():
    return Approve()
