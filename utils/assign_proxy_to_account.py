import json
from loguru import logger as ll
from config import PROXY, ACCOUNTS


class AssignProxy():
    def __init__(self):
        self.file = open('data/account_proxy.json', "r+")
        self.ACCOUNT_PROXY = json.load(self.file)
        self.file.close()
        self.file = open('data/account_proxy.json', "w")

    def change_proxy(self, account_id):
        proxy_file = open("data/proxy.txt", 'w')
        self.ACCOUNT_PROXY[str(account_id)]["proxy"] = PROXY.pop(0)
        a = json.dumps(self.ACCOUNT_PROXY, indent=4)
        self.file.write(a)
        self.file.close()
        for p in PROXY:
            proxy_file.write(p + "\n")
        proxy_file.close()
        return self.ACCOUNT_PROXY

    def check_if_assigned(self, account):
        for key in self.ACCOUNT_PROXY:
            if self.ACCOUNT_PROXY.get(key).get('pk') == account:
                ll.warning(f"Already exist on ID {key} | {account}")
                return False

        return True
    def assign_proxy_to_account(self):
        for account in ACCOUNTS:
            if self.check_if_assigned(account):
                self.ACCOUNT_PROXY[len(self.ACCOUNT_PROXY)] = {
                    "pk": account,
                    "proxy": PROXY.pop(0)
                }

        a = json.dumps(self.ACCOUNT_PROXY, indent=4)
        self.file.write(a)
        self.file.close()


