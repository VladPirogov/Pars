from datetime import datetime
from pymongo import MongoClient
from setings import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME


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
        for card in cards:
            if not card.get('_id'):
                card.update({'_id': 'Not_Exist', 'create_data': now, 'update_data': now})
                self.database.cards.insert_one(card)
            elif self.database.cards.find_one({'_id': card.get('_id')}):
                card.update({'update_data': now})
                self.database.cards.update_one({'_id': card.get('_id')},
                                                 {'$set': card})
                updated.append(card.get('_id'))
            else:
                card.update({'create_data': now, 'update_data': now})
                self.database.cards.insert_one(card)
                created.append(card.get('_id'))
        self.database.update_logs.insert_one({
            'timestamp': now,
            'updated_ids': updated,
            'created_ids': created
        })

    def get_last_update(self):
        log = next(self.database.update_logs.find().sort([('timestamp', -1)]).limit(1))
        return log.get('timestamp')


