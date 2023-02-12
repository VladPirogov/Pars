import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
import json
from database.connection import DbMongo

first_step_url = 'https://della.com.ua/search/a204bd204eflolh0i221102l230103k0m1.html'
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0"
}
domain = 'https://della.com.ua'

db = DbMongo()


def get_cards(soup: BeautifulSoup) -> list:
    request_card_list = soup.find_all("div", {"class": "is_search"})
    ansver = []
    get_text = lambda x: x.text.strip('\n').replace('\n\n\n\n\n\n', '\n').replace(' ', ' ')
    for card in request_card_list:
        _id = card.attrs.get('request_id')
        is_active = True if not card.find("div", {"class": "klushka veshka_deleted"}) else False
        date_add = card.find("div", {"class": "date_add"})
        cube = card.find("div", {"class": "cube"})
        truck_type = card.find("div", {"class": "truck_type"})
        weight = card.find("div", {"class": "weight"})
        price_main = card.find("div", {"class": "price_main"})
        country_abbr = card.find("div", {"class": "country_abbr"})
        price_additional = card.find("div", {"class": "price_additional"})
        distance_obj = card.find("a", {"class": "distance"})
        if distance_obj:
            distance = {
                'text': get_text(distance_obj),
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
                    'city': get_text(i)
                }
            )
        cargo_type = card.find("span", {"class": "cargo_type"})
        request_tags = [get_text(i) for i in card.find("div", {"class": "request_tags"}).find_all('div')] if card.find(
            "div", {"class": "request_tags"}) else None
        price_tags = [get_text(i) for i in card.find("div", {"class": "price_tags"}).find_all('div')] if card.find(
            "div",
            {
                "class": "price_tags"}) else None
        ansver.append(
            {
                '_id': _id,
                'is_active': is_active,
                'date_add': get_text(date_add) if date_add else None,
                'cube': get_text(cube) if cube else None,
                'truck_type': get_text(truck_type) if truck_type else None,
                'weight': get_text(weight) if weight else None,
                'price_main': get_text(price_main) if price_main else None,
                'country_abbr': get_text(country_abbr) if country_abbr else None,
                'price_additional': get_text(price_additional) if price_additional else None,
                'distance': distance,
                'cargo_type': get_text(cargo_type) if cargo_type else None,
                'route': route_parsered,
                'request_tags': request_tags,
                'price_tags': price_tags
            }
        )
    db.insert_update_cards(cards=ansver)
    return ansver


def pars_all_cards(url: str = None):
    response = requests.get(
        url=url if url else first_step_url,
        headers=headers
    )
    if response.status_code == 200:
        soup = BeautifulSoup(response.text)
        cards = get_cards(soup=soup)
        next_page = soup.find('a', text='наступна стор.')
        if next_page:
            cards.extend(pars_all_cards(url=f"{domain}{next_page.get('href')}"))
        return cards
    else:
        raise HTTPException(status_code=response.status_code)


def parser_site():
    data = pars_all_cards()
    with open('data.json', 'w', encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False)
        return file


def get_file():
    with open('data.json', 'r', encoding='utf8') as file:
        return file
