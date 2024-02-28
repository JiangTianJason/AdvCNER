###Use "data_prepration.py" to output evaluation scores for each method first

import csv
from collections import defaultdict

scores_dict = defaultdict(lambda: {'total_score': 0, 'count': 0})

position_scores = [7, 6, 5, 4, 3, 2, 1]

csv_filename = r'bert/score.csv'  # read the 'score.csv' file

print("The folder is：",csv_filename)

with open(csv_filename, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # Multiply each ordinal number of the row data with the corresponding score and accumulate to the corresponding ordinal number
        for position, number in enumerate(row):
            number = int(number.strip())
            scores_dict[number]['total_score'] += position_scores[position]
            scores_dict[number]['count'] += 1

average_scores = {number: score_info['total_score'] / score_info['count']
                 for number, score_info in scores_dict.items()}

for number, average_score in sorted(average_scores.items()):
    print(f"The average score value for index {number} is：{average_score:.2f}")




# File path: ../output_bert/cti-bae-strict-preserve.json
# File path: ../output_bert/cti-deepwordbug-strict-preserve.json
# File path: ../output_bert/cti-morpheus-strict-preserve.json
# File path: ../output_bert/cti-textfooler-strict-preserve.json
# File path: ../output_bert/cti-bae-strict-preserve-CyBERT.json
# File path: ../output_bert/cti-textfooler-strict-preserve-Word2Vec-similar_by_word.json
# File path: ../output_bert/cti-nvjr-strict-preserve-MustInWord2vec-WIR-random-threshold0.2.json