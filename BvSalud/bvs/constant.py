import os

#path_home = os.environ.get('HOME')
#BVSALUD_DOWNLOADS_PATH = os.path.join(path_home,"bvSalud_downloads")

BVSALUD_DOWNLOADS_PATH = ("/data/MESINESP/bvSalud_downloads")

if not os.path.isdir(BVSALUD_DOWNLOADS_PATH):
    os.mkdir(BVSALUD_DOWNLOADS_PATH)

PATH_TO_LAST_RECORD = "bvs/data/last_record.txt" #File to save last record information.
PATH_TO_SAVE_ALL = os.path.join(BVSALUD_DOWNLOADS_PATH,"crawlers_all/") #Folder where all articles's crawler files will be saved.
PATH_TO_SAVE_NONE_INDEXED = os.path.join(BVSALUD_DOWNLOADS_PATH,"crawlers_none_indexed/")##Folder where None indexed's crawler files will be saved
CASE_SAVE = "saving"
CASE_DOWNLOAD = "download"
MODE_NEW = "new"
MODE_ALL = "all"
MODE_INDEXED = "one"
MODE_COMPARE = "compare"
DATA_BASE = "BvSalud"
COLLECTION_ALL = "all_articles"
COLLECTIONS_NONE_INDEXED_T1 ="none_indexed_t1"
COLLECTIONS_NONE_INDEXED_T2 = "none_indexed_t2"
COLLECTION_UPDATE_INFO = "Update_info"
COLLECTION_PENDING = "pending_documents"
COLLECTION_ERRORS = "errors"
OUTPUT_ERROR = "Error"
MODE_PENDING  = "pending"
YEARS = [2018,2019]
PATH_URL_JSON = "bvs/data/baseUrl.json"
SLEEP_TIME1 = 900 # In seconds
SLEEP_TIME2 = 60 # In seconds
TIMEOUT_URL1 = 300 #In seconds, if the url when downloading, stops working or create any problem 
TMP_URL_PATH = "bvs/data/tmp_url.txt" 