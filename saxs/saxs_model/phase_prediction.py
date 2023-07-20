import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision.transforms.v2
import pandas as pd
from PIL import Image

from .model_settings import DEVICE, DEFAULT_TRANSFORMS

def prediction(model,
               path_csv,
               class_names,
               transforms,
               cut_start=None,
               image_size=224,
               device=DEVICE):

    data = pd.read_csv(path_csv, sep=',')
    data.apply(pd.to_numeric, errors='coerce')
    data.dropna()

    I = data.iloc[:, 1]
    if cut_start is not None:
        I = I[cut_start:cut_start+image_size]

    dot_I = np.outer(I, I)
    dot_I_unsq = np.expand_dims(dot_I, axis=0)

    image = np.concatenate([dot_I_unsq, dot_I_unsq, dot_I_unsq], axis=0)

    img = Image.fromarray(np.swapaxes(np.uint8(image/np.max(image)*255), 0, 2))

    model.to(device)
    model.eval()

    with torch.inference_mode():
        transformed_phase_img = transforms(img).unsqueeze(dim=0)
        transformed_phase_img = transformed_phase_img.to(device)

        predicted_phase_tensor = model(transformed_phase_img)

        predicted_phase_probs = torch.softmax(predicted_phase_tensor, dim=1)

        predicted_phase_label = torch.argmax(predicted_phase_probs, dim=1)

    print(class_names[predicted_phase_label])







    # img = Image.fromarray()


def prediction_image(model,
               class_names,
               phase_image_path,
               transforms: torchvision.transforms = None,
               image_size=None,
               device=DEVICE):


    img = Image.open(phase_image_path).convert('RGB')

    if transforms is None:
        transforms = DEFAULT_TRANSFORMS

    model.to(device)
    model.eval()

    # print(transforms(img).shape)

    with torch.inference_mode():
        transformed_phase_img = transforms(img).unsqueeze(dim=0)
        transformed_phase_img = transformed_phase_img.to(DEVICE)

        predicted_phase_tensor = model(transformed_phase_img)

    predicted_phase_probs = torch.softmax(predicted_phase_tensor, dim=1)

    predicted_phase_label = torch.argmax(predicted_phase_probs, dim=1)

    print(class_names[predicted_phase_label])

