#!/usr/bin/env python
from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1,COLLECTION_UPDATE_INFO
from pymongo import MongoClient
import json
import os



client = MongoClient('localhost:27017')
db = client[DATA_BASE]
collection_all = db[COLLECTION_ALL]
collection_duplicate_ab_es = db["duplicate_abstracts"]

def find_articles():
    duplicate_articles = collection_duplicate_ab_es.find()
    print(collection_duplicate_ab_es.count())

    for abstract in duplicate_articles:
        print(abstract)


find_articles()