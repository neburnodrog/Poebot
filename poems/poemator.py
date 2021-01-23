import random
from pyverse import Pyverse
from re import finditer
from typing import Union, Optional, List, Dict, Set, Tuple, Any

from django.db.models.query import QuerySet

from poems.models import Verse, AssonantRhyme, ConsonantRhyme

from django.http import Http404


WordSetType = Dict[str, Dict[str, QuerySet[Verse]]]
RhymeSetType = Dict[str, Optional[Union[ConsonantRhyme, AssonantRhyme]]]


class PoemAutomator:
    def __init__(self, **kwargs):
        #  FROM KWARGS -> Possible keys: "ver_num", "verse_length", "rhy_seq", "rhymes_to_use"
        self.number_verses = kwargs.get("ver_num")
        self.verse_length = kwargs.get(
            "verse_length")
        self.verse_length_type = type(self.verse_length)
        self.rhyme_sequence = RhymeSequence(
            self,
            kwargs.get("rhy_seq"),
            kwargs.get("rhymes_to_use"),
        )

        #  Not from KWARGS
        self.wordset = WordSet(self)

        self.poem = []

    @property
    def number_verses(self) -> int:
        return self._number_verses

    @number_verses.setter
    def number_verses(self, value: str) -> None:
        self._number_verses = random.randint(
            4, 16) if not value else int(value)

    @property
    def verse_length(self) -> Union[List, range]:
        return self._verse_length

    @verse_length.setter
    def verse_length(self, value: str) -> None:
        if not value:
            a, b = random.randint(5, 14), random.randint(5, 14)
            self._verse_length = range(a, b) if a < b else range(b, a)

        #  elif "_" in value:
        #      a, b = value.split("_")
        #      self._verse_length = range(int(a), int(b))

        else:
            len_ver = [int(num) for num in value.split(",")]
            self._verse_length = len_ver[0] if len(len_ver) == 1 else len_ver

    def poem_generator(self):
        rhyme_sequence = self.rhyme_sequence.clean_rhyme_sequence

        for rhyme_code in rhyme_sequence:
            #  For each rhyme code in the sequence append a verse to self.poem
            if self.wordset.word_set:

                word, verses_set = self.wordset.get_verses_from_random_word(rhyme_code)
                verse = self.select_verse(verses_set)
                while not verse:
                    verse = self.alternative_method_for_getting_id(
                        word, rhyme_code)

                self.wordset.exclude_word(
                    verse.last_word.word_text, rhyme_code
                )

            else:
                type_verse = self.type_determiner(self.poem)
                verse = self.wordset.choose_verse_from_verseset(
                    type_verse)

            self.poem.append(verse)

        # inserting the stored empty verses if any
        if empty_lines := self.rhyme_sequence.empty_lines:
            for i in empty_lines:
                self.poem.insert(i, "")

    def select_verse(self, verses: QuerySet[Verse]) -> Optional[Verse]:
        verse_type = self.type_determiner(self.poem)

        verses = verses.values_list("id").filter(**verse_type)

        if not verses:
            return None

        verse_id = random.choice(verses)[0]
        return Verse.objects.get(id=verse_id)

    def type_determiner(self, poem: List[Union[str, Verse]]) -> Dict[str, bool]:
        """Returns a list of booleans. True or False representing [is_beg, is_int, is_end]"""

        types_dict = {}

        if len(poem) == 0 or poem[-1].is_end:
            types_dict["is_beg"] = True

        if len(poem) == self.number_verses - 1:
            types_dict["is_end"] = True

        if not types_dict.get("is_beg") and not types_dict.get("is_end"):
            types_dict["is_int"] = True

        return types_dict

    def alternative_method_for_getting_id(self, used_word: str, rhyme_code: str):
        """Find a different word that rhymes and then substitute"""
        wordset = self.wordset.word_set[rhyme_code]

        for word in wordset.keys():
            if word == used_word:
                continue
            verses = self.wordset.word_set[rhyme_code][word]
            verse = self.select_verse(verses)
            if verse:
                return verse

        raise Http404("Ups, parece que algo me ha atragantado")

"""
            word_to_rhyme_with = random.choice(self.words_used[rhyme_code])
            rhy_type = "c" if rhyme_code.upper() == rhyme_code else "a"
    
            new_words_list = online_rhyme_finder(word=word_to_rhyme_with,
                                                 rhyme_type=rhy_type,
                                                 words_used=self.words_used[rhyme_code])
    
            for word in new_words_list:
                syllables_new_word = Pyverse(word).syllables
                type_new_word = getting_word_type(word)  # 0: Noun or Adjetive, 1: Verb
                first_letter_new_word = find_first_letter(word)
    
                verse_to_use = random.choice(verses_w_type)
    
                i = 0
                while (Pyverse(verse_to_use.last_word).syllables != syllables_new_word
                       and getting_word_type(verse_to_use.last_word) != type_new_word
                       and first_letter_new_word != find_first_letter(verse_to_use.last_word)):
                    verse_to_use = random.choice(verses_w_type)
                    if i == 40:
                        break
    
            if (Pyverse(verse_to_use.last_word).syllables == syllables_new_word
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
    def __init__(self, poemauto: PoemAutomator, rhyme_sequence: str, user_rhymes: Optional[Dict]):
        self.poemauto = poemauto  # parent
        self.verse_length = self.poemauto.verse_length
        self.rhyme_sequence = rhyme_sequence if rhyme_sequence else "_" * self.poemauto.number_verses
        self.empty_lines = self.empty_lines_finder()
        self.clean_rhyme_sequence = list(self.rhyme_sequence.replace(" ", ""))
        self.user_rhymes = user_rhymes
        self.unique_rhymes_keys: Set[str] = set(self.clean_rhyme_sequence)
        self.rhyme_set = self.get_rhyme_set()

    def get_rhyme_set(self) -> RhymeSetType:
        if not self.user_rhymes:  # rhymes_to_use not defined by user
            if "_" in self.rhyme_sequence:  # AND rhy_seq not defined by user -> no rhymes at all
                return {"_": None}
            # BUT rhy_seq defined by user (There are keys but we also need values)
            else:
                return self.randomly_determine_rhymes()
        else:  # just fetch the RhymesObjects defined by the user and populate self.rhyme_set with them
            return self.user_determined_rhymes()

    def randomly_determine_rhymes(self) -> RhymeSetType:
        rhyme_set = {}
        unique_rhymes = self.unique_rhymes_keys

        for key in unique_rhymes:
            # TODO lower this value to use stranger rhymes
            word_limit = self.clean_rhyme_sequence.count(key) * 3
            verse_limit = word_limit * 3

            if key == key.upper():  # if capital letter -> consonant rhyme
                cons_ids = ConsonantRhyme.objects.values_list("id").filter(
                    amount_verses__gte=verse_limit,
                    amount_words__gte=word_limit,)

                rhyme_object = self.choose_rhyme_id(
                    rhyme_set, cons_ids, word_limit, verse_limit, ConsonantRhyme)

            else:  # Assonant
                asson_ids = AssonantRhyme.objects.values_list("id").filter(
                    amount_verses__gte=verse_limit,
                    amount_words__gte=word_limit)

                rhyme_object = self.choose_rhyme_id(
                    rhyme_set, asson_ids, word_limit, verse_limit, AssonantRhyme)

            rhyme_set[key] = rhyme_object

        return rhyme_set

    def choose_rhyme_id(self, rhyme_set, rhyme_ids, word_limit, verse_limit, rhyme_type):
        rhy_id = random.choice(rhyme_ids)[0]
        rhyme_object = rhyme_type.objects.get(id=rhy_id)
        num_word_in_rhy = rhyme_object.verse_set.values_list("last_word").filter(
            verse_length=self.verse_length).distinct().count()
        num_ver_in_rhy = rhyme_object.verse_set.values_list("id").filter(
            verse_length=self.verse_length).count()

        while (rhyme_object in rhyme_set.values()
               or num_ver_in_rhy < verse_limit
               or num_word_in_rhy < word_limit
        ):
            rhy_id = random.choice(rhyme_ids)[0]
            rhyme_object = rhyme_type.objects.get(id=rhy_id)
            num_word_in_rhy = rhyme_object.verse_set.values_list("last_word").filter(
                verse_length=self.verse_length).distinct().count()
            num_ver_in_rhy = rhyme_object.verse_set.values_list("id").filter(
                verse_length=self.verse_length).count()

        return rhyme_object

    def user_determined_rhymes(self) -> RhymeSetType:
        rhyme_set = {}
        rhyme_sequence = self.unique_rhymes_keys

        for key in rhyme_sequence:
            rhyme_string = self.user_rhymes[key]

            if key == key.upper():  # Uppercase letters correspond to consonant rhymes
                rhyme_string = self.determine_rhyme_input(
                    rhyme_string, "consonant")
                rhyme_object = ConsonantRhyme.objects.get(
                    consonant_rhyme=rhyme_string)

            else:  # Lowercase letters correspond to assonant rhymes
                rhyme_string = self.determine_rhyme_input(
                    rhyme_string, "assonant")
                rhyme_object = AssonantRhyme.objects.get(
                    assonant_rhyme=rhyme_string)

            rhyme_set[key] = rhyme_object

        return rhyme_set

    @staticmethod
    def determine_rhyme_input(rhyme: str, rhyme_type: str) -> str:
        """Determine rhyme based on input. If rhyme = '-ae' -> 'ae'; if rhyme = 'word' -> 'ord' """
        if rhyme.startswith("-"):
            return rhyme.strip("-")

        if rhyme_type == "assonant":
            return Pyverse(rhyme).assonant_rhyme

        return Pyverse(rhyme).consonant_rhyme

    def empty_lines_finder(self) -> Optional[List[int]]:
        if self.rhyme_sequence.count(" ") > 0:
            # Array to store the location of the empty verses.
            empty_lines_indexes = []
            matches = finditer(" ", self.rhyme_sequence)
            for match in matches:
                empty_lines_indexes.append(match.regs[0][0])
            return empty_lines_indexes
        else:
            return None


class WordSet:
    def __init__(self, poemauto: PoemAutomator):
        self.poemauto = poemauto
        self.rhyme_sequence: RhymeSequence = self.poemauto.rhyme_sequence
        self.word_set = self.which_word_set()
        if not self.word_set:
            self.verse_set = self.random_verses()

        self.used_words = []

    def which_word_set(self) -> WordSetType:
        """Control flow:
        1. either user specified rhyme_sequence or we create totally random verses without rhyme
        2. either user determined or random rhymes"""

        if "_" in self.rhyme_sequence.unique_rhymes_keys:
            return None

        word_set = self.determine_word_set()
        return word_set

    def random_verses(self) -> QuerySet[Verse]:
        """User either determined: integer A=value, B=a couple of values or C=a range"""
        verse_length_type = self.poemauto.verse_length_type
        verse_length = self.poemauto.verse_length

        if verse_length_type == range:
            verses_to_use = Verse.objects.filter(
                verse_length__gte=verse_length.start,
                verse_length__lte=verse_length.stop,
            )
            return verses_to_use

        # if verse_length_type == list:
        #  Not yet implemented -> import Q; filtering -> return verse_to_use

        verses_to_use = Verse.objects.filter(
            verse_length=verse_length,
        )

        return verses_to_use

    def determine_word_set(self) -> WordSetType:
        """Populates the self.words_available dict with a QuerySet of models.Words objects that matches the requirements"""
        word_set = {}
        rhyme_keys = self.rhyme_sequence.unique_rhymes_keys

        for key in rhyme_keys:
            rhyme_object: Union[ConsonantRhyme, AssonantRhyme] = self.rhyme_sequence.rhyme_set[key]  # Can only be
            if self.poemauto.verse_length_type == range:
                verses_in_rhy_obj = rhyme_object.verse_set.filter(
                    verse_length__gte=self.poemauto.verse_length.start,
                    verse_length__lte=self.poemauto.verse_length.stop,
                )

            #elif self.poemauto.verse_length_type == list:
            else:
                verses_in_rhy_obj = rhyme_object.verse_set.filter(
                    verse_length=self.poemauto.verse_length
                )

            words_in_rhy_obj: QuerySet[Tuple[int]] = verses_in_rhy_obj.values_list("last_word__word_text").distinct()

            verse_set: Dict[str, QuerySet[Verse]] = {}
            for word in words_in_rhy_obj:
                word = word[0]
                verse_set[word] = verses_in_rhy_obj.filter(last_word__word_text=word)

            word_set[key] = verse_set

        return word_set

    def get_verses_from_random_word(self, rhyme_key: str) -> Tuple[str, QuerySet[Verse]]:
        word = random.choice(list(self.word_set[rhyme_key]))
        verses: QuerySet[Verse] = self.word_set[rhyme_key][word]
        return word, verses

    def choose_verse_from_verseset(self, verse_type: Dict[str, bool]) -> Verse:
        verses: Any = self.verse_set.values_list("id").filter(**verse_type)
        verse_id = random.choice(verses)[0]
        verse = self.verse_set.get(id=verse_id)
        while verse.last_word in self.used_words:
            verse_id = random.choice(verses)
            verse = self.verse_set.get(id=verse_id)

        self.verse_set.exclude(last_word=verse.last_word)
        self.used_words.append(verse.last_word)
        return verse

    def exclude_word(self, word: str, rhyme_key: str) -> None:
        del self.word_set[rhyme_key][word]
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

if __name__ == "__main__":
    pass
