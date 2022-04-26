from asyncio import FastChildWatcher
from logging import NOTSET
from operator import index
import re
import itertools
from tracemalloc import start
from numpy import issubdtype, source
from pyparsing import Word
import yaml
from pathlib import Path
from botok.tokenizers.wordtokenizer import WordTokenizer
from utils import *
import datetime
#import write_csv

wt = WordTokenizer()

tibetan_alp_val = {
    'ཀ':1,
    'ཁ':2,
    'ག':3,
    'ང':4,
    'ཅ':5,
    'ཆ':6,
    'ཇ':7,
    'ཉ':8,
    'ཏ':9,
    'ཐ':10,
    'ད':11,
    'ན':12,
    'པ':13,
    'ཕ':14,
    'བ':15,
    'མ':16,
    'ཙ':17,
    'ཚ':18,
    'ཛ':19,
    'ཝ':20,
    'ཞ':21,
    'ཟ':22,
    'འ':23,
    'ཡ':24,
    'ར':25,
    'ལ':26,
    'ཤ':27,
    'ཥ':27,
    'ས':28,
    'ཧ':29,
    'ཨ':30,
}

def built_text():
    new_collated_text=""
    char_walker = 0
    end = ""
    notes = get_notes(collated_text)
    for num,note in enumerate(notes,0):
        _, prev_end = get_prev_note_span(notes, num)
        _,end = note["span"]
        gen_text,char_walker=reform_text(note,char_walker,prev_end)
        new_collated_text+=gen_text
    new_collated_text+=collated_text[end:]    
    return new_collated_text


def reform_text(note,char_walker,prev_end):
    gen_text = ""
    modern_word = None
    start,end = note["span"]
    defualt_word,default_word_start_index = get_default_word(collated_text,start,prev_end)
    alt_options = note['alt_options']
    if is_title_note(note) or not check_all_notes(note):
        gen_text=collated_text[char_walker:end]
    elif is_archaic_case(alt_options):
        modern_word = get_modern_word(alt_options)
        if modern_word != None:
            gen_text=collated_text[char_walker:default_word_start_index]+modern_word
        else:
            gen_text=collated_text[char_walker:end] 
    else:
        gen_text=collated_text[char_walker:end]    
    char_walker = end
    """ if modern_word:
        write_csv.write_csv(note,modern_word,source_file_name) """
    return gen_text,char_walker


def normalize_word(word):
    puncts = ['།','་']
    for punct in puncts:
        word = word.replace(punct,"")
    particle_free_word = remove_particles(word)    
    return particle_free_word   


def remove_particles(text):   
    tokenized_texts = wt.tokenize(text,split_affixes=True)
    particle_free_text = ""
    for tokenized_text in tokenized_texts:
        if tokenized_text.pos and tokenized_text.pos != "PART":
            particle_free_text+=tokenized_text.text    
    return particle_free_text


def get_archaic_modern_words():
    archaic_words = from_yaml(Path("./res/archaic_words.yml"))
    modern_words = from_yaml(Path("./res/modern_words.yml"))
    return archaic_words,modern_words


def is_archaic(word):
    normalized_word = normalize_word(word)
    if normalized_word == "":
        pass
    elif search(normalized_word,archaic_words):
        return True
    return False


def is_archaic_case(options):
    for option in options:
        if is_archaic(option):
            return True
    return False


def search(target_word,words):
    low = 0
    high = len(words) - 1
    if target_word[0] not in tibetan_alp_val:
        return False
    while low <= high:
        middle = (low+high)//2
        if tibetan_alp_val[words[middle][0]] == tibetan_alp_val[target_word[0]]:
            index_plus= middle
            index_minus = middle
            while  tibetan_alp_val[words[index_minus][0]] == tibetan_alp_val[target_word[0]] or tibetan_alp_val[words[index_plus][0]] == tibetan_alp_val[target_word[0]]:
                index_plus += 1
                index_minus -= 1
                if words[index_plus] == target_word or words[index_minus] == target_word:
                    print("PRESENT")
                    return True
            return False
        elif  tibetan_alp_val[words[middle][0]] > tibetan_alp_val[target_word[0]]:
            high = middle - 1
        else:
            low =middle + 1 
    return False          

        
def get_modern_word(options):
    for option in options:
        if not is_archaic(option):
            normalize_option = normalize_word(option)
            if search(normalize_option,modern_words):
                return True
    return None


def resolve_archaics(text):
    global collated_text,archaic_words,modern_words
    collated_text = text
    archaic_words,modern_words = get_archaic_modern_words()
    build_text = built_text()
    return build_text


def main():
    global source_file_name
    sources = list(Path('data/collated_text').iterdir())
    for source in sorted(sources):
        source_file_name = source.stem
        collated_text = Path(str(source)).read_text(encoding="utf-8")
        resolve_archaics(collated_text)
    #write_csv.convert_to_excel()

if __name__ == "__main__":
    text = Path("./test.txt").read_text(encoding="utf-8")
    new_text = resolve_archaics(text)   

    
    
""" check the note iss
default word other function
get _prev_notes """
