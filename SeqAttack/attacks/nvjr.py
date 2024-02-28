"""
OurMethod
"""

from textattack.constraints.pre_transformation import (
    RepeatModification,
    StopwordModification,
)


from textattack.transformations import WordSwapWordHowNetSyn

from seqattack.constraints import SkipNegations

from seqattack.search import NERGreedyWordSwapWIR
from seqattack.utils import postprocess_ner_output

from seqattack.utils.attack import NERAttack
from .seqattack_recipe import SeqAttackRecipe
from textattack.constraints.grammaticality import PartOfSpeech

class OurMethod(SeqAttackRecipe):

    @staticmethod
    def build(
            model,
            tokenizer,
            dataset,
            goal_function_class,
            use_cache=True,
            query_budget=512,
            additional_constraints=[],
            attack_timeout=30,
            **kwargs):
        goal_function = goal_function_class(
            model,
            tokenizer,
            use_cache=use_cache,
            query_budget=query_budget,
            ner_postprocess_func=postprocess_ner_output,
            label_names=dataset.label_names)

        transformation = WordSwapWordHowNetSyn()

        stopwords = set(
            ["is", "has", "have", "were", "was", "had", "been", "am", "being", "be", "are", "will", "feel", "look",
             "smell", "sound", "taste", "seem", "appear", "get", "become", "turn", "grow", "make", "come", "go", "fall",
             "run", "remain", "keep", "stay", "continue", "stand", "rest", "lie", "hold", "s", "S", "c", "C", "a",
             "about", "above", "across", "after", "afterwards", "again", "against", "ain", "all", "almost", "alone",
             "along", "already", "also", "although", "am", "among", "amongst", "an", "and", "another", "any", "anyhow",
             "anyone", "anything", "anyway", "anywhere", "are", "aren", "aren't", "around", "as", "at", "back", "been",
             "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "both",
             "but", "by", "can", "cannot", "could", "couldn", "couldn't", "d", "didn", "didn't", "doesn", "doesn't",
             "don", "don't", "down", "due", "during", "either", "else", "elsewhere", "empty", "enough", "even", "ever",
             "everyone", "everything", "everywhere", "except", "first", "for", "former", "formerly", "from", "hadn",
             "hadn't", "hasn", "hasn't", "haven", "haven't", "he", "hence", "her", "here", "hereafter", "hereby",
             "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "i", "if",
             "in", "indeed", "into", "is", "isn", "isn't", "it", "it's", "its", "itself", "just", "latter", "latterly",
             "least", "ll", "may", "me", "meanwhile", "mightn", "mightn't", "mine", "more", "moreover", "most",
             "mostly", "must", "mustn", "mustn't", "my", "myself", "namely", "needn", "needn't", "neither", "never",
             "nevertheless", "next", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "o",
             "of", "off", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours",
             "ourselves", "out", "over", "per", "please", "s", "same", "shan", "shan't", "she", "she's", "should've",
             "shouldn", "shouldn't", "somehow", "something", "sometime", "somewhere", "such", "t", "than", "that",
             "that'll", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter",
             "thereby", "therefore", "therein", "thereupon", "these", "they", "this", "those", "through", "throughout",
             "thru", "thus", "to", "too", "toward", "towards", "under", "unless", "until", "up", "upon", "used", "ve",
             "was", "wasn", "wasn't", "we", "were", "weren", "weren't", "what", "whatever", "when", "whence",
             "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether",
             "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "with", "within",
             "without", "won", "won't", "would", "wouldn", "wouldn't", "y", "yet", "you", "you'd", "you'll", "you're",
             "you've", "your", "yours", "yourself", "yourselves"]
        )

        constraints = [
            # Do not modify already changed words
            RepeatModification(),
            # Do not modify stopwords
            StopwordModification(stopwords=stopwords),
            SkipNegations()]

        constraints.extend(additional_constraints)

        search_method = NERGreedyWordSwapWIR(
            dataset=dataset,
            tokenizer=tokenizer,
            wir_method="random")

        return NERAttack(
            goal_function,
            constraints,
            transformation,
            search_method,
            attack_timeout=attack_timeout)
