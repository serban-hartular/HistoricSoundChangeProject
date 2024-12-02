from __future__ import annotations

import dataclasses
import itertools
from collections import defaultdict
from typing import Dict, List, Tuple, Set

from word_transformation import WordTransformation, Transition
from contextual_change import ContextualChange, TERMINAL


@dataclasses.dataclass
class ChangeRecord:
    d_in : str
    d_out : str
    pre : str
    post : str
    def __hash__(self):
        return hash((self.d_in, self.d_out, self.pre, self.post))
    def get_len_combos(self, max_len : int = -1):
        pre = self.pre
        post = self.post
        if max_len != -1:
            pre = pre[-max_len:]
            post = post[:max_len]
        before = [pre[:l] for l in range(len(pre)+1)]
        after = [post[:l] for l in range(len(post)+1)]
        return [ChangeRecord(self.d_in, self.d_out, _pre, _post)
                for _pre, _post in itertools.product(before, after)]



class Vocabulary(Dict[str, WordTransformation]):
    def __init__(self, source : List[WordTransformation] | Dict[str, WordTransformation]):
        super().__init__(source if isinstance(source, dict) else {wt.initial : wt for wt in source})
        if len(source) != len(self):
            print('Warning: fewer entries in Vocabulary than in source. Check for duplicates')
        self.change_sequence_flag = False

    def initial(self) -> list[str]:
        return [wt.initial for k, wt in self.items()]

    def final(self) -> list[str]:
        return [wt.final for k, wt in self.items()]


    def apply_change(self, change : ContextualChange) -> Vocabulary:
        return Vocabulary({k : WordTransformation(change(wt.initial), wt.final)
                           for k, wt in self.items()})

    def compute_change_sequences(self):
        if not self.change_sequence_flag:
            for wt in self.values():
                wt.compute_change_sequences()
        self.change_sequence_flag = True
    def to_tuple(self):
        return tuple((k, self[k].initial, self[k].final) for k in self)

    def score(self) -> float:
        return sum([wt.min_changes for wt in self.values()])

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return isinstance(other, Vocabulary) and self.to_tuple() == other.to_tuple()

    def get_change_records(self) -> list[ChangeRecord]:
        self.compute_change_sequences()
        records = []
        for wt in self.values():
            word = TERMINAL + wt.initial + TERMINAL
            for changes in wt.change_sequences:
                i = 0
                for chg in changes:
                    if not chg:
                        i += 1
                        continue
                    d_in = chg.d_in  # if chg.d_in else '0'
                    d_out = chg.d_out  # if chg.d_out else '0'
                    pre = word[:i]
                    post = word[i:]
                    if chg.d_in:  # not insertion
                        i += 1
                        post = post[1:]  # don't include deleted/changed symbol
                    records.append(ChangeRecord(d_in, d_out, pre, post))
        return records


def list_to_vocab(vl : str) -> Vocabulary:
    vl = vl.split('\n')
    vl = [l.strip() for l in vl if l.strip()]
    vl = [l.split() for l in vl]
    return Vocabulary([WordTransformation(l[0], l[1]) for l in vl])

if __name__ == "__main__":
    vocab_list ="""
    pelle   piele
    celum   cer
    culum   cur
    clama   cheama
    mola    moara
    """

    vocab = list_to_vocab(vocab_list)
    import contextual_change
    import alphabet

    cc = contextual_change.parse_contextual_change('l > r / V _ V', alphabet.ro_ortho)
