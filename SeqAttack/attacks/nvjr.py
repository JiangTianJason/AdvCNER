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
             "run", "remain", "keep", "stay", "continue", "stand", "rest", "lie", "hold","s","S","c","C"])
        # linking verbs, can be customized

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
            wir_method="delete")

        return NERAttack(
            goal_function,
            constraints,
            transformation,
            search_method,
            attack_timeout=attack_timeout)
