from pymongo import MongoClient
from setings import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME


class DbMongo:
    collections = (
        'cards',
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


if __name__ == '__main__':
    db = DbMongo()
