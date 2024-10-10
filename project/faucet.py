import time
from account import Account
from loguru import logger as ll
from config import ASIGNED_ACCOUNTS, TWO_API_CAPTCHA_KEY, MAX_SLEEP_FAUCET, MIN_SLEEP_FAUCET
import random
from utils.session import Session


class Faucet(Account):
    def __init__(self, account_id):
        super().__init__(pk=ASIGNED_ACCOUNTS.get(account_id).get('pk'), account_id=account_id)
        self.account_id = account_id
        self.pk = ASIGNED_ACCOUNTS.get(account_id).get('pk')
        self.proxy = ASIGNED_ACCOUNTS.get(account_id).get('proxy').split(":")
        self.start_balance = self.w3.eth.get_balance(self.address)
        self.s = Session(self.account_id)
        self.session = self.s.session()

    def captcha(self):
        for i in range(1, 4):
            url = 'https://api.2captcha.com/createTask'
            payload = {
                "clientKey": TWO_API_CAPTCHA_KEY,
                "task": {
                    "type": "TurnstileTask",
                    "websiteURL": "https://bartio.faucet.berachain.com/",
                    "websiteKey": "0x4AAAAAAARdAuciFArKhVwt",
                    "userAgent": self.s.useragent,
                    "proxyType": "http",
                    "proxyAddress": self.s.proxy_domain,
                    "proxyPort": self.s.proxy_port,
                    "proxyLogin": self.s.proxy_username,
                    "proxyPassword": self.s.proxy_password
                }
            }

            response = self.session.post(url=url, json=payload).json()
            if response.get('errorId') == 0:
                url = 'https://api.2captcha.com/getTaskResult'

                payload = {
                    "clientKey": TWO_API_CAPTCHA_KEY,
                    "taskId": response.get('taskId')
                }

                total_time = 0
                timeout = 360
                while True:
                    response = self.session.post(url=url, json=payload).json()

                    if response.get('status') == 'ready':
                        return response.get('solution').get('token')

                    total_time += 5
                    time.sleep(5)

                    if total_time > timeout:
                        ll.error("Can't solve the captcha ")
                        return False
            else:
                ll.warning(f"[Wallet {self.account_id}] {response.json()}")
                time.sleep(5)
        ll.error(f"[Wallet {self.account_id}] cant solve captcha")

    def claim_berachain_tokens(self, captcha_key):

        ll.info(f'[Wallet {self.account_id}] Claiming $BERA on faucet')

        url = 'https://bartio-faucet.berachain-devnet.com/api/claim?'

        headers = {
            "accept": "*/*",
            "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "authorization": f"Bearer {captcha_key}",
            "content-type": "text/plain;charset=UTF-8",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"123\", \"Chromium\";v=\"123\", \"Not.A/Brand\";v=\"23\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "referrer": "https://bartio.faucet.berachain.com/",
            "referrerPolicy": "strict-origin-when-cross-origin",
            "body": f"{{\"address\":\"{self.address}\"}}",
            "method": "POST",
            "mode": "cors",
            "credentials": "include",
            "userAgent": self.s.useragent

        }
        params = {
            "address": f"{self.address}"
        }
        response = self.session.post(url=url, params=params, json=params, headers=headers)
        if response.json() == 0:
            ll.error(f"[Wallet {self.account_id}] dont have 0.001 ETH on Ethereum Mainnet")
            return False
        elif response.json().get('msg').find('wait') != -1:
            ll.warning(f"[Wallet {self.account_id}] already claimed $BERA. {response.json().get('msg')[34:]}")
            self.session.close()
            return 'claimed'
        sleep = random.randint(MIN_SLEEP_FAUCET, MAX_SLEEP_FAUCET)
        ll.success(f"[Wallet {self.account_id}] $BERA successfully claimed, will go sleep for {sleep} seconds")
        time.sleep(sleep)
        self.session.close()
        return True

    def wait_for_tokens(self):
        for i in range(1, 10):
            balance = self.w3.eth.get_balance(self.address)
            if balance != self.start_balance:
                ll.info(f"[Wallet {self.account_id}] received $BERA on the wallet")
                return True
            time.sleep(random.randint(20, 40))
        ll.warning(f"[Wallet {self.account_id}] didn't receive $BERA on the wallet")
        return False

    def faucet(self):
        for i in range(1, 3):
            try:
                ll.info(f"[Wallet {self.account_id}] start authorization")
                if self.session:
                    data = self.captcha()
                    if data:
                        status = self.claim_berachain_tokens(data)
                        return status
                    else:
                        return False
                else:
                    ll.error(f"[Wallet {self.account_id}] something wrong with session")
            except Exception as err:
                ll.warning(f"[Wallet {self.account_id}] {err}")

