#!/usr/bin/env python

from pymongo import MongoClient




client = MongoClient('localhost:27017')
db = client["BvSalud"]
collection_all = db["all_articles"]



def select_docs(ids_list):
    for i, id in enumerate(ids_list):
        print(i)
        collection_all.update_one({'_id':id},
                                    {'$set':{'selected':True}})

            
file = open("ids_selected.txt")
ids_list = file.readlines()
select_docs(ids_list)