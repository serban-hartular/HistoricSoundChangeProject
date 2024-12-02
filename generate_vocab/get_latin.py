import dataclasses
import json


@dataclasses.dataclass
class WordEtymologyEntry:
    word : str
    definition : str
    inflected : str
    pos : str
    origins : list[list[str]]

    def __post_init__(self):
        self.origins = [[i.strip() for i in o if i.strip()] for o in self.origins]

def load_etym_entries(jsonl_filname : str) -> list[WordEtymologyEntry]:
    with open(jsonl_filname, 'r', encoding='utf-8') as handle:
        lines = handle.readlines()
    ret_list = [] # to be able to provide debug line nr info
    for i, line in enumerate(lines):
        try:
            ret_list.append(WordEtymologyEntry(**json.loads(line)))
        except Exception as e:
            raise Exception(f'Error at line {i+1} in file {jsonl_filname}, "{line}":\n{str(e)}')
    return ret_list

