#!/usr/bin/env python
from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1,COLLECTION_UPDATE_INFO
from pymongo import MongoClient
from datetime import datetime
from langdetect import detect
import argparse
import json, csv
import os
import re


client = MongoClient('localhost:27017')
db = client[DATA_BASE]
collection_difference_dates= db["difference_in_date"]


def mongo_to_csv(o_path):
    cursor_mongo = collection_difference_dates.find()
    print("total records:",collection_difference_dates.count_documents({}))
    csv_columns = ["Difference_update_entry_Date","da","entry_date","update_date","Library","Journal","_id","meshMajor","abstract_es"]
    with open(o_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter='|',fieldnames=csv_columns)
        writer.writeheader()
        for i, doc in enumerate(cursor_mongo):
            print(i)
            writer.writerow(doc)

    









def main(o_path):
    mongo_to_csv(o_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='tesSet.py',usage='%(prog)s [-y ####] [-o file.json]')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')
    args = parser.parse_args()
    output = args.output
    current_dir = os.getcwd()
    path = os.path.join(current_dir,output)
    main(path)
