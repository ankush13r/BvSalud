import json, os,shutil
from constant import  * 
import math,time
from bs4 import BeautifulSoup
from io import open
from datetime import datetime
from urllib.request import urlopen, urlretrieve
import socket
import urllib
from socket import timeout

socket.setdefaulttimeout(TIMEOUT_URL1)

class Crawl:
    """Crawl is a class with **__init__** option. To use it you must instance the class and it receives 4 arguments. 
    All method of this class are callable for the objects instanced by this class (Crawl)
        
    """
    def __init__(self,mode,super_directory,sub_directory,per_page=int(500)):
        """Method __init__ containt mode, base_url, total_record, super_directory, path_to_crawler, per_page, num_pages. And also make the super directory unless exists. 

        :param mode: To define the mode for Crawl (all or new), all is for download all articles, 
        new for new articles (in this case none indexed)
        :type mode: string
        :param super_directory: To define a super folder for all downloads of articles.
        :type super_directory: string
        :param sub_directory: To define a sub folder for downloads.   
        :type sub_directory: string
        :param per_page: (default =500) To define number of document by each file that will be download.
        :type per_page: string
        """
        self.mode = mode
        self.base_url = self.get_base_url(mode)
        self.total_record = self.get_records_num()
        self.super_directory = super_directory
        self.path_to_crawler = os.path.join(self.super_directory,sub_directory)
        self.per_page = int(per_page)
        self.path_to_url = TMP_URL_PATH
        self.num_pages = int(math.ceil(self.total_record/self.per_page))
        if not os.path.isdir(super_directory):
            os.mkdir(super_directory)
    
    def get_base_url(self,type):
        """ Method to get base url to download article. All types are saved in a file with json format. If you need you can modify it (json file).

        :param type: To define the type of url, than it can find a url from the json file and args are (ibecs,lilacs,none_indexed_ibecs,none_indexed_lilacs,all,new, url_for_id).
        :type type: string
        :return: url (string)
        """
        json_data = open(PATH_URL_JSON,"r")
        base_dictionary = json.load(json_data)
        try:
            return base_dictionary[type]
        except:
            print("Error :Wrong data type.\t")

    def get_records_num(self):
        """Method to get total record number depending on article type (url). The method is callable by a object instanced by Crawl (class).
        But receives nothing just self that will be the object.
    
        :returns: Integer (number of records)
        """
        url = self.make_url(1,3,1)
        try:
            xml_content = urlopen(url)
        except:
            print('Timeout Error')
            return 1
        bsObj = BeautifulSoup(xml_content.read(),'lxml')
        try:
            xml_data = bsObj.find(attrs = {'name' :'response'})
            total_records = int(xml_data["numfound"])
            return total_records
        except:
            print("Couldn't find any record, maybe url is wrong")

    def make_url(self,start_record,page, per_page = None):
        """ Method to make by base url to download article. It makes a url for with some conditions passed as argument. 
        By default per page is None, and if it's None than it will get it from self.per_page, defined before in the object instanced.

        :param start_record: Documents (records/article) are start from the number that receives as start_records.   
        :type start_record: int
        :param page: To define the number of page in the web.
        :type page: int

        :return: url (string)
        """
        if per_page is None:
            per_page = self.per_page
        final_url = self.base_url+f'from={start_record}&count={per_page}&page={page}'
        return final_url

    def save_all_urls_list(self):
        """The method make a list of all urls for downloading documents. And the list of urls will be saved into a text file.
        
        :return: list (list of urls)        
        """
        list_all_urls = [(self.make_url(((self.per_page*i)+1),(i)+1)) for i in range(self.num_pages)] 
        print("\nSaving urls")
        with open(self.path_to_url, 'w') as file:
            for url in list_all_urls:
                file.write(url+'\n')
        print("Saved all urls > ",os.getcwd(), self.path_to_url, "\n")
        return list_all_urls

    def __str__(self):
        return (f"Document type:\t\t{self.mode}\nTotal records:\t\t{self.total_record}\nPath to save xml:\t{self.path_to_crawler }\nPer page count:\t\t{self.per_page}\nTotal Pages:\t\t{self.num_pages}")

    def save_records(self,starting_page = 0):
        """Method to download all document in xml format. It downloads all documents and saves into a folder defind by user. Ex: (super_directory/type/sub_directory/....).
        First of all it calls the method make_url and get the list of urls. But if user restart to finish last stopped , it will find urls from the folder. 
        After all it will download all documents and save, one by one.

        :param starting_page: A number to start urls_list. If number is 10 than list will start from position 10. Ex: (list[10:]). And it must be less than number of urls.
        :type starting_page: int 
        
        """
        try:
            num_page = int(starting_page)
        except:
            print("Starting page position is incompatible: ", starting_page)
            num_page = 0
            print("It will start by ", num_page)

        print("\n----------Saving Records------------\n")
        
        if starting_page == 0:
            list_urls= self.save_all_urls_list()
            if not os.path.isdir(self.path_to_crawler):
                os.mkdir(self.path_to_crawler)
            else:
                shutil.rmtree(self.path_to_crawler)
                os.mkdir(self.path_to_crawler)
        else:
            print("Restarting last downloading from", starting_page)
            try:
                with open(self.path_to_url,"r") as file:
                    print("Reading urls file.")
                    list_urls = file.readlines()
                if len(list_urls) != self.num_pages:
                    print("Length of last urls didn't match.")
                    print("Making all urls.")
                    list_urls = self.save_all_urls_list()
            except:
                print("Making all urls.")
                list_urls = self.save_all_urls_list()

        while num_page < self.num_pages:
            print(num_page ," >> Downloading")
            with open(PATH_TO_LAST_RECORD,"w") as file:
                file.write(str(num_page) + " " + CASE_DOWNLOAD + " " + str(self.path_to_crawler) + " "+ str(self.mode))
            destine = os.path.join(self.path_to_crawler,str(num_page)+".xml")
            count = 0
            while True and count < 3:
                try:
                    urlretrieve(list_urls[num_page],destine)
                    break
                except Exception as err:
                    count = count+1
                    print(count,") Error: ",err)
                    print("Sleeping: ",SLEEP_TIME1,"seconds")
                    time.sleep(SLEEP_TIME1)
            print("\tFinished downloading\n")          
            if num_page == (self.num_pages -1):  
                print("Saved all records in ",self.path_to_crawler)
                with open(PATH_TO_LAST_RECORD,"w") as file:
                    file.write("0 saving "+ str(self.path_to_crawler)+" "+ str(self.mode))      
            num_page = num_page+1
            time.sleep(30)



