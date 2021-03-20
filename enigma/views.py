from flask import Flask, render_template, request
from pymongo import MongoClient
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


app = Flask(__name__)


@app.route('/')
def index() -> 'html':
    return render_template('index.html', page_title='Home')


@app.route('/search', methods=['POST'])
def search() -> 'html':
    query = request.form['query']
    retrieved_results = extract_result(query)
    return render_template('search.html', page_title='Search Result', query=query, results=retrieved_results)


def extract_result(query):
    keywords = lemmatizer(query)
    client = MongoClient('127.0.0.1', 27017)
    pipeline = [
        {
            '$project': {
                '_id': 0,
                'word_dictionary': {
                    '$filter': {
                        'input': '$word_dictionary',
                        'as': 'words',
                        'cond': {
                            '$in': [
                                '$$words.word', keywords
                            ]
                        }
                    }
                },
                'url': 1,
                'new_rank': 1,
                'page_title': 1,
                'content': 1
            }
        },
        {
            '$match': {
                'word_dictionary': {
                    '$ne': []
                }
            }
        },
        {
            '$unwind': '$word_dictionary'
        },
        {
            '$group': {
                '_id': '$url',
                'title': {'$first': '$page_title'},
                'content': {'$first': '$content'},
                'score': {
                    '$sum': '$word_dictionary.tfidf',
                },
                'rank': {'$first': '$new_rank'}
            }
        },
        {
            '$project': {
                '_id': 0,
                'url': '$_id',
                'title': 1,
                'content': 1,
                'value': {
                    '$sum': [{'$multiply': ['$score', 70]}, {'$multiply': ['$rank', 30]}],
                },
            }
        },
        {
            '$sort': {'value': -1}
        },
        {
            '$limit': 10
        }
    ]
    return list(client['enigma']['pages'].aggregate(pipeline=pipeline, allowDiskUse=True))


def lemmatizer(text):
    words = []
    lm = WordNetLemmatizer()
    for word in word_tokenize(text):
        words.append(lm.lemmatize(word, get_wordnet_pos(word)))
    return words


def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


if __name__ == '__main__':
    app.run(debug=True)
