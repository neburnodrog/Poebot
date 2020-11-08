# imports
import random
import string
import datetime
from os import path, mkdir
from .analyse_verses import Syllabifier
from .help_funcs import last_word_finder, decapitalize, assonant_rhyme_finder
from data.online_rhymer import Rhymer, getting_word_type, find_first_letter
from data.db_funcs import fetch_verses, fetch_rhyme, is_subset_of
from typing import Tuple, List, Optional, Dict, Any

Verse = Tuple[bool, bool, bool, str, str]
punct = string.punctuation + " ¡¿"
vowels = "aeiouáéíóúÁÉÍÓÚAEIOU"


class PoemAutomator:
    """Types of lines: beginnings (com), intermediate (int), endings (fin) to iterate through"""
    TYPES_VERSES = ["beg", "int", "end"]

    def __init__(self, num_ver: int, long_ver: List, rhy_sequence: str) -> None:
        """User-defined variables
        num_verses -> INT -> 7. Number of verses in the final poem
        long_verses -> INT -> 8. Possibility RANGES in the FUTURE: 5-7 (5<=long<=7)
        rhy_seq -> STR -> "ABAB BABA" -> Each character is a RHYME_CODE. Space = emptyline"""

        self.num_verses = num_ver

        if len(long_ver) == 1:
            self.long_verses = long_ver[0]
        else:
            self.long_verses = long_ver
        self.rhy_seq = rhy_sequence
        self.verses_to_use, self.rhymes_to_use, self.words_used = self.populate_dicts()

    def populate_dicts(self) -> Tuple[Dict, Dict, Dict]:
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

    def user_determined_rhymes(self) -> None:
        """Populates the rhymes_to_use dict if the user wants to decide the rhyme-endings beforehand"""
        for key in self.rhymes_to_use.keys():
            if key == key.upper():
                # Uppercase letters correspond to consonant rhymes

                if not self.rhymes_to_use[key.lower()]:
                    self.rhymes_to_use[key] = input(f"Rima consonante {key}: -")

                    verses_to_use = fetch_verses(self.long_verses, self.rhymes_to_use[key], cons=True, unique=True)
                    while not verses_to_use:
                        self.rhymes_to_use[key] = input(
                            f"La rima consonante que has especificado no existe en la base de datos. Prueba de nuevo: ")

                        verses_to_use = fetch_verses(self.long_verses, self.rhymes_to_use[key], cons=True, unique=True)

                    self.verses_to_use[key] = verses_to_use

                else:
                    #  Here the consonant rhyme must be a subset of the assonant rhyme: abba ABBA -> A ⊆ a, B ⊆ b, etc

                    self.rhymes_to_use[key] = input(
                        f"Rima consonante {key} (ha de rimar asonantemente con -> {key.lower()}): -"
                    )

                    while not is_subset_of(self.long_verses, self.rhymes_to_use[key.lower()], self.rhymes_to_use[key]):
                        self.rhymes_to_use[key] = input(
                            f"Rima consonante {key} (HA DE RIMAR ASONANTEMENTE CON -> {key.lower()}): -"
                        )

                    verses_to_use = fetch_verses(self.long_verses, self.rhymes_to_use[key], cons=True, unique=True)

                    self.verses_to_use[key] = verses_to_use

            else:
                #  lowercase letter corresponds to assonant rhymes

                if not self.rhymes_to_use[key.upper()]:
                    #  There is no corresponding consonant rhyme to the given assonant one.

                    self.rhymes_to_use[key] = input(f"Rima asonante {key}: -")

                    verses_to_use = fetch_verses(self.long_verses, self.rhymes_to_use[key], cons=False, unique=True)
                    while not verses_to_use:
                        self.rhymes_to_use[key] = input(
                            f"La rima asonante que has especificado no existe en la base de datos. Prueba de nuevo: ")

                        verses_to_use = fetch_verses(self.long_verses, self.rhymes_to_use[key], cons=False, unique=True)

                    self.verses_to_use[key] = verses_to_use

                else:
                    #  Assonant rhyme that corresponds to a certain consonant one. A -> a, B -> b, etc

                    cons_rhyme = self.rhymes_to_use[key.upper()]
                    asson_rhyme = assonant_rhyme_finder(cons_rhyme)

                    self.rhymes_to_use[key] = asson_rhyme

                    self.verses_to_use[key] = fetch_verses(self.long_verses, asson_rhyme, cons=False, unique=True)

    def random_rhymes(self) -> None:
        for key in self.rhymes_to_use.keys():
            cons = True if key == key.upper() else False
            limit = self.rhy_seq.count(key) + (self.rhy_seq.count(key) / 2)
            rhyme_to_use = fetch_rhyme(self.long_verses, limit, cons=cons)
            verses_to_use = fetch_verses(self.long_verses, rhyme_to_use, cons=cons, unique=True)
            while len(verses_to_use) < self.rhy_seq.count(key):
                rhyme_to_use = fetch_rhyme(self.long_verses, self.rhy_seq.count(key), cons=cons)
                verses_to_use = fetch_verses(self.long_verses, rhyme_to_use, cons=cons, unique=True)

            self.rhymes_to_use[key] = rhyme_to_use
            self.verses_to_use[key] = verses_to_use

    def poem_generator(self) -> str:
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

    def select_verse_with_rhyme(self, rhyme_code: str, type_verse: int) -> str:
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
                type_str = "beg" if type_verse == 0 else "int" if type_verse == 1 else "end"
                rhyme_to_use_now = fetch_rhyme(self.long_verses, 10)
                verses = fetch_verses(self.long_verses,
                                      rhyme_to_use_now,
                                      type_verse=type_str)

                verse = random.choice(verses)  # This Verse is a random verse with anther rhyme.
                last_word = verse[4]  # The new word need the same number of syllables and the same type as this one.

                word_to_rhyme_with = random.choice(self.words_used[rhyme_code])
                rhy_type = "c" if rhyme_code.upper() == rhyme_code else "a"
                num_syll = Syllabifier(last_word).syllables
                last_word_type = getting_word_type(last_word)
                first_letter = find_first_letter(last_word, sentence=verse[3])

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

    def delete_verse_from_verses_to_use(self, rhyme_code: str, verse: Verse) -> None:
        verse_index = self.verses_to_use[rhyme_code].index(verse)
        del self.verses_to_use[rhyme_code][verse_index]

    def type_determiner(self, poem: List[str]) -> int:
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


def online_rhyme_finder(word: str,
                        rhyme_type: str,
                        syllables: int,
                        first_letter: Optional[str] = None,
                        word_type: Optional[str] = None,
                        words_used: Optional[List] = None) -> str:

    rhymes_object = Rhymer(word, rhyme_type, syllables, first_letter, word_type, words_used)
    rhymes_list = rhymes_object.getting_cronopista()

    if rhymes_list:
        return rhymes_list[0]

    else:
        print("Yo que sé, joder")


def change_type(type_verse: int) -> int:
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


def changes_after_type_change(verse: str, old_type: int, new_type: int) -> str:
    if new_type == 0:
        # new 'beg' -> old 'int'
        return decapitalize(verse, strict=False)

    elif new_type == 1 and old_type == 0:
        # new 'int' -> old 'beg'
        return verse.capitalize()

    # new 'int' -> old 'end'
    return verse.rstrip(string.punctuation) + "."


def save_poem(poem: str) -> None:
    abs_path = path.dirname(__file__)
    rel_path = "poemas/"
    _path = path.join(abs_path, rel_path)
    if not path.exists(_path):
        mkdir(_path)

    poem_name = input("\nWould you like to give the poem a name? (Leave blank otherwise): ")
    if poem_name:
        file_name = f"{_path}{poem_name}.txt"
        with open(file_name, "w") as f:
            print(poem, file=f)

    else:
        now = datetime.datetime.now()
        file_name = f"{_path}poema{now.strftime('%H:%M:%S_%d-%m-%Y')}.txt"
        with open(file_name, "w") as f:
            print(poem, file=f)

    print(f"[+] Saved poem at path {file_name}")


def getting_inputs() -> Tuple[int, List, str]:
    number_verses = input("Número de versos: ")
    while not number_verses.isdigit():
        number_verses = input(
            "La variable number_verses solo puede contener valores numéricos: "
        )

    number_verses = int(number_verses)

    while True:
        size_verses = input(
            "Longitud de los versos en sílabas (O intervalo: 7-9 para versos de 7 a 9 sílabas): "
        ).strip(" -").split("-")

        while not all(elem.isdigit() for elem in size_verses):
            size_verses = input("""La variable size_verses solo puede contener valores numéricos 
                                   o el guión que separa los márgenes de un intervalo: """).strip(" -").split("-")

        size_verses = [int(digit) for digit in size_verses]

        if len(size_verses) == 2:
            if not 3 < size_verses[0] and size_verses[1] < 17:
                print("La longitud de los versos ha de ser entre 4 y 16 sílabas.")
                continue
            break

        elif len(size_verses) == 1:
            if not 3 < size_verses[0] < 17:
                print("La longitud de los versos ha de ser entre 4 y 16 sílabas.")
                continue
            break

    rhyme_sequence = input("Secuencia de rimas (p.ej ABBA): ")
    while int(number_verses) != len([seq for seq in rhyme_sequence if seq != " "]):
        rhyme_sequence = input(
            "Secuencia de rimas (Debe ser igual de larga que el número de versos explicitado anteriormente): "
        )

    return number_verses, size_verses, rhyme_sequence


def create_poem() -> None:
    num_ver, long_ver, rhy_seq = getting_inputs()

    poem = PoemAutomator(num_ver, long_ver, rhy_seq)

    self_decide = input("Quieres elegir las rimas? [Y/N]: ")
    if self_decide.strip().upper() == "Y":
        poem.user_determined_rhymes()
    else:
        poem.random_rhymes()

    generated_poem = poem.poem_generator()
    print(generated_poem)

    save = input("\nWould you like to save this poem? [Y/N]")
    if save.upper() == "Y":
        save_poem(generated_poem)


if __name__ == "__main__":
    create_poem()

    another = input("Would you like to create another poem? [Y/N]")
    if another.upper() == "Y":
        create_poem()
