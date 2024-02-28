from seqattack.goal_functions.ner_goal_function_result import NERGoalFunctionResult
import signal
import numpy as np
import time

from textattack.shared import Attack
from seqattack.utils.ner_attacked_text import NERAttackedText
from textattack.goal_function_results import GoalFunctionResultStatus

from textattack.attack_results import (
    FailedAttackResult,
    SkippedAttackResult,
    SuccessfulAttackResult,
)

############Time consumption For Windows OS. We don't restrict the attack time. Not used.#############
# import eventlet
# eventlet.monkey_patch()
#####################################



class NERAttack(Attack):
    def __init__(
            self,
            goal_function=None,
            constraints=[],
            transformation=None,
            search_method=None,
            transformation_cache_size=2**15,
            constraint_cache_size=2**15,
            max_entities_mispredicted=0.8,
            search_step=0.1,
            attack_timeout=30):
        super().__init__(
            goal_function=goal_function,
            constraints=constraints,
            transformation=transformation,
            search_method=search_method,
            transformation_cache_size=transformation_cache_size,
            constraint_cache_size=constraint_cache_size
        )

        self.search_step = search_step
        self.attack_timeout = attack_timeout
        self.max_entities_mispredicted = max_entities_mispredicted

    def _get_transformations_uncached(self, current_text, original_text=None, **kwargs):
        transformed_texts = super()._get_transformations_uncached(
            current_text,
            original_text=original_text,
            **kwargs)

        # Remove multiple spaces from samples
        for transformed in transformed_texts:
            transformed.strip_remove_double_spaces()

        return transformed_texts


    def timeout_hook(self, signum, frame):
        raise TimeoutError("Attack time expired")


    def attack_dataset(self, dataset, indices=None):
        # FIXME: Same as superclass
        examples = self._get_examples_from_dataset(dataset, indices=indices)
        final_attack_dataset = []
        for goal_function_result in examples:
            if goal_function_result.goal_status == GoalFunctionResultStatus.SKIPPED:
                yield SkippedAttackResult(goal_function_result)
                # final_attack_dataset.append(SkippedAttackResult(goal_function_result))
            else:
                result = self.attack_one(goal_function_result)
                yield result
                # final_attack_dataset.append(result)
        # return final_attack_dataset


    def attack_one(self, initial_result):
        attacked_text = self.goal_function.initial_attacked_text
        # The initial (original) misprediction score
        initial_score = self.goal_function._get_score(
            attacked_text.attack_attrs["model_raw"],
            attacked_text)

        best_result, best_score = None, 0
        # List of misprediction targets [0.1, 0.2, ...]
        target_scores = np.arange(
            max(initial_score, self.search_step),
            self.max_entities_mispredicted + self.search_step,
            self.search_step
        )

        # start_time = time.time()
        for target in target_scores:
            # FIXME: To speed up the search use the current best result
            # FIXME: This code is better suited to be in a search method

            # Check if we can reach a mispredicion of target %
            if target < best_score:
                # If we already obtained a sample with a score higher
                # than the current target skip this iteration
                continue

            self.goal_function.min_percent_entities_mispredicted = target

            try:
                result = super().attack_one(initial_result)                                                 #####into search#####
            except IndexError:
                print(f"Output do not correspond to the original!")
                return FailedAttackResult(initial_result, initial_result)

            current_score = self.goal_function._get_score(
                result.perturbed_result.unprocessed_raw_output,
                result.perturbed_result.attacked_text
            )

            if type(result) == SuccessfulAttackResult:
                if best_result is None or current_score > best_score:
                    best_result, best_score = result, current_score
            elif type(result) == FailedAttackResult:
                if best_result is None:
                    best_result, best_score = result, current_score

                # The attack failed, nothing else we can do
                break
        #
        # end_time = time.time()
        #
        # with open("nvjr_avg_time.txt", "a") as f:
        #     f.write(str(end_time - start_time) + "\n")

        # FIXME: Handle timeouts etc.
        return best_result


    def _get_examples_from_dataset(self, dataset, indices=None):
        final_result = []
        # FIXME: indices is currently ignored
        for example, ground_truth in dataset:
            model_raw, _, valid_prediction = self.__is_example_valid(example,ground_truth)

            attacked_text = NERAttackedText(
                example,
                attack_attrs={
                    "label_names": dataset.label_names,
                    "model_raw": model_raw
                },
                # FIXME: is this needed?
                ground_truth=[int(x) for x in ground_truth]
            )

            if not valid_prediction:
                print("The model cannot correctly predict the sample! Skipped!")
                # final_result.append(NERGoalFunctionResult(
                #     attacked_text=attacked_text,
                #     raw_output=None,
                #     output=None,
                #     goal_status=GoalFunctionResultStatus.SKIPPED,
                #     score=0,
                #     num_queries=0,
                #     ground_truth_output=None,
                #     unprocessed_raw_output=None
                # ))
                yield NERGoalFunctionResult(
                    attacked_text=attacked_text,
                    raw_output=None,
                    output=None,
                    goal_status=GoalFunctionResultStatus.SKIPPED,
                    score=0,
                    num_queries=0,
                    ground_truth_output=None,
                    unprocessed_raw_output=None
                )

            # If the original prediction mispredicts more entities than
            # max_entities_mispredicted then we skip the example
            ###return goal_function_result###
            else:
                self.goal_function.min_percent_entities_mispredicted = self.max_entities_mispredicted
                goal_function_result, _ = self.goal_function.init_attack_example(
                    attacked_text,
                    ground_truth
                )
                # final_result.append(goal_function_result)
                yield goal_function_result
        return final_result


    def __is_example_valid(self, sample,ground_truth):
        """Checks whether the model can correctly predict the sample or not"""
        model_raw = self.goal_function.model([sample])[0]
        # print("model_raw:",model_raw)
        try:
            model_pred = self.goal_function.model.process_raw_output(model_raw, sample)
            # print("model_pred:",model_pred)
        except IndexError:
            return model_raw,model_raw, False       ##output misplacement，DEFAULT operation: skipped
        # print("ground_truth:",ground_truth)
        return model_raw, model_pred, model_pred.numpy().tolist() == ground_truth               ###Must predict each label of tokens correctly

        ####Original code#########
        # return model_raw, model_pred, len(model_pred) > 0
