import codecs
from collections import namedtuple
import csv
import logging
import os
import re
from zipfile import ZipFile
from urllib.request import urlopen

CedictEntry = namedtuple('CedictEntry', ['simplified', 'traditional', 'pronounciation', 'meaning'])
CharacterCardEntry = namedtuple('Entry', ['Hanzi', 'Traditional', 'Meaning', 'Pinyin', 'Decomposition'])
WordCardEntry = namedtuple('Entry', ['Hanzi', 'Traditional', 'Meaning', 'Pinyin'])

Resource = namedtuple('Resource', ['url', 'name'])
ZipResource = namedtuple('Resource', ['url', 'name', 'member_name'])

DATA_FOLDER = 'data'
CEDICT = ZipResource('https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip', 'cedict.zip', 'cedict_ts.u8')
DECOMPOSITIONS = Resource('https://raw.githubusercontent.com/cjkvi/cjkvi-ids/master/ids.txt', 'ids.txt')
CHARACTER_LIST = ZipResource(
    'https://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexch/subtlexchchr.zip/at_download/file',
    'subtlexchchr.zip',
    'SUBTLEX-CH-CHR')
WORD_LIST = ZipResource(
    'https://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexch/subtlexchwf.zip/at_download/file',
    'subtlexchwf.zip',
    'SUBTLEX-CH-WF')

DICTIONARY_REGEX = r'([^\s]+?) ([^\s]+?) \[([^\]]+)\] /(.+)/'
DECOMPOSITION_REGEX = '/U\\+ ([a-fA-F0-0]+)\\t([ ^\\s] +?)\\t([ ^\\s] +?)'


def get_resource_path(resource):
    return os.path.join(DATA_FOLDER, resource.name)


def download_data():
    def download_resource(resource):
        target_path = get_resource_path(resource)
        if os.path.exists(target_path):
            logging.info('File already exists: [%s], skipping!', resource.name)
            return

        logging.info('Downloading [%s] to [%s]', resource.url, resource.name)

        filedata = urlopen(resource.url)
        datatowrite = filedata.read()

        with open(target_path, 'wb') as f:
            f.write(datatowrite)

    os.makedirs(DATA_FOLDER, exist_ok=True)
    download_resource(CEDICT)
    download_resource(DECOMPOSITIONS)
    download_resource(CHARACTER_LIST)
    download_resource(WORD_LIST)


def parse_cedict():
    def parse_cedict_entry(line):
        m = re.match(DICTIONARY_REGEX, line)
        assert m, 'Line did not match: {0}'.format(line)

        traditional = m.group(1).strip()
        simplified = m.group(2).strip()
        pronounciation = m.group(3).strip()
        meaning = m.group(4).strip()

        return CedictEntry(simplified, traditional, pronounciation, meaning)

    cedict = {}

    path = get_resource_path(CEDICT)
    with ZipFile(path, 'r') as zf:
        with zf.open(CEDICT.member_name, 'r') as f:
            for line in codecs.iterdecode(f, 'utf8'):
                if line.startswith('#'):
                    continue
                line = line.strip()
                entry = parse_cedict_entry(line)
                cedict[entry.simplified] = entry
    return cedict


def parse_decompositions():
    decompositions = {}
    path = get_resource_path(DECOMPOSITIONS)
    with open(path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue

            fields = line.strip().split('\t')
            raw_character = fields[0]
            decomposition = fields[2]
            encoded_character = raw_character.replace('U+', '0x')
            character = chr(int(encoded_character, 16))
            decompositions[character] = decomposition
    return decompositions


def parse_frequency_list(resource):
    entries = []
    path = get_resource_path(resource)
    with ZipFile(path, 'r') as zf:
        with zf.open(resource.member_name, 'r') as f:
            for line in codecs.iterdecode(f, 'gbk'):
                if line.startswith('"') or line.startswith('Character'):
                    continue
                entry = line.split('\t')[0]
                entries.append(entry)
    return entries


def build_character_cards(cedict, characters, decompositions):
    entries = []
    for character in characters:
        if character not in cedict:
            logging.info('Character not in dictionary: [%s]', character)
            continue
        cedict_entry = cedict[character]
        traditional = cedict_entry.traditional
        pronounciation = cedict_entry.pronounciation
        meaning = cedict_entry.meaning
        decomposition = decompositions[character]
        entry = CharacterCardEntry(character, traditional, meaning, pronounciation, decomposition)
        entries.append(entry)

    return entries


def build_word_cards(cedict, words):
    entries = []
    for word in words:
        if word not in cedict:
            logging.info('Word not in dictionary: [%s]', word)
            continue
        cedict_entry = cedict[word]
        traditional = cedict_entry.traditional
        pronounciation = cedict_entry.pronounciation
        meaning = cedict_entry.meaning
        entry = WordCardEntry(word, traditional, meaning, pronounciation)
        entries.append(entry)

    return entries


def write_cards_to_csv(cards, path):
    with open(path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(cards)


def main():
    download_data()

    cedict = parse_cedict()
    decompositions = parse_decompositions()
    characters = parse_frequency_list(CHARACTER_LIST)
    words = parse_frequency_list(WORD_LIST)

    character_cards = build_character_cards(cedict, characters, decompositions)
    word_cards = build_word_cards(cedict, words)

    write_cards_to_csv(character_cards, 'character_cards.csv')
    write_cards_to_csv(word_cards, 'word_cards.csv')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    main()
