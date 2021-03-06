#!/usr/bin/env python
from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1
from langdetect import detect
from pymongo import MongoClient
import argparse
import os


cTraining = "training" #Condition to select if training. 
cGold = "gold" #Condition for gold Set
client = MongoClient('localhost:27017')
db = client[DATA_BASE] #DATA_BASE is a constant, please check bvs/constant.py for all constants.
collection_all = db[COLLECTION_ALL] # Also a constant COLLECTION_ALL
collection_None_Indexed_t1 =db[COLLECTIONS_NONE_INDEXED_T1] # Also a constant COLLECTION_NONE_INDEXED_T1


def main(path_output):
    
    cursor_mongo = collection_all.find({"$and":[
            {"ab_es":{"$nin":[None,"No disponible","No disponble","No dispoinble","No disponbile",
                                                        "No disponibles","No  disponible","No dsiponible",
                                                        "resumen está disponible en el texto completo","No dipsonible","es","."]}},
            {"mh":{"$ne":None}}]})

    len_cursor = cursor_mongo.count()
    print("Total Doc:",len_cursor)
    error_file = open(path_output,"w")
    error_file.write("id\tlanguage\tabstract")

    for i, document_dict in enumerate(cursor_mongo):
        print(len_cursor-i)
        try:
            ab_language = detect(document_dict["ab_es"]) # trying to detect the language, if can't it will return false and print a massage.
            if ab_language != 'es': # If the language is spanish it will return a true, else it will return false and print a error massage. 
                error_file.write(str(document_dict["_id"] +"\t"+ ab_language+ "\t"+ document_dict["ab_es"] + "\n"))
        except:
            print("Error: Detecting lang.")
            error_file.write(str(document_dict["_id"] + "\tnull\t"+ document_dict["ab_es"] + "\n"))
    error_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='abstract_info.py',usage='%(prog)s [-o file.json]')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')  

    args = parser.parse_args()
    output = args.output

    current_dir = os.getcwd()
    path_output = os.path.join(current_dir,output)
    main(path_output)
       
  