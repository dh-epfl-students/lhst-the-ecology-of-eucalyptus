import pandas as pd
import re
import spacy

nlp = spacy.load('fr_core_news_sm')
name_db = pd.read_csv("data/nat2022.csv", sep=";", encoding='utf-8')
name_db = list(set(name_db["preusuel"].str.lower().to_list()))

"""
TODO

There are sometimes information about the date but not in the form of d{4} --> get it instead of 'None'
Ex:18..
"""
def clean_date(unclean_date):

    p = re.compile(r"\d{4}")
    m = re.findall(p,unclean_date)


    if len(m) == 0:
        return None
    else:
        return m[0]

"""
TODO

Examples of failed titles:
- Le Figaro. Supplément littéraire du dimanche
- Tunis-journal. Journal politique, littéraire, scientifique, agricole et commercial. Organe des intérêts français en Tunisie...
- Dictionnaire encyclopédique des sciences médicales. Quatrième série, F-K. Tome cinquième, FRAN-FRAN
"""
def clean_title(unclean_title):
    cleaner_title = unclean_title.split(" / ")[0]
    cleaner_title = cleaner_title.split(" [")[0]
    cleaner_title = cleaner_title.split(", par")[0]
    cleaner_title = cleaner_title.split(" :")[0]

    return str(cleaner_title).strip()

def clean_author(unclean_author):
    author = {
        "author_name_clean": None,
        "author_birth_clean": None,
        "author_death_clean": None,
        "author_type_clean": None
    }

    if str(unclean_author) != "nan":
        cleaned_author = unclean_author.split(". Auteur")[0]

        p = re.compile(r"(.+) \((\d{2,4}.{0,2})-(\d{2,4}.{0,2})\)")
        m = re.match(p,cleaned_author)
        if m != None:
            author["author_name_clean"] = m.groups()[0]
            author["author_birth_clean"] = m.groups()[1]
            author["author_death_clean"] = m.groups()[2]
        else:
            author["author_name_clean"] = str(cleaned_author)

        #check if author is person or entity:
        #checks if it's an agency (entity) --> if spacy detects it as a person
        #--> if there is a name from a french database in the author name
        # if not --> entity
        doc = nlp(author["author_name_clean"])
        entities = [ent.label_ for ent in doc.ents]
        if "agence" in author["author_name_clean"].lower() or "Tattersall français" in author["author_name_clean"]:
            author["author_type_clean"] = "entity"
        elif "PER" in entities:
            author["author_type_clean"] = "person"
        elif "(dr)" in author["author_name_clean"].lower() or any(str(token).lower() in name_db for token in doc.ents):
            author["author_type_clean"] = "person"
        else:
            author["author_type_clean"] = "entity"

    return pd.Series(author)
    

def clean_publisher(unclean_publisher):
    publisher = {
        "publisher_name_clean": "[s.n.]",
        "publisher_place_clean": None
    }

    if str(unclean_publisher) != "nan":
        p = re.compile(r"(.*)\((.+)\)")
        m = re.match(p,unclean_publisher)


        if m == None and unclean_publisher != "":
            publisher["publisher_name_clean"] = unclean_publisher

        if m != None:
            #Harmonize [s.n.] notations and write publisher name
            if m.groups()[0].strip() != "" and m.groups()[0].strip() != "[s.n.?]" and m.groups()[0].strip() != "[s. n.]":
                publisher["publisher_name_clean"] = m.groups()[0].strip()
            
            #No need to check for Constantinople / Istanboul (all instances say Constantinople)
            publisher["publisher_place_clean"] = m.groups()[1].strip()

    return pd.Series(publisher)

def clean_type(unclean_type):
    if unclean_type.strip() == "printed monograph":
        return unclean_type.strip()
    
    if unclean_type.strip() == "printed serial":
        return unclean_type.strip()
    
    if unclean_type.strip() == "monographie imprimée":
        return "printed monograph"
    
    if unclean_type.strip() == "manuscrit":
        return "manuscript"


def metadata_cleaner(path):
    print("Reading csv ...")
    df = pd.read_csv(path)
    print("Loaded csv")
    df = df.drop_duplicates()
    print("Cleaning dates ...")
    df['date_clean'] = df['date'].apply(clean_date)
    print("Dates cleaned\nCleaning titles ...")
    df['title_clean'] = df['title'].apply(clean_title)
    print("Titles cleaned\nCleaning authors ...")
    df = pd.concat([df, df['author'].apply(clean_author)], axis=1)
    print("Authors cleaned\nCleaning publishers ...")
    df = pd.concat([df, df['publisher'].apply(clean_publisher)], axis=1)
    print("Publishers cleaned\nCleaning types ...")
    df['type_clean'] = df['type'].apply(clean_type)
    print("Types cleaned\nSaving csv ...")

    df = df[['ark', 'title_clean', 'date_clean', 'author_name_clean', "author_type_clean", 'author_birth_clean', 'author_death_clean', "publisher_name_clean", "publisher_place_clean", "type_clean", "format", "description", "type", "source", "language", "title", "author", "date", "publisher"]]
    df.to_csv("data/document_data_clean.csv", index=False)
    print("csv saved")

if __name__ == "__main__":
    path = "data/document_data.csv"
    metadata_cleaner(path)