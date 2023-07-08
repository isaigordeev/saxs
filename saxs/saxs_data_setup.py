from pathlib import Path

import torch
import torch.utils.data
import os

from torchvision import datasets, transforms
from torch.utils.data import DataLoader

NUM_CPU_CORES = os.cpu_count()

SET_DIR = 'data/'
SET_DIR = Path(SET_DIR)
SEED = 42

data_transform = transforms.Compose([
    # transforms.Resize(size=(64, 64)), #NOTE resolution?
    transforms.ToTensor(),
])


def get_train_val(dataset, val_ratio):
    ntotal = len(dataset)
    ntrain = int((1 - val_ratio) * ntotal)
    torch.manual_seed(SEED)
    return torch.utils.data.random_split(dataset, [ntrain, ntotal - ntrain])


def create_batches(data_dir, data_transform: transforms.Compose, test_ratio: float):
    data = datasets.ImageFolder(root=data_dir,
                                transform=data_transform,
                                target_transform=None)

    train_dataset, test_dataset = get_train_val(data, val_ratio=test_ratio)

    # num_workers = os.cpu_count()//2

    train_loader = torch.utils.data.DataLoader(train_dataset,
                                               batch_size=16,
                                               #  num_workers=1,
                                               shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset,
                                              batch_size=16,
                                              #  num_workers=1,
                                              shuffle=False)

    return data, train_loader, test_loader


def create_data_batches(train_data_dir,
                        test_data_dir,
                        transforms: transforms.Compose,
                        batch_size,
                        num_workers: int = NUM_CPU_CORES
                        ):

    train_data = datasets.ImageFolder(train_data_dir, transform=transforms)
    test_data = datasets.ImageFolder(test_data_dir, transform=transforms)

    phases_names = train_data.classes

    train_batch = DataLoader(
        train_data,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )

    test_batch = DataLoader(
        test_data,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )

    return train_batch, test_batch, phases_names
