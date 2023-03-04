import os 
import random
from PIL import Image
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt


class RemoveAlphaChannel(object):
    """Custom transform to remove the alpha channel from an image tensor"""
    
    def __call__(self, tensor_img):
        # assume tensor_img is a tensor image with shape (4, height, width)
        # where the first channel is the red channel, second is the green channel, 
        # third is the blue channel and the fourth channel is the alpha channel
        
        # remove the alpha channel using torch.narrow()
        tensor_img_rgb = torch.narrow(tensor_img, 0, 0, 3)
        
        return tensor_img_rgb


SET_DIR = 'data/'
SET_DIR = Path(SET_DIR)
SEED = 42


def data_walk(dir_path): 
    for dirpath, dirnames, filenames in os.walk(dir_path):
        print(f'paths: {len(dirnames)}, file:" {len(filenames)} in {dirpath}')

data_walk(SET_DIR)



image_path_list = list(SET_DIR.glob("*/*/*.png"))

random_image_path = random.choice(image_path_list)
image_class = random_image_path.parent.stem
img = Image.open(random_image_path)
# img.show()

print(f"Random image path: {random_image_path}")
print(f"Image class: {image_class}")
print(f"Image height: {img.height}") 
print(f"Image width: {img.width}")


data_transform = transforms.Compose([
    transforms.Resize(size=(64, 64)),
    transforms.ToTensor(),
])

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


plot_transformed_image(image_path_list, data_transform, n=3)

data = datasets.ImageFolder(root=SET_DIR/'dot',
                            transform=data_transform,
                            target_transform=None)

def get_train_val(dataset, val_ratio):
        ntotal = len(dataset)
        ntrain = int((1 - val_ratio) * ntotal)
        torch.manual_seed(SEED)
        return torch.utils.data.random_split(dataset, [ntrain, ntotal - ntrain])

train_dataset, test_dataset = get_train_val(data, 0.2)

num_workers = os.cpu_count()//2
# create DataLoader objects for the training and validation sets
train_loader = torch.utils.data.DataLoader(train_dataset,
                                             batch_size=16,
                                            #  num_workers=1,
                                             shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset,
                                             batch_size=16,
                                            #  num_workers=1,
                                             shuffle=False)



print(data)
print(train_loader)
print(test_loader)

class_names = data.classes
class_dict = data.class_to_idx
print(class_names, class_dict)
print(len(train_dataset), len(test_dataset))


img, label = train_dataset[31][0], train_dataset[31][1]
print(img)
print(label)
print(img.shape)
print(img.dtype)

img_permute = img.permute(1, 2, 0)

# plt.figure(figsize=(10,7))
# plt.imshow(img_permute)
# plt.axis('off')
# plt.title(f'{class_names[label]}')
# plt.show()



def display_random_images(data, n):
    images = random.sample(range(len(data)), n)
    plt.clf()
    for i, x in enumerate(images):
        path, _ = data.samples[x]
        path = Path(path).parent.stem
        # path = Path(path).parent
        plt.subplot(1, n, i+1)
        plt.imshow(data[x][0].permute(1,2,0))
        plt.title(str(data[x][1]) + path)
    plt.savefig('random_images.png')


# display_random_images(data, 3)

