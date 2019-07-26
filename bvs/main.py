from crawler import Crawl
from parse_file import Parse
from mongo import Mongo
from constant import * 

import glob
import sys
from io import open
import argparse
 
def save_to_mongo(path_to_crawler, mode, num_file = 0):
    print("Processing directory: ",path_to_crawler)
    files = glob.glob(path_to_crawler+'/*.xml')
    files.sort()

    while num_file < len(files):
        print(str(num_file)+" >> Saving to mongo, file: ",str(files[num_file]))
        with open(PATH_TO_LAST_RECORD,"w") as f:
                f.write(str(num_file) + " " + CASE_SAVE) 
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
                case = result_splited[1]
            except:
                case = None
            return last_stopped, case
    except:
        return 0 ,None

def main(mode ,path_sub_folder,restart):

    if mode == MODE_ALL:
        path_super_folder = PATH_TO_SAVE_ALL
    elif mode == MODE_COMPARE:
        path_super_folder = PATH_TO_SAVE_NONE_INDEXED
    else:
        print("Wrong argument: ",mode)
        return False
    crawl = Crawl(mode,path_super_folder,path_sub_folder)
    print(crawl)
    print()
    
    last_stopped, case = find_last_stopped(PATH_TO_LAST_RECORD) 
    
    if restart:
        if case == CASE_DOWNLOAD:
            crawl.save_records(last_stopped)
            save_to_mongo(crawl.path_to_crawler,crawl.mode)
        elif case == CASE_SAVE:
            save_to_mongo(crawl.path_to_crawler,crawl.mode,last_stopped)
        else:
            print("No data found to restart the program please check the path: ", PATH_TO_LAST_RECORD)
            return True       
    else:
        if last_stopped != 0 and case in [CASE_SAVE, CASE_DOWNLOAD]:
            print(f"Last time it had been interrupted, while {case}ing records, page number: {last_stopped}")
            input_str = str(input("Do you really want to continue?,yes/no[yes]: ") or "yes") 
            if input_str != 'yes':
                return True 
        crawl.save_records()
        if mode == MODE_ALL:
            Mongo.change_collections_name(DATA_BASE,COLLECTION_ALL,COLLECTION_ALL+"_old")
            Mongo.change_collections_name(DATA_BASE,COLLECTIONS_NONE_INDEXED_T1,COLLECTIONS_NONE_INDEXED_T1+"_old")
            Mongo.change_collections_name(DATA_BASE,COLLECTIONS_NONE_INDEXED_T2,COLLECTIONS_NONE_INDEXED_T2+"_old")
            save_to_mongo(crawl.path_to_crawler,crawl.mode)
        else:
            print("----------------change")
            Mongo.change_collections_name(DATA_BASE,COLLECTIONS_NONE_INDEXED_T2,COLLECTIONS_NONE_INDEXED_T1) 
            save_to_mongo(crawl.path_to_crawler,crawl.mode)
            print("Comparing documents in mongo")
    if mode == MODE_COMPARE:
        Parse.compare_t1_t2(crawl)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog ='BvSalud.py')
    parser.add_argument('-r','--restart',action='store_true',  help ='To restart the program from last interrupted')
    parser.add_argument('-m','--mode',metavar=[MODE_ALL,MODE_COMPARE],default="compare",required=True, help ='To define if the program is excecuting first time or downloading all article.')
    parser.add_argument('-o','--output',required=True, help ='To define the directory for downloads.')   
    args = parser.parse_args()
    mode = args.mode
    output = args.output
    restart = args.restart


    main(mode,output,restart)





