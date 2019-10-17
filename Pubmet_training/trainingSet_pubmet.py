import json
import argparse
import time

from bs4 import BeautifulSoup

from translator import opennmt_caller as tr
from nltk import sent_tokenize



def translate_text(sentence:str):
    """This method is to convert a sentence's language english to spanish.
    
    :param sentence: A sentence in format String. (lang:en)
    :type sentence: str
    :return: A sentence in format String. (lang:es)
    :rtype: str
    """
    sentences_tokenize_list = sent_tokenize(sentence)

    sentence_list_es = []
    for text_en in sentences_tokenize_list:
        print("translating....")
        response = tr.translate_sentence("en","es",text_en)
        text_es = response.json()[0][0].get('tgt')
        sentence_list_es.append(text_es)

    sentence_join = ' '.join(sentence_list_es)
    return sentence_join
 


def extract_data_in_json(articles_xml_list:list,output_path:str):
    """The method extract some xml data and convert it into json format file. After all json articles are saved in a file.
    
    :param articles_xml_list: A list of all articles.
    :type articles_xml_list: list
    :param output_path: [description]
    :type output_path: str
    """
    output_file = open(output_path,"w")
    output_file.write('{"articlesSet":[')

    total_articles = len(articles_xml_list) # length  of all articles.
    i = 0;
    write_coma = False # A boolean variable to control, when to write coma after article.
    for  article in articles_xml_list:
        print(total_articles-i) #printing article number descending order
        i += 1 
        bsObj = BeautifulSoup(article,'html.parser')
        abstract_obj = bsObj.find("abstract")


        id = bsObj.find("pmid").text
        title_obj = bsObj.find("title")
        if title_obj: #If title_obj dosn't exist, it will continue to next for. It will for get all next steps.
            title = title_obj.text
        else:
            print("Tittle is none",id)
            title = None
        
        keywords_cursor = bsObj.find_all("keyword")
        meshMajor = []
        if not keywords_cursor:
            continue
        for keyword in keywords_cursor:
            meshMajor.append(keyword.text)

        if abstract_obj:    #If abstract_obj dosn't exist, it will continue to next for. It will for get all next steps.
            abstract_en = abstract_obj.text
            abstract_es = translate_text(abstract_en)
            #abstract_es = abstract_en
        else:
            continue

        dateRevised = bsObj.find("daterevised")
        if dateRevised: #If dateRevised dosn't exist, it will try to find pubDate.
            date = dateRevised.text
        else:
            pubDate = bsObj.find("pubdate")
            if pubDate: 
                date = pubDate.text
            else: #If pubDate doesn't exist then date will be none.
                date = None

        if date: # If the date was found then it will get just year from date. Otherwise it year value will be none. 
            year = ','.join(date.split()[0])
        else:
            year = None

        medlineTA_journal_obj =  bsObj.find("medlineta")
        if medlineTA_journal_obj:#If medlineTA_journal_obj exists, medlineTA_journal will get the value from it.Otherwise medlineTA_journal will have none value.
            medlineTA_journal = medlineTA_journal_obj.text
        else:
            medlineTA_journal = None
            print("Journal None", id)
        
        nlmUniqueID_journal_obj = bsObj.find("nlmuniqueid") 
        if nlmUniqueID_journal_obj: #If nlmUniqueID_journal_obj exists, nlmUniqueID_journal will get value from it.Otherwise nlmUniqueID_journal will have none value.
            nlmUniqueID_journal =nlmUniqueID_journal_obj.text
        else:
            nlmUniqueID_journal = None
            print("journal id none",id)
        
        
        journal = {"medlineta":medlineTA_journal,"nlmUniqueid":nlmUniqueID_journal}    


        article_dict = {"article":{"journal":journal,"title":title,"pmid":id,"meshMajor":meshMajor,"year":year,"abstractText":abstract_es}}
        json_dict = json.dumps(article_dict,indent=4, ensure_ascii=False)
        if write_coma :
            output_file.write(",")
        output_file.write(json_dict)
        write_coma = True

    output_file.write("]}")
    output_file.close 

def get_list_of_articles(input_path:str):
    """The method split a xml file by /n/n/n and create a list of articles. After it returns a list of articles created.
    
    :param input_path: A paht to get input file.
    :type input_path: str
    :return: List of all articles
    :rtype: List
    """
    file = open(input_path)
    xml_content = file.read()
    xml_content_splited = xml_content.split("\n\n\n")
    file.close
    return (xml_content_splited)

def main(input_path:str, output_path:str):
    """The main method, it recives input file path and output file path. All other method all called by it.
    
    :param input_path: Root for input file.
    :type input_path: str
    :param output_path: Root for output file.
    :type output_path: str
    """
    
    articles_xml_list = get_list_of_articles(input_path)
    extract_data_in_json(articles_xml_list,output_path)

if __name__ == "__main__":   
    
    parser = argparse.ArgumentParser(prog ='trainingSet_pubmed.py',usage='%(prog)s [-i input_file.xml] [-o outPut_file.json]')
    parser.add_argument('-i','--input',metavar='',type=str,required=True, help ='To define a path for input file.')     
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a path for output file.')  
   
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    main(input_path,output_path)
    # current_dir = os.getcwd()
    # path = os.path.join(current_dir,output)

    
