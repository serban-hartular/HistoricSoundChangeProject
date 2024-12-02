import dataclasses

import re

from alphabet import Alphabet
import alphabet

TERMINAL = '#'


def _T0(s: str) -> str:
    return s if s else alphabet.EMPTY

def _Tterm(s : str) -> str:
    s = s.replace(alphabet.BOS, TERMINAL)
    s = s.replace(alphabet.EOS, TERMINAL)
    return s


@dataclasses.dataclass
class ContextualChange:
    initial : str
    final : str
    context_pre : str = ''
    context_post : str = ''
    alphabet : Alphabet = None
    _regex_match : str = None
    _regex_sub : str = None
    _regex_match_comp : re.Pattern = None
    def __post_init__(self):
        self._regex_match = f'({self.context_to_regex(self.context_pre, True)})' +\
            f'{self.initial}' + f'({self.context_to_regex(self.context_post, False)})'
        self._regex_sub = rf'\1{self.final}\2'
        self._regex_match_comp = re.compile(self._regex_match)
        # self._regex_sub_comp = re.compile(self._regex_sub)

    def __call__(self, in_word : str) -> str:
        if self.initial not in in_word:
            return in_word
        return re.sub(self._regex_match_comp, self._regex_sub, in_word)

    def context_to_regex(self, context : str, pre : bool) -> str:
        regex = ''
        if not context:
            return regex
        if context[0] == TERMINAL and pre:
            context = alphabet.BOS + context[1:]
        if context[-1] == TERMINAL and not pre:
            context = context[:-1] + alphabet.EOS

        for c in context:
            if self.alphabet and c in self.alphabet.groups:
                regex += f"[{''.join(self.alphabet.groups[c])}]"
            else:
                regex += c
        return regex

    def __str__(self):
        s = f'{_T0(self.initial)} > {_T0(self.final)}'
        if self.context_pre or self.context_post:
            s += f' / {_Tterm(self.context_pre)} _ {_Tterm(self.context_post)}'
        return s

    @staticmethod
    def from_string(s : str, alph : Alphabet) -> 'ContextualChange':
        return parse_contextual_change(s, alph)

    def __repr__(self):
        return str(self)
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other):
        return isinstance(other, ContextualChange) and str(self) == str(other)


def parse_contextual_change(expr : str, alph : Alphabet = None) -> ContextualChange:
    """ Form is: I > F / C0 _ C1
        (the context part is optional"""
    expr = expr.split('/')
    change = expr[0]
    try:
        initial, final = [_s.strip() for _s in change.split('>')]
    except:
        raise Exception(f'Error parsing change {change}')
    initial, final = ['' if _s == alphabet.EMPTY else _s for _s in (initial, final)]
    if len(expr) == 1:
        context_pre = context_post = ''
    else:
        context = expr[1]
        try:
            context_pre, context_post = [_s.strip() for _s in context.split('_')]
        except:
            raise Exception(f'Error parsing context {context}')
        if context_pre and context_pre[0] == TERMINAL:
            context_pre = alphabet.BOS + context_pre[1:]
        if context_post and context_post[-1] == TERMINAL:
            context_post = context_post[:-1] + TERMINAL
    return ContextualChange(initial, final, context_pre, context_post, alph)

