from account import Account
from config import ASIGNED_ACCOUNTS, BEND_CONTRACT, BEND_ABI, TOKENS_PER_CHAIN
import random
from loguru import logger as ll

class Bend(Account):
    def __init__(self, account_id):
        super().__init__(pk=ASIGNED_ACCOUNTS.get(str(account_id)).get('pk'), account_id=str(account_id))
        self.bend_contract_address = BEND_CONTRACT
        self.bend_contract = self.w3.eth.contract(address=self.bend_contract_address, abi=BEND_ABI)
        self.account_id = str(account_id)
        self.wbtc_balance = round(self.get_erc20_balance(self.wbtc_contract), 3)

    # Make approve | try to send in via ERC20 contract to this address self.bend_contract
    def land(self):
        function_tx = self.bend_contract.functions.supply(TOKENS_PER_CHAIN.get('WBTC'), int(self.wbtc_balance), self.address, 18)
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
            ll.success(f"[Wallet {self.account_id}] Landed https://bartio.beratrail.io/tx/0x{status.get('transactionHash').hex()}")
            return True
        else:
            ll.error(f"[Wallet {self.account_id}] transaction error!")
            return False



    def bend(self):
        if self.wbtc_balance >= 0.0001:
            ll.info(f"[Wallet {self.account_id}] start landing [{self.wbtc_balance / 10**8} WBTC] on BendLanding")
            if self.check_allowance(self.wbtc_contract, self.bend_contract_address) < 1000000000000000000:
                ll.info(f"[Wallet {self.account_id}] will make approve for BendLanding")
                self.approve(spender=self.bend_contract_address, contract=self.wbtc_contract)
            status = self.land()
            return status
        else:
            ll.error(f"[Wallet {self.account_id}] dont have enough WBTC {self.wbtc_balance}")
            return False
