from base64 import b64decode
from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import wait_for_confirmation
from algosdk.kmd import KMDClient
from algosdk.v2client.algod import AlgodClient
from pyteal.ast.expr import Expr
from pyteal.compiler.compiler import compileTeal
from pyteal.ir.ops import Mode

micro_algo = 1
algo = micro_algo * (10 ** 6)


def get_kmd_client(address="http://localhost:4002", token="a" * 64) -> KMDClient:
    return KMDClient(token, address)


def get_keys_from_wallet(
    kmd_client: KMDClient, wallet_name="unencrypted-default-wallet", wallet_password=""
) -> list[str] | None:
    wallets = kmd_client.list_wallets()

    handle = None
    for wallet in wallets:
        if wallet["name"] == wallet_name:
            handle = kmd_client.init_wallet_handle(wallet["id"], wallet_password)
            break

    if handle is None:
        raise Exception("Could not find wallet")

    private_keys = None
    try:
        addresses = kmd_client.list_keys(handle)
        private_keys = [
            kmd_client.export_key(handle, wallet_password, address)
            for address in addresses
        ]
    finally:
        kmd_client.release_wallet_handle(handle)

    return private_keys


def get_algod_client(address="http://localhost:4001", token="a" * 64):
    return AlgodClient(token, address)


def generate_account():
    (private_key, address) = account.generate_account()
    # print(f"Private key: %s" % (private_key))
    # print(f"Address: %s" % (address))
    # print(
    #     f"Address from private key: %s"
    #     % (account.address_from_private_key(private_key))
    # )
    return private_key


def make_atomic(
    signing_keys=[], transactions=[]
) -> list[transaction.SignedTransaction]:
    return [
        tx.sign(key)
        for key, tx in zip(
            signing_keys, transaction.assign_group_id(transactions), strict=True
        )
    ]

def main():
    kmd_client = get_kmd_client()
    keys = get_keys_from_wallet(kmd_client)

    algod_client = get_algod_client()
    # for key in keys:
    #     print(algod_client.account_info(account.address_from_private_key(key))["address"])

    sender_key = keys[0]
    sender_address = account.address_from_private_key(sender_key)

    sp = algod_client.suggested_params()

    temp_account_keys = [generate_account() for _ in range(5)]

    for key in temp_account_keys:
        addr = account.address_from_private_key(key)
        info = algod_client.account_info(addr)
        bal = info["amount-without-pending-rewards"]
        print(f"{addr}: {bal}")

    transactions = [transaction.PaymentTxn(
        sender=sender_address,
        receiver=account.address_from_private_key(key),
        amt=100000,
        sp=sp,
    ) for key in temp_account_keys]

    grouped = make_atomic([sender_key for _ in range(len(transactions))], transactions)

    print(sender_key)
    print(transactions)
    print(grouped)

    txid = algod_client.send_transactions(grouped)

    wait_for_confirmation(algod_client, txid)

    for key in temp_account_keys:
        addr = account.address_from_private_key(key)
        info = algod_client.account_info(addr)
        bal = info["amount-without-pending-rewards"]
        print(f"{addr}: {bal}")


if __name__ == "__main__":
    main()
