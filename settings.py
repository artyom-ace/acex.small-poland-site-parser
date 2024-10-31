import os

prog_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = prog_dir + '/data/'
db_path = prog_dir + '/db.sqlite3'

shop_main_url = 'https://b2b.cedrus.com.pl/produkty'
shop_login_url = 'https://b2b.cedrus.com.pl/logowanie'
shop_credentials = {'login': 'info@raingarden.pl', 'password': '----'}
http_header = {
    # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    # 'Accept-Encoding': 'gzip, deflate, br',
    # 'Accept-Language': 'en-US,en;q=0.5',
    # 'Connection': 'keep-alive',
    # 'Content-Length':
    'Content-Type': 'application/x-www-form-urlencoded',
    # Cookie
    # 'DNT': '1',
    # 'Host': 'b2b.cedrus.com.pl',
    # 'Origin': 'https://b2b.cedrus.com.pl',
    # 'Referer': 'https://b2b.cedrus.com.pl/logowanie',
    # 'Sec-Fetch-Dest': 'document',
    # 'Sec-Fetch-Mode': 'navigate',
    # 'Sec-Fetch-Site': 'same-origin',
    # 'Sec-Fetch-User': '?1',
    # 'Sec-GPC': '1',
    # 'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'
}

stored_cookies = None
