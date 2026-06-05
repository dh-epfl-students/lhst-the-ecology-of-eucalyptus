# The ecology of Eucalyptus

2026 semester project by André da Glória Santiago

Supervised by: Elisabeth Davin-Mortier and Jérôme Baudry

# About

This project aims to do a corpus analysis of the discourse around eucalyptus within the French-speaking world. The goal is to perform an exploratory analysis of the field, and understand who are the actors and how do they shape the discourse around the eucalyptus tree. This project provides the tools to download a comprehensive corpus, to which topic modeling is applied. This methodology offers a way to explore the social and political ramifications of the eucalyptus
tree, as well as identifying new potential cases for more in-depth qualitative research.

# Research Summary

We downloaded a total of 17'191 documents with at least one mention of "eucalyptus" from the [Gallica](https://gallica.bnf.fr/accueil/fr/html/accueil-fr) database. We then applied topic modeling technics using BERTopic, to find 136 different topics within the documents. The topic and metadata analysis showed that there is a clear difference in the discourse around the plant based on the typology of documents, but most importantly based on their place of publication. We see a clear difference in the way the discourse is shaped between mainland France and its colonies, with the first being linked with scientific topics and publicity, while the latter being mostly linked to institutional ones. 


# Installation and Usage

All required packages can be found in `requirements.txt`.

For size and privacy reasons, both the full txt documents and the topic_model file will not be published on Github, possibly rendering some scripts unusable. Please contact me (andre.dagloriasantiago@epfl.ch) if you want to have access to the full data.

The scripts used to download the corpus using Gallica's API can be found in the `data-extraction` folder. The corpus has already been formed, so there should not be any necessity to run most of these files.  
1) `1.search.py` should be run first to create the full corpus, with each document metadata and id (ark). 
2) `2.metadata_cleaning.py` should be run second to clean the metadata outputted by the first script. Here, a filtering can be performed to reduce the amount of total documents
3) `3.download.py` should be run third. It downloads each document through Gallica's API. However, the document API used as such does not work because of the [captcha implementation of december 2025](https://www.bnf.fr/fr/actualites/un-captcha-pour-gallica), which unexpectedly broke the API usage. This script uses a workaround, by specifing the `altcha_pass` and `jsession_id` when querying the API. However, this necessitates the daily solving of the captcha on the browser, then copying these fields to the python script.
4) `4.text_cleaning.py` should be run last (but can be run simultaneously to 3). Performs some basic OCR cleaning, removing some bad documents or contexts around "eucalyptus".

`topic_modeling.ipynb` is the script that runs the topic model, meta-topic assignement and the co-occurrence graph as well as an early exploration of topics. It can be run, however the results have already been integrated to the corpus.

`NER.ipynb` is a tentative to apply Named Entity Recognition to the project. However, due to the size of the files and the different OCR problems, it was not integrated to the project. It allowed however to add the "occurences" and "occurences_ratio" to the final corpus.

`filter_verification.ipynb` shows the exploratory analysis used to solidify the filtering choice.

`actors_exploration.ipynb` and `topic_exploration.ipynb`are two notebooks with exploratory analysis of both actors and topics within the discourse. You can choose the cells you are interested in to see a more in-depth analysis of certain regions or typologies.

`report_figures.ipynb` is the file that created every figure and statistic used in the final report.


The ecology of Eucalyptus - André da Glória Santiago<br>
Copyright (c) 2026 André da Glória Santiago / EPFL<br>
This program is licensed under the terms of the [MIT](https://mit-license.org/) licence.