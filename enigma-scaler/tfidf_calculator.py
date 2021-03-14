from pymongo import MongoClient

client = MongoClient('localhost', 27017)
client['enigma']['crawled_pages'].update_many(
    {},
    {
        "$set": {
            "word_dictionary."
        }
    }
)
