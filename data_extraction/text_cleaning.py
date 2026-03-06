from bs4 import BeautifulSoup
import re
import os

def count_special_char(string):
    spec_char_counter = 0
    for c in string:
        if not c.isalpha() and not c.isdigit() and not c == " ":
            spec_char_counter += 1
    return spec_char_counter

def clean_text(path):
    with open(path, "r", encoding="utf-8") as f:
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

    #TODO: remove (vérif)
    with open(f"data/corpus_txt/{document[:-5]}_pre.txt", "w", encoding="utf-8") as f:
        testtext = "\n\n".join(full_text)
        f.write(testtext)


    #"Old" OCR Postprocessing
    threshold = 0.25
    list_2_char_words = ["au", "ce", "ca", "ci", "de", "du", "en", "et", "eu", "ex", "il", "in", "la", "le", "me", "ne", "ni", "nu", "oc", "or", "on", "sa", "ta", "si", "te", "tu", "un", "us", "ut", "va", "vs", "vu"] 
    for paragraph in full_text[:]:
        #Remove unwanted paragraphs (paragraphs with more than 20% special characters)
        if count_special_char(paragraph) / len(paragraph) > threshold:
            full_text.remove(paragraph)
            continue
        
        #Remove unwanted paragraphrs (paragraphs with les than 3 chars, sauf si propositions données)
        if len(paragraph) <= 2 and paragraph.lower() not in list_2_char_words:
            full_text.remove(paragraph)
            continue

    full_text = "\n\n".join(full_text)

    with open(f"data/corpus_txt/{document[:-5]}_post.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    #print(body)


    # Get gallica's OCR estimation
    """ full_text = xml_file.get_text()
    ocr_estimation = full_text.split('%.', 1)[0][-2:] """

if __name__ == "__main__":

    documents_downloaded = os.listdir("data/documents")
    for document in documents_downloaded[:2]:
        clean_text(f"data/documents/{document}")
