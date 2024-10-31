from httpx import Cookies

from const import Good, GoodStatus
from settings import http_header


def make_headers(cookies: Cookies):
    cookie = f'XSRF-TOKEN={cookies.get("XSRF-TOKEN")}; laravel_session={cookies.get("laravel_session")}'
    headers = {**http_header, 'Cookie': cookie}
    return headers


def goods_on_page_get(html) -> list[Good]:
    # find all elements '.row.product-main-list-row > .products-main-list-body'
    # for each element:
    #   find element '.column.column-code'
    #   find element '.column.column-name > a:nth-child(2)'
    #   find element '.column.column-price > span > div'
    #   find element '.column.column-availability > img'
    #   create Good object
    #   add Good object to data

    result = []
    for row in html.find(selector='.products-main-list-body > .row.product-main-list-row'):
        code = row.find('.column.column-code', first=True).text.replace('Kod: ', '')
        name = row.find('.column.column-name > a:nth-child(2)', first=True).text
        price = row.find('.column.column-price > span > div', first=True).text
        status = good_status_parser(row.find('.column.column-availability > img', first=True).attrs['title']).name
        result.append(Good(code, name, price, status))
    return result


def good_status_parser(good_status: str) -> GoodStatus:
    if good_status in ('Dostępny', 'Wielopak'):
        return GoodStatus.AVAILABLE
    elif good_status.startswith("Rezerwacja"):
        # 'Rezerwacja - planowana dostawa 31.01.2023'
        return GoodStatus.RESERVED
    else:
        raise Exception(f'unknown good status: {good_status}')
