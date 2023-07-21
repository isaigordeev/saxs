import json

import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision.transforms.v2
import pandas as pd
from PIL import Image

from .model_settings import DEVICE, DEFAULT_TRANSFORMS
from .tools import array_transform_for_batches
from .. import DEFAULT_PHASES_PATH


def prediction_from_csv(model,
               path_csv,
               transforms=None,
               cut_start=None,
               image_size=224,
               device=DEVICE):


    with open(DEFAULT_PHASES_PATH, 'r') as file:  # NOTE make it better with string formatting
        phases = json.load(file)

    class_names = list(phases.keys())
    class_to_idx = {cls_name: i for i, cls_name in enumerate(class_names)}


    data = pd.read_csv(path_csv, sep=',')
    data.apply(pd.to_numeric, errors='coerce')
    data.dropna()


    I = data.iloc[:, 1]
    I = np.float32(I)

    img = array_transform_for_batches(I)
    model.to(device)
    model.eval()

    with torch.inference_mode():

        transformed_phase_img = img.unsqueeze(dim=0).to(device)


        predicted_phase_tensor = model(transformed_phase_img)

        predicted_phase_probs = torch.softmax(predicted_phase_tensor, dim=1)

        predicted_phase_label = torch.argmax(predicted_phase_probs, dim=1)

    print(class_names[predicted_phase_label])





    # img = Image.fromarray()


def prediction_from_npy(model,
               path_npy,
               transforms=None,
               cut_start=None,
               image_size=224,
               device=DEVICE):


    with open(DEFAULT_PHASES_PATH, 'r') as file:  # NOTE make it better with string formatting
        phases = json.load(file)

    class_names = list(phases.keys())
    class_to_idx = {cls_name: i for i, cls_name in enumerate(class_names)}


    data = np.load(path_npy)

    I = data[0]
    I = np.float32(I)

    img = array_transform_for_batches(I)
    model.to(device)
    model.eval()

    with torch.inference_mode():

        transformed_phase_img = img.unsqueeze(dim=0).to(device)


        predicted_phase_tensor = model(transformed_phase_img)

        predicted_phase_probs = torch.softmax(predicted_phase_tensor, dim=1)

        predicted_phase_label = torch.argmax(predicted_phase_probs, dim=1)

    print(class_names[predicted_phase_label])

