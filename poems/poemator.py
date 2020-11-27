import random
import sys
from typing import Union, Optional, List, Tuple, Dict, Any, Iterable

from django.db.models import Q, QuerySet

from poems.analyse_verses import Syllabifier
from poems.online_rhymer import Rhymer, getting_word_type, find_first_letter
from poems.models import Verse, AssonantRhyme, ConsonantRhyme, Word


class PoemAutomator:
    """Types of lines: beginnings (com), intermediate (int), endings (fin) to iterate through"""
    VERSE_TYPES = ["is_beg", "is_int", "is_end"]

    def __init__(self, **kwargs):
        #  FROM KWARGS
        self.ver_num = kwargs.get("ver_num")  # type: int
        self.verse_length = kwargs.get("verse_length")  # type: List
        self.rhy_seq = kwargs.get("rhy_seq")  # type: str

        self.rhymes_to_use = kwargs.get("rhymes_to_use")  # type: Dict[str: Union[AssonantRhyme, ConsonantRhyme]]
        self.verses_available = {}  # type: Dict[str: QuerySet[Verse]]
        self.words_used = {}  # type: Dict[str: List[Word]]
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
        1. either user specified rhyme_sequence or we create totally random verses without rhyme
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
        """User either determined a integer A=value, B=a couple of values or C=a range"""
        self.rhy_seq = self.ver_num * "a"

        if isinstance(self.verse_length, range):  # Option C
            start = self.verse_length.start
            stop = self.verse_length.stop
            verses_to_use = Verse.objects.filter(verse_length__gte=start, verse_length__lte=stop)

        elif len(self.verse_length) > 1:  # Option B -> List of Ints
            query = Q(verse_length=self.verse_length[0])
            for ver_len in self.verse_length[1:]:
                query.add(Q(verse_length=ver_len), Q.OR)

            verses_to_use = Verse.objects.filter(query)

        else:  # Option A -> Single integer value
            verses_to_use = Verse.objects.filter(verse_length=self.verse_length[0])

        self.verses_available["a"] = verses_to_use

    def randomly_determine_rhymes(self) -> None:
        """If user didn't select any concrete rhymes -> choose random ones"""
        for key in self.rhymes_to_use.keys():
            limit = self.rhy_seq.count(key) * 3  # TODO Think about using the stranger ones

            if key == key.upper():  # Consonant
                word = random.choice(Word.objects.all())
                rhyme_object = word.consonant_rhyme
                while rhyme_object.amount_words < limit:  # TODO RETHINK THIS
                    word = random.choice(Word.objects.all())
                    rhyme_object = word.consonant_rhyme

            else:  # Assonant
                word = random.choice(Word.objects.all())
                rhyme_object = word.assonant_rhyme
                while rhyme_object.verse_number < limit:
                    word = random.choice(Word.objects.all())
                    rhyme_object = word.assonant_rhyme

            self.rhymes_to_use[key] = rhyme_object

        self.determine_verse_set()

    def user_determined_rhymes(self) -> None:
        """If user chose concrete rhymes: turn string-representation of rhyme into Consonant/Assonant (Rhyme)Objects"""
        for key in self.rhymes_to_use.keys():
            rhyme = self.rhymes_to_use[key]

            if key == key.upper():  # Uppercase letters correspond to consonant rhymes
                rhyme = determine_rhyme_input(rhyme, "consonant")
                rhyme_object = ConsonantRhyme.objects.get(consonant_rhyme=rhyme)

            else:  # Lowercase letters correspond to assonant rhymes
                rhyme = determine_rhyme_input(rhyme, "assonant")
                rhyme_object = AssonantRhyme.objects.get(assonant_rhyme=rhyme)

            self.rhymes_to_use[key] = rhyme_object

        self.determine_verse_set()

    def determine_verse_set(self) -> None:
        """Populates the self.verses_available dict with a QuerySet of models.Verse objects"""
        for key in self.rhymes_to_use.keys():
            rhyme_object = self.rhymes_to_use[key]

            words = rhyme_object.word_set.all()

            for word in words:
                verses_to_use = word.verse_set.filter(verse_length=self.verse_length)
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

    @property
    def ver_num(self) -> int:
        return self._ver_num

    @ver_num.setter
    def ver_num(self, value: str) -> None:
        self._ver_num = random.randint(4, 16) if not value else int(value)

    @property
    def verse_length(self) -> Union[List, Iterable]:
        return self._verse_length

    @verse_length.setter
    def verse_length(self, value: str) -> None:
        if not value:
            a, b = random.randint(4, 14), random.randint(4, 14)
            self._verse_length = range(a, b) if a < b else range(b, a)
        else:
            self._verse_length = [int(num) for num in value.split(",")]

    @property
    def rhy_seq(self):
        return self._rhy_seq

    @rhy_seq.setter
    def rhy_seq(self, value):
        self._rhy_seq = value


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


def determine_rhyme_input(rhyme: str, rhyme_type: str) -> str:
    """Determine rhyme based on input. If rhyme = '-ae' -> 'ae'; if rhyme = 'word' -> 'ord' """
    if rhyme.startswith("-"):
        return rhyme.strip("-")

    if rhyme_type == "assonant":
        return Syllabifier(rhyme).assonant_rhyme

    return Syllabifier(rhyme).consonant_rhyme


def main():
    num_ver, ver_len, rhy_seq = sys.argv[1:]

    poemator = PoemAutomator(num_ver=num_ver, ver_len=ver_len, rhy_seq=rhy_seq)
    poemator.control_branches()
    poem = poemator.poem_generator()
    poem = [verse.verse_text if verse != "" else "" for verse in poem]
    print("\n".join(poem))

if __name__ == "__main__":
    main()
