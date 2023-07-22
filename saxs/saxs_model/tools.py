import os
import random
from pathlib import Path
from timeit import default_timer as timer
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision
import yaml


from PIL import Image

from saxs.saxs_model.model_settings import IMAGE_DIM


def save_model(model: torch.nn.Module,
               target_dir: str,
               model_name: str):
    
    target_dir_path = Path(target_dir)
    target_dir_path.mkdir(parents=True,
                        exist_ok=True)


    assert model_name.endswith(".pth") or model_name.endswith(".pt"), "model_name should end with '.pt' or '.pth'"
    model_save_path = target_dir_path / model_name


    print(f"[INFO] Saving model to: {model_save_path}")
    torch.save(obj=model.state_dict,
             f=model_save_path)

def read_config(path):


    with open(path, 'r') as file:
        config = yaml.safe_load(file)

    param1 = config['training']['epoch']



    return (param1, )

def xtime_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = timer()
        results = func(*args, **kwargs)
        end_time = timer()
        print(f'Taken: {end_time-start_time:.3f} s')
        return results
    return wrapper


def plot_loss_curves(results: Dict[str, List[float]]):

    loss = results['train_loss']
    test_loss = results['test_loss']

    accuracy = results['train_acc']
    test_accuracy = results['test_acc']

    epochs = range(len(results['train_loss']))

    plt.figure(figsize=(15, 7))

    plt.subplot(1, 2, 1)
    plt.plot(epochs, loss, label='train_loss')
    plt.plot(epochs, test_loss, label='test_loss')
    plt.title('Loss')
    plt.xlabel('Epochs')
    plt.legend()


    plt.subplot(1, 2, 2)
    plt.plot(epochs, accuracy, label='train_accuracy')
    plt.plot(epochs, test_accuracy, label='test_accuracy')
    plt.title('Accuracy')
    plt.xlabel('Epochs')
    plt.legend()
    plt.show() #change to saving


def data_walk(dir_path): 
    for dirpath, dirnames, filenames in os.walk(dir_path):
        print(f'paths: {len(dirnames)}, file:" {len(filenames)} in {dirpath}')


def standartization(sample):
    mean = np.mean(sample)
    var = np.std(sample)
    sample -= mean
    sample /= (var ** 0.5)
    sample /= np.max(sample)

    return sample


def array_transform_for_batches(sample, IMAGE_DIM=IMAGE_DIM):
    
    if len(sample) != IMAGE_DIM:

        if len(sample) > IMAGE_DIM:
            print("SAMPLE IS GREAT")
            sample = sample[:IMAGE_DIM]
        elif len(sample) < IMAGE_DIM:
            print("SAMPLE IS NOT GREAT")
            sample = np.concatenate((sample, np.zeros(IMAGE_DIM - len(sample))))

        sample = standartization(sample)

    # sample = np.uint8(sample * 255) #pixelization

    sample = np.repeat(np.expand_dims(np.outer(sample, sample), -1), 3, axis=-1)
    sample = torch.tensor(sample)
    return torch.transpose(sample, 0, 2)
