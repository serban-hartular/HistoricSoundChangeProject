from typing import Iterable

from alphabet import Alphabet
from contextual_change import ContextualChange
from search_tree import SearchNode
from vocabulary import Vocabulary
import multiprocessing as mp

class SearchNode_ParallelExp(SearchNode):
    def __init__(self, vocabulary : Vocabulary, alphabet : Alphabet = None,
                 parent : SearchNode = None, changes_applied : list[ContextualChange] = None):
        super().__init__(vocabulary, alphabet, parent, changes_applied)
        self.manager = mp.Manager()

    def expand_node(self):
        if mp.cpu_count() < 3:
            return super().expand_node()
        changes = self.get_possible_changes()
        if len(changes) < 100:
            # print('Changes small')
            return super().execute_changes(changes)
        job_n = mp.cpu_count() - 2
        # print('Chunking')
        # split vocabulary
        changes = list(changes)
        changes.sort(key=lambda cc : str(cc))
        v_len = int(len(changes) / job_n + 0.5)
        change_chunks = [changes[i*v_len:(i+1)*v_len] for i in range(job_n)]
        m_destination = self.manager.list()
        jobs = [mp.Process(target=generate_children, args=(self.vocabulary, chk, m_destination, str(i)))
                for i, chk in enumerate(change_chunks)]
        set(map(lambda _proc : _proc.start(), jobs))
        set(map(lambda _proc : _proc.join(), jobs))
        self._children_dict = {}
        for vocab_dict in m_destination:
            for key, node in vocab_dict.items():
                if key in self._children_dict:
                    self._children_dict[key].changes_applied.extend(node.changes_applied)
                else:
                    node.parent = self
                    node.alphabet = self.alphabet
                    self._children_dict[key] = node
        m_destination.clear()


def generate_children(vocab : Vocabulary, changes : Iterable[ContextualChange],
                      destination : list, id : str = ''):
    print(f'{id} started')
    node_dict : dict[tuple, SearchNode_ParallelExp] = {}
    for chg in changes:
        new_vocab = vocab.apply_change(chg)
        key = new_vocab.to_tuple()
        if key in destination:
            node_dict[key].changes_applied.append(chg)
        else:
            node_dict[key] = SearchNode_ParallelExp(vocab.apply_change(chg),
                                                      None, None, [chg])
    destination.append(node_dict)
    print(f'{id} done.')


