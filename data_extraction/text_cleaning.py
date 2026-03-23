from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from utils import safe_cast

list_2_char_words = ["au", "ce", "ca", "ci", "de", "du", "en", "et", "eu", "ex", "il", "in", "la", "le", "me", "ne", "ni", "nu", "oc", "or", "on", "sa", "ta", "si", "te", "tu", "un", "us", "ut", "va", "vs", "vu"] 


def count_special_char(string):
    spec_char_counter = 0
    for c in string:
        if not c.isalpha() and not c.isdigit() and not c == " ":
            spec_char_counter += 1
    return spec_char_counter

def clean_text(ark, eucalyptus_only=False, write_ocr=False):
    with open(f"data/documents/{ark}.html", "r", encoding="utf-8") as f:
        xml_file = BeautifulSoup(f, "lxml")
    
    #Parse through xml file. Keep only text after a certain "flag" (hr). Keep paragraph structure
    body = xml_file.find("body")
    full_text = []
    keep_text = False
    for child in body.children:
        if keep_text and child.name == "p":
            paragraph_text = child.get_text(separator=" ",strip=True)
            if paragraph_text != "":
                full_text.append(paragraph_text)
        if child.name == "hr" and keep_text == False:
            keep_text = True

    """ #TODO: remove (vérif)
    with open(f"data/corpus_txt/{document[:-5]}_pre.txt", "w", encoding="utf-8") as f:
        testtext = "\n\n".join(full_text)
        f.write(testtext) """


    #"Old" OCR Postprocessing
    threshold = 0.25
    for paragraph in full_text[:]:
        #TODO: find the context better
        if eucalyptus_only == True and "eucalypt" not in paragraph.lower():
            full_text.remove(paragraph)
            continue

        #Remove unwanted paragraphs (paragraphs with more than 20% special characters)
        if count_special_char(paragraph) / len(paragraph) > threshold:
            full_text.remove(paragraph)
            continue
        
        #Remove unwanted paragraphrs (paragraphs with les than 3 chars, sauf si propositions données)
        if len(paragraph) <= 2 and paragraph.lower() not in list_2_char_words:
            full_text.remove(paragraph)
            continue

    full_text = "\n".join(full_text)

    if eucalyptus_only:
        with open(f"data/corpus_eucalyptus_only/{ark}.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
    else:
        with open(f"data/corpus_txt/{ark}.txt", "w", encoding="utf-8") as f:
            f.write(full_text)


    # Get gallica's OCR estimation
    if write_ocr:
        df_filtered = pd.read_csv("data/document_data_clean_filtered.csv", encoding='utf-8')

        full_text = xml_file.get_text()
        ocr_estimation = full_text.split('%.', 1)[0][-3:].strip()
        

        #TODO handle case where it is not in the list
        if document in df_filtered["ark"].to_list():
            df_filtered.loc[df_filtered['ark'] == ark, "ocr_quality"] = safe_cast(ocr_estimation, int)

        df_filtered.to_csv("data/document_data_clean_filtered.csv", encoding='utf-8', index=False)


if __name__ == "__main__":

    documents_downloaded = os.listdir("data/documents")
    documents_downloaded = [x.split(".")[0] for x in documents_downloaded]
    print(f"Documents downloaded: {len(documents_downloaded)}")

    documents_cleaned = os.listdir("data/corpus_txt")
    documents_cleaned = [x.split(".")[0] for x in documents_cleaned]
    print(f"Documents cleaned: {len(documents_cleaned)}")

    documents_to_download = list(set(documents_downloaded) - set(documents_cleaned))
    print(f"Documents to clean: {len(documents_to_download)}")

    counter = len(documents_cleaned)
    for document in documents_to_download:
        clean_text(document, write_ocr=True)
        counter += 1
        
        if counter % 50 == 0:
            print(f"{counter} documents have been cleaned.")

