#!/usr/bin/env python
from bvs.constant import DATA_BASE,COLLECTION_ALL,COLLECTIONS_NONE_INDEXED_T1
from langdetect import detect
from pymongo import MongoClient
from datetime import datetime
import argparse
import json
import os
import re

cTraining = "training" #Condition to select if training. 
cGold = "gold" #Condition for gold Set
client = MongoClient('localhost:27017')
db = client[DATA_BASE] #DATA_BASE is a constant, please check bvs/constant.py for all constants.
collection_all = db[COLLECTION_ALL] # Also a constant COLLECTION_ALL
collection_None_Indexed_t1 =db[COLLECTIONS_NONE_INDEXED_T1] # Also a constant COLLECTION_NONE_INDEXED_T1

try:
    abstract_language_error_file = open("training_errors/abstract_language_error.txt","w")
except Exception as err:
    print("Error while opening file for meSh language errors: ",err)

try:
    mesh_case_info_file = open("training_errors/mesh_case_info.txt","w")
    mesh_case_info_file.write("ID\tMeSH header\n")
except Exception as err:
    print("Error while opening file for headers case insensitive info: ",err)


def get_mongo_cursor(condition,year):
    """The method receives two parameters condition adn year and it returns a mongo cursor of data depending on parameters 
    
    :param condition: A string with condition as (gold or training)
    :type condition: String
    :param year: Year. Data will be greater or equal.
    :type year: Int
    .. Notes::
        **training**:
    """ 
    #The method returns a cursor of data from mongoDB collection.
    #Condition parameter is if it for training ot gold Set.
    # Year parameter is for gold set, if you want data since any specific year, until today. 
    print("Collecting data.")
    if condition == cGold: #If the condition is "gold".
        date = datetime.strptime(str(year), '%Y')
        print(date)
        # Conditions for gold: 
                                # entry date must be greater than year received as parameters.
                                # ab_es (abstract spanish ) mustn't have null value.
                                # mh (medical subject header) mustn't have null value.
                                # selected: All article must be selected before for test Set 
        cursor_mongo = collection_all.find({"$and":[
                    {"entry_date": {"$gte": date}},
                    {"ab_es":{"$ne": None}},
                    {"mh":{"$ne":None}},
                    {"selected": True}
                    ]})
  
    elif condition == cTraining: #If the condition is "training".

        # Condition for training:
                                    # ab_es can't be null.
                                    # if test_training is true or (mh not null and test_training not true. Uncomment line in query to do it.
                                    
        cursor_mongo = collection_all.find(#{ "$and":[
            {"ab_es":{"$ne": None}} #,
            #{"$or":[{"$and":[{"mh":{"$ne":None}},{"test_training":{"$ne":True}}]},{"test_training":True}]}
            #]}
             )
    else:# If the condition is wrong or different, it will print an error massage and return false
        print(f"\tError: condition must be {cTraining} or {cGold}.")
        return False
    total_len = cursor_mongo.count(True)
    return cursor_mongo,total_len # Returns cursos and it's size.

def read_valid_decs_file(path_valid_decs): # Method to read the file of valid decs (header). In the file each line must have just one header or synonym, no more. 
    """Method to read the file of valid decs. It reads the file and create a list of all decs. 
    
    :param path_valid_decs: This is the root/path for file of valid decs.
    :type path_valid_decs: String. Ex: "data/valid_codes.txt"
    :return: list of valid decs.
    :rtype: List []
    """
    try: #try to catch any errors if the root is bad or doesn't exist, .... 
        valid_mh_headers_file = open(path_valid_decs,'r') # Reading the file.
        valid_mh_headers_list = valid_mh_headers_file.readlines() # Reeding each line.
        valid_mh_headers_list_strip = [word.strip() for word in valid_mh_headers_list] #Eliminate all none printable word as space , before and after string.
        valid_mh_headers_file.close() # Close file
        return valid_mh_headers_list_strip # It return the list of valid headers

    except Exception as err: #If any error it will print the Exception and return false.
        print("\t-Error reading file: ",path_valid_decs," :",err)
        return False

def is_Spanish_lang(document_dict): # Method for detection language of abstract tet from a article. It receives whole article and will find ab_es
    """Method to detect language of abstract_es, if it's english or another. If the language is english than it will return True, otherwise it will return False.
    
    :param document_dict: Dictionart of document/article
    :type document_dict: Dict()
    :return: True/False
    :rtype: boolean

    """

    try:
        ab_language = detect(document_dict["ab_es"]) # trying to detect the language, if can't it will return false and print a massage.
    except:
        abstract_language_error_file.write(str("null\t"+ document_dict["ab_es"] + "\n"))
        return False

    if ab_language == 'es': # If the language is spanish it will return a true, else it will return false and print a error massage. 
        return True
    else:
        abstract_language_error_file.write(str(ab_language+ "\t"+ document_dict["ab_es"] + "\n"))
        return False


def get_journal_year(document_dict): # Method to get year and journal from document.
    """ Method to get journal and year from document/article format json/Dict. 

    :param document_dict: A dictionary of document/article
    :type document_dict: Dict()
    :return: journal, year
    :rtype: String, Int 
    """


    if document_dict['ta'] is not None: # "ta" is journal but in some article it's null, and if it's null then it will get "fo"
        journal = document_dict['ta'][0]
    else:
        journal = document_dict['fo'] # If "ta" was null than it will go for "fo".
       
    try: # Trying to format entry date and obtains just year, but if it's null than it will print the error.
        year = int((document_dict['entry_date']).strftime("%Y"))
    except Exception as err:
        print("Error: ",err, "<< entry_date is None >>")
    return journal, year # Returns journal and year.


def get_mesh_major_list(document_dict,valid_mh_headers_list,valid_mh_headers_list_upper): #Method to extract mesh from a article. It receives a article and the list of valid mh header in the case  to compare all headers. 
    
    """Method to get list of meSH_major form the document matching with valid decs. If any header doesn't belongs to the list of valid decs, 
    it will be exclude from the list of meSS_major. 
    Also it will delete all words after a slash (/), if any header contains it.
        
    :param document_dict: Dictionary of document/article
    :type document_dict: Dict()
    :param valid_mh_headers_list: List of valid decs/meSH_headers
    :type valid_mh_headers_list: List []
    :param valid_mh_headers_list_upper: List of valid decs/meSh_headers in upper case. This list is to match in case insensitive.
    :type  valid_mh_headers_list_upper: List []

    
    :return: List of meSH_major
    :rtype: List []
    """
    

    #It the mesh header is null than it will return a empty list.
    if not document_dict['mh']:
        return list()

    try: #Trying to join mh or sh list, but if it can't it will just get mh , because some time sh is null.
        mesh_major = list(set(document_dict['mh']+document_dict['sh']))
    except: #Just get mh
        #if document_dict['mh'] is not None and document_dict['sh'] is None: # sh is null
        mesh_major = document_dict['mh']
            
    mesh_major_none_slash = [] # A local variabel to create the list of mesh headers.
    for header in mesh_major: #Some mesh headers contain words or caracters with slash and after slash are not important. So it will delete words or caracters after slash (/)
        if "/" in  header: # If header contains (/) it will enter in the condition and will get just the string before /.
            headers_split = str(header).split('/')[0] #String before /
            if len(headers_split) != 0: # If the string length is 0 like (/humans). Before / is empty.
                header_none_slash = headers_split # Header before slash (/).
            else: #if string length was 0, it will omit all next functions and enter into next loop 
                continue                   
        else:
            header_none_slash = header 
            
        if valid_mh_headers_list and header_none_slash: #this variable can be None or a list it's none will just append headers to the list without comparing with valid headers.
            
            if header_none_slash in valid_mh_headers_list: # The header exists in the list of valid mesh header than it will append else it will ignore and print a massage.
                mesh_major_none_slash.append(header_none_slash)
            
            elif header_none_slash.upper() in valid_mh_headers_list_upper: # Searching in case insensitive
                mesh_major_none_slash.append(header_none_slash)
                mesh_case_info_file.write(str(document_dict["_id"])+"\t"+str(header_none_slash)+"\n")
      
            else:
                print("\nHeader not Valid:  >> After: ", (header_none_slash),"  >> Before: "+(header), "Doc id: " + (document_dict["_id"])) #If the header is not valid.
              
        else: #Appending header to the list.
            mesh_major_none_slash.append(header_none_slash)

    mesh_major_none_slash_unique = list(set(mesh_major_none_slash))
 
    return mesh_major_none_slash_unique


def make_dictionary_for_goldSet(document_dict,condition,valid_mh_headers_list,valid_mh_headers_list_upper):
    """Method to create dictionary for goldSet.
    
    :param document_dict: The document/article
    :type document_dict: Dict()
    :param condition: A condition as (gold or training)
    :type condition: String
    :param valid_mh_headers_list: valid decs list
    :type valid_mh_headers_list: list []
    :param valid_mh_headers_list_upper: List of valid decs/meSh_headers in upper case. This list is to match in case insensitive.
    :type  valid_mh_headers_list_upper: List []
    :return: dictionary
    :rtype: Dict()
    """
    # if len(document_dict["ab_es"]) < 100: # If the length is less than 100 it won't get that article
    #     print("length < 100 :",document_dict["ab_es"])
    #     return False

    if not is_Spanish_lang(document_dict):
        return False

    journal,year = get_journal_year(document_dict)

    if condition == cTraining and "test_training" in document_dict: # If condition is training and document was selected as test_training true in mongoDB, while doing testSet.
        print("\t-From test to training: ",document_dict["_id"])
        mesh_major = ""
    else:
        mesh_major = get_mesh_major_list(document_dict,valid_mh_headers_list,valid_mh_headers_list_upper)
        
    if condition == cGold and "test_training" in document_dict:
            collection_all.update_one({'_id': document_dict['_id']},
                                {'$set':{'test_training_gold': True}})
                                
            collection_all.update_one({'_id': document_dict['_id']},
                                {'$unset':{'test_training':True}})

    data_dict = {"journal":journal,
            "title":document_dict['ti_es'],
            "db":document_dict['db'],
            "pmid": document_dict['_id'],
            "meshMajor": mesh_major,
            "year": year,
            "abstractText":document_dict['ab_es']}
    return data_dict


def main(year,output,condition,valid_decs):
    """Method main that handle all other method
    
    :param year: [description]
    :type year: [type]
    :param output: [description]
    :type output: [type]
    :param condition: [description]
    :type condition: [type]
    :param valid_decs: [description]
    :type valid_decs: [type]
    :return: [description]
    :rtype: [type]
    """
    cursor_mongo,total_len = get_mongo_cursor(condition,year)
    if not cursor_mongo:
        return False

    if valid_decs:
        try:
            valid_mh_headers_list = read_valid_decs_file("data/mesh_valid_codes_2019.txt")
            valid_mh_headers_list_upper = list(map(str.upper, valid_mh_headers_list))
        except Exception as err:
            print("\tError: while reading file >> ",err,)
            return False
    else:
        valid_mh_headers_list = None
        valid_mh_headers_list_upper = None

    
    outputFile = open(output,'w')
    outputFile.write('{"articles":[')

    count_valid_docs = 0
    for i, document_dict in enumerate(cursor_mongo):
        print(total_len - i ,"ID:",document_dict["_id"])
        
        dict_data_gold = make_dictionary_for_goldSet(document_dict,condition,valid_mh_headers_list,valid_mh_headers_list_upper)
        if dict_data_gold:
            count_valid_docs = count_valid_docs + 1
            if i > 0:
                outputFile.write(',')

            data_json = json.dumps(dict_data_gold,indent=4,ensure_ascii=False)
            outputFile.write(data_json)
    outputFile.write(']}')
    try:
        mesh_case_info_file.close()
    except:
        pass
    try:
        abstract_language_error_file.close
    except:
        pass

    outputFile.close()
    print("Total valid documents: ",count_valid_docs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='goalSet.py',usage='%(prog)s [-y ####] [-o file.json]')
    parser.add_argument('-y','--year',metavar='', type=int,help ='All data will be greater then that year.\n')
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for file.')  
    parser.add_argument('-c','--condition',choices=[cGold,cTraining],metavar='',type=str,required=True, help =f"<{cTraining}> or <{cGold}>")   
    parser.add_argument('--valid',action='store_true', help ='Valid header with decs')  

    args = parser.parse_args()
    year = args.year
    to_valid_decs = args.valid

    condition = args.condition
    output = args.output
    if condition == cGold and year is None:
        parser.error('The -c/--condition "gold" argument requires the --{year [-y ####]} or -SourceFile')
    else:
        current_dir = os.getcwd()
        path = os.path.join(current_dir,output)
        main(year, path, condition,to_valid_decs)
