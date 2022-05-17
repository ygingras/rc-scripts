#!/usr/bin/env python3

# The format of the pairing signup sheet should closely mirror this one:
# https://docs.google.com/spreadsheets/d/1S0kXTRi5HHM69-Z-t3dECLeC99AcPIJpzjIFpeC0vUI/edit#gid=0

import sys
import itertools
import math
from random import choices
from pprint import pprint
import pandas

FILE = "pairing-demo-data.ods"


def gen_pairing_scores(df, langs):
    """ Score each possible pairing. 
    Return the result as a {(person_a, person_b): score} mapping; higher is better.
    """
    scores = {}
    for pair in map(sorted, itertools.combinations(df["Recurser"], 2)):
        key = tuple(pair)
        a, b = pair
        a_row = df.loc[df["Recurser"] == a]
        b_row = df.loc[df["Recurser"] == b]
        score = 0
        for lang in langs:
            a_lang = a_row[lang].iloc[0]
            b_lang = b_row[lang].iloc[0]
            match [a_lang, b_lang]:
                case ["ok", "ok"]:
                    score += 1
                case ["preferred", "ok"] | ["ok", "preferred"]:
                    score += 2
                case ["preferred", "preferred"]:
                    score += 4
        scores[key] = score
    return scores

def gen_pairing(names, scores):
    """ Generate a random pairing biased towards a high total pairing value. """
    names = set(names)
    value = 0
    pairing = set()
    while len(names) > 1:
        items = [(pair, s+0.1) for pair, s in scores.items() 
                 if set(pair) <= names]
        # Little bit of random magic: choices() will bias towards picking items with a 
        # high rank value.
        pairs, ranks = zip(*items)
        pair = choices(pairs, ranks)[0]
        names -= set(pair)
        pairing.add(pair)
        value += scores[pair]
    return pairing, value, names


def main():
    # TODO: 
    # - read list of skip names
    # MAYBE: --help
    if sys.version_info[:2] < (3, 10):
        raise RuntimeError("This script uses pattern matching, which is only available"
                           " in Python 3.10 and above.")
    df = pandas.read_excel(sys.argv[1])

    # only keep the interseting cells
    langs = [str(cell) for cell in df.iloc[4, 2:-1]]
    df = df.iloc[5:, 1:-1]
    df.columns = ["Recurser"] + langs
    df.dropna(how="all", inplace=True)
    names = list(df["Recurser"])

    # find the matching scrore for all possible pairs, using pattern matching
    scores = gen_pairing_scores(df, langs)
    pprint(scores)
    
    # pick a random set of matches
    pairing, value, unmatched = gen_pairing(names, scores)
    print("Generated pairing:")
    pprint(pairing)
    print(f"Pairing score: {value}, unmatched: {unmatched or None}")
    

if __name__ == "__main__":
    main()
