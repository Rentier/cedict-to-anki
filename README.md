# cedict-to-anki

This script is used to create an Anki deck of all important words and characters. Most important here means that it has to appear in a frequency list. The list used here is [SUBTLEX-CH](https://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexch/). The dictionary used is [CC-CEDict](https://www.mdbg.net/chinese/dictionary?page=cedict).

## Why?

When I encounter new characters or words, then I do not want to spend time on creating new Anki cards. Instead, I built these two decks for characters and words programatically, import them once and suspend all of it. Instead of adding new cards, I just unsuspend them.

## Usage

You need to install Python and the `requests` module. Download `main.py` and run it, it takes care of grabbing the dictionary and word list for you. It will create two `.csv` files which can be imported into Anki. You can use the card design of the excellent [Chinese Support Addon](https://ankiweb.net/shared/info/1128979221).
