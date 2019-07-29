#!/usr/bin/env python
from crawler import Crawl
from parse_file import Parse
from mongo import Mongo
from constant import *

import glob
import sys, os
from io import open
import argparse
 
def save_to_mongo(path_to_crawler, mode, num_file = 0):
    print("Processing directory: ",path_to_crawler)
    files = glob.glob(path_to_crawler+'/*.xml')
    files.sort()

    while num_file < len(files):
        print(str(num_file)+" >> Saving to mongo, file: ",str(files[num_file]))
        with open(PATH_TO_LAST_RECORD,"w") as f:
                f.write(str(num_file) + " " + CASE_SAVE + " " + str(path_to_crawler) +" " +str(mode)) 
        documents_dict_list = Parse.parse_file(files[num_file])
        try:
            for document_dict in documents_dict_list:
                try:
                    Mongo.save_dict_to_mongo(document_dict,mode)
                except Exception as e:
                    Mongo.save_exception_to_mongo(document_dict['_id'],'Saving one <doc> to Mongo',path_to_crawler,str(e))        
        except Exception as e:
            Mongo.save_exception_to_mongo(None,'Saving multiple (for) <doc> to Mongo',path_to_crawler,str(e))
        num_file = num_file + 1
        if num_file == (len(files)):
                with open(PATH_TO_LAST_RECORD,"w") as f:
                    f.write("0")    
        print("\t>> Saved file.\n")

def find_last_stopped(path_to_find_last_stoped):
    try:
        with open(path_to_find_last_stoped,"r") as file:
            result = file.read()
        if str(result) == "0":
            return 0 ,None
        else:
            result_splited = result.split()
            last_stopped = int(result_splited[0])
            try:   
                last_case = result_splited[1]
            except:
                last_case = None
            try: 
                path = result_splited[2]
            except:
                path = None
            try: 
                condition = result_splited[3]
            except:
                condition = None
            return last_stopped, last_case, path, condition
    except:
        return 0 ,None, None, None

def backup_collection(mode):
    if crawl.mode == MODE_ALL:
        Mongo.change_collections_name(DATA_BASE,COLLECTION_ALL,COLLECTION_ALL+"_old")
        Mongo.change_collections_name(DATA_BASE,COLLECTIONS_NONE_INDEXED_T1,COLLECTIONS_NONE_INDEXED_T1+"_old")
        Mongo.change_collections_name(DATA_BASE,COLLECTIONS_NONE_INDEXED_T2,COLLECTIONS_NONE_INDEXED_T2+"_old")
    else:
        print("----------------change")
        Mongo.change_collections_name(DATA_BASE,COLLECTIONS_NONE_INDEXED_T2,COLLECTIONS_NONE_INDEXED_T1)

def loop_case_restart(crawl):
    last_stopped, last_case, last_path, last_mode = find_last_stopped(PATH_TO_LAST_RECORD) 
    if last_path == crawl.path_to_crawler and crawl.mode == last_mode:
        if last_case == CASE_DOWNLOAD:
            crawl.save_records(last_stopped) # Downloading records
            last_saving_num = 0
            return True
        elif last_case == CASE_SAVE:
            last_saving_num = last_stopped  
            return True  
        else:
            print(">>>> Error:\tCase doesn't match to the last case was: ",last_case,"\nPlease check the file: {os.getcwd()}/{PATH_TO_LAST_RECORD}")
            return False
    else:
        print(">>>> Error:\tThe last output folder or/and condition don't match.\n")
        print(f"\t\tLast output folder:\t{last_path},\tNew output folder: {crawl.path_to_crawler}")
        print(f"\t\tLast condition:\t\t{last_mode},\tNew condition: {crawl.mode}\n")
        print(f"You can check also:\t{os.getcwd()}/{PATH_TO_LAST_RECORD}\n")
        return False


def loop_case_all(crawl):
    last_stopped, last_case, last_path, last_mode = find_last_stopped(PATH_TO_LAST_RECORD) 
    if (last_stopped != 0 and last_case == CASE_DOWNLOAD) or last_case == CASE_SAVE:
        print(f"Last time it had been interrupted, while {last_case}ing records,\tpage number: {last_stopped},\tfolder: {last_path},\tIn condition: {last_mode}")
        input_str = str(input("Do you really want to continue?,yes/no[yes]: ") or "yes") 
        if input_str != 'yes':
            return False
    crawl.save_records() # Downloading records.
    return 0

def  create_super_folder_path(mode):
    if mode == MODE_ALL:
        path_super_folder = PATH_TO_SAVE_ALL
    elif mode == MODE_COMPARE:
        path_super_folder = PATH_TO_SAVE_NONE_INDEXED
    else:
        print("Wrong argument: ",mode)
        return False
    return path_super_folder

def main(mode ,path_sub_folder,restart):

    path_super_folder = create_super_folder_path(mode)
    if not path_super_folder:
        return False

    crawl = Crawl(mode,path_super_folder,path_sub_folder)
    print(crawl)
    print()
    
    if restart:
      last_saving_num = loop_case_restart(crawl)
      if not last_saving_num: 
          return False
    else:
        last_saving_num = loop_case_all(crawl)
        if not last_saving_num:
            return False   

    backup_collection(crawl.mode)
    save_to_mongo(crawl.path_to_crawler,crawl.mode,last_saving_num) #Saving records to MongoDB.
    if crawl.mode == MODE_COMPARE:
        print("Comparing documents in mongo")
        Parse.compare_t1_t2(crawl)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog ='BvSalud.py')
    parser.add_argument('--restart',action='store_true',  help ='To restart the program from last interrupted')
    parser.add_argument('-m','--mode',metavar=[MODE_ALL,MODE_COMPARE],required=True, help ='To define if the program is excecuting first time or downloading all article again.')
    parser.add_argument('-o','--output',required=True, help ='To define the directory for downloads.')   
    args = parser.parse_args()

    mode = args.mode
    output = args.output
    restart = args.restart
    main(mode,output,restart)





