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


def get_mh_none_slash(mesh_list):

    new_mesh_list=[]
    if mesh_list:
        for header in mesh_list:
            if "/" in  header: # If header contains (/) it will enter in the condition and will get just the string before /.
                headers_split = str(header).split('/')[0] #String before /
                if len(headers_split) != 0: # If the string length is 0 like (/humans). Before / is empty.
                    header_none_slash = headers_split # Header before slash (/).
                else: #if string length was 0, it will omit all next functions and enter into next loop 
                    header_none_slash = header                   
            else:
                header_none_slash = header
            
            new_mesh_list.append(header_none_slash)
    else:
        new_mesh_list = 0  
    return new_mesh_list


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
            if not article["mh"]: #If mesh is null then it will pass all next steps.
                continue
            mesh  = get_mh_none_slash(article["mh"])
            sh = get_mh_none_slash(article["sh"])
            article_dict = {"matching_code":i,
                "id": article["_id"],
                "title": article["ti_es"],
                "abstract" :article["ab_es"],
                "article_date" : article["da"],
                "entry_date" : article["entry_date"],
                "journal" : article["cc"],
                "mh" :mesh,
                "sh" : sh}
            writer.writerow(article_dict)
        
    csv_file.close()

def main(o_path):
    find_articles(o_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='get_duplicate_ab_es_articles.py',usage='%(prog)s[-o file.csv]')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')   
    args = parser.parse_args()
    output = args.output
    current_dir = os.getcwd()
    path = os.path.join(current_dir,output)
    main(path)