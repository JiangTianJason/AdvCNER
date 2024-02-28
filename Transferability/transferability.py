################Transferability (Section 5.4.2)################
###!!!! Remember to first align /root/SeqAttack-master/seqattack/utils/__init__.py according to different "target_model"

from seqattack.models import NERModelWrapper
from seqattack.utils.ner_attacked_text import NERAttackedText
from seqattack.goal_functions import StrictUntargetedNERGoalFunction
from seqattack.utils import postprocess_ner_output
import json
import logging
import os
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

victim_model = "bert"
attack_method = "textfooler"
target_model = "xlm"

labels_map={
        0: 0,
        1: 2,
        2: 6,
        3: 8,
        4: 3,
        5: 4,
        6: 5,
        7: 1,
        8: 7,
        9: 9,
        10: 10
}

def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key


if target_model == "albert":
        model_path = r'/root/albert-large-v2_20'
        label_names = ["B-Malware", "I-Malware", "O", "B-System", "I-System", "B-Organization", "B-Indicator", "I-Organization", "I-Indicator", "B-Vulnerability", "I-Vulnerability"]
else:
        label_names = ["B-Malware", "O", "B-Indicator", "I-Indicator", "B-System", "I-System","B-Organization", "I-Malware", "I-Organization", "B-Vulnerability", "I-Vulnerability"]
        if target_model == "bert":
                model_path = r'/root/ckpt_bert_20'
        else:
                model_path = r'/root/ckpt_20'



tokenizer, model = NERModelWrapper.load_huggingface_model(model_path)
goal_function = StrictUntargetedNERGoalFunction(model_wrapper=NERModelWrapper.load_huggingface_model(model_path)[1],
        tokenizer=tokenizer,
        min_percent_entities_mispredicted=0.1,
        ner_postprocess_func=postprocess_ner_output,
        label_names=label_names)


def check_is_success(initial_sample,attacked_sample,ground_truth):

        if target_model == "albert":
                ground_truth = [labels_map[i] for i in ground_truth]

        if victim_model == "albert":
                ground_truth = [find_key_by_value(labels_map,i) for i in ground_truth]

        initial_sample = initial_sample
        initial_text = NERAttackedText(initial_sample,
                                       ground_truth=ground_truth)

        attacked_sample = attacked_sample
        attacked_text = NERAttackedText(attacked_sample,
                                        ground_truth=ground_truth)

        initial_model_raw_output = model([initial_sample])[0]

        attacked_model_raw_output = model([attacked_sample])[0]

        try:
                initial_score = goal_function._get_score(initial_model_raw_output, initial_text)

                preds, _, named_entities_mask, all_labels_confidences = goal_function._preprocess_model_output(
                        attacked_model_raw_output,
                        attacked_text)

                mapped_ground_truth = goal_function._preprocess_ground_truth(attacked_text)

                pred_token_labels = [goal_function.label_names[x] for x in preds]
                truth_token_labels = [goal_function.label_names[x] for x in mapped_ground_truth]

                for i, j in zip(pred_token_labels, truth_token_labels):
                        pred_label = i.replace("I-", "").replace("B-", "")
                        truth_label = j.replace("I-", "").replace("B-", "")
                        if pred_label != truth_label:
                                if goal_function._get_score(attacked_model_raw_output, attacked_text) > max(0.1, initial_score):
                                        return True
        except:
                return False

        return False


def do_it(victim_model,target_model, attack_method):
        with open(r"./output_{}/cti-{}-strict-preserve.json".format(victim_model, attack_method), 'r',
                  encoding='utf-8') as fp:
                json_data = json.load(fp)
                all_indices = json_data["attacked_examples"]

        output_file = r"./generatedon_{}_attack_{}/{}-check.txt".format(victim_model,target_model,attack_method)

        logging.info("Output file：----> {}".format(output_file))

        if os.path.exists(output_file):  ###Prevent processing interruptions, continue from the breakpoint

                generated_samples = [eval(line) for line in open(output_file, 'r', encoding="utf-8").readlines()]
                if len(generated_samples) == len(all_indices):
                        print("All ready done!")
                        return
                remain_indices = all_indices[len(generated_samples):]
                logging.info('Restore progress')
        else:
                remain_indices = all_indices

        for sample in tqdm(remain_indices):
                if sample["status"] == "Successful":
                        if check_is_success(sample["original_text"],sample["perturbed_text"],sample["ground_truth"]):
                                f = open(output_file, "a", encoding='utf-8')
                                f.write(str(sample) + "\n")
                                f.close()

        return

do_it(victim_model,target_model, attack_method)


# #####Provide data for drawing Fig.5#######
# import json
# for generatedon in ["bert","albert","xlm"]:
#         for attack in ["bert","albert","xlm"]:
#                 if generatedon != attack:
#                         temp = []
#                         for k in ['morpheus', 'deepwordbug', 'textfooler-Word2Vec', 'textfooler', 'bae-CyBERT', 'bae','nvjr']:
#
#                                 successed_sample = [eval(line) for line in open(r"./generatedon_{}_attack_{}/{}.txt".format(generatedon, attack,k), 'r', encoding="utf-8").readlines()]
#
#                                 all_sample = [eval(line) for line in open(r"../SRL_based_defense/{}/{}_total.txt".format(generatedon, k), 'r', encoding="utf-8").readlines()]
#
#                                 temp.append(round(len(successed_sample) / all_sample[0]["all_adversarial_count"],4))
#
#                         print("{}_{}: {}".format(generatedon,attack,temp))




# # ######################Draw Fig.5####################
# import matplotlib.pyplot as plt
# import numpy as np
#
#
# data = {
#     'BERT_ALBERT': [10.00, 14.68,19.23,19.90,19.31,22.00,22.22],
#     'BERT_XLM-RoBERTa': [0.00,6.83,23.08,3.40,17.33,8.00,0.74],
#         'ALBERT_BERT': [25.00, 35.16, 27.12, 30.61, 29.20, 32.29, 27.96],
#         'ALBERT_XLM-RoBERTa': [8.33, 7.14, 10.17, 6.12, 10.95, 11.46, 3.23],
#     'XLM-RoBERTa_ALBERT': [40.00, 41.13, 36.84, 33.93, 24.70, 25.23, 26.32],
#     'XLM-RoBERTa_BERT': [40.00, 22.70, 42.11, 25.00, 22.89, 21.62, 21.05]
# }
#
# temp = []
# for i,j in data.items():
#     print(temp.append(j))
# temp = np.asarray(temp)
# print(np.mean(temp,axis=0))
#
#
# x_values = ['Morpheus', 'DeepWordBug', 'TextFooler\n(Word2Vec)', 'TextFooler','BAE\n(CyBERT)', 'BAE', 'Ours']
#
# markers = ['o', 's', '^', 'D', 'v', 'p']
#
# plt.figure(figsize=(16, 6))
#
# for i, (group, values) in enumerate(data.items()):
#     marker = markers[i % len(markers)]
#     plt.plot(x_values, values, label=group, marker=marker)
#
#
# plt.xlabel('Methods')
# plt.ylabel('ASR (%)')
#
# plt.grid(True, linestyle='dashed', color='gray', alpha=0.4)
#
# plt.xticks(fontweight='bold')
#
# plt.legend(ncol = 3)
#
# plt.savefig('./transferability.jpg', dpi=600,bbox_inches='tight')
#
# plt.show()
