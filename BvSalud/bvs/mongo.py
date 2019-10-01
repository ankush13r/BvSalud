#!/usr/bin/env python
from constant import *
from datetime import datetime
from pymongo import MongoClient


f"""**MongoDB**:

    .. warning:: MongoDb must be running. Otherwise it will give you an error. 
    .. note:: MongoDB  is initialized just by calling the module *parse_xml_new_and_update*.

    +----------------+-------------------------------------------+
    |   Data base    |                Collection                 |
    +================+===========================================+
    | {DATA_BASE}    | {COLLECTION_ALL}                          |
    +                +-------------------------------------------+
    |                | {COLLECTIONS_NONE_INDEXED_T1}             |
    +                +-------------------------------------------+
    |                | {COLLECTIONS_NONE_INDEXED_T2}             |
    |                +-------------------------------------------+
    |                | {COLLECTION_UPDATE_INFO}                  |
    |                +-------------------------------------------+
    |                | {COLLECTION_ERRORS}                       |
    +----------------+-------------------------------------------+    

"""

client = MongoClient('localhost:27017')
db = client[DATA_BASE]
collection_all = db[COLLECTION_ALL]
collection_None_Indexed_t1 =db[COLLECTIONS_NONE_INDEXED_T1]
collection_None_Indexed_t2 =db[COLLECTIONS_NONE_INDEXED_T2]
collection_Update_info = db[COLLECTION_UPDATE_INFO]
collection_pending_docs = db[COLLECTION_PENDING]
errors = db[COLLECTION_ERRORS]

class Mongo:

    def get_all_ids_list(collection):
        f"""The method make a list of all articles from the collection that recives as parameter.
        The Data Base is already defined as ({DATA_BASE}).
        :param collection: Name of the collection like ({COLLECTION_ALL}).
        :type collection: string
        :return: List [id,id,id,...]        
        """
   
        all_ids =  db[collection].find({},{"_id":1})
        ids_list=[]
        for item in all_ids:
            ids_list.append(item['_id'])

        return ids_list
    def delete_document_in_pending_coll(doc_id):
        """The method delete document in the pending collection. 
        :param doc_id: ID of the article.
        :type doc_id: String ('lil:23434')
        :return doc_id: Boolean if all correct.(True)
        """
        collection_pending_docs.delete_one({'_id':doc_id})
        return True

    def replace_doc_to_mongo(new_document_dict,old_id):
        """The method replace old document by a new. First it deletes old document and after save the new one. And nothing returns.
        :param new_document_dict: Recives a dictionary of new document.
        :type new_document_dict: Dict (dictionary)
        :param old_id: Recives a old_id of document to modify the document with the new one.
        :type old_id: String ('lil:23434')
         
        """
        print(f"Replacing Document: {old_id} <<>> {new_document_dict['_id']} ")
        old_document =  collection_all.find_one({"_id":old_id}) 
        new_document_dict['parsing_update_date'] = datetime.utcnow()
        if old_document is not None:
            try:
                new_document_dict['selected'] = old_document['selected']
                print("\t:: Was selected for test Set.")
            except:
                print("\t:: Wasn't selected for test Set.")
            new_document_dict['entry_date'] = old_document['entry_date']
            new_document_dict['parsing_entry_date'] = old_document['parsing_entry_date']
        else:
            print("Error: No document found in mongo: while replacing, id: ",old_id)
        try:
            collection_all.delete_one({'_id':old_id})
        except Exception as err:
            print("Error while replace_doc_to_mongo mongo.py: ", err)
        collection_all.insert_one(new_document_dict)

    def save_exception_to_mongo(id,type_error,detail_error,exception):
        """The method save errors into the collection errors. It receives id, type_error, detail_error and exception as parameters.
        :param id: Article ID.
        :type id: String ('lil:2343')
        :param type_error: Receives a string.
        :type type_error: String.
        :param detail_error: Full detail of error like when it has been occurred, ...
        :type detail_error: String
        :param exception: Any Exception occurred.
        :type exception: String
        """
        errors.insert_one(dict(date_time=datetime.utcnow(),
                        doc_id=id,
                        type_error=type_error,
                        detail_error=detail_error,
                        exception_str=str(exception)))           

    def get_document(collection,id):
        """Method to find a document from a collection. It receives the collection's name and a id to find the document.
        :param collection: The name of collection. 
        :type collection: String
        :param id: The article id.
        :type id: String ('lil:23432')
        :return: Dict (Article in format json/dict)
        """
        document =  db[collection].find_one({"_id":id})  
        return document

    def save_dict_to_mongo(document_dict, condition=None):
        if condition != MODE_PENDING:
            try:
                entry_date = int((document_dict['entry_date']).strftime("%Y"))
            except:
                entry_date = None
        try:
            if condition == MODE_NEW and  document_dict['mh'] is None:
                collection_None_Indexed_t2.insert_one(document_dict)
            elif condition == MODE_ALL:
                collection_all.insert_one(document_dict)
                if entry_date in YEARS and document_dict['mh'] is None:
                    collection_None_Indexed_t1.insert_one(document_dict)
            elif condition == MODE_INDEXED:
                collection_all.insert_one(document_dict)
            elif condition == MODE_PENDING:
                collection_pending_docs.insert_one(document_dict)
        except Exception as e:
            Mongo.save_exception_to_mongo(document_dict['_id'],'Saving one <doc> from single XML file, in mode: ',condition,document_dict['_id'],str(e))                         

    def save_to_mongo_updated_info(id,type,db):

        date = datetime.utcnow()
        dictionary = dict({'id':id,'type':type,'db':db,'parsing_date':date}) 
        collection_Update_info.insert_one(dictionary)

   
    def change_collections_name(data_base,old_name,new_name):
        """It changes the name of a collaction if the target name is exist than it will delete that collaction.
    (Ex: vs.training_collection_old  -> vs.training_collection_new). 

    :param old_name: The collection's name which will be changed by a new one.
    :type: strint
    :param new_name: A new name for the collection. 
    :returns: Nothing to return     

    .. warning:: Please do not pass new_name same as old_name, those must be diffrent.
    """
        old_colletion = f"{data_base}.{old_name}"
        new_colletion = f"{data_base}.{new_name}"
        try:
            client.admin.command("renameCollection", old_colletion, to = new_colletion,dropTarget=True)
        except:
            pass
