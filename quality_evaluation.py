######################Quality of generation in Table 4 (Section 5.3.2)#####################

import logging
import os
import OpenAttack
import tensorflow_text
from tqdm import tqdm
from OpenAttack.metric import *
from gingerit.gingerit import GingerIt
import json

logging.basicConfig(level=logging.INFO)

##Suitable for model "albert"
labels = ["B-Malware", "I-Malware", "O", "B-System", "I-System", "B-Organization", "B-Indicator", "I-Organization", "I-Indicator", "B-Vulnerability", "I-Vulnerability"]

##Suitable for models "bert" and "xlm"
# labels = ["B-Malware", "O", "B-Indicator", "I-Indicator", "B-System", "I-System","B-Organization", "I-Malware", "I-Organization", "B-Vulnerability", "I-Vulnerability"]


def total_calc(victim_model,attack_method):

    all_indices = [eval(line) for line in open(r"./evaluation_result/{}/{}-Word2Vec.txt".format(victim_model,attack_method), 'r',encoding="utf-8").readlines()]

    quality_total_path = r"./evaluation_result/{}/{}-Word2Vec_total.txt".format(victim_model, attack_method)

    if os.path.exists(quality_total_path):
        logging.info("All done！")

    else:
        Distance,Mistake,Fluency,Semantic,WMR = 0,0,0,0,0

        for sample in tqdm(all_indices):

            Distance += sample['Levenshtein Edit Distance']
            Mistake += sample["mistake"]
            Fluency += sample['Fluency (ppl)']
            Semantic += sample['Semantic Similarity']
            WMR += sample['Word Modif. Rate']

        dict4 = {"Dis":Distance/len(all_indices),"Err":Mistake/len(all_indices),"Flu":Fluency/len(all_indices),"Sem":Semantic/len(all_indices),"WMR":WMR/len(all_indices)}

        f = open(quality_total_path, "a",encoding="utf-8")
        f.write(str(dict4) + "\n")
        f.close()

        logging.info("All done！")



def evaluate(input_sample):

    fluency = Fluency()
    semantic = SemanticSimilarity()
    distance = EditDistance()
    modification = ModificationRate()

    attack_eval = OpenAttack.attack_eval.AttackEval(language= "english",metrics=[fluency,semantic,distance,modification])

    analysis = attack_eval.measure(input_sample["original_text"],input_sample["perturbed_text"])

    output = GingerIt().parse(input_sample["perturbed_text"][:600])

    result = [i for i in output["corrections"] if i["definition"] != 'Accept space']
    mistake = len(result) if result else 0
    analysis["mistake"] = mistake


    ###Label switching

    label_switching = []
    for i,j in zip(input_sample["ground_truth"],input_sample["perturbed_pred"]):
        if i != j:
            true_label, pred_label = labels[int(i)], labels[int(j)]
            label_switching.append([true_label,pred_label])
    analysis["label_switching"] = label_switching


    ###Score

    analysis["original_score"] = input_sample["original_score"]
    analysis["perturbed_score"] = input_sample["perturbed_score"]

    return analysis



def do_it(victim_model,attack_method):
    with open(r"./output_{}/cti-{}-strict-preserve-Word2Vec.json".format(victim_model,attack_method), 'r',encoding='utf-8') as fp:
        json_data = json.load(fp)
        all_indices = json_data["attacked_examples"]
    output_file = r"./evaluation_result/{}/{}-Word2Vec.txt".format(victim_model,attack_method)

    logging.info("Output file：----> {}".format(output_file))

    if os.path.exists(output_file):             ###Prevent processing interruptions, continue from the breakpoint

        generated_samples = [eval(line) for line in open(output_file, 'r', encoding="utf-8").readlines()]
        if generated_samples[-1]["perturbed_score"] == all_indices[-1]['perturbed_score']:
            total_calc(victim_model, attack_method)
            return
        success_count,break_index = 0,0
        for sample in all_indices:
            break_index += 1
            if sample["status"] == "Successful":
                success_count += 1
                if success_count == len(generated_samples):
                    remain_indices = all_indices[break_index:]
        logging.info('Restore progress')
    else:
        remain_indices = all_indices

    for sample in tqdm(remain_indices):
        if sample["status"] == "Successful":
            f = open(output_file, "a", encoding='utf-8')
            f.write(str(evaluate(sample)) + "\n")
            f.close()

    total_calc(victim_model, attack_method)

    return


if __name__ == "__main__":
    do_it("albert","textfooler")         ###xlm,bert,albert
    # print(evaluate("Phones ?","Phones ."))
