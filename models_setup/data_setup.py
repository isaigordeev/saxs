from pathlib import Path
from torchvision import datasets, transforms
import torch


SET_DIR = 'data/'
SET_DIR = Path(SET_DIR)
SEED = 42


data_transform = transforms.Compose([
    transforms.Resize(size=(64, 64)),
    transforms.ToTensor(),
])

def get_train_val(dataset, val_ratio):
        ntotal = len(dataset)
        ntrain = int((1 - val_ratio) * ntotal)
        torch.manual_seed(SEED)
        return torch.utils.data.random_split(dataset, [ntrain, ntotal - ntrain])

def create_batches(data_dir : Path, data_transform : transforms.Compose, test_ratio: float):

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



