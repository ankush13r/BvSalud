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

    date = datetime.strptime(str(year), '%Y')
    cursor_mongo = collection_all.find({"$and":[
                {"da": {"$gte": date}},
                {"ab_es":{"$ne": None}},
                {"mh":{"$ne":None}},
                {"selected":{"$ne":None}}
                ]})

    outputFile = open(output,'w')
    outputFile.write('{"articles":[')
    for i, document_dict in enumerate(cursor_mongo):
        print(i)
    return 1
    for i, document_dict in enumerate(cursor_mongo):
        print(i)
        if i > 0:
            outputFile.write(',')
        if document_dict['db'] == 'IBECS':
            id =  document_dict['alternate_id']
        else:
            id =  document_dict['_id']

        if document_dict['ta'] is not None:
            journal = document_dict['ta'][0]
        else:
            journal = document_dict['fo']
        try:
            mesh_major = list(set(document_dict['mh']+document_dict['sh']))
        except Exception as err:
            print("Error: ", err)
            if document_dict['mh'] is not None and document_dict['sh'] is None:
                mesh_major = document_dict['mh']

        year = int((document_dict['da']).strftime("%Y"))
        data_dict = {"journal":journal,
                "title":document_dict['ti_es'],
                "db":document_dict['db'],
                "pmid": id,
                "meshMajor": mesh_major,
                "Year": year,
                "abstractText":document_dict['ab_es']}
        data_json = json.dumps(data_dict,indent=4)
        outputFile.write(data_json) 
    outputFile.write(']}')
    outputFile.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='goalSet.py',usage='%(prog)s [-y ####] [-o file.json]')
    parser.add_argument('-y','--year',metavar='',required=True, type=int,help ='All data will be greater then that year.\n')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')   
    args = parser.parse_args()
    year = args.year
    output = args.output
    current_dir = os.getcwd()
    path = os.path.join(current_dir,output)
    main(year, path)
