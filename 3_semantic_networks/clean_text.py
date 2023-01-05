import argparse

import pickle
import re
import sys
from collections import Counter
import nltk
import numpy as np
import pandas as pd
import spacy

# write docstring
def write_docstring():
    """
    This script cleans text from a csv file and saves it as a pickle file. The script
    removes punctuation, unicode characters, stopwords and lemmatizes the text.
    """
    return


# nlp = spacy.load("da_core_news_lg")

with open("stopord.txt", "r") as file:
    stopwords = [line.rstrip() for line in file]

### some cleaning functions:

# remove whitespace from text
def remove_whitespace(text):
    return " ".join(text.split())


# remove punctuation
def remove_punctuation(text):
    translator = str.maketrans("", "", string.punctuation)
    return text.translate(translator)


# lowercase text
def text_lowercase(text):
    return text.lower()


# removing unicode characters:
def remove_unicode(text):
    return re.sub(
        r"(@\[A-Za-zÆæØøÅå0-9]+)|([^0-9A-Za-zÆæØøÅå\t])|(\w+:\/\/\S+)|^rt|http.+?",
        " ",
        text,
    )

# remove stopwords
def remove_stopwords(text):
    return " ".join([word for word in text.split() if word not in stopwords])

# lemmatize
def lemmatize(text):
    return " ".join([token.lemma_ for token in nlp(text)])


# nltk.download("punkt")

## preprocessing

def preprocessing(corpus):
    # initialize
    clean_text = []
    for row in corpus:
        # lowercase
        text = text_lowercase(row)
        # remove unicode characters
        text = remove_unicode(text)
        # remove stopwords
        text = remove_stopwords(text)
        # tokenize
        tokens = text.split()
        # isword
        tokens = [token for token in tokens if token.isalpha()]
        # lemmatize
        clean_sentence = " ".join(tokens) # lemmatize(" ".join(tokens))
        clean_text.append(clean_sentence)
    return clean_text


# read file from command line argument and save it as df
df = pd.read_csv(sys.argv[1], header=None)

# parse path to csv file from command line argument and save it as df
# and parse command line argument name of the column used for analysis with default name "tags"
parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to csv file")
parser.add_argument(
    "--column",
    help="name of the column used for analysis",
    default="text",
    type=str,
)
args = parser.parse_args()

# read file from command line argument and save it as df
df = pd.read_csv(args.path)


# run preprocessing for parsed column
clean_text = preprocessing(df[args.column])


# save clean text as pickle
with open("clean_text.pkl", "wb") as file:
    pickle.dump(clean_text, file)

