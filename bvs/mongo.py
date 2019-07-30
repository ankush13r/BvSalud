
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
errors = db[COLLECTION_ERRORS]

class Mongo:

    def get_all_ids_list(collection):
   
        all_ids =  db[collection].find({},{"_id":1})
        ids_list=[]
        for item in all_ids:
            ids_list.append(item['_id'])

        return ids_list
    
    def replace_doc_to_mongo(new_document_dict,old_id):
        old_document =  collection_all.find_one({"_id":old_id})  
        new_document_dict['parsing_update_date'] = datetime.utcnow()
        new_document_dict['entry_date'] = old_document['entry_date']
        new_document_dict['parsing_entry_date'] = old_document['parsing_entry_date']


        collection_all.delete_one({'_id':old_id})
        collection_all.insert_one(new_document_dict)


    def save_exception_to_mongo(id,type_error,detail_error,exception):  
        errors.insert_one(dict(date_time=datetime.utcnow(),
                        doc_id=id,
                        type_error=type_error,
                        detail_error=detail_error,
                        exception_str=str(exception)))           

    def get_document(collection,id): 
        document =  db[collection].find_one({"_id":id})  
        return document

    def save_dict_to_mongo(document_dict, condition=None):
        entry_date = int((document_dict['entry_date']).strftime("%Y"))
        try:
            if condition == MODE_NEW and  document_dict['mh'] is None:
                collection_None_Indexed_t2.insert_one(document_dict)
            elif condition == MODE_ALL:
                collection_all.insert_one(document_dict)
                if entry_date in YEARS and document_dict['mh'] is None:
                    collection_None_Indexed_t1.insert_one(document_dict)
            elif condition == MODE_INDEXED:
                collection_all.insert_one(document_dict)

        except Exception as e:
            Mongo.save_exception_to_mongo(document_dict['_id'],'Saving one <doc> from single XML file',document_dict['_id'],str(e))                         

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
