from contracts.rps.step_01 import approval

from pyteal_helpers import program

if __name__ == "__main__":
    print(program.to_teal_app(approval()))
