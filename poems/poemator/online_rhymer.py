import bs4
import requests
from typing import List, Optional

"""FROM FIlES TO DB CHANGE EVERYTHING"""


class Rhymer:
    def __init__(self,
                 word: str,
                 rhy_type: Optional[str] = "c",
                 syllables: Optional[int] = "I",
                 first_letter: Optional[str] = None,
                 word_type: Optional[str] = None,
                 words_to_discard: Optional[List] = None
                 ) -> None:

        self.word = word
        self.rhy_type = rhy_type
        self.syllables = syllables
        self.first_letter = first_letter
        self.words_to_discard = words_to_discard
        self.word_type = word_type

    def getting_cronopista(self) -> List:
        if not self.word_type:
            self.word_type = getting_word_type(self.word)
        if not self.first_letter:
            self.first_letter = find_first_letter(self.word)

        url = f"https://www.cronopista.com/onlinedict/index.php?word={self.word}&type={self.rhy_type}&silables={self.syllables}&orderBy=R&begining={self.first_letter}&category={self.word_type}"

        headers = {"user-agent": "Chrome/86.0.4240.114"}

        resp = requests.get(url, headers=headers)
        soup = bs4.BeautifulSoup(resp.text, "lxml")

        rhymes_list = self.parsing_the_soup(soup)
        return rhymes_list

    def parsing_the_soup(self, soup: bs4.BeautifulSoup) -> List:
        rhymes_tags = soup.select("div[class=lr] b")
        rhymes_text = [rhyme.text for rhyme in rhymes_tags]

        if self.words_to_discard:
            rhymes = []

            for rhyme in rhymes_text:
                if rhyme not in self.words_to_discard and rhyme != self.word:
                    rhymes.append(rhyme)

            return rhymes

        return rhymes_text


def getting_word_type(word) -> str:
    resp = requests.get(f"https://www.buscapalabra.com/categoria-gramatical-tiempo-verbal.html?palabra={word}")
    soup = bs4.BeautifulSoup(resp.text, "lxml")

    type_word = soup.select("h3[class=catgram]")

    for type_word in type_word:

        if "Nombre" in type_word.text or "Adjetivo" in type_word.text:
            return "0"

        if "Verbo" in type_word.text:
            return "1"

    return "I"


def find_first_letter(word: str, sentence: Optional[str] = False) -> str:
    if sentence:
        if sentence[:sentence.rfind(" ")][-1] not in "aeiouAEIOUáéíóúÁÉÍÓÚhH":
            return "I"

    if word[0] in "aeiouAEIOUáéíóúÁÉÍÓÚhH":
        return "true"
    else:
        return "false"


def main():
    input_word = input("palabra a rimar: ")

    rhymer = Rhymer(input_word)

    print(rhymer.getting_cronopista())

if __name__ == "__main__":
    main()
