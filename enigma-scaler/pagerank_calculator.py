from pymongo import MongoClient
from database_wrangler import DataWrangler
from time import time, sleep
from pprint import pprint

client = MongoClient('localhost', 27017)

data = DataWrangler()
start = time()
documents = data.pagerank_import()
print(time() - start)
sleep(5)
pprint(sorted(documents, key=lambda k: k['new_rank']))
data.update_pagerank(documents)
