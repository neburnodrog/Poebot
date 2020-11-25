import random
import sys
from typing import List, Dict

from django.db.models import Q

from poems.analyse_verses import Syllabifier
from poems.online_rhymer import Rhymer, getting_word_type, find_first_letter
from poems.models import Verse, AssonantRhyme, ConsonantRhyme


class PoemAutomator:
    """Types of lines: beginnings (com), intermediate (int), endings (fin) to iterate through"""
    VERSE_TYPES = ["is_beg", "is_int", "is_end"]

    def __init__(self, **kwargs):
        #  FROM KWARGS
        self.ver_num = kwargs.get("ver_num")  # TODO --> range #if len(long_ver) == 1: #  self.verse_length = long_ver[0]#else:#  self.verse_length = long_ver
        self.verse_length = kwargs.get("verse_length")
        self.rhy_seq = kwargs.get("rhy_seq")
        self.rhymes_to_use = kwargs.get(
            "rhymes_to_use")  # rhymes_to_use -> DICT -> {RHYME_CODE: str|RhymeObjects} -> Example: {A: "ado", B: "es"}

        self.verses_available = {}  # verses_available -> DICT -> {RHYME_CODE: models.Verse-QuerySet}
        self.words_used = {}  # DICT -> {RHYME_CODE: List[words]}

        #  IF KW-ARG EMPTY
        self.fill_and_clean_init_kwargs()

    def fill_and_clean_init_kwargs(self) -> None:
        self.ver_num = random.randint(4, 16) if not self.ver_num else int(self.ver_num)

        # TODO -> NORMALIZE verse_length to be a List -> [7] OR from range -> [7, 8, 9, 10] OR  -> [7, 11]
        if not self.verse_length:
            a, b = random.randint(4, 14), random.randint(4, 14)
            self.verse_length = [i for i in range(a, b)] if a < b else [i for i in range(b, a)]
        else:
            self.verse_length = int(self.verse_length)

        self.populate_dicts()

    def populate_dicts(self) -> None:
        to_populate = [self.verses_available, self.words_used]
        if not self.rhymes_to_use:
            self.rhymes_to_use = {}
            to_populate.append(self.rhymes_to_use)

        if self.rhy_seq:
            for rhyme_code in set(self.rhy_seq):
                if rhyme_code != " ":
                    for dict_elem in to_populate:
                        dict_elem[rhyme_code] = None
        else:
            for dict_elem in to_populate:
                dict_elem["a"] = None

    def control_branches(self) -> None:
        """Control flow:
        1. either rhyme_sequence or random verses
        2. either user determined or random rhymes"""
        if not self.rhy_seq:
            self.random_verses()

        else:
            for key in self.rhymes_to_use:
                if not self.rhymes_to_use[key]:
                    self.randomly_determine_rhymes()
                    break
                self.user_determined_rhymes()
                break

    def random_verses(self):
        pass

    def user_determined_rhymes(self) -> None:
        """If user chose concrete rhymes: turn string-representation of rhyme into Consonant/Assonant (Rhyme)Objects"""
        for key in self.rhymes_to_use.keys():
            rhyme = self.rhymes_to_use[key]
            rhyme_syllabified = Syllabifier(rhyme)

            if key == key.upper():  # Uppercase letters correspond to consonant rhymes
                rhyme_object = ConsonantRhyme.objects.get(consonant_rhyme=rhyme_syllabified.consonant_rhyme)

            else:  # Lowercase letters correspond to assonant rhymes
                rhyme_object = AssonantRhyme.objects.get(assonant_rhyme=rhyme_syllabified.assonant_rhyme)

            self.rhymes_to_use[key] = rhyme_object

        self.determine_verse_set()

    def randomly_determine_rhymes(self) -> None:
        """If user didn't select any concrete rhymes -> choose a random ones"""
        for key in self.rhymes_to_use.keys():
            limit = self.rhy_seq.count(key) * 3  # TODO Think about using the stranger ones

            if key == key.upper():
                verse = random.choice(Verse.objects.all())
                rhyme_object = verse.cons_rhy
                while rhyme_object.verse_number < limit:
                    verse = random.choice(Verse.objects.all())
                    rhyme_object = verse.cons_rhy

            else:
                verse = random.choice(Verse.objects.all())
                rhyme_object = verse.asson_rhy
                while rhyme_object.verse_number < limit:
                    verse = random.choice(Verse.objects.all())
                    rhyme_object = verse.asson_rhy

            self.rhymes_to_use[key] = rhyme_object

        self.determine_verse_set()

    def determine_verse_set(self) -> None:
        """Populates the self.verses_available dict with a QuerySet of models.Verse objects"""
        for key in self.rhymes_to_use.keys():
            rhyme_object = self.rhymes_to_use[key]

            verses_to_use = rhyme_object.verse_set.all().filter(verse_length=self.verse_length)
            self.verses_available[key] = verses_to_use

    def poem_generator(self) -> List[Verse]:
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

    def select_verse_with_rhyme(self, rhyme_code: str, verse_types: Dict) -> Verse:
        verses = self.verses_available[rhyme_code]
        verses_w_type = verses.filter(**verse_types)

        verses_filtered = verses_w_type

        if self.words_used[rhyme_code]:
            for word in self.words_used[rhyme_code]:
                verses_filtered = verses_filtered.filter(**verse_types).exclude(last_word=word)

        if verses_filtered:
            verse_object = random.choice(verses_filtered)

            self.verses_available[rhyme_code] = verses.filter().exclude(id=verse_object.id)
            self.words_used[rhyme_code] = verse_object.last_word

            return verse_object

        else:
            """Find a different word that rhymes and then substitute"""
            word_to_rhyme_with = random.choice(self.words_used[rhyme_code])
            rhy_type = "c" if rhyme_code.upper() == rhyme_code else "a"

            new_words_list = online_rhyme_finder(word=word_to_rhyme_with,
                                                 rhyme_type=rhy_type,
                                                 words_used=self.words_used[rhyme_code])

            for word in new_words_list:
                syllables_new_word = Syllabifier(word).syllables
                type_new_word = getting_word_type(word)  # 0: Noun or Adjetive, 1: Verb
                first_letter_new_word = find_first_letter(word)

                verse_to_use = random.choice(verses_w_type)

                i = 0
                while (Syllabifier(verse_to_use.last_word).syllables != syllables_new_word
                       and getting_word_type(verse_to_use.last_word) != type_new_word
                       and first_letter_new_word != find_first_letter(verse_to_use.last_word)):
                    verse_to_use = random.choice(verses_w_type)
                    if i == 40:
                        break

            if (Syllabifier(verse_to_use.last_word).syllables == syllables_new_word
                       and getting_word_type(verse_to_use.last_word) == type_new_word
                       and first_letter_new_word == find_first_letter(verse_to_use.last_word)):
                new_word = word

            else:
                new_word="It all failed... troubleshooting this at some point"
            #  Now change the new_word for the old one in verse_to_use
            new_verse_text = verse_to_use.verse_text.replace(verse_to_use.last_word, new_word)
            new_verse_object = save_new_verse_object(new_verse_text)

            self.words_used[rhyme_code] = new_word
            return new_verse_object

    def type_determiner(self, poem: List[Verse]) -> Dict:
        """Returns a list of booleans. True or False representing [is_beg, is_int, is_end]"""

        if len(poem) == 0 or poem[-1].verse_text.endswith("."):
            types_dict = {"is_beg": True, "is_int": False}

        elif len(poem) == self.ver_num - 1:
            types_dict = {"is_int": False, "is_end": True}

        else:
            types_dict = {"is_int": True}

        return types_dict


def online_rhyme_finder(**kwargs) -> List[str]:
    rhymes_object = Rhymer(**kwargs)
    rhymes_list = rhymes_object.getting_cronopista()

    if rhymes_list:
        return rhymes_list

    else:
        word = kwargs.get("word")
        rhyme_type = kwargs.get("rhyme_type")
        words_used = kwargs.get("words_used")

        rhymes_object = Rhymer(word=word, rhyme_type=rhyme_type, words_used=words_used, first_letter="I")
        rhymes_list = rhymes_object.getting_cronopista()

        if rhymes_list:
            return rhymes_list

        else:
            return ["Qué coño voy a saber yo.. joder"]


def change_type(verse_types):
    pass
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


def save_new_verse_object(new_verse_text: str) -> Verse:
    verse_analysed = Syllabifier(new_verse_text)
    try:
        assonant_object = AssonantRhyme.objects.get(assonant_rhyme=verse_analysed.assonant_rhyme)
    except AssonantRhyme.DoesNotExist:
        assonant_object = AssonantRhyme.objects.create(assonant_object=verse_analysed.assonant_rhyme)

    try:
        consonant_object = ConsonantRhyme.objects.get(consonant_rhyme=verse_analysed.consonant_rhyme)
    except AssonantRhyme.DoesNotExist:
        consonant_object = ConsonantRhyme.objects.create(consonant_rhyme=verse_analysed.consonant_rhyme)

    new_verse = Verse.objects.create(verse_text=verse_analysed.sentence,
                                     verse_length=verse_analysed.syllables,
                                     last_word=verse_analysed.last_word,
                                     is_beg=verse_analysed.beg,
                                     is_int=verse_analysed.int,
                                     is_end=verse_analysed.end,
                                     asson_rhy=assonant_object,
                                     cons_rhy=consonant_object,
                                     )

    new_verse.save()
    return new_verse


def main():
    num_ver, ver_len, rhy_seq = sys.argv[1:]

    poemator = PoemAutomator(num_ver=num_ver, ver_len=ver_len, rhy_seq=rhy_seq)
    poemator.setup()
    poem = poemator.poem_generator()
    poem = [verse.verse_text if verse != "" else "" for verse in poem]
    print("\n".join(poem))

if __name__ == "__main__":
    main()
