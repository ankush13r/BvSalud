#!/usr/bin/env python
from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1
from pymongo import MongoClient
from datetime import datetime
import argparse
import json
import os
import csv
import re
from langdetect import detect
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS,  ImageColorGenerator
import random
from PIL import Image

REGEX_WORD_AFTER_SLASH = r"\/\w[^( &)&,]*"


client = MongoClient('localhost:27017')
db = client[DATA_BASE]
collection_all = db[COLLECTION_ALL]

def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0,0%%, %d%%)" % random.randint(60, 100)

def make_word_cloud(text):
    try:
        word_cloud = WordCloud(width = 1920,height = 1080, random_state=1).generate(text)
        plt.figure(figsize=(10,8),facecolor = 'white', edgecolor='blue')
        plt.imshow(word_cloud.recolor(color_func=grey_color_func, random_state=3),
           interpolation="spline16")
        plt.axis("off")
        plt.show()
    except: pass

def main(year,output):
    if year is None:
        year = 1980
    date = datetime.strptime(str(year), '%Y')

    cursor_mongo = collection_all.find({"$and":[
                {"entry_date": {"$gte": date}},
                {"$and":[{"ab_es":{"$ne": "No disponible"}},{"ab_es":{"$ne": None}}]},
                {"mh":{"$ne":None}}
                ]})

    outputFile_headers_count = open(output+'.txt','w')
    
    csv.register_dialect('myDialect',quoting=csv.QUOTE_NONNUMERIC,skipinitialspace=True)
    outputFile_csv = open(output+'.csv','w')
    csv_writer = csv.writer(outputFile_csv,dialect='myDialect')
    csv_writer.writerow(["id",'language','abstractText_length','abstract text'])
    heading_text = ""
    mesh_major_length_list = []

    for i, document_dict in enumerate(cursor_mongo):
        print(i)

#        if document_dict['db'] == 'IBECS':
#            id =  document_dict['_id']
#        else:
#            id =  document_dict['_id']

        id =  document_dict['_id']
        try:
            mesh_major = list(set(document_dict['mh']+document_dict['sh']))
        except Exception as err:
            if document_dict['mh'] is not None and document_dict['sh'] is None:
                print("\t->> sh:  NULL")
                mesh_major = document_dict['mh']

        abstractText = document_dict['ab_es'] #saving abstract text in a variable
        try:
            abstractText_langage = detect(abstractText)  # detecting language, return string language type (es,pt,fr,en, etc...).
        except:
            abstractText_langage = "No detected"

        try:
            abstractText_length = len(abstractText)
        except:
            abstractText_langage = 0
        if abstractText_length < 100:
            row = [id,abstractText_langage,abstractText_length,abstractText]
            csv_writer.writerow(row)
        if abstractText_langage != 'es':
            row = [id,abstractText_langage,abstractText_length,abstractText]
            csv_writer.writerow(row)

        outputFile_headers_count.write((str(len(mesh_major)) +'\n')) #writing number of mesh major into file

        mesh_major_none_slash = []
        for header in mesh_major:
            if "/" in  header:
                header_none_slash = re.sub(REGEX_WORD_AFTER_SLASH,"",header)
            else:
                header_none_slash = header
            mesh_major_none_slash.append(header_none_slash)

        heading_text = heading_text + " " + str(' '.join(mesh_major_none_slash)) #Joining all mesh major giving it a space between

    try:
        make_word_cloud(heading_text)
    except:
        print("Couldn't make words cloud")
    
    outputFile_csv.close()
    outputFile_headers_count.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='goalSet.py',usage='%(prog)s [-y ####] [-o file.json]')
    parser.add_argument('-y','--year',metavar='', type=int,help ='All data will be greater then that year.\n')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')   
    args = parser.parse_args()
    year = args.year
    output = args.output
    current_dir = os.getcwd()
    path = os.path.join(current_dir,output)
    main(year, path)
