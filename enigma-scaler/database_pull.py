from pymongo import MongoClient

client = MongoClient('localhost', 27017)
client['enigma']['pages'].update_many(
    {},
    {
        "$pull": {
            "word_dictionary": {"tfidf": 0}
        }
    }
)

print('Successful!')
