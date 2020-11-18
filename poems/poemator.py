import random
import string
from typing import List, Dict

from django.db.models import Count, Q

from poems.analyse_verses import Syllabifier
from poems.help_funcs import last_word_finder, decapitalize
from poems.online_rhymer import Rhymer, getting_word_type, find_first_letter
from poems.models import Verse, AssonantRhyme, ConsonantRhyme


class PoemAutomator:
    """Types of lines: beginnings (com), intermediate (int), endings (fin) to iterate through"""
    VERSE_TYPES = ["is_beg", "is_int", "is_end"]

    def __init__(self, ver_num, **kwargs):
        self.ver_num = ver_num
        # TODO --> range #if len(long_ver) == 1: #  self.verse_length = long_ver[0]#else:#  self.verse_length = long_ver
        self.verse_length = kwargs.get("verse_length")
        self.rhy_seq = kwargs.get("rhy_seq")

        self.verses_available, self.rhymes_to_use, self.words_used = self.populate_dicts()

        if kwargs.get("select_verses"):
            for key in self.rhymes_to_use.keys():
                self.rhymes_to_use[key] = kwargs.get(key)

    def populate_dicts(self):
        """verses_available -> DICT -> {RHYME_CODE: models.Verse-QuerySet}
           rhymes_to_use -> DICT -> {RHYME_CODE: str|RhymeObjects} -> Example: {A: "ado", B: "es"}
           words_used -> DICT -> {RHYME_CODE: List[last_word, last_word], RHYME_CODE: List[last_word, etc]}"""

        verses_available = {}
        rhymes_to_use = {}
        words_used = []

        for rhyme_code in self.rhy_seq:
            if rhyme_code != " ":
                verses_available[rhyme_code] = []
                rhymes_to_use[rhyme_code] = ""

        return verses_available, rhymes_to_use, words_used

    def user_determined_rhymes(self):
        """If user chose concrete rhymes: turn string-representation of rhyme into Consonant/Assonant (Rhyme)Objects"""
        for key in self.rhymes_to_use.keys():
            rhyme = self.rhymes_to_use[key]

            if key == key.upper():  # Uppercase letters correspond to consonant rhymes
                rhyme_object = ConsonantRhyme.objects.get(consonant_rhyme=rhyme)

            else:  # Lowercase letters correspond to assonant rhymes
                rhyme_object = AssonantRhyme.objects.get(assonant_rhyme=rhyme)

            self.rhymes_to_use[key] = rhyme_object

        self.determine_verse_set()

    def determine_rhymes(self):
        """If user didn't select any concrete rhymes -> choose a random ones"""
        for key in self.rhymes_to_use.keys():
            limit = self.rhy_seq.count(key) * 2

            if key == key.upper():
                rhyme_candidates = ConsonantRhyme.objects.filter(verse_number__mt=limit)

            else:
                rhyme_candidates = AssonantRhyme.objects.filter(verse_number__mt=limit)

            rhyme_to_use = random.choice(rhyme_candidates)
            self.rhymes_to_use[key] = rhyme_to_use

        self.determine_verse_set()

    def determine_verse_set(self):
        """Populates the self.verses_available dict with a QuerySet of models.Verse objects"""
        for key in self.rhymes_to_use.keys():

            rhyme = self.rhymes_to_use[key]

            if key == key.upper():  # Uppercase letters correspond to consonant rhymes
                rhyme_object = ConsonantRhyme.objects.get(consonant_rhyme=rhyme)

            else:  # Lowercase letters correspond to assonant rhymes
                rhyme_object = AssonantRhyme.objects.get(assonant_rhyme=rhyme)

            verses_to_use = rhyme_object.verse_set.all().filter(verse_length=self.verse_length)
            self.verses_available[key] = verses_to_use

    def poem_generator(self):
        poem = []  # List of verses

        empty_lines_indexes = []  # Array to store the location of the empty verses.
        rhy_seq_list = list(self.rhy_seq)
        for i, rhyme_code in enumerate(rhy_seq_list):
            if rhyme_code == " ":
                empty_lines_indexes.append(i)

        rhy_seq = "".join(self.rhy_seq.split())  # Array without the empty characters.

        for i, rhyme_code in enumerate(rhy_seq):
            verse_type = self.type_determiner(poem)
            verse = self.select_verse_with_rhyme(rhyme_code, verse_type)
            poem.append(verse)

        # inserting the stored empty verses
        for i in empty_lines_indexes:
            poem.insert(i, "")

        return poem

    def select_verse_with_rhyme(self, rhyme_code, verse_types):
        verses = self.verses_available[rhyme_code]

        verses_w_type = verses.filter(**verse_types)

        if verses_w_type:
            verse = random.choice(verses_w_type)

            self.words_used.append(verse.last_word)
            self.verses_available[rhyme_code] = verses.filter().exclude(last_word=verse.last_word)
            return verse

        else:
            """Choose a different verse object and change its final word for one that matches our current rhyme"""
            verses_to_choose_from = Verse.objects.filter(verse_length=self.verse_length, **verse_types)
            verse_to_use = random.choice(verses_to_choose_from)

            word_to_rhyme_with = random.choice(self.rhymes_to_use[rhyme_code].verse_set.all()).last_word
            rhy_type = "c" if rhyme_code.upper() == rhyme_code else "a"

            word_to_change = verse_to_use.last_word
            num_syll_word_to_change = Syllabifier(word_to_change).syllables
            word_to_change_type = getting_word_type(word_to_change)
            first_letter = find_first_letter(word_to_change)

            new_word = online_rhyme_finder(word=word_to_rhyme_with,
                                           rhyme_type=rhy_type,
                                           syllables=num_syll_word_to_change,
                                           first_letter=first_letter,
                                           word_type=word_to_change_type,
                                           words_used=self.words_used)

            #  Now change the new_word for the old one in verse_to_use
            new_verse_text = verse_to_use.verse_text.replace(word_to_change, new_word)
            new_verse_object = save_new_verse_object(new_verse_text)

            self.words_used.append(new_word)
            self.verses_available[rhyme_code] = verses.filter().exclude(last_word=new_word)

            return new_verse_object

    def type_determiner(self, poem: List) -> Dict:
        """Returns a list of booleans. True or False representing [is_beg, is_int, is_end]"""

        if len(poem) == 0 or poem[-1].endswith("."):
            types_dict = {"is_beg": True, "is_int": False}

        elif len(poem) == self.ver_num - 1:
            types_dict = {"is_int": False, "is_end": True}

        else:
            types_dict = {"is_int": True}

        return types_dict


def online_rhyme_finder(**kwargs):
    rhymes_object = Rhymer(**kwargs)
    rhymes_list = rhymes_object.getting_cronopista()

    if rhymes_list:
        return rhymes_list[0]

    else:
        print("Yo que sé, joder")


def change_type(verse_types):
    """Possible solutions:
    1. Convert other kinds of lines into the one whe needs (com -> int, com -> fin etc.)
    3. Try RegEx for different but similar rhymes -> another script!
    4. Another length of verse -> maybe here after the other fail."""

    #  For now return a new query
    if verse_types.get("is_beg"):
        query = Q(is_int=True)
        query.add(Q(is_end=True), Q.OR)
    elif verse_types.get("is_int"):
        query = Q(is_beg=True)
        query.add(Q(is_end=True), Q.OR)
    else:
        query = Q(is_int=True)
        query.add(Q(is_beg=True), Q.OR)

    return query




def save_new_verse_object(new_verse_text):
    verse_analysed = Syllabifier(new_verse_text)
    new_verse = Verse.objects.create(verse_text=verse_analysed.sentence,
                                     verse_length=verse_analysed.syllables,
                                     last_word=verse_analysed.last_word,
                                     is_beg=verse_analysed.beg,
                                     is_int=verse_analysed.int,
                                     is_end=verse_analysed.end,
                                     asson_rhy=AssonantRhyme.objects.get(assonant_rhyme=verse_analysed.assonant_rhyme),
                                     cons_rhy=ConsonantRhyme.objects.get(consonant_rhyme=verse_analysed.consonant_rhyme))

    new_verse.save()
    return new_verse


if __name__ == "__main__":
    pass
