import torch
import torchvision.transforms.v2
from PIL import Image

from .model_settings import DEVICE, DEFAULT_TRANSFORMS


def prediction(model,
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
