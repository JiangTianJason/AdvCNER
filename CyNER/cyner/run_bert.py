from tner.model import TrainTransformersNER
from transformers_ner import TransformersNER

def run_bert(model,adversarial_number,mode):

    def output_transformers_model(model):
        if model == "albert":
            transformers_model = "/root/albert-large-v2_20"
        elif model == "bert":
            transformers_model = "/root/ckpt_bert_20"
        else:
            transformers_model = "/root/ckpt_20"
        return transformers_model

    if mode == "adv_train":
        #### Adversarial training ####
        cfg1 = {'checkpoint_dir': 're-trained_model/{}_retrain_with_{}_examples'.format(model,adversarial_number),      ###Path to load retrained models
                'dataset': '../../adversarial_training/datasets/{}/{}'.format(model,adversarial_number),
                'model': output_transformers_model(model),
                'lr': 5e-06,
                'epochs': 20,
                'batch_size': 32,
                'max_seq_length': 128}
        adversarial_training_model = TransformersNER(cfg1)
        adversarial_training_model.train()

    elif mode == "test":
        ##Test adversarial trained models on original test set and adversarial test set####
        if adversarial_number == 0:
            model_path = output_transformers_model(model)
        else:
            model_path = r"re-trained_model/{}_retrain_with_{}_examples".format(model,adversarial_number)      ###Path to load retrained models

        ###Let's see the performance on "original test set" improved or not
        data_path = r"../../Seqattack/datasets/mitre"


        model = TrainTransformersNER(
            checkpoint_dir=model_path,
            dataset= data_path,
            transformers_model =model_path,
            lr = 5e-6,
            epochs = 20,
            max_seq_length = 128,
            batch_size=8
        )
        model.test(test_dataset = data_path)

if __name__ == '__main__':
        run_bert("xlm",100,"test")               ###"adv_train" or "test"
