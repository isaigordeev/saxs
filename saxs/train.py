import torch

import saxs_data_setup
from saxs import engine
from saxs.model import SAXSViT
from saxs.settings import TRAIN_DIR, TEST_DIR, DEVICE
import phase_prediction

saxs = SAXSViT()

train_saxs_batches, test_saxs_batches, saxs_phases = saxs_data_setup.create_data_batches(train_data_dir=TRAIN_DIR,
                                                                                          test_data_dir=TEST_DIR,
                                                                                          transforms=saxs.data_transforms,
                                                                                          batch_size=32,
                                                                                          num_workers=0
                                                                                          )




optimizer = torch.optim.Adam(params=saxs.parameters(),
                             lr=1e-3)
loss_fn = torch.nn.CrossEntropyLoss()

pretrained_vit_results = engine.train(model=saxs,
                                      train_dataloader=train_saxs_batches,
                                      test_dataloader=test_saxs_batches,
                                      optimizer=optimizer,
                                      loss_fn=loss_fn,
                                      epochs=1,
                                      device=DEVICE)



phase_prediction.prediction(saxs, saxs_phases, 'data/dot/train/Im3m/075773_treated_xye.png')

