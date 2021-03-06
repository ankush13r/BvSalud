

import csv
from collections import defaultdict
import ast
import json
import argparse
import os

def read_csv(csv_path):
    documents_list = []
    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file,delimiter='\t')
        for  row in csv_reader:
            try:
                int(row[0])
                documents_list.append(row)
            except:
                pass
    return documents_list


def get_list_dict_by_code(list_documents):
    matching_code = 0
    documents_list_dict_by_match_code = defaultdict(list) # This methode defaultdict create a dictionary with list inside, so you can append into those list.
    for row in list_documents:
        documents_list_dict_by_match_code[row[0]].append(row)
    return documents_list_dict_by_match_code



def compare_headers(documents_list_dict_by_code,output_path):
    output_file = open(output_path,"w")
    output_file.write('{"articles":[')
    count_coma = 0
    for i, list_documents_matched in enumerate(documents_list_dict_by_code.values()):
        print(i)
        
        matched_dict_list= list()
        for x, documents_1 in enumerate(list_documents_matched):
            
            j = x + 1 # j(second document) is next of i(firstDocument)
            while j < len(list_documents_matched):
                documents_2 = list_documents_matched[j]
                meSH1 = documents_1[7]
                meSH2 = documents_2[7]
                if len(meSH1) != 0 or len(meSH2) != 0:
                    
                    meSH1_list = list(set(meSH1.replace("'","").strip("][").split(', ')))
                    meSH2_list = list(set(meSH2.replace("'","").strip("][").split(', ')))
                    meSH_joined_list = meSH1_list + meSH2_list

                    full_length = len(meSH_joined_list)

                    uniqs_length = len(set(meSH_joined_list))
                    matched_length = full_length - uniqs_length
                    
                    #if matched_length != 0 and (uniqs_length != matched_length):
                    print(">>> matched")
                    matched_mh_dict = {"id_1":documents_1[1],"id_2":documents_2[1],"mh_1":meSH1_list,"mh_2":meSH2_list,
                                "matched_mh":matched_length,"total_mh":uniqs_length,"prediction:":(str(matched_length)+ "/" + str(uniqs_length)),"percentage":round((matched_length/uniqs_length)*100,1)}
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

def main(path_output,path_input):
    documents_list = read_csv(path_input)
    documents_list_dict_by_code = get_list_dict_by_code(documents_list)
    compare_headers(documents_list_dict_by_code,path_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog ='match_mh.py',usage='%(prog)s[-o file.csv]')
    parser.add_argument('-i','--input',metavar='',type=str,required=True, help ='Input file path.')
#    parser.add_argument('-F','--field',metavar='',type=str,required=True, help ='To define field separete character.')

    args = parser.parse_args()
    input = args.input
#    delimiter = args.field

    current_dir = os.getcwd()
    path_input = os.path.join(current_dir,input)
    path_output = (str(path_input) + ".json")
    main(path_output,path_input)
