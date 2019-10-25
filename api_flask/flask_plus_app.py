from flask import Flask
from flask_restplus import Resource, Api
from flask_pymongo import PyMongo
from flask import jsonify
from flask import request

#MongoDB constants variable
DB_NAME = 'BvSalud'
MONOG_URI = 'mongodb://localhost:27017/'+DB_NAME

#Constats Article fields
ABSTRACT = "ab_es"
DECSCODES = "decsCodes"
DECSCODES_ANNOTATOR = "decsCodes_Annotator"


APP = Flask(__name__)   # creating a Flask application

APP.config['MONGO_DBNAME'] = DB_NAME
APP.config['MONGO_URI'] = MONOG_URI
MONGO = PyMongo(APP)

API = Api(APP)          # creating a Flask-RESTPlus API
NAME_SPACE = API.namespace('/')

def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('API', __name__, url_prefix='/API')
    API.init_app(blueprint)
    API.add_namespace(blog_posts_namespace)
    API.add_namespace(blog_categories_namespace)
    flask_app.register_blueprint(blueprint)

    db.init_app(flask_app)



@NAME_SPACE.route('/articles')
@API.response(404,'Category not found.')
class Articles(Resource):
    def get(self):
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


    def put(self,id):
        print(request.json)


if __name__ == '__main__':
    APP.run(debug = True)