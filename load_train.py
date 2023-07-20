


import os

import matplotlib.pyplot as plt
import torch
from torch.nn import ModuleList
from torchvision.transforms import transforms

import saxs.saxs_model.saxs_dataset as data_setup
from saxs import PACKAGE_PATH
import saxs.saxs_model.phase_prediction as phase_prediction
from saxs.saxs_model import engine
from saxs.saxs_model.model import SAXSViT
from saxs.saxs_model.model_settings import DEVICE



weights = torch.load('model0.pth')
model = SAXSViT()

model.load_state_dict(weights)
model.train()

train_saxs_batches, test_saxs_batches, saxs_phases = \
    data_setup.create_data_batches_from_dataset_files(path='/content/small_joined_phases.npz',
                                                    transforms=d.data_transforms,
                                                    batch_size=32,
                                                    num_workers=0
                                                    )


# print(list(train_saxs_batches)[0][1])
#
# print(saxs_model(list(train_saxs_batches)[0][0]))
#
# print('finished')

optimizer = torch.optim.Adam(params=model.parameters(),
                             lr=1e-1)
loss_fn = torch.nn.CrossEntropyLoss()

pretrained_vit_results = engine.train(model=model,
                                      train_dataloader=train_saxs_batches,
                                      test_dataloader=test_saxs_batches,
                                      optimizer=optimizer,
                                      loss_fn=loss_fn,
                                      epochs=5,
                                      device=DEVICE)


torch.save(model.state_dict(), 'model1.pth')


