import importlib
import sys

from pyteal_helpers import program
from pyteal_helpers import utils

if __name__ == "__main__":
    module = sys.argv[1]

    outfile = sys.argv[2]

    contract = importlib.import_module(module)

    contract_args = sys.argv[3:]

    pyteal = contract.create(contract_args)

    algod_client = utils.get_algod_client()

    sig = program.signature(algod_client, pyteal)

    print(f"Logic Signature Address: {sig.address}")

    with open(outfile, "w") as h:
        h.write(sig.teal)
