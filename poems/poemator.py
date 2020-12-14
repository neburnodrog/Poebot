import random
from re import finditer
from typing import Union, Optional, List, Dict, Iterable
################
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poemautomator.settings")
django.setup()
#################
from django.db.models import QuerySet
from poems.analyse_verses import Syllabifier
from poems.models import Verse, AssonantRhyme, ConsonantRhyme, Word


class PoemAutomator:
    def __init__(self, **kwargs):
        #  FROM KWARGS -> Possible keys: "ver_num", "verse_length", "rhy_seq", "rhymes_to_use"
        self.number_verses = kwargs.get("ver_num")  # type: int
        self.length_of_verses = kwargs.get("verse_length")  # type: List
        self.rhyme_sequence = RhymeSequence(kwargs.get("rhy_seq"), kwargs.get("rhymes_to_use"),
                                            self.number_verses)  # type: RhymeSequence

        #  Not from KWARGS
        self.wordset_available = WordSet(self.rhyme_sequence, self.length_of_verses)
        self.poem = self.poem_generator()

    @property
    def number_verses(self) -> int:
        return self._number_verses

    @number_verses.setter
    def number_verses(self, value: str) -> None:
        self._number_verses = random.randint(4, 16) if not value else int(value)

    @property
    def length_of_verses(self) -> Union[List, Iterable]:
        return self._length_of_verses

    @length_of_verses.setter
    def length_of_verses(self, value: str) -> None:
        if not value:
            a, b = random.randint(4, 14), random.randint(4, 14)
            self._length_of_verses = range(a, b) if a < b else range(b, a)
        elif "_" in value:
            a, b = value.split("_")
            self._length_of_verses = range(int(a), int(b))
        else:
            self._length_of_verses = [int(num) for num in value.split(",")]

    def poem_generator(self) -> List[Union[Verse, str]]:
        poem = []

        rhyme_sequence = self.rhyme_sequence.clean_rhyme_sequence

        for rhyme_code in rhyme_sequence:
            #  For each rhyme code in the sequence append a verse to self.poem
            if self.wordset_available.word_set:
                word = self.wordset_available.choose_word(rhyme_code)
                verse = self.select_verse(word, poem)
                while not verse:
                    verse = self.alternative_method_for_getting_id(word, poem, rhyme_code)

                self.wordset_available.exclude_word(verse.last_word, rhyme_code)
                poem.append(verse)

            else:
                type_verse = self.type_determiner(poem)
                verse = self.wordset_available.choose_verse_from_verseset(type_verse)

        # inserting the stored empty verses if any
        if empty_lines := self.rhyme_sequence.empty_lines:
            for i in empty_lines:
                poem.insert(i, "")

        return poem

    def select_verse(self, word: Word, poem: List[Union[Verse, str]]) -> Union[Verse, None]:
        verse_type = self.type_determiner(poem)

        if isinstance(self.length_of_verses, range):  # Option C
            start, stop = self.length_of_verses.start, self.length_of_verses.stop
            verses = word.verse_set.values_list("id").filter(**verse_type,
                                                             verse_length__gte=start,
                                                             verse_length__lte=stop)
        elif len(self.length_of_verses) > 1:
            verses = "something"
            pass  # TODO -> later

        else:
            verses = word.verse_set.values_list("id").filter(**verse_type,
                                                             verse_length=self.length_of_verses[0])

        if not verses:
            return None

        verse_id = random.choice(verses)[0]
        return Verse.objects.get(id=verse_id)

    def type_determiner(self, poem: List) -> Dict[str, bool]:
        """Returns a list of booleans. True or False representing [is_beg, is_int, is_end]"""

        types_dict = {}

        if len(poem) == 0 or poem[-1].is_end:
            types_dict["is_beg"] = True

        if len(poem) == self.number_verses - 1:
            types_dict["is_end"] = True

        if not types_dict.get("is_beg") and not types_dict.get("is_end"):
            types_dict["is_int"] = True

        return types_dict

    def alternative_method_for_getting_id(self, word: Word, poem: List, rhyme_code: str):
        """Find a different word that rhymes and then substitute"""
        wordset = self.wordset_available.word_set[rhyme_code]

        if wordset.count() > 10:
            i = 0
            while i < wordset.count():
                new_word = self.wordset_available.choose_word(rhyme_code)
                if new_word == word:
                    continue
                verse = self.select_verse(new_word, poem)
                if verse:
                    return verse
                i += 1

        else:
            wordset_list = list(wordset)

            for new_word in wordset_list:
                if new_word == word:
                    continue
                verse = self.select_verse(new_word, poem)

                if verse:
                    return verse


"""
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
                new_word = "It all failed... troubleshooting this at some point"
            #  Now change the new_word for the old one in verse_to_use
            new_verse_text = verse_to_use.verse_text.replace(verse_to_use.last_word, new_word)
            new_verse_object = save_new_verse_object(new_verse_text)
    
            self.words_used[rhyme_code] = new_word
            return new_verse_object"""


class RhymeSequence:
    def __init__(self, rhyme_sequence, user_rhymes, number_verses):
        self.rhyme_sequence = rhyme_sequence if rhyme_sequence else "_" * number_verses
        self.empty_lines = self.empty_lines_finder()
        self.clean_rhyme_sequence = list(self.rhyme_sequence.replace(" ", ""))
        self.user_rhymes = user_rhymes
        self.unique_rhymes_keys = set(self.clean_rhyme_sequence)
        self.rhyme_set = self.get_rhyme_set()

    def get_rhyme_set(self):
        if not self.user_rhymes:  # rhymes_to_use not defined by user
            if "_" in self.rhyme_sequence:  # AND rhy_seq not defined by user -> no rhymes at all
                return {"_": None}
            else:  # BUT rhy_seq defined by user (There are keys but we also need values)
                return self.randomly_determine_rhymes()
        else:  # just fetch the RhymesObjects defined by the user and populate self.rhyme_set with them
            return self.user_determined_rhymes()

    def randomly_determine_rhymes(self) -> Dict[str, Union[ConsonantRhyme, AssonantRhyme, None]]:
        rhyme_set = {}
        unique_rhymes = self.unique_rhymes_keys

        for key in unique_rhymes:
            limit = self.clean_rhyme_sequence.count(key) * 2  # TODO lower this value to use stranger rhymes

            if key == key.upper():  # if capital letter -> consonant rhyme
                words = Word.objects.values_list("consonant_rhyme_id").filter(
                    amount_verses__gte=limit,
                    consonant_rhyme__amount_words__gte=limit
                )
                cons_rhy_id = random.choice(words)[0]
                rhyme_object = ConsonantRhyme.objects.get(id=cons_rhy_id)

            else:  # Assonant
                words = Word.objects.values_list("assonant_rhyme_id").filter(
                    amount_verses__gte=limit,
                    assonant_rhyme__amount_words__gte=limit
                )
                asson_rhy_id = random.choice(words)[0]
                rhyme_object = AssonantRhyme.objects.get(id=asson_rhy_id)

            rhyme_set[key] = rhyme_object

        return rhyme_set

    def user_determined_rhymes(self) -> Dict[str, Union[ConsonantRhyme, AssonantRhyme, None]]:
        rhyme_set = {}
        rhyme_sequence = self.unique_rhymes_keys

        for key in rhyme_sequence:
            rhyme_string = self.user_rhymes[key]

            if key == key.upper():  # Uppercase letters correspond to consonant rhymes
                rhyme_string = self.determine_rhyme_input(rhyme_string, "consonant")
                rhyme_object = ConsonantRhyme.objects.get(consonant_rhyme=rhyme_string)

            else:  # Lowercase letters correspond to assonant rhymes
                rhyme_string = self.determine_rhyme_input(rhyme_string, "assonant")
                rhyme_object = AssonantRhyme.objects.get(assonant_rhyme=rhyme_string)

            rhyme_set[key] = rhyme_object

        return rhyme_set

    @staticmethod
    def determine_rhyme_input(rhyme: str, rhyme_type: str) -> str:
        """Determine rhyme based on input. If rhyme = '-ae' -> 'ae'; if rhyme = 'word' -> 'ord' """
        if rhyme.startswith("-"):
            return rhyme.strip("-")

        if rhyme_type == "assonant":
            return Syllabifier(rhyme).assonant_rhyme

        return Syllabifier(rhyme).consonant_rhyme

    def empty_lines_finder(self) -> Optional[List[int]]:
        if self.rhyme_sequence.count(" ") > 0:
            empty_lines_indexes = []  # Array to store the location of the empty verses.
            matches = finditer(" ", self.rhyme_sequence)
            for match in matches:
                empty_lines_indexes.append(match.regs[0][0])
            return empty_lines_indexes
        else:
            return None


class WordSet:
    def __init__(self, rhyme_sequence, verse_length):
        self.rhyme_sequence = rhyme_sequence
        self.word_set = self.which_word_set()  # type: Dict[str, QuerySet[Word]]
        if not self.word_set:
            self.verse_set = self.random_verses(verse_length)
        self.used_words = []  # type: List

    def which_word_set(self) -> Union[None, Dict[str, QuerySet[Word]]]:
        """Control flow:
        1. either user specified rhyme_sequence or we create totally random verses without rhyme
        2. either user determined or random rhymes"""
        if "_" in self.rhyme_sequence.rhyme_sequence:
            return None

        word_set = self.determine_word_set()
        return word_set

    @staticmethod
    def random_verses(verse_length: Union[List, range]) -> QuerySet[Verse]:
        """User either determined: integer A=value, B=a couple of values or C=a range"""
        if isinstance(verse_length, range):
            verses_to_use = Verse.objects.filter(
                verse_length__gte=verse_length.start,
                verse_length__lte=verse_length.stop,
            )
            return verses_to_use

        # if len(verse_length) > 1:
            #  Not yet implemented

        verses_to_use = Verse.objects.filter(
            verse_length=verse_length[0],
        )

        return verses_to_use

    def determine_word_set(self) -> Dict[str, QuerySet[Word]]:
        """Populates the self.words_available dict with a QuerySet of models.Words objects that matches the requirements"""
        word_set = {}
        rhyme_sequence = self.rhyme_sequence.unique_rhymes_keys

        for key in rhyme_sequence:
            rhyme_object = self.rhyme_sequence.rhyme_set[key]
            words_in_rhyme_object = rhyme_object.word_set.filter(amount_verses__gt=1)
            word_set[key] = words_in_rhyme_object

        return word_set

    def choose_word(self, rhyme_key) -> Word:
        word_id = self.get_random_word_id(rhyme_key)
        word = self.word_set[rhyme_key].get(id=word_id)
        return word

    def choose_verse_from_verseset(self, verse_type):
        verses = self.verse_set.values("id").filter(**verse_type)
        verse_id = random.choice(verses)
        verse = self.verse_set.get(id=verse_id)
        while verse.last_word in self.used_words:
            verse_id = random.choice(verses)
            verse = self.verse_set.get(id=verse_id)

        self.used_words.append(verse.last_word)
        return verse

    def get_random_word_id(self, rhyme_key: str) -> int:
        return random.choice(self.word_set[rhyme_key].values_list("id"))[0]

    def exclude_word(self, word, rhyme_key):
        self.word_set[rhyme_key] = self.word_set[rhyme_key].exclude(id=word.id)
        self.used_words.append(word)


'''
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
'''


def main():
    ver_num = input("Enter number of verses:").strip()
    verse_length = input("Enter length of verses (ex: 5 or 5_8 (range) or 5, 8 (list of possible length): ").strip()
    rhy_seq = input("Enter sequence of rhymes").strip()
    poem_automator = PoemAutomator(ver_num=ver_num, verse_length=verse_length, rhy_seq=rhy_seq)
    print("\n".join([verse.verse_text if isinstance(verse, Verse) else "" for verse in poem_automator.poem]))


if __name__ == "__main__":
    main()
