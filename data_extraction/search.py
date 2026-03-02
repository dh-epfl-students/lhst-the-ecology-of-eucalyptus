import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import pandas as pd
from utils import safe_cast
import warnings
import shutil
import os

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def single_search_gallica(query, startRecord, maximumRecord=50):
    """
    Use gallica API to get indexes of documents, based on user query

    Return xml file processed through beautifulsoup4
    """

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'accept': 'application/xml',
    }

    params = {
        'version': '1.2',
        'operation': 'searchRetrieve',
        'query': query,
        'startRecord': startRecord,
        'maximumRecords': maximumRecord,
        'collapsing': 'false'
    }

    response = requests.get('https://gallica.bnf.fr/SRU', params=params, headers=headers)

    soup = BeautifulSoup(response.content, "lxml")


    if not os.path.exists("data/tmp"):
        os.makedirs("data/tmp")

    with open(f"data/tmp/{startRecord}-{startRecord + maximumRecord - 1}.xml", "w", encoding='utf-8') as f:
        f.write(soup.prettify())

    return soup


def full_search_gallica(query, startRecord=1, max_queries=-1, keep_xml=False, keep_previous_data=True):
    """
    Input: CQL query, max_queries

    Loops through all documents and calls "single_search_gallica" and "result_parser" to create a csv file with all relevant 
    documents
    """


    if keep_previous_data == False:
        #Remove all previous xml files
        if os.path.exists("data/tmp"):
            shutil.rmtree("data/tmp")
        #get 1st results
        xml_data = single_search_gallica(query, startRecord)
        result_parser(xml_data, overwrite=True)
    else:
        #get 1st results
        xml_data = single_search_gallica(query, startRecord)
        result_parser(xml_data)

    tot_documents = safe_cast(xml_data.find("srw:numberofrecords").text.strip(), int)
    print(f"Sucessfully recovered [{startRecord} - {min(startRecord + 49, tot_documents)}] documents")
    
    num_queries = 1
    for i in range(startRecord + 50, tot_documents, 50):
        # Stop loop if atteins max queries
        if num_queries == max_queries:
            break

        xml_data = single_search_gallica(query, i)
        result_parser(xml_data)

        print(f"Sucessfully recovered [{i} - {i + 49}] documents")

        num_queries += 1

    if keep_xml == False:
        shutil.rmtree("data/tmp")


def result_parser(xml_result, overwrite=False):
    """
    Input: xml file produced by a gallica search

    Output: csv file with each book as its own line
    """
    books = xml_result.find_all('srw:record')
    books_parsed = []

    for book in books:
        #Create dict template 
        book_parsed = {
            'title': None,
            'author': None,
            'date': None,
            'publisher': None,
            'description': None,
            'type': None,
            'source': None,
            'format': None,
            'ark': None,
            'language': None,
        }

        if book.find("dc:creator"):
            book_parsed['author'] = book.find("dc:creator").text.strip()

        if book.find("dc:date"):
            book_parsed['date'] = book.find("dc:date").text.strip()

        if book.find("dc:language"):
            book_parsed['language'] = book.find("dc:language").text.strip()

        if book.find("dc:format"):
            book_parsed['format'] = book.find("dc:format").text.strip()

        if book.find("dc:publisher"):
            book_parsed['publisher'] = book.find("dc:publisher").text.strip()

        if book.find("dc:source"):
            book_parsed['source'] = book.find("dc:source").text.strip()

        if book.find("dc:title"):
            book_parsed['title'] = book.find("dc:title").text.strip()

        if book.find("dc:type"):
            book_parsed['type'] = book.find("dc:type").text.strip()        #might be more than one, check

        if book.find("dc:identifier"):
            book_parsed['ark'] = book.find("dc:identifier").text.strip()[34:]   #gets all identifier, keep only ark

        if book.find("dc:description"):
            book_parsed['description'] = book.find("dc:description").text.strip()  #might be more than one, check

        books_parsed.append(book_parsed)
    
    if overwrite:
        df = pd.DataFrame(books_parsed)
    else:
        old_df = pd.read_csv("data/document_data.csv")
        new_df = pd.DataFrame(books_parsed)
        df = pd.concat([old_df, new_df], axis=0)

    # Saving to CSV
    df.to_csv('data/document_data.csv', index=False)


if __name__ == "__main__":

    query = 'gallica all "Eucalyptus" and dc.date <= "1920" and dc.type any "monographie fascicule manuscrit" and dc.language any "fre frd" sortby dc.date/sort.ascending'

    full_search_gallica(query, startRecord=27051, keep_xml=True)
