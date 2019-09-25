#!/usr/bin/env python
from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1,COLLECTION_UPDATE_INFO
from pymongo import MongoClient
import json
import os, csv
import argparse



client = MongoClient('localhost:27017')
db = client[DATA_BASE]
collection_all = db[COLLECTION_ALL]
collection_duplicate_ab_es = db["duplicate_abstracts"]

def find_articles(o_path):
    duplicate_articles = collection_duplicate_ab_es.find()
    print(collection_duplicate_ab_es.count())
    
    csv_columns = ["matching_code","id","title","abstract","article_date","entry_date","journal","mh","sh"]
    csv_file = open(o_path, 'w')
    writer = csv.DictWriter(csv_file, delimiter='|',fieldnames=csv_columns)
    writer.writeheader()

    for i, abstract in enumerate(duplicate_articles):
        for id in abstract["Ids"]:
            print(i)
            article = collection_all.find_one({"_id":id})
            article_dict = {"matching_code":i,
                "id": article["_id"],
                "title": article["ti_es"],
                "abstract" :article["ab_es"],
                "article_date" : article["da"],
                "entry_date" : article["entry_date"],
                "journal" : article["cc"],
                "mh" :article["mh"],
                "sh" : article["sh"]}
            writer.writerow(article_dict)
        
    csv_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='get_duplicate_ab_es_articles.py',usage='%(prog)s[-o file.csv]')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')   
    args = parser.parse_args()
    output = args.output
    current_dir = os.getcwd()
    path = os.path.join(current_dir,output)
    find_articles(path)