from mongo import Mongo
from crawler import Crawl
from constant import *
import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen, urlretrieve
import re, time
from io import open
import socket
from socket import timeout
socket.setdefaulttimeout(300)

class Parse:
    def xml_to_dictionary(document_xml):
        """The method converts a **xml document** to a **dictionary (json) format**. The method is just for article BVSalud **LILACS** or **IBECS**.
difference_between_entry_update_date.

:param document_xml: A **single article document** in the **xml** format. 
:type document_xml: xml
:returns: A **single article document** in the **dictionary (json)** format.
:rtype: dictionary/json
"""
        document_dict = dict()
        document_values = ['id','type','ur','au','afiliacao_autor','ti_es','ti_pt',
                        'ti_en','ti','fo','ta','is','la','cp','da','ab_pt','ab_en','ab_es','ab',
                        'entry_date','_version_','ct','mh','sh','cc','mark_ab_es','mark_ab_pt','mark_ab_en',
                        'db','alternate_id','update_date']

        for code in document_values:
            try:
                value =document_xml.find(attrs= {'name':code}) # Find the value by code. If it doesn't exit than returns none
                if not value: # Check if the value is None
                    document_dict[code] = value #Saving the value to the dictionary by code as key. In this case it must be None.      
                elif code == 'da':
                    try:
                        document_dict[code] = (datetime.strptime(value.text[:6],'%Y%m%d'))
                    except:
                        try:
                            document_dict[code] = (datetime.strptime(value.text[:4],'%Y'))
                        except:
                            document_dict[code] =value.text
                elif code in ['entry_date','update_date']:
                    try:
                        document_dict[code] = (datetime.strptime(value.text,'%Y%m%d'))
                    except:
                        try:
                            document_dict[code] = datetime.strptime(value.text[:6], '%Y%m%d')
                        except:
                            try:
                                document_dict[code] = datetime.strptime(value.text[:4], '%Y')
                            except (TypeError, AttributeError) as e:
                                Mongo.save_exception_to_mongo(document_xml.find(attrs= {"name":"id"}).text,
                                 'Extract and converting date format single doc',code,str(e))
                                document_dict[code] =value.text
                else:                
                    children = value.findChildren() #Find if it has children. If it doesn't have than returns None.
                    if len(children) > 0:    #If children exists, so get into the loop for appending all child
                        if code in ['type','ti_es','ti_pt','fo','cp','ab_pt','ab_en','ab_es','cc','ti_en', 'db', 'alternate_id']:
                            document_dict[code] = children[0].text
                        elif code in ['ur','au','afiliacao_autor','ti','ta','is','la','ab','ct','mh','sh']:
                            strings_list = []
                            for child in children:
                                strings_list.append(child.text)
                            document_dict[code] = strings_list              
                        elif code in ['mark_ab_es','mark_ab_pt','mark_ab_en']:
                            document_dict[code] = children[0].text             
                    else:
                        document_dict[code] = value.text
            except (TypeError, AttributeError) as e:
                Mongo.save_exception_to_mongo(document_xml.find(attrs= {"name":"id"}).text,
                                         'Extract field information from single doc',code,str(e))                                   
        document_dict['_id'] = document_dict.pop('id')
        document_dict['parsing_entry_date'] = datetime.utcnow()
        return document_dict

    def parse_file(path_to_file):
        """The method parse a files and extract all documents one by one, 
        and after it converts **each document** by calling the function **xml_to_dictionary**.
        After **all the documents** one by one will be saved in the **data base MongoDB** as well all **ERROR**.

    :param path_to_file: The root of file to be parsed. 
    :type path_to_file: string (Ex: ./crawled/IBECS_LILACS_17072019_pg_1.xml).
    :param mode: The mode is condition if it receives **"compare"** will saved into a collection time 2. 
                Otherwise in the collection normal, maybe time 1. By default it's None.
    :type mode: string
    :returns: Nothing to return.

    """
        try:
            file = open(path_to_file)
            xml_content = file.read()
            bsObj = BeautifulSoup(xml_content,features='lxml')
            documents = bsObj.findAll("doc")
            document_dict_list = []
            for i, document_xml in enumerate(documents):
                try:
                    document_dict = Parse.xml_to_dictionary(document_xml)
                    document_dict['file'] = path_to_file
                    document_dict_list.append(document_dict)
                except Exception as e:
                    Mongo.save_exception_to_mongo(document_xml.find(attrs= {"name":"id"}).text,
                                    'XML to DICTIONARY one <doc> from single XML file',document_xml.find(attrs= {"name":"id"}).text,str(e))
            return document_dict_list
        except Exception as e:
            Mongo.save_exception_to_mongo(path_to_file,'XML to DICTIONARY (for) multiple <doc> from single XML file',path_to_file,str(e))

    def find_id_by_alternate_id(alternate_id):
       
        base_url = 'http://pesquisa.bvsalud.org/portal/resource/en/'
        url = base_url + str(alternate_id.strip())
        content = urlopen(url)
        bsObj = BeautifulSoup(content,features ='lxml') 
        data_string = (bsObj.find(attrs = {'class' :'data'})).text  #Get the string whose class is data, for extracing the id.
        found_object = re.search(r"(?<=ID:).*",data_string) # Regex For get id from the string
        doc_id = found_object.group().strip()
        print("url:", url)
        print("new_id: ", doc_id)
        time.sleep(2)
        return doc_id 

    def compare_t1_t2():

        json_data = open(PATH_URL_JSON,"r")
        base_dictionary = json.load(json_data)
        try:
            base_url =  base_dictionary["url_for_id"]
        except:
            base_url =  "http://pesquisa.bvsalud.org/portal/?output=xml&lang=en&from=&sort=&format=&count=&fb=&page=1&index=tw&q=id%3A"
                           
        list_ids_t1 = Mongo.get_all_ids_list(COLLECTIONS_NONE_INDEXED_T1)
        list_ids_t2 = Mongo.get_all_ids_list(COLLECTIONS_NONE_INDEXED_T2)

        list_new_ids  = list(set(list_ids_t2) - set(list_ids_t1))
        list_modified_ids  = list(set(list_ids_t1) - set(list_ids_t2))
        new_records_len = len(list_new_ids)
        print("\nNew records: ",new_records_len,"\n")

        for i, id in enumerate(list_new_ids):
            document_t2 = Mongo.get_document(COLLECTIONS_NONE_INDEXED_T2,id)
            try:
                print("\n",new_records_len-i, ") New Document <<",document_t2['_id'],">>\tmh: ",document_t2['mh'])
                print()
                Mongo.save_dict_to_mongo(document_t2,MODE_INDEXED)
                Mongo.save_to_mongo_updated_info(id,'new',document_t2['db'])                                                        
            except (TypeError, AttributeError) as e:
                Mongo.save_exception_to_mongo(id,'Saveing new none indexed document into mongo',id, str(e))

        modify_records_len = len(list_modified_ids)
        print("\nRecords to modify: ",modify_records_len,"\n")
        for i, id in enumerate(list_modified_ids):
            document_t1 = Mongo.get_document(COLLECTIONS_NONE_INDEXED_T1,id)
            
            print("\n",modify_records_len-i,"-> Document to modify: ",document_t1['_id'])
            if document_t1['db'] == 'IBECS':
                try:
                    doc_id = Parse.find_id_by_alternate_id(document_t1['_id'])                
                except:
                    doc_id = id
                    print("Error: <<Finding id by alternate id >>")
            else:
                doc_id = id
            url = base_url + doc_id
            count = 0
            while True and count < 2:
                try:
                    xml = urlopen(url)
                    time.sleep(2)
                    break
                except Exception as err:
                    count = count + 1
                    print(count,") Error: xml = urlopen(url) 170: ",err)
                    print("Sleeping: ",SLEEP_TIME2, "seconds")
                    time.sleep(SLEEP_TIME2)    
            bsObj = BeautifulSoup(xml,features='lxml')
            document_xml = bsObj.find('doc')
            
            if document_xml is not None:
                try:
                    document_dict = Parse.xml_to_dictionary(document_xml)
                    print("Updating document: ", doc_id)
                    Mongo.replace_doc_to_mongo(document_dict,document_t1['_id'])
                    Mongo.save_to_mongo_updated_info(document_dict['_id'],'update',document_dict['db'])
                    print("->> Updated!\n")
                except Exception as e:
                    print("Error (while Mongo.replace_do_to_mongo(document_dict,document_t1['_id'])): ",e)
                    Mongo.save_exception_to_mongo(document_dict['_id'],'Update information from single <doc>',url,str(e))
            else:
                tmp_dict = {'_id' : doc_id}
                Mongo.save_dict_to_mongo(tmp_dict,MODE_PANDING)
                print(f"Error: No Document Found: {url}")

        return True        

    def get_pending_documents():
        print("Finding all panding documents")
        json_data = open(PATH_URL_JSON,"r")
        base_dictionary = json.load(json_data)
        try:
            base_url =  base_dictionary["url_for_id"]
        except:
            base_url =  "http://pesquisa.bvsalud.org/portal/?output=xml&lang=en&from=&sort=&format=&count=&fb=&page=1&index=tw&q=id%3A"


        ids_list = Mongo.get_all_ids_list(COLLECTION_PANDING)

        
        modify_records_len = len(ids_list)
        for i, old_id in enumerate(ids_list):
            print("\n",modify_records_len -i,"-> Document to modify: ",old_id)
            try:
                new_id = Parse.find_id_by_alternate_id(old_id)                
            except:
                new_id = old_id
                print("Error: <<Finding id by alternate id >>")
    
            url = base_url + new_id
            count = 0
            while True and count < 2:
                try:
                    xml = urlopen(url)
                    time.sleep(2)
                    break
                except Exception as err:
                    count = count + 1
                    print(count,") Error: xml = urlopen(url) 170: ",err)
                    print("Sleeping: ",SLEEP_TIME2, "seconds")
                    time.sleep(SLEEP_TIME2)    
            bsObj = BeautifulSoup(xml,features='lxml')
            document_xml = bsObj.find('doc')
            
            if document_xml is not None:
                try:
                    document_dict = Parse.xml_to_dictionary(document_xml)
                    print("Updating document: ", new_id)
                    Mongo.replace_doc_to_mongo(document_dict,old_id)
                    Mongo.save_to_mongo_updated_info(document_dict['_id'],'update',document_dict['db'])
                    print("->> Updated!\n")
                    Mongo.delete_document_in_panding_coll(old_id)
                except Exception as e:
                    print("Error (while Mongo.replace_do_to_mongo(document_dict,document_t1['_id'])): ",e)
                    Mongo.save_exception_to_mongo(document_dict['_id'],'Update information from single <doc>',url,str(e))
            else:
                tmp_dict = {'_id' : old_id}
                Mongo.save_dict_to_mongo(tmp_dict,MODE_PANDING)
                print(f"Error: No Document Found: {url}")