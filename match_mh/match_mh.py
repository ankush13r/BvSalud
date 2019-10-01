

import csv
from collections import defaultdict
import ast
import json

def read_csv(csv_path):
    documents_list = []
    
    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file,delimiter='|')
        for  row in csv_reader:
            try:
                int(row[0])
                documents_list.append(row)
            except:
                pass
    return documents_list



def get_list_dict_by_code(list_documents):
    matching_code = 0
    documents_list_dict_by_match_code = defaultdict(list)
    for row in list_documents:
        documents_list_dict_by_match_code[row[0]].append(row)
    return documents_list_dict_by_match_code



def compare_headers(documents_list_dict_by_code):
    output_file = open("matched_mh_list.json","w")
    output_file.write('{"articles":[')
    count_coma = 0
    for i, list_documents_matched in enumerate(documents_list_dict_by_code.values()):
        print(i)
        
        matched_dict_list= list()
        for x, documents_1 in enumerate(list_documents_matched):
            
            j = x + 1
            while j < len(list_documents_matched):
                documents_2 = list_documents_matched[j]
                meSH1 = documents_1[7]
                meSH2 = documents_2[7]
                if len(meSH1) != 0 or len(meSH2) != 0:
                    
                    meSH1_list = list(set(meSH1.replace("'","").strip("][").split(', ')))
                    meSH2_list = list(set(meSH2.replace("'","").strip("][").split(', ')))
                    meSH_joined_list = meSH1_list + meSH2_list

                    full_length = len(meSH_joined_list)
                    distinc_length = len(set(meSH_joined_list))
                    matched_length = full_length - distinc_length
                    
                    if matched_length != 0 and (distinc_length != matched_length):
                        matched_mh_dict = {"id_1":documents_1[1],"id_2":documents_2[1],"mh_1":meSH1_list,"mh_2":meSH2_list,
                                    "matched_mh":matched_length,"total_mh":distinc_length,"prediction:":(str(matched_length)+ "/" + str(distinc_length)),"percentage":round((matched_length/distinc_length)*100,1)}
                        matched_dict_list.append(matched_mh_dict)
                j = j +1
        if len(matched_dict_list) > 0 :
            if count_coma > 0:
                output_file.write(",")
            count_coma = count_coma + 1
            dictionary_equal_Abstract = {"documents":matched_dict_list}
            json_dict = json.dumps(dictionary_equal_Abstract, indent=4,ensure_ascii=False)
            output_file.write(json_dict)
            
            
    output_file.write("]}")
    output_file.close()

documents_list = read_csv("duplicate_articles.csv")
documents_list_dict_by_code = get_list_dict_by_code(documents_list)
compare_headers(documents_list_dict_by_code)