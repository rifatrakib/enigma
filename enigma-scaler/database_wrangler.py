from pymongo import MongoClient
from nltk.corpus import words
from math import log
from pprint import pprint


class DataWrangler:
    def __init__(self):
        self.conn = MongoClient('localhost', 27017)
        database = self.conn['enigma']
        self.enigma = database['crawled_pages']

    def dictionary_reshape(self):
        document_frequency = {}
        pipeline = [
            {
                "$project": {
                    "_id": 1,
                    "word_dictionary": 1
                }
            }
        ]
        count = 0
        for doc in self.enigma.aggregate(pipeline=pipeline):
            count += 1
            print(count)
            document_frequency = self.data_merger(document_frequency, doc['word_dictionary'])
        return document_frequency

    def data_merger(self, x, y):
        keys = list(y.keys())
        for key in keys:
            # if key in word_list:
            x[key] = x.get(key, 0) + 1
        return x

    def calculate_idf(self, word_dictionary, total_document):
        idf_values = {}
        for word in word_dictionary:
            idf_values[word] = log(total_document / word_dictionary[word])
        return idf_values

    def data_cleaner(self, word_dictionary):
        allowed_words = set(words.words())
        refined_word_list = set(word_dictionary.keys()).intersection(allowed_words)
        cleaned_data = {}
        for word in refined_word_list:
            cleaned_data[word] = word_dictionary[word]
        return cleaned_data

    def update_idf(self, word_dict):
        for key, value in word_dict.items():
            field = "word_dictionary." + key
            print('Updating idf of', key, '...')
            self.enigma.update_many({field: {"$exists": "true"}}, {"$set": {field+'.idf': value}})

    def pagerank_import(self):
        pipeline = [
            {
                "$project": {"_id": 0, "url": 1, "links": 1, "new_rank": 1}
            }
        ]
        req_docs = []
        urls = set()
        current_ranks = {}
        for doc in self.enigma.aggregate(pipeline=pipeline):
            urls.add(doc['url'])
            if 'links' in doc:
                req_docs.append(doc)
            current_ranks[doc['url']] = doc['new_rank']
        return self.calculate_pagerank(req_docs, current_ranks, urls)

    def calculate_pagerank(self, req_docs, current_ranks, urls):
        iteration = 30
        new_ranks = {}
        number_of_documents = len(urls)
        for i in range(iteration):
            for doc in req_docs:
                damping_factor = 0.85
                page_rank = 0
                number_of_backlinks = len(doc['links'])
                for link in doc['links']:
                    if link in urls:
                        page_rank += current_ranks[link]
                    else:
                        continue
                page_rank = page_rank / number_of_backlinks
                page_rank = ((1 - damping_factor) / number_of_documents) + (damping_factor * page_rank)
                doc['new_rank'] = page_rank / number_of_backlinks
                new_ranks[doc['url']] = doc['new_rank']
            if i == iteration:
                break
            for key, value in new_ranks.items():
                current_ranks[key] = value
        updated_docs = []
        for key, value in new_ranks.items():
            doc = {
                'url': key,
                'old_rank': current_ranks[key],
                'new_rank': value
            }
            updated_docs.append(doc)
        return updated_docs

    def update_pagerank(self, updated_documents):
        for doc in updated_documents:
            self.enigma.update_one(
                {
                    "url": doc['url']
                },
                {
                    "$set": {
                        "old_rank": doc['old_rank'],
                        "new_rank": doc['new_rank']
                    }
                }
            )
        print('Successful!')
