import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import random
import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='data_extraction/download.log', encoding='utf-8', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')



def single_gallica_download(ark_id, altcha_pass, jsession_id):

    cookies = {
        'JSESSIONID': jsession_id,
        'altcha_pass': altcha_pass,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0',
    }

    response = requests.get(f'https://gallica.bnf.fr/ark:/12148/{ark_id}.texteBrut', cookies=cookies, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # check for bad response
    if response.status_code != 200:
        with open(f"data/error/{ark_id}.html", "w", encoding='utf-8') as f:
            f.write(soup.prettify())
        return str(response.status_code)

    # check for bad captcha
    if "Gallica | Vérification de sécurité" in str(soup):
        with open(f"data/error/{ark_id}.html", "w", encoding='utf-8') as f:
            f.write(soup.prettify())
        return "captcha_error"

    with open(f"data/documents/{ark_id}.html", "w", encoding='utf-8') as f:
        f.write(soup.prettify())

    return "Safe"


def full_gallica_download(document_data_path, altcha_pass, jsession_id, check_if_downloaded=True, randomize_download_order=False, filter=False, time_to_wait=15):

    df_documents = pd.read_csv(document_data_path)

    #remove documents based on filter
    if filter:
        df_author = df_documents.dropna(subset = "author_type_clean")
        df_publisher = df_documents.dropna(subset = "publisher_name_clean")
        df_documents = pd.concat([df_author,df_publisher]).drop_duplicates().reset_index(drop=True)

    
    documents_to_download = df_documents["ark"].to_list()

    total_docs_downloaded = 0
    # remove documents already downloaded
    if check_if_downloaded:
        documents_downloaded = os.listdir("data/documents")
        documents_downloaded = list(set([x.split('.')[0] for x in documents_downloaded]))

        errors_downloaded = os.listdir("data/error")
        errors_downloaded = list(set([x.split('.')[0] for x in errors_downloaded]))

        total_docs_downloaded = len(documents_downloaded)

        documents_to_download = list(set(documents_to_download) - set(documents_downloaded))
        documents_to_download = list(set(documents_to_download) - set(errors_downloaded))

    if randomize_download_order:
        random.shuffle(documents_to_download)

    #download documents
    for doc in documents_to_download:
        log = single_gallica_download(doc, altcha_pass, jsession_id)
        #wait for X seconds in order to not surcharge the server
        time.sleep(time_to_wait)

        if log == "Safe":
            total_docs_downloaded += 1
            logger.info(f"{doc} document sucessfully downloaded ({total_docs_downloaded})")
        elif log == "403":
            logger.error(f"{doc} failed to download. Error {log} (unauthorised document)")
            continue
        elif log == "503":
            logger.error(f"{doc} failed to download. Error {log} (Server temporarily down)")
            time.sleep(600)
            continue
        else:
            logger.error(f"{doc} failed to download. Error {log}")
            print(f"Download failed. Error {log}")
            break
    
    print("All documents have been downloaded")
    logger.info(f"All documents have been downloaded")


if __name__ == "__main__":
    
    data_path = "data/document_data_clean_filtered.csv"
    altcha_pass = '1776569303509.4d286adf.ZIGRL5nMwajKas1YM8-Z05Pj3baDTBcDoe2E0s66pT8'
    jsession_id = "F4792277C4E45A1EC6409B4D8E93ABBF"
    full_gallica_download(data_path, altcha_pass, jsession_id, randomize_download_order=True, filter=True)
