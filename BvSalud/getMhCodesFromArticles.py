#!/usr/bin/env python
from bvs.constant import DATA_BASE, COLLECTION_ALL, COLLECTIONS_NONE_INDEXED_T1
from pymongo import MongoClient
from datetime import datetime
import argparse
import json
import os
import re


client = MongoClient('localhost/mongo_admin:PlanTL2019:27017')
db = client[DATA_BASE]
collection_all = db[COLLECTION_ALL]
collection_None_Indexed_t1 = db[COLLECTIONS_NONE_INDEXED_T1]

# Regex to delete any word after a slash (/) and also the slash
REGEX_WORD_AFTER_SLASH = r"\/\w[^( &)&,]*"


def create_Dict_codes(codes_file_root):
    keyword_dict = {}
    # Saves all codes to a dictionary, key as code and value as words in format list.
    with open(codes_file_root) as f:
        for line in f:

            (key, val) = line.split('@',1)  # Seprates codes and words
            values_list = val.split('|')  # Synonims separater
            # Deleting line break from last number of list.
            values_list[-1] = values_list[-1].strip('\n')
            keyword_dict[key] = values_list

    return keyword_dict


def getMongoCursor():
    print("Collecting data.")
    # Collecting all data from mongoDB with some conditions.
    cursor_mongo = collection_all.find({"$and": [
        {"ab_es": {"$ne": None}},
        {"mh": {"$ne": None}}
    ]})

    return cursor_mongo


def getMeshNoneQuali(mhList):
    mesh_major_none_slash = []
    for header in mhList:
        if "/" in header:
            header_splited = str(header).split('/')
            header_before_slash = header_splited[0]
        else:
            header_before_slash = header
        mesh_major_none_slash.append(header_before_slash)
    return list(set(mesh_major_none_slash))


# Method to extract mesh from a article. It receives a article and the list of valid mh header in the case  to compare all headers.
def get_mesh_decs_list(decsCodes_list_dict, mhList):
    listMhObjs = []
    for header in mhList:
        # A for for find Dec code for header.
        for key, values in decsCodes_list_dict.items():
            if header in values: 
                mhObj = {"Code": str(key),
                         "Word": header}
                listMhObjs.append(mhObj)
                break


    return listMhObjs


def extractDataIntofile(cursor_articles,decsCodes_list_dict, output):
    # Output file where all record will be saved.
    outputFile = open(output, 'w')
    # Starting with creating a json format file, all article will be inside the article.
    outputFile.write('{"articles":[')

    i = 0
    for document_dict in cursor_articles:
        print(i)
        if i > 0:
            outputFile.write(',')

        id = document_dict['_id']
        try:
            mesh_major = list(set(document_dict['mh']+document_dict['sh']))
        except Exception as err:
            if document_dict['mh'] is not None and document_dict['sh'] is None:
                  mesh_major = document_dict['mh']
        meshNoneQuali = getMeshNoneQuali(mesh_major)
        MhCodeObj = get_mesh_decs_list(decsCodes_list_dict,meshNoneQuali)

        data_dict = {"title": document_dict['ti_es'],
                     "pmid": id,
                     "abstractText": document_dict['ab_es'],
                     "Mesh":MhCodeObj
                     }
        data_json = json.dumps(data_dict, indent=4, ensure_ascii=False)
        outputFile.write(data_json)
        i = i + 1

    outputFile.write(']}')
    outputFile.close()


def main(output):
    try:
        decsCodes_list_dict = create_Dict_codes("data/codesMH.txt")
    except Exception as err:
        print("\tError: while reading file >> ", err)
        return False
    mongoCursor = getMongoCursor();
    extractDataIntofile(mongoCursor, decsCodes_list_dict, output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='make_all_Data_Set.py', usage='%(prog)s [file.json]')
    parser.add_argument('-o', '--output', metavar='', type=str,
                        required=True, help='To define a name for file.')
    args = parser.parse_args()
    output = args.output
    current_dir = os.getcwd()
    path = os.path.join(current_dir, output)
    main(path)
