"""[summary]
"""
from flask import Flask
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
MONGO = PyMongo(APP)

APP_rst = Api(app=APP)





ABSTRACT = "ab_es"
DECSCODES = "decsCodes"
DECSCODES_ANNOTATOR = "decsCodes_Annotator"


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


@APP.route('/modify', methods=['PUT'])
def update_article(result):
    
    if not request.json:
        abort(400)
    json_obj = request.json()
    
    # id = json_obj['id']
    
    # MONGO.db.selected_importants.update_one({"_id":id},
    # {'$set':
    # {"decsCodes":json_obj["decsCodes"],
    # "decsCodes_Annotator":json_obj["decsCodes_Annotator"]}
    # })

    return jsonify({'done':json_obj})


if __name__ == '__main__':
    APP.run(debug=True)

