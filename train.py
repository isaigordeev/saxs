import json
import os

import matplotlib.pyplot as plt
import torch
from torchvision.transforms import transforms


import saxs.saxs_model.saxs_dataset as data_setup
from saxs import PACKAGE_PATH
import saxs.saxs_model.phase_prediction as phase_prediction
from saxs.saxs_model import engine
from saxs.saxs_model.model import SAXSViT10
from saxs.saxs_model.model_settings import DEVICE


with open('train_config.json') as file:
    config = json.load(file)


model = SAXSViT10(**config)

TRAIN_DATA_PATH = os.path.join(os.getcwd(), 'train_data')


train_saxs_batches, test_saxs_batches, saxs_phases = \
    data_setup.create_data_batches_from_dataset_files(path=TRAIN_DATA_PATH,
                                                    transforms=None,
                                                    batch_size=32,
                                                    num_workers=0
                                                    )



optimizer = torch.optim.Adam(params=model.parameters(),
                             lr=1e-3)
loss_fn = torch.nn.CrossEntropyLoss()

pretrained_vit_results = engine.train(model=model,
                                      train_dataloader=train_saxs_batches,
                                      test_dataloader=test_saxs_batches,
                                      optimizer=optimizer,
                                      loss_fn=loss_fn,
                                      epochs=5,
                                      device=DEVICE)



torch.save(model.state_dict(), 'model0.pth')
