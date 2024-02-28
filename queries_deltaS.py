############Statistics in Table 5###############
###Δ𝑆 (perturbed score - initial score)  +   Number of Queries


import json
import os
import glob
for model in ["bert","albert","xlm"]:
    folder_path = "output_{}".format(model)

    file_list = glob.glob(os.path.join(folder_path, "*.json"))
    # file_list_CyBERT = glob.glob(os.path.join(folder_path, "*-strict-preserve-CyBERT.json"))
    # file_list_Word2Vec = glob.glob(os.path.join(folder_path, "*-strict-preserve-Word2Vec.json"))
    #
    # file_list += file_list_CyBERT + file_list_Word2Vec

    all_temp = []

    for file_path in file_list:
        total_queries, total_perturbed_score, success = 0, 0, 0
        file_name = os.path.basename(file_path)
        print("File path:", file_path)
        temp = set()
        with open(os.path.join(folder_path,file_name), 'r',encoding='utf-8') as fp:
            json_data = json.load(fp)
            all_indices = json_data["attacked_examples"]
            for i in range(len(all_indices)):
                try:
                    if all_indices[i]["status"] == "Successful":
                        total_queries += all_indices[i]["num_queries"]              ###Number of Queries
                        total_perturbed_score += (all_indices[i]["perturbed_score"] - all_indices[i]["original_score"])     ###Δ𝑆, perturbed score - initial score
                        success += 1

                except:
                    pass                        ###skipped

            print("avg_query, avg_deltaS", total_queries / success,total_perturbed_score / success)