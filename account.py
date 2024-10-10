from web3 import Web3
from eth_account import Account as EthereumAccount
from config import ERC20_ABI, TOKENS_PER_CHAIN
import random
from loguru import logger as ll

class Account():
    def __init__(self, pk, account_id):
        self.private_key = pk
        self.account_id = account_id
        self.w3 = Web3(Web3.HTTPProvider('https://bartio.rpc.berachain.com'))
        self.account = EthereumAccount.from_key(self.private_key)
        self.address = self.account.address
        self.wbtc_contract = self.w3.eth.contract(address=TOKENS_PER_CHAIN.get('WBTC'), abi=ERC20_ABI)

    def approve(self , contract, spender):
        function_tx = contract.functions.approve(spender=spender, amount=self.w3.to_wei(random.randint(100, 1000), 'ether'))
        estimate_gas = random.randint(270000, 300000)
        tx = {
            'from': self.w3.to_checksum_address(self.address),
            'value': 0,
            'gas': estimate_gas,
            'nonce': self.w3.eth.get_transaction_count(self.w3.to_checksum_address(self.address)),
        }
        base_fee = self.w3.eth.gas_price
        max_priority_fee_per_gas = int(self.get_priotiry_fee() * 2)
        max_fee_per_gas = base_fee + max_priority_fee_per_gas
        tx['maxPriorityFeePerGas'] = max_priority_fee_per_gas
        tx['maxFeePerGas'] = int(max_fee_per_gas * 1.5)
        tx['type'] = '0x2'
        txn = function_tx.build_transaction(tx)
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        status = self.w3.eth.wait_for_transaction_receipt(tx_hash.hex())
        if status.get('status') == 1:
            ll.success(
                f"[Wallet {self.account_id}] Approved https://bartio.beratrail.io/tx/0x{status.get('transactionHash').hex()}")
        else:
            ll.error(f"[Wallet {self.account_id}] transaction error!")

    def check_allowance(self, contract, spender):
        stat = contract.functions.allowance(self.address, spender).call()
        return stat

    def balance(self):
        balance = self.w3.eth.get_balance(self.w3.to_checksum_address(self.address))
        return balance / 10 ** 18

    def get_erc20_balance(self, contract):
        balance = contract.functions.balanceOf(self.address).call()
        return balance

    def get_priotiry_fee(self):
        fee_history = self.w3.eth.fee_history(25, 'latest', [20.0])
        non_empty_block_priority_fees = [fee[0] for fee in fee_history["reward"] if fee[0] != 0]

        divisor_priority = max(len(non_empty_block_priority_fees), 1)

        priority_fee = int(round(sum(non_empty_block_priority_fees) / divisor_priority))

        return priority_fee

