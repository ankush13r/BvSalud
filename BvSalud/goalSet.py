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

REGEX_WORD_AFTER_SLASH = r"\/\w[^( &)&,]*"
def main(year,output,condition):
    print("Collecting data.")
    if condition == cGold:
        date = datetime.strptime(str(year), '%Y')

        cursor_mongo = collection_all.find({"$and":[
                    {"entry_date": {"$gte": date}},
                    {"ab_es":{"$ne": None}},
                    {"mh":{"$ne":None}},
                    {"selected":{"$ne":None}}
                    ]})
    elif condition == cTraining:
        cursor_mongo = collection_all.find({"$and":[
            {"ab_es":{"$ne": None}},
            {"mh":{"$ne":None}}
            ]})
    else:
        print(f"\tError: condition must be {cTraining} or {cGold}")
        return False
    outputFile = open(output,'w')
    outputFile.write('{"articles":[')
    try:
        valid_mh_headers_file = open("data/mesh_valids_list.txt",'r')
        valid_mh_headers_list = valid_mh_headers_file.readlines()
        valid_mh_headers_list_strip = [word.strip() for word in valid_mh_headers_list]
    except Exception as err:
        print(err)
        return False
    i = 0
    for document_dict in cursor_mongo:
        # if len(document_dict["ab_es"]) < 100: # If the length is less than 100 it won't get that article
        #     print("length < 100 :",document_dict["ab_es"])
        # else:

            try:
                ab_language = detect(document_dict["ab_es"])
            except:
                ab_language = "No detected"
                print("\tError detecting language: ab_es ->>",document_dict["ab_es"])
            if ab_language != 'es':
                print("\tlanguage error: ", ab_language,"  -----  ",document_dict["ab_es"] )
            else:
                print(i)
                if i > 0:
                    outputFile.write(',')

                id =  document_dict['_id']
                
                if document_dict['ta'] is not None:
                    journal = document_dict['ta'][0]
                else:
                    journal = document_dict['fo']
                try:
                    mesh_major = list(set(document_dict['mh']+document_dict['sh']))
                except Exception as err:
                    if document_dict['mh'] is not None and document_dict['sh'] is None:
                        print("\t->> sh:  NULL")
                        mesh_major = document_dict['mh']
                try: 
                    year = int((document_dict['entry_date']).strftime("%Y"))
                except Exception as err: 
                    print("Error: ",err, "<< entry_date is None >>")
            

                
                mesh_major_none_slash = []
                for header in mesh_major:
                    if "/" in  header:
                        header_none_slash = re.sub(REGEX_WORD_AFTER_SLASH,"",header)
                    else:
                        header_none_slash = header
                
                    if header_none_slash in valid_mh_headers_list_strip:
                        mesh_major_none_slash.append(header_none_slash)
                    else:
                        print("Header None compatible ->", header_none_slash)
                mesh_major_none_slash_unique = list(set(mesh_major_none_slash))

                data_dict = {"journal":journal,
                        "title":document_dict['ti_es'],
                        "db":document_dict['db'],
                        "pmid": id,
                        "meshMajor": mesh_major_none_slash_unique,
                        "year": year,
                        "abstractText":document_dict['ab_es']}
                data_json = json.dumps(data_dict,indent=4,ensure_ascii=False)
                outputFile.write(data_json)
                i = i + 1 
    outputFile.write(']}')
    outputFile.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='goalSet.py',usage='%(prog)s [-y ####] [-o file.json]')
    parser.add_argument('-y','--year',metavar='', type=int,help ='All data will be greater then that year.\n')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')  
    parser.add_argument('-c','--condition',choices=[cGold,cTraining],metavar='',type=str,required=True, help =f"<{cTraining}> or <{cGold}>")   

    args = parser.parse_args()
    year = args.year
    condition = args.condition
    output = args.output
    if condition == cGold and year is None:
        parser.error('The -c/--condition "gold" argument requires the --{year [-y ####]} or -SourceFile')
    else:
        current_dir = os.getcwd()
        path = os.path.join(current_dir,output)
        main(year, path, condition)
