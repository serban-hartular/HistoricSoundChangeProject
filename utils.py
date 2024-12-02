
import json
import pandas as pd

import alphabet
from word_transformation import WordTransformation
from vocabulary import Vocabulary


def import_jsonl(filename : str) -> list[dict]:
    with open(filename, 'r', encoding='utf-8') as handle:
        lines = handle.readlines()
    data = []
    for i, line in enumerate(lines):
        try:
            data.append(json.loads(line))
        except Exception as e:
            raise Exception(f'Error parsing line {i}, "{line}":{str(e)}')
    return data

def csv_to_word_pairs(filename : str, initial_label : str, final_label) -> list[tuple[str, str]]:
    data = pd.read_csv(filename, sep='\t', encoding='utf-8')
    data = data.fillna('')
    data = data.to_dict(orient='records')
    return [(d[initial_label], d[final_label]) for d in data]

def csv_to_vocabulary(filename: str, initial_label: str, final_label) -> Vocabulary:
    data = csv_to_word_pairs(filename, initial_label, final_label)
    wt_list = [WordTransformation(*d) for d in data
               if d[0] and d[1]]
    return Vocabulary(wt_list)

from contextual_change import ContextualChange
from vocabulary import ChangeRecord

class ContextualChangeCache:
    def __init__(self, alph : alphabet.Alphabet):
        self.cache = {}
        self.alph = alph
    def get(self, rec : ChangeRecord):
        if rec in self.cache:
            return self.cache[rec]
        cc = ContextualChange(rec.d_in, rec.d_out, rec.pre, rec.post, self.alph)
        self.cache[rec] = cc
        return cc
