import requests
from bs4 import BeautifulSoup
from threading import Thread
from fastapi import HTTPException
import time

first_step_url = 'https://della.com.ua/search/a204bd204eflolh0i221102l230103k0m1.html'
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0"
}
domain = 'https://della.com.ua'

threads = []
results = []


def get_cards(soup: BeautifulSoup) -> list:
    request_card_list = soup.find_all("div", {"class": "is_search"})
    ansver = []
    for card in request_card_list:
        is_active = True if not card.find("div", {"class": "klushka veshka_deleted"}) else False
        date_add = card.find("div", {"class": "date_add"})
        truck_type = card.find("div", {"class": "truck_type"})
        weight = card.find("div", {"class": "weight"})
        price_main = card.find("div", {"class": "price_main"})
        country_abbr = card.find("div", {"class": "country_abbr"})
        price_additional = card.find("div", {"class": "price_additional"})
        distance_obj = card.find("a", {"class": "distance"})
        if distance_obj:
            distance = {
                'text': distance_obj.text,
                'url': distance_obj.get('href')
            }
        else:
            distance = {}
        route_unparsing = [i for i in card.find("a", {"class": "request_distance"}).find_all('span') if
                           i.get('class') != ['locality']]
        route_parsered = []
        for i in route_unparsing:
            route_parsered.append(
                {
                    'region': i.get('title'),
                    'city': i.text
                }
            )
        cargo_type = card.find("span", {"class": "cargo_type"})
        request_tags = [i.text for i in card.find("div", {"class": "request_tags"}).find_all('div')] if card.find(
            "div", {"class": "request_tags"}) else None
        price_tags = [i.text for i in card.find("div", {"class": "price_tags"}).find_all('div')] if card.find("div",
                                                                                                              {
                                                                                                                  "class": "price_tags"}) else None
        ansver.append(
            {
                'is_active': is_active,
                'date_add': date_add.text if date_add else None,
                'truck_type': truck_type.text if truck_type else None,
                'weight': weight.text if weight else None,
                'price_main': price_main.text if price_main else None,
                'country_abbr': country_abbr.text if country_abbr else None,
                'price_additional': price_additional.text if price_additional else None,
                'distance': distance,
                'cargo_type': cargo_type.text if cargo_type else None,
                'route': route_parsered,
                'request_tags': request_tags,
                'price_tags': price_tags
            }
        )
    return ansver


def parser_site(url: str):
    response = requests.get(
        url=url,
        headers=headers
    )
    if response.status_code == 200:
        soup = BeautifulSoup(response.text)
        return get_cards(soup=soup)
    else:
        raise HTTPException(status_code=response.status_code)


def pars_all(url: str = None):
    response = requests.get(
        url=url if url else first_step_url,
        headers=headers
    )
    if response.status_code == 200:
        soup = BeautifulSoup(response.text)
        cards = get_cards(soup=soup)
        next_page = soup.find('a', text='наступна стор.')
        if next_page:
            cards.extend(pars_all(url=f"{domain}{next_page.get('href')}"))
        return cards
    else:
        raise HTTPException(status_code=response.status_code)


if __name__ == '__main__':
    start_time = time.time()
    temp = pars_all()
    print("--- %s seconds ---" % (time.time() - start_time))
    # print(temp)
