import pandas as pd
import re
import numpy as np

"""
TODO

There are sometimes information about the date but not in the form of d{4} --> get it instead of 'None'
Ex:18..
"""
def clean_date(unclean_date):

    p = re.compile(r"\d{4}")
    m = re.findall(p,unclean_date)
    m = [int(item) for item in m]


    if len(m) == 0:
        return None
    else:
        return str(round(np.mean(m)))

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
        "author_death_clean": None
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

    return pd.Series(author)
    

def clean_publisher(unclean_publisher):
    publisher = {
        "publisher_name_clean": "[s.n]",
        "publisher_place_clean": None
    }

    if str(unclean_publisher) != "nan":
        p = re.compile(r"(.*)\((.+)\)")
        m = re.match(p,unclean_publisher)


        if m == None and unclean_publisher != "":
            publisher["publisher_name_clean"] = unclean_publisher

        if m != None:
            if m.groups()[0].strip() != "":
                publisher["publisher_name_clean"] = m.groups()[0].strip()
            publisher["publisher_place_clean"] = m.groups()[1].strip()

    return pd.Series(publisher)


def metadata_cleaner(path):
    df = pd.read_csv(path)
    df = df.drop_duplicates()
    df['date_clean'] = df['date'].apply(clean_date)
    df['title_clean'] = df['title'].apply(clean_title)
    df = pd.concat([df, df['author'].apply(clean_author)], axis=1)
    df = pd.concat([df, df['publisher'].apply(clean_publisher)], axis=1)

    df = df[['ark', 'title_clean', 'date_clean', 'author_name_clean', 'author_birth_clean', 'author_death_clean', "publisher_name_clean", "publisher_place_clean", "format", "description", "type", "source", "language", "title", "author", "date", "publisher"]]
    df.to_csv("data/document_data_clean.csv", index=False)

if __name__ == "__main__":
    path = "data/document_data.csv"
    metadata_cleaner(path)