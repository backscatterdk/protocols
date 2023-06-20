import argparse
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd

# import spacy

##########  FUNCTIONS ############
# write docstring
def write_docstring():
    """
    Clean CSV Text Column

    This script clean a text column from a csv file and appends a new column with cleaned texts. It
    removes punctuation, unicode characters and stopwords. 
    """
    return


# nlp = spacy.load("da_core_news_lg")

with open("stopord.txt", "r") as file:
    stopwords = [line.rstrip() for line in file]

### some cleaning functions:

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
        clean_sentence = " ".join(tokens)  # lemmatize(" ".join(tokens))
        clean_text.append(clean_sentence)
    return clean_text


######### EXECUTION #############
def main():

    # parse path to csv file from command line argument and save it as df
    # and parse command line argument name of the column used for analysis with default name "tags"
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="path to csv file")
    parser.add_argument(
        "--column", help="name of the column used for analysis", default="text", type=str,
    )
    args = parser.parse_args()

    # read file from command line argument and save it as df
    df = pd.read_csv(args.path)

    # run preprocessing for parsed column
    clean_text = preprocessing(df[args.column])

    df["clean_text"] = clean_text

    df.to_csv("clean_text.csv", index=False)


if __name__:
    main()
