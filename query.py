from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1,COLLECTION_UPDATE_INFO
from pymongo import MongoClient
from datetime import datetime
import argparse
import json



client = MongoClient('localhost:27017')
db = client[DATA_BASE]
collection_all = db[COLLECTION_ALL]
collection_None_Indexed_t1 =db[COLLECTIONS_NONE_INDEXED_T1]
collection_Update_info = db[COLLECTION_UPDATE_INFO]


def main(year,output):
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
    parser = argparse.ArgumentParser(prog ='BvSalud.py')
    parser.add_argument('-y','--year',metavar='year',required=True, type=int,help ='To define a year')
    parser.add_argument('-o','--output',required=True, help ='To define the file to save data.')   
    
    args = parser.parse_args()

    year = args.year
    output = args.output
    path = str(output)+".json"
    main(year, path)
