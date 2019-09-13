#! /usr/bin/python
# -*- coding: utf-8 -*-

import getopt, sys, json
from flashtext import KeywordProcessor
import argparse


def encode_articles(codes_file_root, articles_file_root, output_root):
   """
   Method to convert text into codes from article, it uses flashtext (keywordProcessor) to convert a word to a code.
   """
   # reads input file with decs codes into a dict

   keyword_processor = KeywordProcessor()

   keyword_dict = {}
   with open(codes_file_root) as f: #Saves all codes to a dictionary, key as code and value as words in format list.
      for line in f:
         (key, val) = line.split('@') #Seprates codes and words
         values_list = val.split(',')
         values_list[-1] = values_list[-1].strip('\n')
         keyword_dict[key] = values_list

   keyword_processor.add_keywords_from_dict(keyword_dict) # Saves all codes dictionary into keyword_processor made before.

   # reads JSON goal set
   outputFile = open(output_root,'w') #output file opening
   outputFile.write('{"documents": [') 
   
   with open(articles_file_root) as json_file:
      records = json.load(json_file)

      for i, article in enumerate(records['articles']):
         if i > 0:
            outputFile.write(',')
                
         results = {}
         text = ''.join(map(str,[article['title'],' ',article['abstractText']]))
         keywords_found = keyword_processor.extract_keywords(text)
         mylist = list(dict.fromkeys(keywords_found)) #to remove duplicates
         results["pmid"] = article['pmid'] 
         results["labels"] = mylist 

         data_json = json.dumps(results,indent=4,ensure_ascii=False) #making dictionary into json -> text format
         outputFile.write(data_json) #writing json data as text into the file
      outputFile.write(']}') #writing text to close the list and json format in the file.
      outputFile.close() # file clossing

def main(input, output):
   codes_file = "copy_codes.txt"
   try:
      open(codes_file, "r")
      open(input, "r")
   except Exception as err:
        print("Error: ", err)
        return False
   encode_articles(codes_file,input, output)

if __name__ == '__main__':
   parser = argparse.ArgumentParser(prog ='goalSet.py',usage='%(prog)s [-o file.json] [Input_file.json]')
   parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a output file.')  
   parser.add_argument('filename', help='Input file in format json')
   args = parser.parse_args()
   input = args.filename
   output = args.output
   main(input, output)
