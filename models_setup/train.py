from torch import nn
from setup import SEED, NUM_EPOCHS, DEVICE, SET_DIR, SAVE_MODEL_DIR

import torch, data_setup, model_build, engine, utils

torch.manual_seed(SEED)

data, train_loader, test_loader = data_setup.create_batches(SET_DIR/'dot',
                                                             data_setup.data_transform,
                                                             0.2)

model_name = 'tiny_model' + '.pth'
tiny_model = model_build.TinyVGG(input_shape=3, 
                     hidden_units=10,
                     output_shape=len(data.classes)).to(DEVICE)

loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(params=tiny_model.parameters(),
                             lr=0.001)



tiny_model_results = engine.train(model=tiny_model,
                           train_dataloader=train_loader,
                           test_dataloader=test_loader,
                           optimizer=optimizer,
                           loss_fn=loss_fn,
                           epochs=NUM_EPOCHS
                           )

print(tiny_model_results)


utils.save_model(model=model_build.TinyVGG,
            target_dir=SAVE_MODEL_DIR,
            model_name=model_name)
