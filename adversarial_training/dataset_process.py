import json
import os
import glob


# ###Output adversarial examples into test.txt###
for model in ["bert","albert","xlm"]:
    folder_path = "../output_{}".format(model)

    file_list = glob.glob(os.path.join(folder_path, "*-strict-preserve.json"))
    file_list_CyBERT = glob.glob(os.path.join(folder_path, "*-strict-preserve-CyBERT.json"))
    file_list_Word2Vec = glob.glob(os.path.join(folder_path, "*-strict-preserve-Word2Vec.json"))

    file_list += file_list_CyBERT + file_list_Word2Vec

    for file_path in file_list:
        file_name = os.path.basename(file_path)
        print("File path:", file_path)
        with open(os.path.join(folder_path,file_name), 'r',encoding='utf-8') as fp:
            json_data = json.load(fp)
            all_indices = json_data["attacked_examples"]
            for i in all_indices:
                if i["status"] == "Successful":
                    with open(r"datasets/{}/test.txt".format(model),"a",encoding="utf-8") as tp:
                        text = i["perturbed_text"].split(" ")
                        if model != "albert":
                            labels = i["ground_truth_labels"]
                        else:
                            albert_labels = ["B-Malware", "I-Malware", "O", "B-System", "I-System", "B-Organization", "B-Indicator", "I-Organization", "I-Indicator", "B-Vulnerability", "I-Vulnerability"]
                            labels = [albert_labels[k] for k in i["ground_truth"]]

                        for count in range(len(labels)):
                            tp.write(text[count] + "\t" + labels[count] + "\n")
                            if count == len(labels) - 1:
                                tp.write("\n")



###Output adversarial examples into train.txt###
# for model in ["albert","bert","xlm"]:
#     folder_path = "./output_{}".format(model)
#
#     file_list = glob.glob(os.path.join(folder_path, "*-strict-preserve.json"))
#
#     file_list_CyBERT = glob.glob(os.path.join(folder_path, "*-strict-preserve-CyBERT.json"))
#     file_list_Word2Vec = glob.glob(os.path.join(folder_path, "*-strict-preserve-Word2Vec.json"))
#
#     file_list += file_list_CyBERT + file_list_Word2Vec
#
#     for file_path in file_list:
#         file_name = os.path.basename(file_path)
#         print("File path:", file_path)
#         with open(os.path.join(folder_path,file_name), 'r',encoding='utf-8') as fp:
#             json_data = json.load(fp)
#             all_indices = json_data["attacked_examples"][:100]
#             for i in all_indices:
#                 if i["status"] == "Successful":
#                     with open(r"./datasets/{}/train.txt".format(model),"a",encoding="utf-8") as tp:
#                         text = i["perturbed_text"].split(" ")
#                         if model != "albert":
#                             labels = i["ground_truth_labels"]
#                         else:
#                             albert_labels = ["B-Malware", "I-Malware", "O", "B-System", "I-System", "B-Organization", "B-Indicator", "I-Organization", "I-Indicator", "B-Vulnerability", "I-Vulnerability"]
#                             labels = [albert_labels[k] for k in i["ground_truth"]]
#
#                         for count in range(len(labels)):
#                             tp.write(text[count] + "\t" + labels[count] + "\n")
#                             if count == len(labels) - 1:
#                                 tp.write("\n")
#
#     os.rename(r"./datasets/{}/train.txt".format(model), r"./datasets/{}/train_100.txt".format(model))