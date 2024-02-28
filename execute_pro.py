import os
#####
##strict: I-CLS -> B-CLS is not allowed
##preserve: NonNamedEntityConstraint, checked by the pre-trained NER model "xlm-roberta"
##"--dataset-config" should be assigned to configs/cti-config-for-albert.json or adversarial_training/configs/cti-config-for-albert.json when using "albert"
#####

attack_method = "nvjr"
goal_function = "untargeted-strict"
start_index = 0        #Begin from the 0th sample by DEFAULT


####adversarial generation####

####xlm-roberta###
# os.system("python cli.py attack --model-name /root/ckpt_20 --goal-function {} --output-path output_xlm/cti-{}-strict-preserve.json --num-examples {} --no-cache --dataset-config configs/cti-config.json {}".format(goal_function,attack_method,start_index,attack_method))


# #### bert####
# os.system("python cli.py attack --model-name /root/ckpt_bert_20 --goal-function {} --output-path output_bert/cti-{}-strict-preserve.json --num-examples {} --no-cache --dataset-config configs/cti-config.json {}".format(goal_function,attack_method,start_index,attack_method))


###albert###
# os.system("python cli.py attack --model-name /root/albert-large-v2_20 --goal-function {} --output-path output_albert/cti-{}-strict-preserve.json --num-examples {} --no-cache --dataset-config configs/cti-config.json {}".format(goal_function,attack_method,start_index,attack_method))



#####generation for adversarial training####

####xlm-roberta###
# os.system("python cli.py attack --model-name /root/ckpt_20 --goal-function {} --output-path adversarial_training/output_xlm/cti-{}-strict-preserve-Word2Vec.json --num-examples {} --no-cache --dataset-config adversarial_training/configs/cti-config.json {}".format(goal_function,attack_method,start_index,attack_method))
#
#
# #### bert####
# os.system("python cli.py attack --model-name /root/ckpt_bert_20 --goal-function {} --output-path adversarial_training/output_bert/cti-{}-strict-preserve.json --num-examples {} --no-cache --dataset-config adversarial_training/configs/cti-config.json {}".format(goal_function,attack_method,start_index,attack_method))
#
#
###albert###
os.system("python cli.py attack --model-name /root/albert-large-v2_20 --goal-function {} --output-path adversarial_training/output_albert/cti-{}-strict-preserve.json --num-examples {} --no-cache --dataset-config adversarial_training/configs/cti-config.json {}".format(goal_function,attack_method,start_index,attack_method))