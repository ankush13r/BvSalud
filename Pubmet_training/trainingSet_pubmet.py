from bs4 import BeautifulSoup



def extract_data(bsObj):
    children = list(bsObj.children)
    children2 = list(children[0].children)
    print(children2[0])


def xml_to_json(xml_content):

    bsObj = BeautifulSoup(xml_content,'html.parser')
    extract_data(bsObj)       

def read_xml(path):
    file = open(path)
    xml_content = file.read()
    xml_to_json(xml_content)



read_xml("../../pubmet_doc.xml")