import json
import fake_useragent


with open('data/proxy.txt', 'r+') as file:
    PROXY = [row.strip() for row in file]

with open('data/accounts.txt', 'r+') as file:
    ACCOUNTS = [row.strip() for row in file]

with open('data/account_proxy.json', 'r') as file:
    ASIGNED_ACCOUNTS = json.load(file)

with open("data/ABI/erc_20_abi.json", 'r') as file:
    ERC20_ABI = json.load(file)

with open("data/ABI/bex_abi.json", 'r') as file:
    BEX_ABI = json.load(file)

with open("data/ABI/bend_abi.json") as file:
    BEND_ABI = json.load(file)

TOKENS_PER_CHAIN = {
        'BERA': "0x7507c1dc16935B82698e4C63f2746A2fCf994dF8",
        'WBERA': "0x7507c1dc16935B82698e4C63f2746A2fCf994dF8",
        'BGT': "0xAcD97aDBa1207dCf27d5C188455BEa8a32E80B8b",
        'STGUSDC': "0x6581e59A1C8dA66eD0D313a0d4029DcE2F746Cc5",
        'WBTC': "0x2577D24a26f8FA19c1058a8b0106E2c7303454a4",
        'HONEY': "0x7EeCA4205fF31f947EdBd49195a7A88E6A91161B",
        'WETH': "0x8239FBb3e3D0C2cDFd7888D8aF7701240Ac4DcA4"
}

BEX_CONTRACT = "0x21e2C0AFd058A89FCf7caf3aEA3cB84Ae977B73D"
BEND_CONTRACT = '0x30A3039675E5b5cbEA49d9a5eacbc11f9199B86D'

UA = fake_useragent.UserAgent()
# ------------------------------------------->CONFIG START<--------------------------------------------------

TWO_API_CAPTCHA_KEY = "YOUR KEY"
accounts_to_make = [3, 40]

MIN_SLEEP_FAUCET = 3
MAX_SLEEP_FAUCET = 6

MIN_SLEEP_FARM = 1
MAX_SLEEP_FARM = 200

SWAP_MIN = 94
SWAP_MAX = 96
