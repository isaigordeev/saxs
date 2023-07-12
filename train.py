import torch

import saxs.model.saxs_data_setup as data_setup
import saxs.model.phase_prediction as phase_prediction
from saxs.model import engine
from saxs.model.model import SAXSViT
from saxs.model.model_settings import TRAIN_DIR, TEST_DIR, DEVICE

model = SAXSViT()

train_saxs_batches, test_saxs_batches, saxs_phases = \
    data_setup.create_data_batches_from_folder(train_data_dir=TRAIN_DIR,
                                                    test_data_dir=TEST_DIR,
                                                    transforms=model.data_transforms,
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
                                      epochs=1,
                                      device=DEVICE)



phase_prediction.prediction(model, saxs_phases, 'data/dot/train/Im3m/075773_treated_xye.png')

