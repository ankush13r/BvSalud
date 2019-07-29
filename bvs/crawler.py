from constant import  * 
import json, os,shutil
import math,time
from bs4 import BeautifulSoup
from io import open
from datetime import datetime
from urllib.request import urlopen, urlretrieve
import socket
import urllib
from socket import timeout

socket.setdefaulttimeout(300)

class Crawl:
    def __init__(self,mode,super_directory,sub_directory,per_page=int(500)):
        self.mode = mode
        self.base_url = self.get_base_url(mode)
        self.total_record = self.get_records_num()
        self.super_directory = super_directory
        self.path_to_crawler = os.path.join(self.super_directory,sub_directory)
        self.per_page = int(per_page)
        self.path_to_url = "bvs/data/tmp_url.txt"
        self.num_pages = int(math.ceil(self.total_record/self.per_page))
        if not os.path.isdir(super_directory):
            os.mkdir(super_directory)
    
    def get_base_url(self,mode):
        json_data = open(PATH_URL_JSON,"r")
        base_dictionary = json.load(json_data)
        try:
            return base_dictionary[mode]
        except:
            print("Error :Wrong data type.\t")

    def get_records_num(self):
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
        if per_page is None:
            per_page = self.per_page
        final_url = self.base_url+f'from={start_record}&count={per_page}&page={page}'
        return final_url

    def save_all_urls_list(self):
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
            
            while True:
                try:
                    urlretrieve(list_urls[num_page],destine)
                    break
                except Exception as err:
                    print("Error: ",err)
                    time.sleep(900)
            print("\tFinished downloading\n")          
            if num_page == (self.num_pages -1):  
                print("Saved all records in ",self.path_to_crawler)
                with open(PATH_TO_LAST_RECORD,"w") as file:
                    file.write("0 saving "+ str(self.path_to_crawler)+" "+ str(self.mode))      
            num_page = num_page+1
            time.sleep(30)



