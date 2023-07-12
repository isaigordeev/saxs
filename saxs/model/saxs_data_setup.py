from pathlib import Path

import torch
import torch.utils.data
import os

from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Dataset

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




def create_data_batches_from_folder(train_data_dir,
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

def create_data_batches_from_dataset_files(train_data_dir,
                                    test_data_dir,
                                    transforms: transforms.Compose,
                                    batch_size,
                                    num_workers: int = NUM_CPU_CORES
                                    ):

    # train_data = #TODO
    # test_data =

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


class SAXSData(Dataset):
    def __init__(self):
        self.data = [...]

        self.find_classes(self.root)

    def __getitem__(self, index):
        item = self.data[index]
        # transformed_im = ...  # TRANSFORM
        # return transformed_im

    def __len__(self):
        # Return the size of the dataset
        return len(self.data)

    def find_classes(self, directory):
        dataset_names = os.listdir(directory)
        classes = [filename[:4] for filename in dataset_names]

        class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        return classes, class_to_idx