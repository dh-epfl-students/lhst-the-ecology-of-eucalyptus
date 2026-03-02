from bs4 import BeautifulSoup
import re
import os

def clean_text(path):
    with open(path, "r", encoding="utf-8") as f:
        xml_file = BeautifulSoup(f, "lxml")
    
    body = xml_file.find("body")
    full_text = []
    keep_text = False
    for child in body.children:
        if keep_text and child.name == "p":
            full_text.append(child.get_text(separator=" ",strip=True))
        if child.name == "hr" and keep_text == False:
            keep_text = True

    full_text = "\n\n".join(full_text)

    with open(f"data/documents/{document[:-5]}.txt", "w", encoding="utf-8") as f:

        f.write(full_text)
    #print(body)


    # Get gallica's OCR estimation
    """ full_text = xml_file.get_text()
    ocr_estimation = full_text.split('%.', 1)[0][-2:] """

if __name__ == "__main__":

    documents_downloaded = os.listdir("data/documents")
    for document in documents_downloaded:
        clean_text(f"documents/{document}")
