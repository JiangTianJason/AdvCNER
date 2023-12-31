##########################Intelligent assessment in Table 6 (Section 5.4.1)############################
##  Each time we copy one line in input.txt to the dialog box, and record the feedback in score.csv (for example).######
##  We don't use the official API provided by OpenAI.
##

import json
import os
import glob

for model in ["bert","albert","xlm"]:
    folder_path = "../../output_{}".format(model)

    file_list = glob.glob(os.path.join(folder_path, "*-strict-preserve.json"))
    file_list_CyBERT = glob.glob(os.path.join(folder_path, "*-strict-preserve-CyBERT.json"))
    file_list_Word2Vec = glob.glob(os.path.join(folder_path, "*-strict-preserve-Word2Vec.json"))

    file_list += file_list_CyBERT + file_list_Word2Vec

    all_temp = []
    for file_path in file_list:
        file_name = os.path.basename(file_path)
        print("File path:", file_path)
        temp = []
        with open(os.path.join(folder_path,file_name), 'r',encoding='utf-8') as fp:
            json_data = json.load(fp)
            all_indices = json_data["attacked_examples"]
            for i in range(len(all_indices)):
                try:
                    if all_indices[i]["ground_truth"] != all_indices[i]["perturbed_pred"]:
                        temp.append(i)
                except:
                    pass                        ###skipped
        all_temp.append(temp)

    common_elements = set(all_temp[0])


    for sublist in all_temp[1:]:
        common_elements.intersection_update(sublist)

    common_elements_list = sorted(list(common_elements))

    for k in common_elements_list:
        single_line = []
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            print("File path:", file_path)
            temp = []
            with open(os.path.join(folder_path,file_name), 'r',encoding='utf-8') as fp:
                json_data = json.load(fp)
                all_indices = json_data["attacked_examples"]
                single_line.append(all_indices[k]["perturbed_text"])


        with open(r"./{}/input.txt".format(model),"a",encoding="utf-8") as tp:

            tp.write(str(single_line) + "\n")                   ###Record the results generated by all methods on the same sample