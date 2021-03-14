from pymongo import MongoClient


class EnigmaSearch:
    def __init__(self):
        self.conn = MongoClient('localhost', 27017)
        database = self.conn['enigma']
        self.enigma = database['crawled_pages']

    def search(self):
        pass
