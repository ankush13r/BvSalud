#!/usr/bin/env python
from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1
from langdetect import detect
from pymongo import MongoClient
from datetime import datetime
import argparse
import json
import os
import re


client = MongoClient('localhost:27017')
db = client[DATA_BASE]
collection_all = db[COLLECTION_ALL]
collection_None_Indexed_t1 =db[COLLECTIONS_NONE_INDEXED_T1]

REGEX_WORD_AFTER_SLASH = r"\/\w[^( &)&,]*"
def main(output):

    print("Collecting data.")
    cursor_mongo = collection_all.find({"$and":[
                {"$and":[{"ab_es":{"$ne": "No disponible"}},{"ab_es":{"$ne": None}}]},
                {"mh":{"$ne":None}}
                ]})

    outputFile = open(output,'w')
    outputFile.write('{"articles":[')
    removable_words_file = open("data/list_words_to_remove.txt",'r')
    i = 0
    for document_dict in cursor_mongo:
        if len(document_dict["ab_es"]) < 100:
            print("length < 100 :",document_dict["ab_es"])

        else:
            try:
                ab_language = detect(document_dict["ab_es"])
            except:
                ab_language = "No detected"
                print("\tError detecting language: ab_es ->>",document_dict["ab_es"][:20])
            if ab_language != 'es':
                print("\tlanguage error: ", ab_language,"  -----  ",document_dict["ab_es"][:20] )
            else:
                print(i)
                if i > 0:
                    outputFile.write(',')
        #        if document_dict['db'] == 'IBECS':
        #            id =  document_dict['alternate_id']
        #        else:
        #            id =  document_dict['_id']
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
                removable_words_list = removable_words_file.readlines()
                removable_words_list_strip = [word.strip() for word in removable_words_list]
                mesh_major_none_slash = []

                for header in mesh_major:
                    if "/" in  header:
                        header_none_slash = re.sub(REGEX_WORD_AFTER_SLASH,"",header)
                    else:
                        header_none_slash = header
                
                    if header_none_slash not in removable_words_list_strip:
                        mesh_major_none_slash.append(header_none_slash)
                    else:
                        print("Header None compatible ->", header)
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
    removable_words_file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='make_all_Data_Set.py',usage='%(prog)s [file.json]')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')   
    args = parser.parse_args()
    output = args.output
    current_dir = os.getcwd()
    path = os.path.join(current_dir,output)
    main(path)
