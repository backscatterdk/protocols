import argparse
import pickle
import sys
from collections import Counter
import networkx as nx
import numpy as np
import pandas as pd


"""
This script creates a tag network from a csv file. The csv file must contain a column with tags and a column with areas.
The script creates a graph where nodes are tags and areas and edges are connections between tags and areas.
The script takes two command line arguments:
    1. path to csv file
    2. name of the column used for analysis (default: "tags")
"""

# parse path to csv file from command line argument
parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to csv file")
parser.add_argument(
    "--column",
    help="name of tag column used for analysis",
    default="tags",
    type=str,
)
parser.add_argument(
    "--attribute ",
    help="name of attribute column used for analysis",
    default="area",
    type=str,
)
args = parser.parse_args()

# parse csv file as command line argument and load it as df 
df = pd.read_csv(args.path)


## add area tags
# area2tag = nx.Graph()
g = nx.Graph()


### Count tag occurrences accross areas
area2count = {area.upper().strip(", "): Counter() for area in df.area.unique()}
tag2tag = {}
### Count tag occurrence overall
tag_count = Counter()


# for each area count tags (area2count)
# for each tag count cooccuring tags (tag2tag)
for area, tags in df[["area", "tags"]].values:
    tags = [i.strip() for i in tags.split(",")]
    area = area.upper().strip(", ")
    for t in tags:
        tag_count[t] += 1
        area2count[area][t] += 1
        if not t in tag2tag:
            tag2tag[t] = Counter()
        for t2 in tags:
            if t == t2:
                continue
            tag2tag[t][t2] += 1

## Add tag2tag edges
for tag, c in tag2tag.items():
    if len(c) == 0:
        continue
    g.add_node(tag, **{"type": "tag", "count": tag_count[tag]})
    rank = 0
    last = max(c.values())
    for tag2, count in c.most_common():
        if count < last:
            rank += 1
            last = count
        g.add_node(tag2, **{"type": "tag", "count": tag_count[tag]})
        g.add_edge(
            tag,
            tag2,
            **{"edge_type": "tag2tag", "weight": count, "rank": rank, "rank2": 0}
        )

## Add area2tag edges
# for each area:
# add area node and connect with cooccuring tags
# add node attribute for each cooccuring tag that describes how important the tag is in the area
for area, c in area2count.items():
    if len(c) == 0:
        continue
    last = max(c.values())
    rank = 0
    g.add_node(area, **{"type": "area"})
    sum_ = sum(c.values())
    for tag, count in c.most_common():
        if count < last:
            rank += 1
            last = count
        g.nodes[tag][area] = count / sum_
        g.add_edge(
            area,
            tag,
            **{"edge_type": "area2tag", "weight": count, "rank": rank, "rank2": 0}
        )

# save graph as gexf
nx.write_gexf(g, "tag_network_with_attribute.gexf")
