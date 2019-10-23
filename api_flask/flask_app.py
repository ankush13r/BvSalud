"""[summary]
"""
from flask import Flask
from flask_restplus import Api, Resource
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

#MongoDB constants variable
DB_NAME = 'BvSalud'
MONOG_URI = 'mongodb://localhost:27017/'+DB_NAME


#APP Flask
APP = Flask(__name__)
APP.config['MONGO_DBNAME'] = DB_NAME
APP.config['MONGO_URI'] = MONOG_URI


APP_rst = Api(app=APP)

name_space = APP_rst.namespace('main', description='Main APIs')

MONGO = PyMongo(APP)



ABSTRACT = "ab_es"
DECSCODES = "decsCodes"
DECSCODES_ANNOTATOR = "decsCodes_Annotator"






def modify_article_dictionary(dict_result:dict):
    id = dict_result['id']
    
    MONGO.db.selected_importants.update_one({"_id":id},
    {'$set':
    {"decsCodes":dict_result["decsCodes"],
    "decsCodes_Annotator":dict_result["decsCodes_Annotator"]}

    })



@APP.route('/articles', methods=['GET','POST'])
def get(Resource):
    """[summary]
    """
    
    articles_list_output = []
    data = request.get_json()
    print(request.values)
    found_articles_cursor = MONGO.db.selected_importants.find()
    for article in found_articles_cursor:
        tmp_dict = {"id":article["_id"],
                    "abstractText":article.get(ABSTRACT),
                    "decsCodes":article.get(DECSCODES),
                    "decsCodes_Annotator":article.get(DECSCODES_ANNOTATOR)}

        articles_list_output.append(tmp_dict)
    return jsonify({'results':articles_list_output})


@APP.route('/modify', methods=['PATCH'])
def update_article(result):
    modify_article_dictionary()


if __name__ == '__main__':
    APP.run(debug=True)

