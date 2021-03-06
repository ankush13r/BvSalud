#!/usr/bin/env python
from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1,COLLECTION_UPDATE_INFO
from pymongo import MongoClient
from datetime import datetime
from langdetect import detect
import argparse
import json
import os
import re

client = MongoClient('localhost:27017')
db = client[DATA_BASE]
collection_all = db[COLLECTION_ALL]
collection_None_Indexed_t1 =db[COLLECTIONS_NONE_INDEXED_T1]
collection_Update_info = db[COLLECTION_UPDATE_INFO]




def get_title(document_dict):
    if document_dict["ti_es"]:
        return document_dict["ti_es"]
        
    else:
        for ti in document_dict["ti"]:
            if detect(ti)== "es":
                return ti
    return None



def main(year,output):
    current_year = int(datetime.now().strftime('%Y'))
    last_year = 2000
    if year < last_year or year > current_year:
        print(f"\n\tError: The year must be between {last_year} and {current_year}\n")
        return False 

    #try:
    #    with open('data/valid_libraries.txt') as file:
    #        tmp = file.readlines()
    #except Exception as err:
    #    print("Error: ",err)
    #    return False
    #libraries = []
    #for item in tmp:
    #    libraries.append(item.strip())

    date = datetime.strptime(str(year), '%Y')
    regex_ES = re.compile("^ES", re.IGNORECASE)
    print("Getting data...")

    cursor_mongo = collection_all.find(
            {"$or":[
                    {"goldToTest" :True}, 
                    {"$and":[
                        {"mh":None},
                        {"entry_date": {"$gte": date}},
                        {"ab_es":{"$ne": None}}
                            ]}
                    ]})
            
         

        #,{"$or":[{"cc":{"$in":libraries}},{"cc":regex_ES}]}
      

    len_cursor = cursor_mongo.count(True)

    list_json_doc = []
    try:
        outputFile = open(output,'w')
    except Exception as err:
        print("Error: ",err)
    outputFile.write('{"articles":[')
    print("Total Records: ",len_cursor )
  
    for i, dict_doc in enumerate(cursor_mongo):
        print("\n>> ",len_cursor-i, "ID: ",dict_doc["_id"])
        try:
            ab_language = detect(dict_doc["ab_es"])
        except Exception as err:
            ab_language = "No detected"

        # try:
        #     articles_matched = collection_all.find(
        #         {"ti_es":dict_doc["ti_es"]})
        # except:
        #     pass

        if ab_language != 'es':
            print("\tlanguage not Spanish: ", ab_language, )
        else:
            # if i % 2 == 0 and divide: #If number of document is even
            #     print("For Training")
            #     collection_all.update_one({'_id': dict_doc['_id']},
            #                                 {'$set':{'test_training': True}})
            # else:

            if i > 0:
                outputFile.write(',')
            if dict_doc['ta'] is not None:
                journal = dict_doc['ta'][0]
            else:
                journal = dict_doc['fo']
            year = int((dict_doc['entry_date']).strftime("%Y"))
            try:
                title = get_title(dict_doc)                
            except:
                title = None
            
            data_dict = {"id": dict_doc['_id'],
                    "journal":journal,
                    "title":title,
                    "db":dict_doc['db'],
                    "year":year,
                    "abstractText":dict_doc['ab_es']}
            data_json = json.dumps(data_dict,indent=4, ensure_ascii=False)
            outputFile.write(data_json)
            
            """
            if "goldSet" in dict_doc:
                collection_all.update_one({'_id': dict_doc['_id']},
                                    {'$unset':{'goldSet':True}})
            """
            collection_all.update_one({'_id': dict_doc['_id']},
                                        {'$set':{'selected': True}
                                        })
            if "goldToTest" in dict_doc:
                collection_all.update_one({'_id': dict_doc['_id']},
                                    {'$unset':{'goldToTest':True}})
                                    
    outputFile.close()
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='tesSet.py',usage='%(prog)s [-y ####] [-o file.json]')
    parser.add_argument('-y','--year',metavar='',required=True, type=int,help ='All data will be greater then that year.\n')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')   
    #parser.add_argumentdivide('--divide',action='store_true', help ='Valid header with decs')  
    

    args = parser.parse_args()
    year = args.year
    #divide = args.divide

    output = args.output
    current_dir = os.getcwd()
    path = os.path.join(current_dir,output)
    main(year, path)
