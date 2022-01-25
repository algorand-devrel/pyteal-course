from algosdk import account
from algosdk.future import transaction
from algosdk.kmd import KMDClient
from algosdk.v2client.algod import AlgodClient

MICRO_ALGO = 1
ALGO = MICRO_ALGO * (10 ** 6)


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
    (private_key, _) = account.generate_account()
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
