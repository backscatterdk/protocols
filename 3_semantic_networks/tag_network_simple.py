import argparse
from collections import Counter
import networkx as nx
import numpy as np
import pandas as pd
# sklearn countvectorizer
from sklearn.feature_extraction.text import CountVectorizer


def split_sents(df, col_name):
    """
    seperate the sentences in the tag collumn on punctuation
    create seperate rows in the df for each sentence 
    """
    # seperate into seperate tag lists - on punctuation
    df[col_name] = df[col_name].str.split(".")
    # make into seperate rows
    df = df.explode(col_name)
    return df

def create_co_occurance_matrix(texts,min_count = 1):
    """
    creates co_occurance matrix based on list of strings. min_count specifies the required minimum 
    degree of the nodes
    """
    # Convert a collection of text documents to a matrix of token counts
    cv = CountVectorizer(ngram_range=(1,1))
    X = cv.fit_transform(texts)
    Xc = (X.T * X) # matrix manipulation
    Xc.setdiag(0) # set the diagonals to be zeroes as it's pointless to be 1
    names = cv.get_feature_names() # This are the entity names (i.e. keywords)
    df_matrix = pd.DataFrame(data = Xc.toarray(), columns = names, index = names)
    mask = list(df_matrix.sum() >= min_count) # remove nodes with degree < min_count
    df_matrix = df_matrix.loc[mask, mask] 
    return df_matrix

def create_graph(df_matrix):
    """
    creates a networkx graph from a co-occurance matrix
    """
    G = nx.from_pandas_adjacency(df_matrix)
    return G

def create_tag_network(corpus, min_count = 1):
    """
    creates a tag network from a corpus. min_count specifies the required minimum degree of the nodes
    """
    df_matrix = create_co_occurance_matrix(corpus, min_count)
    G = create_graph(df_matrix)
    return G


def main():
    # parse path to csv file from command line argument and save it as df
    # and parse command line argument name of the column used for analysis with default name "tags"
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", 
                        help="path to csv file",
                        type=str)
    parser.add_argument(
        "--column",
        help="name of the column used for analysis",
        default="tags",
        type=str,
        required=False
    )
    args = parser.parse_args()

    # parse csv file as command line argument and load it as df 
    df = pd.read_csv(args.path)

    # remove rows with missing values from column 
    df = df.dropna(subset=[args.column])

    # split "sentences" on "."
    df = split_sents(df)

    # create tag network
    G = create_tag_network(list(df[args.column]), min_count = 1)

    # save graph
    nx.write_gexf(G, "tag_network.gexf")

if __name__:
    main()
