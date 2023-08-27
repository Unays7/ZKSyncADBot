import json
import time
from web3 import Web3
from eth_account import Account

"""
Load accounts from main account and bridge on each account to zksync
"""

with open("config.json", "r") as f:
    config = json.load(f)
with open("ERC20.json") as f:
    erc20_abi = json.load(f)

# sending eth from main address to other addresses
main_pk = config["main_account_pk"]
eth_rpc = config["eth_rpc_url"]
wallet_addresses = config["wallet_addresses"]

w3 = Web3(Web3.HTTPProvider(eth_rpc))
if not w3.is_connected():
    print("Not connected to Ethereum node.")
    exit(1)

converted_wallet_addy = [w3.to_checksum_address(address) for address in wallet_addresses]

account = Account.from_key(main_pk)
amount =  w3.eth.get_balance(account.address) / len(converted_wallet_addy) - ((w3.eth.gas_price * 10) / len(converted_wallet_addy))
print(amount, w3.eth.get_balance(account.address))
for destination_address in converted_wallet_addy:
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price * 10

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
        # Delete this if you don't want to wait for receipt. 
        # Although you might get timedout
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
        if txn_receipt['status']:
            print(f"Transfer successful to {destination_address}")
        else:
            print(f"Transfer failed to {destination_address}")

    except Exception as e:
        print(f"Error")