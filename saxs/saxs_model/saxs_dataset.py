import json
from pathlib import Path

import numpy as np
import torch
import torch.utils.data
import os

from PIL import Image
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Dataset
from saxs import DEFAULT_PHASES_PATH
from saxs.saxs_model.tools import array_transform_for_batches

NUM_CPU_CORES = os.cpu_count()

SET_DIR = 'test_processing_data/'
SET_DIR = Path(SET_DIR)
SEED = 42

data_transform = transforms.Compose([
    # transforms.Resize(size=(64, 64)), #NOTE resolution?
    transforms.ToTensor(),
])


def get_train_val(dataset, train_ratio):
    ntotal = len(dataset)
    ntrain = int(train_ratio * ntotal)
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


def create_data_batches_from_dataset_files(path,
                                           batch_size,
                                           transforms: transforms.Compose = None,
                                           num_workers: int = 0
                                           ):
    dataset = SAXSData(path=path, transforms=transforms)
    train_data, test_data = get_train_val(dataset, 0.8)

    # print(train_data)
    phases_names = train_data.dataset.classes

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
    def __init__(self, path=None, transforms=None):
        self.samples = []
        self.path = path
        self.transforms = transforms
        self.classes, self.classes_dict = self.find_classes()

        self.data = None

        self.make_dataset_from_npy()

    def make_dataset_from_npz(self):
        assert os.path.isfile(self.path)

        self.data = np.load(self.path)
        for phase in self.classes:
            index = self.classes_dict[phase]
            for sample in self.data[phase]:
                self.samples.append((sample, index))

    def make_dataset_from_npy(self):
        assert os.path.isdir(self.path)

        files = os.listdir(self.path)

        for phase in self.classes:
            index = self.classes_dict[phase]
            for file in files:
                if phase in file:
                    self.data = np.load(os.path.join(self.path, file))

                    for sample in self.data:
                        self.samples.append((sample, index))
                    break

        print(len(self.samples), ": LEN OF SAMPLES")

    def __getitem__(self, index):
        sample, target = self.samples[index]

        sample = array_transform_for_batches(sample)

        # if self.transforms is not None:
        #     sample = self.transforms(sample)
        # else:
        #     sample = transforms.ToTensor()(sample)
        sample = torch.tensor(sample, dtype=torch.float32)
        return sample, torch.nn.functional.one_hot(torch.tensor(target), num_classes=len(self.classes)).float()

    def __len__(self):
        # Return the size of the dataset
        return len(self.samples)

    def find_classes_old(self, directory):
        dataset_names = os.listdir(directory)
        classes = [filename[:4] for filename in dataset_names]

        class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        return classes, class_to_idx

    def find_classes(self, path=DEFAULT_PHASES_PATH):
        with open(path, 'r') as file:  # NOTE make it better with string formatting
            phases = json.load(file)

        classes = list(phases.keys())
        class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        return classes, class_to_idx
