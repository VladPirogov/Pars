import requests
import json
from datetime import datetime
from copy import deepcopy
from bs4 import BeautifulSoup
from fastapi import HTTPException
from database.connection import DbMongo
from setings import CARDS_ON_PAGE

first_step_url = 'https://della.com.ua/search/a204bd204eflolh0i221102l230103k0m1.html'
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0"
}
domain = 'https://della.com.ua'


class DellParser:

    def __init__(self, first_step_url: str = first_step_url):
        self.first_step_url = first_step_url
        self.headers = headers
        self.db = DbMongo()
        self.domain = domain

    def _get_last_timestamp(self):
        return self.db.get_last_update()

    def pars_cards(self, soup: BeautifulSoup) -> list:
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
            request_tags = [get_text(i) for i in
                            card.find("div", {"class": "request_tags"}).find_all('div')] if card.find(
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
        return ansver

    def pars_all_cards(self, url: str = None):
        response = requests.get(
            url=url if url else self.first_step_url,
            headers=headers
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text)
            cards = self.pars_cards(soup=soup)
            next_page = soup.find('a', text='наступна стор.')
            if next_page:
                cards.extend(self.pars_all_cards(url=f"{self.domain}{next_page.get('href')}"))
            return cards
        else:
            raise HTTPException(status_code=response.status_code)

    def parser_site(self, forse_update: bool = False):
        last_timestamp = self._get_last_timestamp()
        if not last_timestamp or (datetime.now() - last_timestamp).total_seconds() > 150 or forse_update:
            data = self.pars_all_cards()
            self.db.insert_update_cards(cards=deepcopy(data))
            return data

    def get_cards(self):
        return self.db.get_all_active_cards()

    def get_file(self):
        data = self.parser_site()
        with open('../data.json', 'w', encoding='utf8') as file:
            json.dump(data, file, ensure_ascii=False)
            return file

    def paginate(self, index_page: int = 0, cards_on_pages: int = None):
        if not index_page:
            self.parser_site()
        if not cards_on_pages:
            cards_on_pages = CARDS_ON_PAGE
        page = self.db.get_page(index_page=index_page, cards_on_pages=cards_on_pages)
        max_pages = self.db.get_max_number_pages(cards_on_pages=cards_on_pages)
        return page, max_pages
