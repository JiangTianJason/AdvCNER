from tner.model import TrainTransformersNER

def run_bert(model):
    # cfg1 = {'checkpoint_dir': 'logs/xlm-roberta-base',
    #         'dataset': 'dataset/mitre',
    #         'transformers_model': 'xlm-roberta-base',
    #         'lr': 1e-5,
    #         'epochs': 20,
    #         'batch_size': 8,
    #         'max_seq_length': 128}
    # model1 = TransformersNER(cfg1)
    # model1.train()

    # cfg2 = {'checkpoint_dir': 'logs/xlm-roberta-large',
    #         'dataset': 'dataset/mitre',
    #         'transformers_model': 'xlm-roberta-large',
    #         'lr': 5e-6,
    #         'epochs': 20,
    #         'max_seq_length': 256}
    # model2 = TransformersNER(cfg2)
    # model2.train()

    # cfg = {'checkpoint_dir': '.ckpt',
    #        'dataset': 'dataset/mitre',
    #        'transformers_model': 'xlm-roberta-large',
    #        'lr': 5e-6,
    #        'epochs': 20,
    #        'max_seq_length': 128}

    if model == "bert":
        model_path = r"D:\Download\Cyber-Security-NER_attack\adversarial_training\re-trained_model_correct\bert_retrain_with_100_examples"
        data_path = r"D:\Download\Cyber-Security-NER_attack\seqattack\datasets\mitre"
    elif model == "albert":
        model_path = r"D:\Download\Cyber-Security-NER_attack\adversarial_training\re-trained_model_correct\albert_retrain_with_100_examples"
        data_path = r"D:\Download\Cyber-Security-NER_attack\seqattack\datasets\mitre"
    elif model == "xlm":
        model_path = r"D:\Download\Cyber-Security-NER_attack\adversarial_training\re-trained_model_correct\xlm_retrain_with_100_examples"
        data_path = r"D:\Download\Cyber-Security-NER_attack\seqattack\datasets\mitre"

    model = TrainTransformersNER(
        checkpoint_dir=model_path,
        dataset= data_path,
        transformers_model =model_path,
        lr = 5e-6,
        epochs = 20,
        max_seq_length = 128,
        batch_size=1
    )
    model.test(test_dataset = data_path)

if __name__ == '__main__':
    run_bert("albert")
