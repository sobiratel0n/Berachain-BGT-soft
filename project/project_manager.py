import random
import time

from utils.assign_proxy_to_account import AssignProxy
from project.faucet import Faucet
from config import accounts_to_make, MIN_SLEEP_FARM, MAX_SLEEP_FARM
from project.bex_swap import Bex
from project.bend_landing import Bend
from loguru import logger as ll
from colorama import Fore

class ProjectManager():
    def __init__(self, project):
        self.project = project

    def start(self):
        for account_id in range(accounts_to_make[0], accounts_to_make[1]):
            account_id = str(account_id)
            if self.project == "faucet":
                acc = Faucet(account_id=account_id)
                acc.faucet()
            elif self.project == 'bex':
                acc = Bex(account_id=account_id)
                acc.bex_swap()
            elif self.project == 'bend':
                acc = Bend(account_id=account_id)
                acc.bend()

    def farm(self):
        store_error_accs = []
        error_file = open('data/log/error_accs.txt', 'a')
        success_file = open('data/log/success_accs.txt', 'a')
        for account_id in range(accounts_to_make[0], accounts_to_make[1]):
            account_id = str(account_id)
            sleep = random.randint(MIN_SLEEP_FARM, MAX_SLEEP_FARM)
            faucet = Faucet(account_id)
            status = faucet.faucet()
            if status == True:
                time.sleep(random.randint(10, 100))
                if faucet.wait_for_tokens() == True:
                    bex = Bex(account_id)
                    status = bex.bex_swap()
                    if status == True:
                        time.sleep(random.randint(1, 300))
                        bend = Bend(account_id)
                        status = bend.bend()
                        if status == True:
                            ll.success(f"[Wallet {account_id}] complete all tasks and started farming $BGT")
                            success_file.write(f"{time.asctime(time.localtime())} | Account {account_id} | Success \n")
                            ll.info(Fore.BLUE + f"Go to sleep for {sleep} sec" + Fore.RESET)
                            time.sleep(sleep)
                        else:
                            error_file.write(f"{time.asctime(time.localtime())} | Account {account_id} | Error: BendLanding \n")
                    else:
                        error_file.write(f"{time.asctime(time.localtime())} | Account {account_id} | Error: BexSwap \n")
                else:
                    store_error_accs.append(account_id)

            elif status == 'claimed':
                bex = Bex(account_id)
                status = bex.bex_swap()
                if status == True:
                    time.sleep(random.randint(1, 300))
                    bend = Bend(account_id)
                    status = bend.bend()
                    if status == True:
                        ll.success(f"[Wallet {account_id}] complete all tasks and started farming $BGT")
                        success_file.write(f"{time.asctime(time.localtime())} | Account {account_id} | Success \n")
                        ll.info(Fore.BLUE + f"Go to sleep for {sleep} sec" + Fore.RESET)
                        time.sleep(sleep)
                    else:
                        error_file.write(
                            f"{time.asctime(time.localtime())} | Account {account_id} | Error: BendLanding \n")
                else:
                    error_file.write(f"{time.asctime(time.localtime())} | Account {account_id} | Error: BexSwap \n")

            else:
                error_file.write(f"{time.asctime(time.localtime())} | Account {account_id} | Error: Faucet \n")
        error_file.write(f"---------------------------------{time.asctime(time.localtime())}---------------------------------- \n")
        error_file.close()







    def manage(self):
        if self.project == "assign_proxy":
            acc = AssignProxy()
            acc.assign_proxy_to_account()
        elif self.project == "faucet":
            self.start()
        elif self.project == 'bex':
            self.start()
        elif self.project == 'farm':
            self.farm()
        elif self.project == 'bend':
            self.start()
