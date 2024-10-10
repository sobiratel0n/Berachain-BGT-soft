import random
import time

from account import Account
from config import ASIGNED_ACCOUNTS, SWAP_MAX, SWAP_MIN, BEX_CONTRACT, BEX_ABI, TOKENS_PER_CHAIN
from loguru import logger as ll
from utils.session import Session

class Bex(Account):
    def __init__(self, account_id):
        super().__init__(pk=ASIGNED_ACCOUNTS.get(str(account_id)).get('pk'), account_id=str(account_id))
        self.bex_contract = self.w3.eth.contract(abi=BEX_ABI, address=self.w3.to_checksum_address(BEX_CONTRACT))
        self.account_id = str(account_id)
        self.s = Session(self.account_id)
        self.session = self.s.session()
        self.balance = round(self.balance(), 3)


    def request_swap_steps(self, swap_from, swap_to, amount):
        url = 'https://bartio-bex-router.berachain-devnet.com/dex/route?'
        headers = {
            'authority': 'bartio-bex-router.berachain-devnet.com',
            'method': 'GET',
            'path': f'/dex/route?fromAsset={swap_from}&toAsset={swap_to}&amount={self.w3.to_wei(amount, "ether")}',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://bartio.bex.berachain.com',
            'priority': 'u=1, i',
            'referer': 'https://bartio.bex.berachain.com/',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': self.s.useragent
        }
        params = {
            'fromAsset': swap_from,
            'toAsset': swap_to,
            'amount': self.w3.to_wei(amount, "ether")
        }
        for i in range(1, 3):
            try:
                response = self.session.get(url=url, params=params, headers=headers)
                if response.json().get('steps') is None:
                    ll.warning(f"[Wallet {self.account_id}] retry get bex_swap steps")
                else:
                    return response.json()
            except Exception as err:
                ll.warning(f"[Wallet {self.account_id}] {err}")
        ll.error(f"[Wallet {self.account_id}] can't get steps for bex_swap")


    def request_min_amount(self, steps, amount):
        min_out = self.bex_contract.functions.previewMultiSwap(steps, self.w3.to_wei(amount, "ether")).call()
        return min_out




    def swap(self):
        for i in range(1, 3):
            swap = random.randint(SWAP_MIN, SWAP_MAX)
            amount_bera = round((self.balance * swap) / 100, 4)
            steps = self.request_swap_steps(swap_from=TOKENS_PER_CHAIN.get('BERA'), swap_to=TOKENS_PER_CHAIN.get('WBTC'), amount=amount_bera)
            if steps:
                ll.info(f"[Wallet {self.account_id}] make swap [{amount_bera} $BERA] -> WBTC")
                steps = steps.get('steps')[0]
                steps = [steps.get('poolIdx'), steps.get('base'), steps.get('quote'), steps.get('isBuy')]
                steps[0] = int(steps[0])
                steps = [(steps[0], self.w3.to_checksum_address(steps[1]), self.w3.to_checksum_address(steps[2]), steps[3])]
                min_out = self.request_min_amount(steps=steps, amount=amount_bera)[0]
                steps = [(steps[0][0], steps[0][1], self.w3.to_checksum_address('0x0000000000000000000000000000000000000000'), steps[0][3])]
                function_tx = self.bex_contract.functions.multiSwap(steps, self.w3.to_wei(amount_bera, 'ether'), min_out)
                estimate_gas = random.randint(270000, 300000)
                tx = {
                    'from': self.address,
                    'value': self.w3.to_wei(amount_bera, 'ether'),
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
                    ll.success(f"[Wallet {self.account_id}] Swaped https://bartio.beratrail.io/tx/0x{status.get('transactionHash').hex()}")
                    return True
                else:
                    ll.warning(f"[Wallet {self.account_id}] transaction error try resend new transaction")
                    time.sleep(5)
        ll.error(f"[Wallet {self.account_id}] can't send transactions!")
        return False


    def bex_swap(self):
        if self.balance <= 0.5:
            ll.error(f"[Wallet {self.account_id}] {self.balance} $BERA balance if too low  need at least 0.5 $BERA")
            return False
        status = self.swap()
        return status






