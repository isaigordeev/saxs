import os
import random
from pathlib import Path
from timeit import default_timer as timer
from typing import Dict, List

import matplotlib.pyplot as plt
import torch
import torchvision
from PIL import Image


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
    plt.legend();
    plt.show() #change to saving


def data_walk(dir_path): 
    for dirpath, dirnames, filenames in os.walk(dir_path):
        print(f'paths: {len(dirnames)}, file:" {len(filenames)} in {dirpath}')



def display_random_images(data: torchvision.datasets.ImageFolder, n):
    image_path_list = list(data.glob("*/*/*.png"))
    images = random.sample(range(len(image_path_list)), n)
    plt.clf()
    for i, x in enumerate(images):
        path, _ = data.samples[x]
        path = Path(path).parent.stem
        plt.subplot(1, n, i+1)
        plt.imshow(data[x][0].permute(1,2,0))
        plt.title(str(data[x][1]) + path)
    plt.savefig('random_images.png')

def plot_transformed_image(image_paths, transform, n=3, seed=42):
    random.seed(seed)
    random_image_paths = random.sample(image_paths, k = n)
    print(len(random_image_paths))
    i = 0
    for image_path in random_image_paths:
        with Image.open(image_path) as f:
            fig, ax = plt.subplots(1,2)
            ax[0].imshow(f)
            ax[0].set_title(f'Origi {f.size}')


            transformed = transform(f)
            transformed = torch.narrow(transformed, 0,0,3).permute(1,2,0)
            ax[1].imshow(transformed)
            ax[1].set_title(f'Origi {transformed.shape}')


            fig.suptitle(f'{image_path.parent.stem}')
        plt.savefig(f'image number {i}.png')
        i += 1
        plt.clf()

def display_random_image(data_dir: Path, n):
    image_path_list = list(data_dir.glob("*/*/*.png"))

    random_image_path = random.choice(image_path_list)
    image_class = random_image_path.parent.stem
    img = Image.open(random_image_path)
    # img.show()

    print(f"Random image path: {random_image_path}")
    print(f"Image class: {image_class}")
    print(f"Image height: {img.height}") 
    print(f"Image width: {img.width}")