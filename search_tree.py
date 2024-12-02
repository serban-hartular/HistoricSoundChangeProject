from __future__ import annotations

import dataclasses
import itertools
import time
import timeit
from typing import Iterator, Iterable

import alphabet
from word_transformation import ChangeSequence, WordTransformation
from contextual_change import ContextualChange, TERMINAL
from alphabet import Alphabet

from vocabulary import Vocabulary, ChangeRecord, list_to_vocab
import utils

def string_to_group_combos(text : str, alph : Alphabet) -> list[str]:
    combos = [c + ''.join(alph.symbol_in_groups(c)) for c in text]
    substitutions = itertools.product(*combos)
    return [''.join(s) for s in substitutions]

def change_record_group_combos(rec : ChangeRecord, alph : Alphabet) -> set[ChangeRecord]:
    pre_combos = string_to_group_combos(rec.pre, alph)
    post_combos = string_to_group_combos(rec.post, alph)
    return {ChangeRecord(rec.d_in, rec.d_out, _pre, _post)
            for _pre, _post in itertools.product(pre_combos, post_combos)}


_cc_cache : utils.ContextualChangeCache = None

class SearchNode:
    CONTEXT_LIMIT = 2
    def __init__(self, vocabulary : Vocabulary, alphabet : Alphabet = None,
                 parent : SearchNode = None, changes_applied : list[ContextualChange] = None):
        self.vocabulary = vocabulary
        self.alphabet = alphabet
        self.parent = parent
        self.depth = self.parent.depth + 1 if self.parent else 0
        self.score = self.vocabulary.score()
        self._children_dict = None
        self.changes_applied = [] if changes_applied is None else changes_applied
    def __str__(self):
        return str(self.changes_applied[0]) if self.changes_applied else 'START' +\
            f', {self.depth}'
    def __repr__(self):
        return str(self)
    def eval_fn(self):
        return self.depth * 0.99 + self.score
    def children(self) -> Iterator[SearchNode]:
        if self._children_dict is None:
            return None
        return self._children_dict.values()
    def is_expanded(self) -> bool:
        return self._children_dict is not None
    def get_possible_changes(self) -> set[ContextualChange]:
        max_len = 2
        # print('Vocab change records...', end='')
        context_records = self.vocabulary.get_change_records()
        # print(f'{len(context_records)} full')
        context_records_len = set(itertools.chain.from_iterable(
            [r.get_len_combos(max_len) for r in context_records]))
        context_records = [r for r in context_records_len if not r.d_in or not r.d_out or\
            set(self.alphabet.symbol_in_groups(r.d_in)).intersection(self.alphabet.symbol_in_groups(r.d_out))]
        # print(f'{len(context_records_len)} distinct of max_len {max_len}, ', end='')
        context_records_group = set(itertools.chain.from_iterable(
            [change_record_group_combos(r, self.alphabet) for r in context_records]))
        # print(f'{len(context_records_group)} unique by group. Changes...', end='')
        if _cc_cache is None:
            changes = {ContextualChange(r.d_in, r.d_out, r.pre, r.post, self.alphabet)
                   for r in context_records_group}
        else:
            changes = {_cc_cache.get(r) for r in context_records_group}
        return changes
    def expand_node(self):
        changes = self.get_possible_changes()
        self.execute_changes(changes)
    def execute_changes(self, changes : Iterable[ContextualChange]):
        self._children_dict : dict[tuple, SearchNode] = {}
        for chg in changes:
            new_vocab = self.vocabulary.apply_change(chg)
            key = new_vocab.to_tuple()
            if key in self._children_dict:
                self._children_dict[key].changes_applied.append(chg)
            else: #SearchNode
                self._children_dict[key] =\
                    self.__class__(new_vocab, self.alphabet, self, [chg])
        # sort changes_applied
        for child in self.children():
            child.changes_applied.sort(key=lambda chg :
                min(len(chg.context_pre), len(chg.context_post)) + max(len(chg.context_pre), len(chg.context_post))/100)
    @staticmethod
    def find_solution(queue : list[SearchNode] | SearchNode)\
            -> (SearchNode, list[SearchNode]):
        if not isinstance(queue, Iterable):
            queue = [queue]
        while True:
            # queue = [n for n in queue if n not in avoid]
            # if not queue:
            #     return None, None
            queue.sort(key=lambda n : n.eval_fn())
            e = queue.pop(0)
            # print(f'{e.changes_applied[0] if e.changes_applied else 0}\t{e.eval_fn():.2f}', end='')
            # e = max(queue, key=lambda n: n.score)
            # queue.remove(e)
            if e.score < 0.1:
                # print()
                return e, queue
            else:
                if not e.is_expanded():
                    e.expand_node()
                children = list(e.children())
                queue.extend(children)
                # print(f'\t{len(children)}\t{len(queue)}')


def solution_path(solution : SearchNode) -> list[SearchNode]:
    path = []
    while solution:
        path.append(solution)
        solution = solution.parent
    return path[::-1]

def print_path(path : list[SearchNode]):
    for p in path:
        print('\t'.join([str(i) for i in [p, p.score] + p.vocabulary.initial()]))


if __name__ == "__main__":
    vocab_list = """
    pellem   piele
    celum   cer
    culum   cur
    clama   cheama
    molam    moara
    ollam    oala
    """

    _cc_cache = utils.ContextualChangeCache(alphabet.la_ro_ortho)
    alph = alphabet.la_ro_ortho
    # vocab = utils.csv_to_vocabulary('./data/latin_rom_nouns0.csv', 'LaAcc', 'Ro')
    vocab = list_to_vocab(vocab_list)
    # m_final = ContextualChange.from_string('m > 0 / _ #', alph)
    # vlv = ContextualChange.from_string('l > r / V _ V', alph)
    # print(timeit.timeit(stmt='vocab.apply_change(m_final)', globals=globals(), number=10) / 10)
    # print(timeit.timeit(stmt='vocab.apply_change(vlv)', globals=globals(), number=10) / 10)

    from parallel_search_tree import SearchNode_ParallelExp

    root = SearchNode_ParallelExp(vocab, alphabet.la_ro_ortho)
    # root = SearchNode(vocab, alphabet.la_ro_ortho)
    print('Starting')
    t0 = time.time()
    solution, queue = SearchNode.find_solution(root)
    t1 = time.time()
    print(f'Done in {t1-t0}')
    # children = list(root.children())
    # children.sort(key=lambda c: c.eval_fn())
    path = solution_path(solution)
    for p in path:
        print('\t'.join([str(i) for i in (p, p.score, p.vocabulary.initial())]))

