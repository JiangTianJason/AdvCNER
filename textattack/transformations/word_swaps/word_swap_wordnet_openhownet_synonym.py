"""
Word Swap by swaping synonyms in WordNet and OpenHowNet
==========================================================
"""

import textattack

from .word_swap import WordSwap
from pattern.en import *
from nltk.corpus import wordnet as wn
from .word_swap_hownet import WordSwapHowNet
import cyner



class WordSwapWordHowNetSyn(WordSwap):
    """Transforms an input by replacing its words with synonyms provided by
    WordNet and OpenHowNet."""

    def __init__(self, language="eng"):
        # if language not in wordnet.langs():
        #     raise ValueError(f"Language {language} not one of {wordnet.langs()}")
        self.language = language

        self._enptb_to_universal = {
            "VBN": "VERB",
            "VBP": "VERB",
            "VBZ": "VERB",
            "VBG": "VERB",
            "NN": "NOUN",
            "VBD": "VERB",
            "VB": "VERB",
            "NNS": "NOUN",
            "VP": "VERB",
            "TO": "VERB",
            "SYM": "NOUN",
            "MD": "VERB",
            "JJ": "ADJ",
            "JJR": "ADJ",
            "JJS": "ADJ",
            "RB": "ADV",
            "RBR": "ADV",
            "RBS": "ADV"
        }

        self.standard_map = {"NOUN": wn.NOUN,
                             "VERB": wn.VERB,
                             "ADJ": wn.ADJ,
                             "ADV": wn.ADV}

        self.entity_check_model = cyner.CyNER(transformer_model=r'D:\Download\Cyber-Security-NER_attack\venv\Lib\site-packages\textattack\utils\ckpt_20', use_heuristic=False, flair_model=None)        ###we use the "xlm-roberta" model to check whether entities are introduced


    def adjustment_replace_words(self,substitution_word,original_word,word_part_of_speech,current_text, index_now):
        """align the inflection of substitution words with original words"""

        substitute = None

        substitution_word = lemma(substitution_word)

        if self._enptb_to_universal[word_part_of_speech] == "NOUN":
            number = "single" if word_part_of_speech in ["NN", "NNP"] else "plural"
            try:
                aeiou_n = True if current_text.words[index_now - 1] in ["an", "An"] else False  # starts with a vowel
            except IndexError:                                                                                                # 名词在句首
                aeiou_n = False
            if aeiou_n:
                if substitution_word[0] in "aeiou":  # Satisfied
                    substitute = pluralize(substitution_word) if number == "plural" else substitution_word
                else:
                    substitute = None                          # Unsatisfied
            else:
                substitute = pluralize(substitution_word) if number == "plural" else substitution_word

        elif self._enptb_to_universal[word_part_of_speech] == "VERB":
            tense = "present" if word_part_of_speech in ["VB", "VBG", "VBP", "VBZ"] else "past"
            number = "single" if word_part_of_speech in ["VBP", "VBZ"] else "plural"
            final_number = SG if number == "single" else PL
            substitute = conjugate(verb=substitution_word, tense=tense, number=final_number)

        elif self._enptb_to_universal[word_part_of_speech] == "ADV":
            if word_part_of_speech == "RBR":
                substitute = comparative(substitution_word).split(" ")[-1]
            elif word_part_of_speech == "RBS":
                substitute = superlative(substitution_word).split(" ")[-1]
            else:
                substitute = substitution_word

        elif self._enptb_to_universal[word_part_of_speech] == "ADJ":
            try:
                aeiou_n = True if current_text.words[index_now - 1] in ["an", "An"] else False  # starts with a vowel
            except IndexError:                                                                                                # 形容词在句首
                aeiou_n = False
            if aeiou_n:
                if substitution_word[0] in "aeiou":  # Satisfied
                    if word_part_of_speech == "JJR":
                        substitute = comparative(substitution_word).split(" ")[-1]
                    elif word_part_of_speech == "JJS":
                        substitute = superlative(substitution_word).split(" ")[-1]
                    else:
                        substitute = substitution_word
                else:
                    substitute = None                          # Unsatisfied
            else:
                if word_part_of_speech == "JJR":
                    substitute = comparative(substitution_word).split(" ")[-1]
                elif word_part_of_speech == "JJS":
                    substitute = superlative(substitution_word).split(" ")[-1]
                else:
                    substitute = substitution_word

        return substitute



    def _get_replacement_words(self, word, word_part_of_speech, current_text, index_now):
        """Returns a list containing all possible substitution words."""

        if word_part_of_speech not in self._enptb_to_universal:
            return []

        word_property = wn.synsets(word, pos=self.standard_map[self._enptb_to_universal[word_part_of_speech]])

        ####Searching synonyms using OpenHowNet

        OpenHowNet_synonym =[]
        transformation = WordSwapHowNet()
        OpenHowNet_synonym_candidates = transformation.get_replacement_words(word, self._enptb_to_universal[word_part_of_speech])

        for i in OpenHowNet_synonym_candidates:
            almost_OpenHowNet_synonym_substitute = self.adjustment_replace_words(i, word, word_part_of_speech, current_text, index_now)
            if "_" not in i and "-" not in i and almost_OpenHowNet_synonym_substitute != None and almost_OpenHowNet_synonym_substitute != word:
                OpenHowNet_synonym.append(almost_OpenHowNet_synonym_substitute)


        ###Searching synonyms using WordNet

        synonyms = []

        for syn in word_property:                                       ###Must have consistent parts of speech
            for syn_word in syn.lemma_names():
                almost_substitute = self.adjustment_replace_words(syn_word, word, word_part_of_speech, current_text, index_now)
                if (
                    (almost_substitute != word)
                    and ("_" not in syn_word)
                    and (textattack.shared.utils.is_one_word(syn_word))
                    and almost_substitute != None
                ):
                    # WordNet can suggest phrases that are joined by '_' but we ignore phrases.
                    synonyms.append(almost_substitute)

        return list(set(OpenHowNet_synonym + synonyms))


    def _get_transformations(self, current_text, indices_to_modify):
        words = current_text.words
        transformed_texts = []

        for i in indices_to_modify:
            word_to_replace = words[i]
            replacement_words = self._get_replacement_words(word_to_replace,current_text.pos_of_word_index(i),current_text,i)
            transformed_texts_idx = []
            for r in replacement_words:
                if r != word_to_replace and r != None and len(self.entity_check_model.get_entities(r)) == 0:
                    transformed_texts_idx.append(current_text.replace_word_at_index(i, recover_word_case(r,word_to_replace)))
            transformed_texts.extend(transformed_texts_idx)

        return transformed_texts


def recover_word_case(word, reference_word):
    """Makes the case of `word` like the case of `reference_word`.

    Supports lowercase, UPPERCASE, and Capitalized.
    """
    if reference_word.islower():
        return word.lower()
    elif reference_word.isupper() and len(reference_word) > 1:
        return word.upper()
    elif reference_word[0].isupper() and reference_word[1:].islower():
        return word.capitalize()
    else:
        # if other, just do not alter the word's case
        return word