import dataclasses
from typing import ClassVar

BOS = '^'
EOS = '$'
EMPTY = '0'

symbols_english_ortho = 'abcdefghijklmnopqrstuvwxyz'

@dataclasses.dataclass
class Alphabet:
    symbols : list[str] = None
    groups : dict[str, list[str]] = dataclasses.field(default_factory=dict)
    _symbol_to_group : dict[str, list[str]] = None


    def __post_init__(self):
        if self.symbols == None:
            self.symbols = list(symbols_english_ortho)
        self._symbol_to_group = {s:list() for s in self.symbols}
        for s in self.symbols:
            for gr, sym_list in self.groups.items():
                if s in sym_list:
                    self._symbol_to_group[s].append(gr)

    def __contains__(self, item):
        return item in self.symbols

    def is_in_group(self, sym : str, group : str) -> bool:
        return group in self._symbol_to_group[sym]

    def symbol_in_groups(self, sym : str) -> list[str]:
        return self._symbol_to_group[sym] if sym in self._symbol_to_group else []



_ro_ortho_symbols = list('abcdefghijklmnopqrstuvwxyzăîșț')
_ro_ortho_vowels = list('aeiouăî')
_ro_ortho_consonants = list(set(_ro_ortho_symbols) - set(_ro_ortho_vowels))
_ro_ortho_groups = {'V' : _ro_ortho_vowels, 'C':_ro_ortho_consonants}
ro_ortho = Alphabet(_ro_ortho_symbols, _ro_ortho_groups)

_la_ro_ortho_vowels = _ro_ortho_vowels + list('ūōāēī')
la_ro_ortho = Alphabet(_la_ro_ortho_vowels + _ro_ortho_consonants,
                       {'V' : _la_ro_ortho_vowels, 'C':_ro_ortho_consonants})
