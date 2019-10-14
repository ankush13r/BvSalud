#! /usr/bin/python

import json
from langdetect import detect
import argparse
import sys



def info_abstractText(file_root):
    new_articls = []
    with open(file_root) as json_file:
        data = json.load(json_file)
        for article in data['articles']:
            abs_info_dict = dict()
            abstractText = article['abstractText']
            abs_info_dict['pmid'] = article['pmid']
            abs_info_dict['language_abstractText'] = detect(abstractText)
            abs_info_dict['characters_abstractText'] = len(abstractText)
            abs_info_dict['tokens_abstractText'] = len(abstractText.split())
            abs_info_dict['abstract'] = abstractText
            new_articls.append(abs_info_dict)
    return new_articls

def make_new_json(input_files,output):
    outputFile = open(output,'w')
    outputFile.write('{"articles":')
    for i, input_file in enumerate(input_files):
        print("File: ", input_file)

        json_data = info_abstractText(input_file)
        data_json = json.dumps(json_data,indent=4,ensure_ascii=False)
        outputFile.write(data_json)



    outputFile.write('}') 

def main(input_files,output):
    try:
        for input_file in input_files:
            open(input_file, "r")
    except Exception as err:
        print("Error: ", err)
        return False
    make_new_json(input_files,output)
    print("\nDone!")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='abstract_info.py',usage='%(prog)s [-i input_file_root_1, input_file_2, N+] [-o file.json]')   
    parser.add_argument('-o','--output',metavar='output_file.json',type=str,required=True, help ='To define a name for file.')   
    parser.add_argument('file', nargs='+', help='Input file in format json')
    
    args = parser.parse_args()
    output = args.output
    input_files = args.file
    print(input_files)
    main(input_files,output)
