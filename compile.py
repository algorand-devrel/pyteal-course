import sys
# import contracts_01.counter.step_01 as contract
# import contracts_01.counter.task1 as contract
import contracts_01.rps.step_01 as contract

from pyteal_helpers import program

if __name__ == "__main__":

    try:
        approval_out = sys.argv[1]
    except IndexError:
        approval_out = None

    try:
        clear_out = sys.argv[2]
    except IndexError:
        clear_out = None

    if approval_out is None:
        print(program.application(contract.approval()))
    else:
        with open(approval_out, "w") as h:
            h.write(program.application(contract.approval()))

    if clear_out is not None:
        with open(clear_out, "w") as h:
            h.write(program.application(contract.clear()))
