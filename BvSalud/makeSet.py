#!/usr/bin/env python
from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1
from langdetect import detect
from pymongo import MongoClient
from datetime import datetime
import argparse
import json
import os
import re
from langdetect import detect

cTraining = "training"
cGold = "gold"

client = MongoClient('localhost:27017')
db = client[DATA_BASE]
collection_all = db[COLLECTION_ALL]
collection_None_Indexed_t1 =db[COLLECTIONS_NONE_INDEXED_T1]

def get_mongo_cursor(condition,year):
    print("Collecting data.")
    if condition == cGold:
        date = datetime.strptime(str(year), '%Y')

        cursor_mongo = collection_all.find({"$and":[
                    {"entry_date": {"$gte": date}},
                    {"ab_es":{"$ne": None}},
                    {"mh":{"$ne":None}},
                    {"selected": True}
                    ]})
  
    elif condition == cTraining:
        cursor_mongo = collection_all.find({"$and":[
            {"ab_es":{"$ne": None}},
            {"$or":[{"$and":[{"mh":{"$ne":None}},{"test_training":{"$ne":True}}]},{"test_training":True}]}
            ]})
    else:
        print(f"\tError: condition must be {cTraining} or {cGold}.")
        return False
    total_len = cursor_mongo.count()
    return cursor_mongo,total_len

def read_valid_decs_file(path_valid_decs):
    try:
        valid_mh_headers_file = open(path_valid_decs,'r')
        valid_mh_headers_list = valid_mh_headers_file.readlines()
        valid_mh_headers_list_strip = [word.strip() for word in valid_mh_headers_list]
        valid_mh_headers_file.close()
        return valid_mh_headers_list_strip
    except Exception as err:
        print("\t-Error reading file: ",path_valid_decs," :",err)
        return False


def is_Spanish_lang(document_dict):
    try:
        ab_language = detect(document_dict["ab_es"])
    except:
        print("\tError detecting language: ab_es ->>",document_dict["ab_es"])
        return False

    if ab_language == 'es':
        return True
    else:
        print("\tlanguage error: ", ab_language,"  -----  ",document_dict["ab_es"] )
        return False


def get_journal_year(document_dict):

    if document_dict['ta'] is not None:
        journal = document_dict['ta'][0]
    else:
        journal = document_dict['fo']

       
    try: 
        year = int((document_dict['entry_date']).strftime("%Y"))
    except Exception as err: 
        print("Error: ",err, "<< entry_date is None >>")
    return journal, year


def get_mesh_major_list(document_dict,valid_mh_headers_list):
    try:
        mesh_major = list(set(document_dict['mh']+document_dict['sh']))
    except:
        if document_dict['mh'] is not None and document_dict['sh'] is None:
            mesh_major = document_dict['mh']
            
    mesh_major_none_slash = []
    for header in mesh_major:
        if "/" in  header:
            slash_position = header.find("/")
            header_none_slash = header[:(slash_position-1)]
        else:
            header_none_slash = header

        if valid_mh_headers_list:
            if header_none_slash in valid_mh_headers_list:
                mesh_major_none_slash.append(header_none_slash)
            else:
                print("Header None compatible ->", header_none_slash, "Doc id: ",document_dict["_id"])
        else:
            mesh_major_none_slash.append(header_none_slash)

    mesh_major_none_slash_unique = list(set(mesh_major_none_slash))

    mesh_major_none_slash_unique = list(set(mesh_major_none_slash))
    return mesh_major_none_slash_unique


def make_dictionary_for_goldSet(document_dict,condition,valid_mh_headers_list):
    # if len(document_dict["ab_es"]) < 100: # If the length is less than 100 it won't get that article
    #     print("length < 100 :",document_dict["ab_es"])
    #     return False

        if not is_Spanish_lang(document_dict):
            return False
 
        journal,year = get_journal_year(document_dict)

        if condition == cTraining and "test_training" in document_dict:
            print("\t-From test to training: ",document_dict["_id"])
            mesh_major = ""
        else:
            mesh_major = get_mesh_major_list(document_dict,valid_mh_headers_list)
            
        if condition == cGold and "test_training" in document_dict:
                collection_all.update_one({'_id': document_dict['_id']},
                                    {'$set':{'test_training_gold': True}})
                                    
                collection_all.update_one({'_id': document_dict['_id']},
                                    {'$unset':{'test_training':True}})

        data_dict = {"journal":journal,
                "title":document_dict['ti_es'],
                "db":document_dict['db'],
                "pmid": document_dict['_id'],
                "meshMajor": mesh_major,
                "year": year,
                "abstractText":document_dict['ab_es']}
        return data_dict


def main(year,output,condition,valid_decs):
    
    cursor_mongo,total_len = get_mongo_cursor(condition,year)
    if not cursor_mongo:
        return False

    if valid_decs:
        try:
            valid_mh_headers_list = read_valid_decs_file("data/mesh_valids_list.txt")
        except Exception as err:
            print("\tError: while reading file >> ",err,)
    else:
        valid_mh_headers_list = None
    outputFile = open(output,'w')
    outputFile.write('{"articles":[')
    count_valid_docs = 0
    for i, document_dict in enumerate(cursor_mongo):
        print(total_len - i ,"ID:",document_dict["_id"])
        
        dict_data_gold = make_dictionary_for_goldSet(document_dict,condition,valid_mh_headers_list)
        if dict_data_gold:
            count_valid_docs = count_valid_docs + 1
            if i > 0:
                outputFile.write(',')

            data_json = json.dumps(dict_data_gold,indent=4,ensure_ascii=False)
            outputFile.write(data_json)
            
    outputFile.write(']}')
    outputFile.close()
    print("Total valid documents: ",count_valid_docs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='goalSet.py',usage='%(prog)s [-y ####] [-o file.json]')
    parser.add_argument('-y','--year',metavar='', type=int,help ='All data will be greater then that year.\n')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')  
    parser.add_argument('-c','--condition',choices=[cGold,cTraining],metavar='',type=str,required=True, help =f"<{cTraining}> or <{cGold}>")   
    parser.add_argument('--valid',action='store_true', help ='Valid header with decs')  

    args = parser.parse_args()
    year = args.year
    to_valid_decs = args.valid

    condition = args.condition
    output = args.output
    if condition == cGold and year is None:
        parser.error('The -c/--condition "gold" argument requires the --{year [-y ####]} or -SourceFile')
    else:
        current_dir = os.getcwd()
        path = os.path.join(current_dir,output)
        main(year, path, condition,to_valid_decs)
