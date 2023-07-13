import torch
from torch.utils.data import Dataset, DataLoader, random_split

class CustomDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        return sample

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

dataset = CustomDataset(data)

train_ratio = 0.8
val_ratio = 0.2

train_size = int(train_ratio * len(dataset))
val_size = len(dataset) - train_size

train_set, val_set = random_split(dataset, [train_size, val_size])

batch_size = 3
shuffle = True
num_workers = 0

train_dataloader = DataLoader(train_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)
val_dataloader = DataLoader(val_set, batch_size=batch_size, shuffle=False, num_workers=num_workers)

for batch in train_dataloader:
    inputs = batch
    print("Training batch:", inputs)
for batch in val_dataloader:
    inputs = batch

    print("Validation batch:", inputs)
