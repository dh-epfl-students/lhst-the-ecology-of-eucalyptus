import pandas as pd
import re
import spacy
import numpy as np

nlp = spacy.load('fr_core_news_sm')
name_db = pd.read_csv("data/other/nat2022.csv", sep=";", encoding='utf-8')
name_db = list(set(name_db["preusuel"].str.lower().to_list()))

with open("data/other/presse_generaliste.txt", encoding='utf-8') as f:
    presse_quotidienne = f.readlines()
    presse_quotidienne = list(set([presse.strip() for presse in presse_quotidienne]))

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

    # Is this pertinent?
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

        p = re.compile(r"(.+) \((\d{0,4}.{0,4})-(\d{0,4}.{0,4})\)")
        m = re.match(p,cleaned_author)
        if m != None:
            author["author_name_clean"] = m.groups()[0]

            #Discard "unclean" dates (such as 18..)
            clean_date_regex = re.compile(r"\d{4}")
            birth_date = re.findall(clean_date_regex, m.groups()[1])
            if len(birth_date) != 0:
                author["author_birth_clean"] = birth_date[0]
            death_date = re.findall(clean_date_regex, m.groups()[2])
            if len(death_date) != 0:
                author["author_death_clean"] = death_date[0]
                
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
        "publisher_name_clean": None,
        "publisher_place_clean": None
    }

    if str(unclean_publisher) != "nan":
        p = re.compile(r"(.*)\((.+)\)")
        m = re.match(p,unclean_publisher)


        if m == None and unclean_publisher != "":
            publisher["publisher_name_clean"] = unclean_publisher

        if m != None:
            #Harmonize [s.n.] notations and write publisher name
            pub_name = m.groups()[0].strip()
            if pub_name != "" and pub_name != "[s.n.?]" and pub_name != "[s. n.]" and pub_name != "[s.n.]" and pub_name != "[s.n]":
                publisher["publisher_name_clean"] = pub_name
            
            #No need to check for Constantinople / Istanboul (all instances say Constantinople)
            publisher["publisher_place_clean"] = m.groups()[1].strip()

    return pd.Series(publisher)

def clean_type(unclean_type, title):
    #check for monographies
    if unclean_type.strip() == "printed monograph" or unclean_type.strip() == "manuscrit" or unclean_type.strip() == "monographie imprimée":
        return "monographie"
    
    #Return more precise information if printed serial based on title
    #check for "annuaires":
    if "annuaire" in title.lower():
        return "annuaire"
    
    #Check for médical / specialised key words
    specialized_word_list = ["médecin", "médic", "académie", "mycologique", "cosmos"]
    for word in specialized_word_list:
        if word.lower() in title.lower():
            return "presse spécialisée"
    
    #check if in journal database
    for presse in presse_quotidienne:
        if presse.lower() in title.lower():
            return "presse généraliste"
    
    #Check if "official" publication (from governments)
    official_word_list = ["comité de madagascar", "actes administratifs", "budget", "procès-verbaux", "comité de l'afrique française", "comité de l'asie française", "régence", "république", "ministère", "chambre des députés", "préfecture", "gouvernement", "président", "assemblée", "officiel", "conseil général", "session", "projets de lois"]
    for word in official_word_list:
        if word.lower() in title.lower():
            return "presse officielle"

    #Check for journal "Paris" without checking for every single title that has "Paris" on it:
    if title.lower() == "paris":
        return "presse généraliste"
    
    #check if title contains words typically associated with quotidien presse:
    quotidien_word_list = ["politique", "théâtr", "prose", "almanach", "spirituel", "poète", "eglise", "express", "automobile", "jésus", "chemin" "missions", "paroiss", "dimanche", "chrét", "cathol", "annonce", "illustr", "élégan", "industri", "art moderne", "portefeuille", "évangélique", "syndic", "économie", "artist", "patri", "musical", "populaire", "sociali", "religi", "sport", "humoristique", "administration", "gazette", "judiciaire", "municipal", "dépêche", "colon", "républicain", "hebdomadaire", "quotidien", "démocratie"]
    for word in quotidien_word_list:
        if word.lower() in title.lower():
            return "presse généraliste"
    
    #Default to presse scientifique if it does not check any other box
    return "presse spécialisée"

def metadata_cleaner(path, filter=False, save_path="data/document_data_clean.csv"):
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
    df['type_clean'] = df.apply(lambda x: clean_type(x["type"], x["title"]), axis=1)
    print("Types cleaned\nSaving csv ...")

    df["ocr_quality"] = np.nan

    df = df[['ark', 'title_clean', 'date_clean', 'author_name_clean', "author_type_clean", 'author_birth_clean', 'author_death_clean', "publisher_name_clean", "publisher_place_clean", "type_clean", "format", "description", "type", "source", "language", "title", "author", "date", "publisher", "ocr_quality"]]
    if filter:
        print("Removing unwanted documents ...")
        df_author = df.dropna(subset = "author_type_clean")
        df_publisher = df.dropna(subset = "publisher_name_clean")
        df = pd.concat([df_author,df_publisher]).drop_duplicates().reset_index(drop=True)
        print("Removed unwanted documents")
        df.to_csv(save_path[:-4] + "_filtered.csv", index=False)
    else:
        df.to_csv(save_path, index=False)
    print("csv file saved as " + save_path)

if __name__ == "__main__":
    path = "data/missed_data.csv"
    metadata_cleaner(path, filter=True, save_path=path)