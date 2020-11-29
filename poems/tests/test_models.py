from django.test import TestCase
from poems.models import AssonantRhyme, ConsonantRhyme, Word, Verse


class TestVerse(TestCase):
    """Tests for poems.models.Verse"""

    def verse_cut_verse_right(self):
        verse1 = Verse(verse_text="Todos los días nos vemos las caras")
        self.assertIs(verse1.cut_verse(), "Todos los días nos vemos las")

    def test_is_beg_FALSE(self):
        verse = Verse(verse_text="la muerte andaba caminando")
        self.assertIs(verse.is_beg(), False)

    def test_is_beg_TRUE(self):
        verse = Verse(verse_text="¿...Otro verso de los cojones?")
        self.assertIs(verse.is_beg(), True)

    def test_is_int_FALSE(self):
        verse1 = Verse(verse_text="el ganchillo de la abuela.")
        verse2 = Verse(verse_text="Los muros del metro son aureos")
        verse3 = Verse(verse_text="En medio de las cacas...")
        self.assertIs(verse1.is_int(), False)
        self.assertIs(verse2.is_int(), False)
        self.assertIs(verse3.is_int(), False)

    def test_is_int_TRUE(self):
        verse1 = Verse(verse_text="muñecos saltinbanquis menudean por doquier...")
        verse2 = Verse(verse_text="en la Aurora ponen rock,")
        self.assertIs(verse1.is_int(), True)
        self.assertIs(verse2.is_int(), True)

    def test_is_end_FALSE(self):
        verse1 = Verse(verse_text="monigotes con bigotes...")
        verse2 = Verse(verse_text="alumbramiento del César,")
        self.assertIs(verse1.is_end(), False)
        self.assertIs(verse2.is_end(), False)

    def test_is_end_TRUE(self):
        verse1 = Verse(verse_text="monigotes con bigotes.")
        verse2 = Verse(verse_text="Alumbramiento del César.")
        self.assertIs(verse1.is_end(), True)
        self.assertIs(verse2.is_end(), True)

