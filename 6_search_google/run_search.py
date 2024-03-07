"""Code for using google search to extract N followers/followees for a list og IG acconuts
Use engine argument to choose: 
    --engine 0 (Aol)
    --engine 1 (Yahoo)
    --engine 2 (Startpage)

The idea is that you run the script and get all the ones you can w Aol
Then you save the ones you get succesful result for in one file - and the ones still missing in other file
Then you can run the ones you are still missing with another search engine to try and get a result

To do this you need to change the file name still_missing.txt to targets_names.txt and make sure the other txt files are clean
Then you can run the script again
"""


import pandas as pd
import os
from search_engines import Aol, Yahoo, Startpage
import time
import datetime
import argparse

# filepaths (constants)
file_path = os.path.join(os.getcwd(), "targets_names.txt")
outpath = os.path.join(os.getcwd(), "targets_names_followes.txt")
outpath2 = os.path.join(os.getcwd(), "targets_names_followes_clean.txt")
outpath3 = os.path.join(os.getcwd(), "still_missing.txt")

# functions
def run_loop(engine, df, outpath):
    with open(outpath, 'r') as file:
        lines = file.readlines()
        num_lines = len(lines)

    for idx, n in enumerate(df["username"].to_list()[num_lines:]):
        print(n)
        results = engine.search("instagram @" + n, pages=1)

        try:
            result = results[0]['text']
            with open(outpath, 'a') as file:
                file.write(str(n) + "###" + result + "\n")

            if (idx + 1) % 100 == 0:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{timestamp} - Got to index {idx}, with name {n}. Sleeping 2 minutes.")
                time.sleep(60*2)

        except IndexError:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp} - Ran out of tries. Got to index {idx}, with name {n}. Sleeping 2 minutes.")
            time.sleep(60*2)
            continue

def clean_df(df):
    df['text'] = df['text'].fillna('')
    df['text'] = df['text'].str.lower()
    pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?[MK]?) followers, (\d{1,3}(?:,\d{3})*) following'
    df[['followers', 'following']] = df['text'].str.extract(pattern)
    df['followers'] = df['followers'].str.replace(',', '').str.replace('K', '000').str.replace('M', '000000')
    df['following'] = df['following'].str.replace(',', '').str.replace('K', '000').str.replace('M', '000000')
    df['followers'] = pd.to_numeric(df['followers'], errors='coerce')
    df['following'] = pd.to_numeric(df['following'], errors='coerce')
    df['followers'] = df['followers'].fillna(0).astype(int)
    df['following'] = df['following'].fillna(0).astype(int)
    return df

def run_cleaning(df, outpath):
    df_done = pd.read_csv(outpath, sep='###', header=None, names=['username', 'text'], engine='python')
    final_df = clean_df(df_done)
    df.drop_duplicates(inplace=True)
    final_df.drop_duplicates(inplace=True)
    ff = pd.merge(df, final_df, on="username")
    ff_done = ff[ff["followers"] != 0]
    still_missing = ff[ff["followers"] == 0]
    print(f"For {ff_done.shape[0]} results, we found N followers.\nFor {still_missing.shape[0]} results, we did not find N followers.")
    return ff_done, still_missing

def save_output(outpath, df, missing=False):
    ids = df["id"].to_list()
    usernames = df["username"].to_list()
    followers = df["followers"].to_list()
    followees = df["following"].to_list()

    if missing:
        with open(outpath, 'w') as file:
            for number, name in zip(ids, usernames):
                file.write(f"{number}, {name}\n")
    else:
        with open(outpath, 'w') as file2:
            for number, name, f1, f2 in zip(ids, usernames, followers, followees):
                file2.write(f"{number}, {name}, {f1}, {f2}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", help="number of search engine to use (0: Aol, 1: Yahoo, 2: Startpage)", default=0, type=int, required=False)
    args = parser.parse_args()

    with open(outpath, 'r') as file:
        lines = file.readlines()
    num_lines = len(lines)
    print(f"Number finished searches when starting script: {num_lines}")

    # input df with targets to run
    dfn = pd.read_csv(file_path, header=None)
    dfn.columns = ["id", "username"]
    dfn["username"] = dfn["username"].str.replace(' ', '')
    print(f"Number of targets to run: {dfn.shape[0]}")

    # define engines
    e1 = Aol()
    e2 = Yahoo()
    e3 = Startpage()
    engines = [e1, e2, e3]

    # run code with chosen engine
    run_loop(engine=engines[args.engine], df=dfn, outpath=outpath)
    ff_done, still_missing = run_cleaning(dfn, outpath)
    save_output(outpath2, ff_done) # save results where N followers was found
    save_output(outpath3, still_missing, missing=True) # save results where N followers is still missing

if __name__ == "__main__":
    main()
