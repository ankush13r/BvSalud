import os

path_home = os.environ.get('HOME')
BVSALUD_DOWNLOADS_PATH = os.path.join(path_home,"bvSalud_downloads")

if not os.path.isdir(BVSALUD_DOWNLOADS_PATH):
    os.mkdir(BVSALUD_DOWNLOADS_PATH)

PATH_TO_LAST_RECORD = "bvs/data/last_record.txt"
PATH_TO_SAVE_ALL = os.path.join(BVSALUD_DOWNLOADS_PATH,"crawlers_all/")
PATH_TO_SAVE_NONE_INDEXED = os.path.join(BVSALUD_DOWNLOADS_PATH,"crawlers_none_indexed/")
CASE_SAVE = "saving"
CASE_DOWNLOAD = "download"
MODE_COMPARE = "new"
MODE_ALL = "all"
MODE_NEW = "new"
DATA_BASE = "BvSalud"
COLLECTION_ALL = "all_articles"
COLLECTIONS_NONE_INDEXED_T1 ="none_indexed_t1"
COLLECTIONS_NONE_INDEXED_T2 = "none_indexed_t2"
COLLECTION_UPDATE_INFO = "Update_info"
COLLECTION_ERRORS = "errors"
YEARS = [2018,2019]
PATH_URL_JSON = "bvs/data/baseUrl.json"
