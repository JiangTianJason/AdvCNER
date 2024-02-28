from subject_verb_object_extract import findSVOs, nlp
# nlp = spacy.load("en_core_web_lg")
from allennlp.predictors.predictor import Predictor
from nltk.stem.wordnet import WordNetLemmatizer
import allennlp_models
# from preprocessings  import *
from list_iocs import iocs
from lists_patterns import load_lists, fpath
main_verbs = load_lists(fpath)['verbs']
main_verbs = main_verbs.replace("'", "").strip('][').split(', ')

import cyner
import json
import os
from tqdm import tqdm
import logging
import re

logging.basicConfig(level=logging.INFO)

from transformers import BertModel

model_path = '/root/bert-base-uncased'
model = BertModel.from_pretrained(model_path)
config = model.config

def roles(sentences):
    all_nodes = []
    for i in range(len(sentences)):
        # Download "structured-prediction-srl-bert.2020.12.15.tar.gz" to local and unzip to folder first
        predictor = Predictor.from_path(r"./structured-prediction-srl-bert",
                                        overrides={
                                            "model.bert_model": config.to_dict(),
                                            "dataset_reader.bert_model_name": model_path,
                                        }
                                        )
        predictions = predictor.predict(sentences[i])
        lst = []
        nodes = []
        for k in predictions['verbs']:
            if k['description'].count('[') > 1:
                lst.append(k['description'])
        for jj in range(len(lst)):
            nodes.append([])
            for j in re.findall(r"[^[]*\[([^]]*)\]", lst[jj]):
                nodes[jj].append(j)
        return nodes

# print(roles(["of startup and launch , the Android user changes the exploit vulnerability vulnerability ."]))


if __name__ == "__main__":

    model = cyner.CyNER(
        transformer_model=r'/root/albert-large-v2_20',      ###Change the model path
        use_heuristic=False, flair_model=None)

    def check_is_adversarial(input_text):
        srl_results = roles([input_text])
        print(srl_results)

        final_result_origin = set()
        final_result_check = set()

        words = input_text.split()
        words_original = words

        # words = [word.lower() for word in words]            ###Suitable for "xlm"
        words = [word for word in words]                              ###Suitable for "bert" and "albert"

        print("words: ",words)

        ###Output from the complete sentence
        for k in model.get_entities(input_text):
            print("k: ",k)

            entities_probable_list = k.text.split(" ")
            start_index = k.start
            count = 0
            for idx in range(len(words)):
                try:
                    if (words[idx].startswith(entities_probable_list[0]) or entities_probable_list[0] in words[idx]) and (abs(start_index - input_text.index(words_original[idx])) <= 5 or (re.search(r"\b{}".format(words_original[idx]), input_text) and abs(start_index - re.search(r"\b{}".format(words_original[idx]), input_text).start()) <= 5)):
                        final_result_origin.add((words[idx],"B-{}".format(k.entity_type)))
                        count += 1
                        while count < len(entities_probable_list):
                            idx += 1
                            try:
                                if words[idx].startswith(entities_probable_list[count]) or entities_probable_list[count] in words[idx]:
                                    final_result_origin.add((words[idx],"I-{}".format(k.entity_type)))
                                else:
                                    break
                            except:
                                break
                            count += 1
                        break

                except:
                    if (words[idx].startswith(entities_probable_list[0]) or entities_probable_list[0] in words[
                        idx]) and (abs(start_index - input_text.index(words_original[idx])) <= 5):
                        final_result_origin.add((words[idx], "B-{}".format(k.entity_type)))
                        count += 1
                        while count < len(entities_probable_list):
                            idx += 1
                            try:
                                if words[idx].startswith(entities_probable_list[count]) or entities_probable_list[
                                    count] in words[idx]:
                                    final_result_origin.add((words[idx], "I-{}".format(k.entity_type)))
                                else:
                                    break
                            except:
                                break
                            count += 1
                        break

        ###Output from each part after SRL
        for i in srl_results:
            for j in i:
                if "ARG" in j:
                    for k in model.get_entities(j[j.index(": ") + 2:]):
                        print("ARG-k:  ",k)
                        entities_probable_list = k.text.split(" ")
                        count = 0
                        for idx in range(len(words)):

                            # if (words[idx].startswith(entities_probable_list[0]) or entities_probable_list[0] in words[idx]) and words[idx] in "".join(j[j.index(": ") + 2:]).replace(" ","").lower():          ### Suitable for "xlm"
                            if (words[idx].startswith(entities_probable_list[0]) or entities_probable_list[0] in words[idx]) and words[idx] in "".join(j[j.index(": ") + 2:]).replace(" ",""):                    ### Suitable for "bert" and "albert"

                                final_result_check.add((words[idx],"B-{}".format(k.entity_type)))
                                count += 1
                                while count < len(entities_probable_list):
                                    idx += 1
                                    try:
                                        if (words[idx].startswith(entities_probable_list[count]) or entities_probable_list[count] in words[idx]):
                                            final_result_check.add((words[idx],"I-{}".format(k.entity_type)))
                                        else:
                                            break
                                    except:
                                        break
                                    count += 1
                                break

        print("final_result_check: ",final_result_check)
        print("final_result_origin: ",final_result_origin)
        if final_result_check == final_result_origin:
            return False            ### is Not adversarial
        else:
            return True             ### is adversarial


    def total_calc(victim_model, attack_method):

        all_indices = [eval(line) for line in
                       open(r"../SRL_based_defense/{}/{}-check.txt".format(victim_model, attack_method), 'r',
                            encoding="utf-8").readlines()]

        quality_total_path = r"../SRL_based_defense/{}/{}-check_total.txt".format(victim_model, attack_method)

        if os.path.exists(quality_total_path):
            logging.info("Done！")

        else:
            all_adversarial_judged, all_adversarial_include_Failed_judged, all_adversarial_count, all_adversarial_include_Failed_count= 0, 0, 0, 0

            for sample in tqdm(all_indices):
                if sample["status"] == "Successful":
                    all_adversarial_count += 1
                    if sample["judgment"] == "correct":
                        all_adversarial_judged += 1

                elif sample["status"] == "Failed":
                    if sample["original_pred"] != sample["perturbed_pred"]:  ###Flip at least one label, but not over the threshold
                        all_adversarial_include_Failed_count += 1
                        if sample["judgment"] == "correct":
                            all_adversarial_include_Failed_judged += 1

            dict4 = {"all_adversarial_judged": all_adversarial_judged, "all_adversarial_count": all_adversarial_count,
                     "all_adversarial_include_Failed_judged": all_adversarial_include_Failed_judged, "all_adversarial_include_Failed_count": all_adversarial_include_Failed_count}

            f = open(quality_total_path, "a", encoding="utf-8")
            f.write(str(dict4) + "\n")
            f.close()

            logging.info("Done！")


    def do_it(victim_model, attack_method):

        with open(r"../output_{}/cti-{}-strict-preserve.json".format(victim_model,attack_method), 'r',
                  encoding='utf-8') as fp:
            json_data = json.load(fp)
            all_indices = json_data["attacked_examples"]

        output_file = r"../SRL_based_defense/{}/{}-check.txt".format(victim_model, attack_method)

        logging.info("Output file：----> {}".format(output_file))

        if os.path.exists(output_file):  ### Continue from breakpoint

            generated_samples = [eval(line) for line in open(output_file, 'r', encoding="utf-8").readlines()]
            if len(generated_samples) == len(all_indices):
                total_calc(victim_model, attack_method)
                return
            remain_indices = all_indices[len(generated_samples):]
            logging.info('Restore progress')
        else:
            remain_indices = all_indices

        for sample in tqdm(remain_indices):

            #####Check on original sentence####
            original_result = check_is_adversarial(sample["original_text"])
            ##################

            if original_result:
                adversarial_result = original_result
                judgment = "incorrect"
            else:
                if sample["status"] == "Successful":
                    adversarial_result = check_is_adversarial(sample["perturbed_text"])
                    judgment = "correct" if adversarial_result else "incorrect"
                elif sample["status"] == "Failed":
                    if sample["original_pred"] != sample["perturbed_pred"]:      ###Flip at least one label, but not over the threshold
                        adversarial_result = check_is_adversarial(sample["perturbed_text"])
                        judgment = "correct" if adversarial_result else "incorrect"
                    else:           ###Totally "Failed"
                        adversarial_result = original_result
                        judgment = "correct"
                else:       ###"Skipped"
                    adversarial_result = original_result
                    judgment = "correct"

            if sample["status"] == "Skipped":
                original_pred = []
                perturbed_pred = []
            else:
                original_pred = sample["original_pred"]
                perturbed_pred = sample["perturbed_pred"]

            f = open(output_file, "a", encoding='utf-8')
            f.write(str({"status": sample["status"],"original_result": original_result, "adversarial_result": adversarial_result, "judgment": judgment, "original_pred": original_pred, "perturbed_pred": perturbed_pred }) + "\n")
            f.close()

        total_calc(victim_model, attack_method)

        return

    do_it("albert","textfooler")