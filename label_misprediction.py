########################Top-3 Label Misprediction in Table 4#######################


from collections import Counter

def misprediction_top_3(victim_model,attack_method):
    all_indices = [eval(line) for line in open(r"./evaluation_result/{}/{}.txt".format(victim_model, attack_method), 'r',
                                               encoding="utf-8").readlines()]

    all_count = []
    for i in all_indices:
        for j in i["label_switching"]:
            origin_mis = "".join(j)
            all_count.append(origin_mis)

    d2 = Counter(all_count)
    sorted_x = sorted(d2.items(), key=lambda x: x[1], reverse=True)
    print(sorted_x)

if __name__ == "__main__":
    misprediction_top_3("albert","textfooler-Word2Vec")  ###xlm,bert,albert