# imports
import random
import string
from poems.analyse_verses import Syllabifier
from poems.help_funcs import last_word_finder, decapitalize, assonant_rhyme_finder
from poems.online_rhymer import Rhymer, getting_word_type, find_first_letter
from poems.models import fetch_verses, fetch_rhyme, Verse


class PoemAutomator:
    """Types of lines: beginnings (com), intermediate (int), endings (fin) to iterate through"""
    TYPES_VERSES = ["beg", "int", "end"]

    def __init__(self, select_verses=False, **kwargs):
        self.num_verses = kwargs.get("verse_num")
        # TODO --> range #if len(long_ver) == 1: #  self.long_verses = long_ver[0]#else:#  self.long_verses = long_ver
        if "verse_length" in kwargs:
            self.long_verses = kwargs.get("verse_length")
        if "rhy_seq" in kwargs:
            self.rhy_seq = kwargs.get("rhy_seq")

        self.verses_to_use, self.rhymes_to_use, self.words_used = self.populate_dicts()

        if select_verses:
            for key in self.rhymes_to_use.keys():
                self.rhymes_to_use[key] = kwargs.get[key]

    def populate_dicts(self):
        """verses_to_use -> DICT -> {RHYME_CODE: TUPLE(verse, last_word, beg, int, end)} from DB
           rhymes_to_use -> DICT -> {RHYME_CODE: str} -> Example: {A: "ado", B: "es"}
           words_used -> DICT -> {RHYME_CODE: LIST[last_word, last_word], RHYME_CODE: LIST[last_word, etc]}"""

        verses_to_use = {}
        rhymes_to_use = {}
        words_used = {}

        for rhyme_code in self.rhy_seq:
            if rhyme_code != " ":
                verses_to_use[rhyme_code] = []
                rhymes_to_use[rhyme_code] = ""
                words_used[rhyme_code] = []

        return verses_to_use, rhymes_to_use, words_used

    def user_determined_rhymes(self):
        """Populates the rhymes_to_use dict if the user wants to decide the rhyme-endings beforehand"""
        for key in self.rhymes_to_use.keys():
            if key == key.upper():
                # Uppercase letters correspond to consonant rhymes

                if not self.rhymes_to_use[key.lower()]:
                    self.rhymes_to_use[key] = input(f"Rima consonante {key}: -")

                    verses_to_use = fetch_verses(verse_length=self.long_verses,
                                                 cons_rhy=self.rhymes_to_use[key],
                                                 unique=True)

                    while not verses_to_use:
                        self.rhymes_to_use[key] = input(
                            f"La rima consonante que has especificado no existe en la base de datos. Prueba de nuevo: ")

                        verses_to_use = fetch_verses(verse_length=self.long_verses,
                                                     cons_rhy=self.rhymes_to_use[key],
                                                     unique=True)

                    self.verses_to_use[key] = verses_to_use

                else:
                    #  Here the consonant rhyme must be a subset of the assonant rhyme: abba ABBA -> A ⊆ a, B ⊆ b, etc

                    self.rhymes_to_use[key] = input(
                        f"Rima consonante {key} (ha de rimar asonantemente con -> {key.lower()}): -"
                    )

                    while not Syllabifier(self.rhymes_to_use[key]).assonant_rhyme == self.rhymes_to_use[key.lower()]:
                        self.rhymes_to_use[key] = input(
                            f"Rima consonante {key} (HA DE RIMAR ASONANTEMENTE CON -> {key.lower()}): -"
                        )

                    verses_to_use = fetch_verses(verse_length=self.long_verses,
                                                 cons_rhy=self.rhymes_to_use[key],
                                                 unique=True)

                    self.verses_to_use[key] = verses_to_use

            else:
                #  lowercase letter corresponds to assonant rhymes

                if not self.rhymes_to_use[key.upper()]:
                    #  There is no corresponding consonant rhyme to the given assonant one.

                    self.rhymes_to_use[key] = input(f"Rima asonante {key}: -")

                    verses_to_use = fetch_verses(verse_length=self.long_verses,
                                                 asson_rhy=self.rhymes_to_use[key],
                                                 unique=True)
                    while not verses_to_use:
                        self.rhymes_to_use[key] = input(
                            f"La rima asonante que has especificado no existe en la base de datos. Prueba de nuevo: ")

                        verses_to_use = fetch_verses(verse_length=self.long_verses,
                                                     asson_rhy=self.rhymes_to_use[key],
                                                     unique=True)

                    self.verses_to_use[key] = verses_to_use

                else:
                    #  Assonant rhyme that corresponds to a certain consonant one. A -> a, B -> b, etc

                    cons_rhyme = self.rhymes_to_use[key.upper()]
                    asson_rhyme = assonant_rhyme_finder(cons_rhyme)

                    self.rhymes_to_use[key] = asson_rhyme

                    self.verses_to_use[key] = fetch_verses(verse_length=self.long_verses,
                                                           asson_rhy=asson_rhyme,
                                                           unique=True)

    def random_rhymes(self):
        for key in self.rhymes_to_use.keys():
            cons = True if key == key.upper() else False
            limit = self.rhy_seq.count(key) + (self.rhy_seq.count(key) / 2)
            rhyme_to_use = fetch_rhyme(self.long_verses, limit=limit, cons=cons)

            if cons:
                verses_to_use = fetch_verses(verse_length=self.long_verses, cons_rhy=rhyme_to_use, unique=True)
            else:
                verses_to_use = fetch_verses(verse_length=self.long_verses, asson_rhy=rhyme_to_use, unique=True)

            while len(verses_to_use) < self.rhy_seq.count(key):
                rhyme_to_use = fetch_rhyme(self.long_verses, limit=self.rhy_seq.count(key), cons=cons)
                if cons:
                    verses_to_use = fetch_verses(verse_length=self.long_verses, cons_rhy=rhyme_to_use, unique=True)
                else:
                    verses_to_use = fetch_verses(verse_length=self.long_verses, asson_rhy=rhyme_to_use, unique=True)

            self.rhymes_to_use[key] = rhyme_to_use
            self.verses_to_use[key] = verses_to_use

    def poem_generator(self):
        poem = []

        for i, rhyme_code in enumerate(self.rhy_seq):
            if rhyme_code == " ":
                poem[-1] = poem[-1] + "\n"
                continue

            else:
                type_verse = self.type_determiner(poem)
                verse = self.select_verse_with_rhyme(rhyme_code, type_verse)

            poem.append(verse)

        return "\t" + "\n\t".join(poem)

    def select_verse_with_rhyme(self, rhyme_code, type_verse):
        verses = [verse for verse in self.verses_to_use[rhyme_code] if verse[type_verse]]

        try:
            verse = random.choice(verses)

        except IndexError:
            new_type = change_type(type_verse)
            verses = [verse for verse in self.verses_to_use[rhyme_code] if verse[new_type]]

            try:
                verse = random.choice(verses)
                self.delete_verse_from_verses_to_use(rhyme_code, verse)

                verse_text = changes_after_type_change(verse[3], type_verse, new_type)
                self.words_used[rhyme_code].append(verse[4])
                return verse_text

            except IndexError:
                type_verse_kw = {"is_beg": True} if type_verse == 0 else {"is_int": True} if type_verse == 1 else {
                    "is_end": True}
                rhyme_to_use_now = fetch_rhyme(self.long_verses, limit=10)
                verses = fetch_verses(verse_length=self.long_verses,
                                      cons_rhy=rhyme_to_use_now,
                                      **type_verse_kw)

                verse = random.choice(verses)  # This Verse is a random verse with anther rhyme.

                word_to_rhyme_with = random.choice(self.words_used[rhyme_code])
                rhy_type = "c" if rhyme_code.upper() == rhyme_code else "a"
                num_syll = Syllabifier(verse.last_word).syllables
                last_word_type = getting_word_type(verse.last_word)
                first_letter = find_first_letter(verse.last_word)

                words_used = []
                for word_list in self.words_used.values():
                    for word in word_list:
                        words_used.append(word)

                new_word = online_rhyme_finder(word_to_rhyme_with,
                                               rhy_type,
                                               num_syll,
                                               first_letter,
                                               last_word_type,
                                               words_used)

                verse_last_word = last_word_finder(verse[3])
                verse_text = verse[3].replace(verse_last_word, new_word)

                self.words_used[rhyme_code].append(new_word)

                return verse_text

        self.delete_verse_from_verses_to_use(rhyme_code, verse)

        #  Add last_word to self.words_used and return the verse to poem_random_generator
        self.words_used[rhyme_code].append(verse[4])
        verse_text = verse[3]
        return verse_text

    def delete_verse_from_verses_to_use(self, rhyme_code, verse):
        verse_index = self.verses_to_use[rhyme_code].index(verse)
        del self.verses_to_use[rhyme_code][verse_index]

    def type_determiner(self, poem):
        """Returns 0, 1 or 2 depending on which kind of verse we need at each moment. The number stands for the index
        of 'beg', 'int' and 'end' in self.verses_to_use. Tuple(verse, last_word, beg, int, end)"""

        if len(poem) == 0:
            return 0

        elif len(poem) == self.num_verses - 1:
            return 2

        elif poem[-1].endswith("."):
            return 0

        else:
            return 1


def online_rhyme_finder(word, rhyme_type, syllables, first_letter=None, word_type=None, words_used=None):
    rhymes_object = Rhymer(word, rhyme_type, syllables, first_letter, word_type, words_used)
    rhymes_list = rhymes_object.getting_cronopista()

    if rhymes_list:
        return rhymes_list[0]

    else:
        print("Yo que sé, joder")


def change_type(type_verse):
    """Possible solutions:
    1. Convert other kinds of lines into the one whe needs (com -> int, com -> fin etc.)
    3. Try RegEx for different but similar rhymes -> another script!
    4. Another length of verse -> maybe here after the other fail."""

    new_type = (type_verse + 1) % 2
    """  self.TYPES_VERSES = ["beg", "int", "end"]   
            'beg' -> 'int'
            'int' -> 'beg'
            'end' -> 'int'      """

    return new_type


def changes_after_type_change(verse, old_type, new_type):
    if new_type == 0:
        # new 'beg' -> old 'int'
        return decapitalize(verse, strict=False)

    elif new_type == 1 and old_type == 0:
        # new 'int' -> old 'beg'
        return verse.capitalize()

    # new 'int' -> old 'end'
    return verse.rstrip(string.punctuation) + "."


if __name__ == "__main__":
    pass
