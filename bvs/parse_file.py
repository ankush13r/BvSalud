from mongo import Mongo
from crawler import Crawl
from constant import *
import os
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
        """Method for obtained article's **id** by **alternate id**. It finds a document by document's *id* or *alternate_id*. 
        The logic of this method is use for find a **id** by **alternate id**.

    :param alternate_id: Article's alternate id. If it's a normal id than it will return the same (Ex: biblio-986217). 
    :type alternate_id: string
    :returns: Article's id.
    :rtype: string (Ex: biblio-1001042)
    """
        base_url = 'http://pesquisa.bvsalud.org/portal/resource/en/'
        url = base_url + alternate_id
        content = urlopen(url)
        bsObj = BeautifulSoup(content,features ='lxml') 
        data_string = (bsObj.find(attrs = {'class' :'data'})).text  #Get the string whose class is data, for extracing the id.
        found_object = re.search(r"(?<=ID:).*",data_string) # Regex For get id from the string
        doc_id = found_object.group().strip()
        time.sleep(5)
        return doc_id  

    def compare_t1_t2(crawl):

        path_url_error = os.path.join(BVSALUD_DOWNLOADS_PATH,"urlsError.txt")
        file = open(path_url_error,'w')

        file.write("No documents in urls")         
        list_ids_t1 = Mongo.get_all_ids_list(COLLECTIONS_NONE_INDEXED_T1)
        list_ids_t2 = Mongo.get_all_ids_list(COLLECTIONS_NONE_INDEXED_T2)

        list_new_ids  = list(set(list_ids_t2) - set(list_ids_t1))
        list_modified_ids  = list(set(list_ids_t1) - set(list_ids_t2))

        print("\nNew records: ",len(list_new_ids),"\n")

        for id in list_new_ids:
            document_t2 = Mongo.get_document(COLLECTIONS_NONE_INDEXED_T2,id)
            try:
                print("New Document <<",document_t2['_id'],">>\tmh: ",document_t2['mh'])
                print()
                Mongo.save_dict_to_mongo(document_t2,MODE_ALL)
                Mongo.save_to_mongo_updated_info(id,'new',document_t2['db'])                                                        
            except (TypeError, AttributeError) as e:
                Mongo.save_exception_to_mongo(id,'Saveing new none indexed document into mongo',id, str(e))

        print("\nRecords to modify: ",len(list_modified_ids),"\n")
        for id in list_modified_ids:
            document_t1 = Mongo.get_document(COLLECTIONS_NONE_INDEXED_T1,id)
            
            print("\nDocument to modify: ",document_t1['_id'])
            if document_t1['db'] == 'IBECS':
                doc_id = Parse.find_id_by_alternate_id(id)                
            else:
                doc_id = id
            base_url = crawl.get_base_url("url_for_id")
            url = base_url + doc_id
            while True:
                try:
                    xml = urlopen(url)
                    time.sleep(2)
                    break
                except Exception as err:
                    print("Error: ",err)
                    time.sleep(90)    
            bsObj = BeautifulSoup(xml,features='lxml')
            document_xml = bsObj.find('doc')
            
            if document_xml is not None:
                try:
                    document_dict = Parse.xml_to_dictionary(document_xml)
                    print("Updating document: ", doc_id)
                    Mongo.update_modified(doc_id, document_dict['_id'],document_dict['alternate_id'],document_dict['mh'],document_dict['sh'])
                    Mongo.save_to_mongo_updated_info(document_dict['_id'],'update',document_dict['db'])
                    print("Updated\n")
                except Exception as e:
                    print("Error: ",e)
                    Mongo.save_exception_to_mongo(document_dict['_id'],'Update information from single <doc>',url,str(e))
            else:
                try:
                    print("Error: << id >> {url}")
                    file.write("\n"+url)
                except: pass
        file.close()
        return True              
