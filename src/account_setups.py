from web3 import Web3
from eth_account import Account
from utils.utils import *

config = open_file("/Users/unaysangus/Desktop/Projects/Crypto Trading/DeFi/ZKSyncADBot/config.json")
erc20_abi = open_file("/abi/ERC20.json")
eth_rpc = config["eth_rpc_url"]


def distribute_eth():
    main_pk = config["main_account_pk"]
    wallet_addresses = config["wallet_addresses"]

    w3 = Web3(Web3.HTTPProvider(eth_rpc))
    if not w3.is_connected():
        print("Not connected to Ethereum node.")
        exit(1)

    converted_wallet_addy = [w3.to_checksum_address(address) for address in wallet_addresses]

    account = Account.from_key(main_pk)
    amount = w3.eth.get_balance(account.address) / len(converted_wallet_addy) - (
            w3.eth.gas_price * len(converted_wallet_addy))

    for destination_address in converted_wallet_addy:
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price

        print(f"Transferring $10 to {destination_address} from {account.address}")

        transfer_txn = {
            'to': destination_address,
            'value': int(amount),
            'gas': 21000,
            'gasPrice': gas_price,
            'nonce': nonce
        }

        signed_txn = account.sign_transaction(transfer_txn)

        try:
            txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"Transaction sent for {destination_address} with hash {txn_hash.hex()}")
            txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
            if txn_receipt['status']:
                print(f"Transfer successful to {destination_address}")
            else:
                print(f"Transfer failed to {destination_address}")

        except Exception as e:
            print(f"Error")


def create_zk_transaction(wallet_address, private_key):
    w3 = Web3(Web3.HTTPProvider(eth_rpc))
    if not w3.is_connected():
        print("Not connected to Ethereum node.")
        exit(1)
    zksync_abi = open_file("/abi/zksync.json")
    contract_address = w3.to_checksum_address("0x32400084C286CF3E17e7B677ea9583e60a000324")

    zksync_contract = w3.eth.contract(address=contract_address, abi=zksync_abi)
    amount = wei_to_ether(w3.eth.get_balance(wallet_address) - w3.eth.gas_price)
    contract_call = zksync_contract.functions.requestL2Transaction(wallet_address, amount, b'', 21000, 80, [],
                                                                   wallet_address)
    transfer_txn = contract_call.build_transaction({
        'from': wallet_address,
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(wallet_address),
    })

    signed_transaction = w3.eth.account.sign_transaction(transfer_txn, private_key)
    txn = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    print(f"***** Transaction: https://etherscan.io/tx/{txn} *****")


def bridge_to_zk():
    private_keys = config["privatekeys"]
    w3 = Web3(Web3.HTTPProvider(eth_rpc))
    if not w3.is_connected():
        print("Not connected to Ethereum node.")
        exit(1)

    for pk in range(private_keys):
        account = Account.from_key(pk)
        wallet_address = w3.to_checksum_address(account.address)
        create_zk_transaction(wallet_address, account)

