from datetime import datetime
from math import ceil
from pymongo import MongoClient, UpdateOne, InsertOne
from setings import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME, CARDS_ON_PAGE


class DbMongo:
    collections = (
        'cards',
        'update_logs'
    )
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = cls.__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def __init__(self):
        uri = f"mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}" if DB_USER else f"mongodb://{DB_HOST}:{DB_PORT}"
        self.connection = MongoClient(uri)
        self.database = self.connection[DB_NAME]
        self.__check_collection()

    def __check_collection(self):
        existing_collections = self.database.list_collection_names()
        for collection in self.collections:
            if collection not in existing_collections:
                self.database.create_collection(collection)

    def insert_update_cards(self, cards: list[dict]):
        updated = []
        created = []
        now = datetime.now()
        bulk_operations = []
        for card in cards:
            if not card.get('_id'):
                card.update({'_id': 'Not_Exist', 'create_data': now, 'update_data': now})
                bulk_operations.append(InsertOne(card))
            elif self.database.cards.find_one({'_id': card.get('_id')}):
                card.update({'update_data': now})
                bulk_operations.append(UpdateOne({'_id': card['_id']}, {'$set': {'update_data': now, **card}}, upsert=True))
                updated.append(card.get('_id'))
            else:
                card.update({'create_data': now, 'update_data': now})
                bulk_operations.append(InsertOne(card))
                created.append(card.get('_id'))
        self.database.cards.bulk_write(bulk_operations)
        self.database.update_logs.insert_one({
            'timestamp': now,
            'updated_ids': updated,
            'created_ids': created
        })

    def get_last_update(self):
        log = next(self.database.update_logs.find().sort([('timestamp', -1)]).limit(1))
        return log.get('timestamp')

    def get_all_active_cards(self):
        return self.database.cards.find({'is_active': True}).sort([('update_data', -1)])

    def get_max_number_pages(self, cards_on_pages: int = CARDS_ON_PAGE):
        active_cards = self.database.cards.count_documents({'is_active': True})
        if active_cards:
            return ceil(active_cards/cards_on_pages)
        else:
            return 0

    def get_page(self, index_page: int = 0, cards_on_pages: int = CARDS_ON_PAGE):
        cards = self.database.cards.find({'is_active': True}).sort([('update_data', -1)]).skip(index_page*cards_on_pages).limit(cards_on_pages)
        return list(cards)
