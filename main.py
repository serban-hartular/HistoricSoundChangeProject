
import utils
from string_distance import simple_string_distance
from word_transformation import WordTransformation

if __name__ == '__main__':
    # words = utils.csv_to_word_pairs('./data/latin_rom_nouns0.csv', 'LaAcc', 'Ro')
    # vocab = utils.csv_to_vocabulary('./data/latin_rom_nouns0.csv', 'LaAcc', 'Ro')
    from utils import import_jsonl
    noun_list = import_jsonl('./dictionary_scrape/ipa_ro.jsonl')
    for n in noun_list:
        print(n['nom'] + '\t' + n['ipa'])
