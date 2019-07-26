from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1,COLLECTION_UPDATE_INFO
from pymongo import MongoClient
from datetime import datetime
import argparse
import json
import os

client = MongoClient('localhost:27017')
db = client[DATA_BASE]
collection_all = db[COLLECTION_ALL]
collection_None_Indexed_t1 =db[COLLECTIONS_NONE_INDEXED_T1]
collection_Update_info = db[COLLECTION_UPDATE_INFO]


def main(year,output):
    current_year = int(datetime.now().strftime('%Y'))
    last_year = 2000
    if year < last_year or year > current_year:
        print(f"\n\tError: The year must be between {last_year} and {current_year}\n")
        return False 

    try:
        with open('data/valid_libraries.txt') as file:
            tmp = file.readlines()
    except Exception as err:
        print("Error: ",err)
        return False
    libraries = []
    for item in tmp:
        libraries.append(item.strip())

    date = datetime.strptime(str(year), '%Y')
    cursor_mongo = collection_all.find({"$and":[
        {"mh":None},
        {"ab_es":{"$ne": None}},
        {"da": {"$gte": date}},  
        {"cc":{"$in":libraries}}
        ]})
    list_json_doc = []
    outputFile = open(output,'w')
    outputFile.write('{"articles":[')

    for i, dict_doc in enumerate(cursor_mongo):
        print(i)
        if i > 0:
            outputFile.write(',')
        if dict_doc['ta'] is not None:
            journal = dict_doc['ta'][0]
        else:
            journal = dict_doc['fo']
        year = int((dict_doc['da']).strftime("%Y"))
        data_dict = {"journal":journal,
                "title":dict_doc['ti_es'],
                "db":dict_doc['db'],
                "pmid": dict_doc['_id'],
                "Year":year,
                "abstractText":dict_doc['ab_es']}
        data_json = json.dumps(data_dict,indent=4) # ensure_ascii=False).encode('utf8')
        outputFile.write(data_json)
        collection_all.update_one({'_id': dict_doc['_id']},
                                    {'$set':
                                        {'selected': True}
                                    }) 
    outputFile.write(']}')
    outputFile.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='testSet.py',usage='%(prog)s [-y ####] [-o file.json]')
    parser.add_argument('-y','--year',metavar='',required=True, type=int,help ='All data will be greater then that year.\n')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')   
    args = parser.parse_args()
    year = args.year
    output = args.output
    current_dir = os.getcwd()
    path = os.path.join(current_dir,output)
    main(year, path)
