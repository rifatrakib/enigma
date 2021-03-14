from database_wrangler import DataWrangler
from pprint import pprint
from time import time

start = time()
data = DataWrangler()
# data.word_polisher()
doc_frequency_per_word = data.dictionary_reshape()
pprint(doc_frequency_per_word)
print(len(doc_frequency_per_word))
total_document = len(doc_frequency_per_word)

doc_frequency_per_word = data.data_cleaner(doc_frequency_per_word)
pprint(sorted(doc_frequency_per_word.items(), key=lambda k: k[1]))
print(len(doc_frequency_per_word))

doc_frequency_per_word = data.calculate_idf(doc_frequency_per_word, total_document)
# pprint(sorted(doc_frequency_per_word.items(), key=lambda k: k[1], reverse=True))
# print(len(doc_frequency_per_word))

idf_dict = dict(sorted(doc_frequency_per_word.items(), key=lambda k: k[0]))
data.update_idf(idf_dict)
pprint(idf_dict)
end = time()
print(end - start)
