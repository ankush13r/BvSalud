#!/usr/bin/env python
from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1
from langdetect import detect
from pymongo import MongoClient


cTraining = "training" #Condition to select if training. 
cGold = "gold" #Condition for gold Set
client = MongoClient('localhost:27017')
db = client[DATA_BASE] #DATA_BASE is a constant, please check bvs/constant.py for all constants.
collection_all = db[COLLECTION_ALL] # Also a constant COLLECTION_ALL
collection_None_Indexed_t1 =db[COLLECTIONS_NONE_INDEXED_T1] # Also a constant COLLECTION_NONE_INDEXED_T1


def main():
    cursor_mongo = collection_all.find({"$and":[
            {"ab_es":{"$nin":[None,"No disponible","No disponble","No dispoinble","No disponbile",
                                                        "No disponibles","No  disponible","No dsiponible",
                                                        "resumen está disponible en el texto completo","No dipsonible","es","."]}},
            {"mh":{"$ne":None}}]})

    len_cursor = cursor_mongo.count()
    print("Total Doc:",len_cursor)
    error_file = open("abstract_lang_error.txt","w")


    for i, document_dict in enumerate(cursor_mongo):
        print(len_cursor-i)
        try:
            ab_language = detect(document_dict["ab_es"]) # trying to detect the language, if can't it will return false and print a massage.
            if ab_language != 'es': # If the language is spanish it will return a true, else it will return false and print a error massage. 
                error_file.write(str(ab_language+ "\t"+ document_dict["ab_es"] + "\n"))
        except:
            error_file.write(str("null\t"+ document_dict["ab_es"] + "\n"))

main()
       
  