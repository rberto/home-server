import requests

class btcoin(object):
    def __init__(self, p_addr, key):
        self.pool_address = p_addr
        self.api_key = key

    def get_user_stat(self):
        payload = {'key': self.api_key, 'action': 'userstats'}
        r = requests.get(self.pool_address, params=payload)
        return r.json()

if __name__ == '__main__':
    bt = btcoin("https://eclipsemc.com/api.php", "533943365f90f2311df3904bcdbc6c")
    data = bt.get_user_stat()
    print data["workers"][0]["hash_rate"]
    print data["data"]["user"]["confirmed_rewards"]
