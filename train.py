import os

import matplotlib.pyplot as plt
import torch
from torchvision.transforms import transforms

import saxs.saxs_model.saxs_dataset as data_setup
from saxs import PACKAGE_PATH
import saxs.saxs_model.phase_prediction as phase_prediction
from saxs.saxs_model import engine
from saxs.saxs_model.model import SAXSViT
from saxs.saxs_model.model_settings import DEVICE





model = SAXSViT()

train_saxs_batches, test_saxs_batches, saxs_phases = \
    data_setup.create_data_batches_from_dataset_files(path=os.path.join(PACKAGE_PATH, 'cache/small_joined_phases.npz'),
                                                    transforms=model.data_transforms,
                                                    batch_size=32,
                                                    num_workers=0
                                                    )


# print(list(train_saxs_batches)[0][1])
#
# print(saxs_model(list(train_saxs_batches)[0][0]))
#
# print('finished')

optimizer = torch.optim.Adam(params=model.parameters(),
                             lr=1e-3)
loss_fn = torch.nn.CrossEntropyLoss()

pretrained_vit_results = engine.train(model=model,
                                      train_dataloader=train_saxs_batches,
                                      test_dataloader=test_saxs_batches,
                                      optimizer=optimizer,
                                      loss_fn=loss_fn,
                                      epochs=1,
                                      device=DEVICE)



phase_prediction.prediction(model,
                            'res/075773_treated_xye.csv',
                            saxs_phases,
                            model.data_transforms,
                            230,
                            )

# torch.save(saxs_model.state_dict(), 'model0.pth')
