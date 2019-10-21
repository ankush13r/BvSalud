import os
import json
import datetime
from bson.objectid import  ObjectId
from flask import Flask
from flask_pymongo import PyMongo


class JSONEncoder(json.JSONEncoder):                           
    ''' extend json-encoder class'''    
    def default(self, o):                               
        if isinstance(o, ObjectId):
            return str(o)                               
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)



app = Flask(__name__)

#adding url to flask config, so flask_pymongo can use it to make connection.
app.config['MONGO_URI'] = "mongodb://localhost:27017/newTest"
mongo = PyMongo(app)


#Use the modified encoder class to handle ObjectId & datetime object while json finding the respone
app.json_encoder = JSONEncoder


@app.route("/")
def home_page():
    online_users = mongo.db.users.find({"online": True})
    return (online_users)