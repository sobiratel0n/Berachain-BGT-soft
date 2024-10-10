import requests
from config import ASIGNED_ACCOUNTS, UA
from utils.assign_proxy_to_account import AssignProxy
from loguru import logger as ll

class Session():
    def __init__(self, account_id):
        self.account_id = account_id
        self.s = requests.session()
        self.proxy = ASIGNED_ACCOUNTS.get(account_id).get('proxy').split(":")
        self.proxy_domain = self.proxy[0]
        self.proxy_port = self.proxy[1]
        self.proxy_username = self.proxy[2]
        self.proxy_password = self.proxy[3]
        self.useragent = UA.random

    def check_proxy(self):
        # FORMAT http://{proxy_username}:{proxy_password}@{http_proxy_url}
        url = 'https://jsonip.com'
        for i in range(1, 3):
            self.proxy = f'{self.proxy_username}:{self.proxy_password}@{self.proxy_domain}:{self.proxy_port}'
            proxy = {
                'http': f'http://{self.proxy}',
                'https': f'http://{self.proxy}'
                     }
            try:
                self.s.proxies = proxy

                response = self.s.get(url=url)
                if response.status_code == 200:
                    return True
                else:
                    ll.warning('Proxy Error')
                    acc = AssignProxy()
                    ASIGNED_ACCOUNTS = acc.change_proxy(account_id=self.account_id)
                    self.proxy = ASIGNED_ACCOUNTS.get(self.account_id).get('proxy').split(":")
                    self.proxy_domain = self.proxy[0]
                    self.proxy_port = self.proxy[1]
                    self.proxy_username = self.proxy[2]
                    self.proxy_password = self.proxy[3]

            except Exception as err:
                ll.warning(f'[Wallet {self.account_id}] {err}')
                acc = AssignProxy()
                ASIGNED_ACCOUNTS = acc.change_proxy(account_id=self.account_id)
                self.proxy = ASIGNED_ACCOUNTS.get(self.account_id).get('proxy').split(":")
                self.proxy_domain = self.proxy[0]
                self.proxy_port = self.proxy[1]
                self.proxy_username = self.proxy[2]
                self.proxy_password = self.proxy[3]

        ll.error(f'[Wallet {self.account_id}] changing proxy didnt help')
        return False



    def session(self):
        if self.check_proxy():
            return self.s
        else:
            return False

