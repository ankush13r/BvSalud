"""[summary]
"""
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

DB_NAME = 'BvSalud'
MONOG_URI = 'mongodb://localhost:27017/'+DB_NAME

APP = Flask(__name__)

APP.config['MONGO_DBNAME'] = DB_NAME
APP.config['MONGO_URI'] = MONOG_URI


MONGO = PyMongo(APP)

ABSTRACT = "ab_es"
DECSCODES = "decsCodes"
DECSCODES_ANNOTATOR = "decsCodes_Annotator"


@APP.route('/articles', methods=['GET'])
def get_articles():
    """[summary]
    """
    collection = MONGO.db.selected_importants
    articles_list_output = []

    found_articles_cursor = collection.find()
    for article in found_articles_cursor:
        tmp_dict = {"id":article["_id"],
                    "abstractText":article.get(ABSTRACT),
                    "decsCodes":article.get(DECSCODES),
                    "decsCodes_Annotator":article.get(DECSCODES_ANNOTATOR)},

        articles_list_output.append(tmp_dict)
    return jsonify({'results':articles_list_output})





if __name__ == '__main__':
    APP.run(debug=True)

