######################Adversarial detection (Section 5.3.3)#########################

import os
import glob

for model in ["bert","albert","xlm"]:
    folder_path = "./{}".format(model)

    file_list = glob.glob(os.path.join(folder_path, "*_total.txt"))
    total_score = 0

    for file_path in file_list:
        file_name = os.path.basename(file_path)
        file_prefix = file_name.rsplit("_total.txt", 1)[0]
        print("File path:", file_path)
        print("File prefix:", file_prefix)


        all_indices = [eval(line) for line in open(os.path.join(folder_path,file_name), 'r',encoding="utf-8").readlines()]
        for i in all_indices:

            rounded_number = i["all_adversarial_judged"] / i["all_adversarial_count"]           ### "status": "Successful"
            # rounded_number = (i["all_adversarial_judged"] + i["all_adversarial_include_Failed_judged"]) / (i["all_adversarial_count"] + i["all_adversarial_include_Failed_count"])    ### ("status": "Successful") + ("status": "Failed", Perturbed prediction != Original prediction)

            total_score += rounded_number
    print("average_on_{}".format(model),total_score / 7)





#######################Draw Fig.4#######################


# import matplotlib.pyplot as plt
# import numpy as np
# from matplotlib.font_manager import FontProperties
#
# categories = ['Morpheus', 'DeepWordBug', 'TextFooler\n(Word2Vec)', 'TextFooler','BAE\n(CyBERT)', 'BAE', 'Ours']
# values1 = [50.00,74.74,57.69,73.79,74.26,72.67,71.11]
# values2 = [33.33,67.03,66.10,65.31,64.96,58.33,62.37]
# values3 = [20.00,66.67,36.84,58.93,69.88,71.17,47.37]
#
# plt.figure(figsize=(16, 6))
# # plt.tight_layout()
#
# bar_width = 0.3
# index = np.arange(len(categories))
#
# plt.bar(index, values1, bar_width, label='BERT',color = "#5E8BC5")
#
# plt.bar(index + bar_width, values2, bar_width, label='ALBERT', color = "#D4695E")
#
# plt.bar(index + 2 * bar_width, values3, bar_width, label='XLM-RoBERTa', color = "#DCA11D")
#
# plt.xlabel('Methods')
# plt.ylabel('Accuracy (%)')
#
# plt.legend(loc='upper left')
#
# plt.xticks(index + bar_width, categories,fontproperties = FontProperties(weight='bold'))
# plt.ylim(10)
# plt.grid(True, linestyle='dashed',axis = "y", color='gray', alpha=0.5)
#
# x = np.arange(len(categories))
# for i in range(len(categories)):
#     plt.text(x[i], values1[i] + 0.5, str(values1[i]), ha='center', va='bottom')
#     plt.text(x[i] + bar_width, values2[i] + 0.5, str(values2[i]), ha='center', va='bottom')
#     plt.text(x[i] + 2 * bar_width, values3[i] + 0.5, str(values3[i]), ha='center', va='bottom')
#
# plt.savefig('./detection.jpg', dpi=600,bbox_inches='tight')
# plt.show()
