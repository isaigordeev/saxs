import os

import matplotlib.pyplot as plt
import torch
from torchvision.transforms import transforms

import saxs.saxs_model.saxs_dataset as data_setup
from saxs import PACKAGE_PATH
import saxs.saxs_model.phase_prediction as phase_prediction
from saxs.saxs_model import engine
from saxs.saxs_model.model import SAXSViT
from saxs.saxs_model.model_settings import TRAIN_DIR, TEST_DIR, DEVICE

from PIL import Image

from torchinfo import summary

# Example image file path
# image_path = 'saxs/data/dot/train/Im3m/075773_treated_xye.png'


# transform = transforms.Compose([
#     transforms.Resize((256, 256)),        # Resize the image to a specific size
#     transforms.RandomCrop((224, 224)),    # Randomly crop the image
#     transforms.ToTensor(),                 # Convert the image to a PyTorch tensor
#     transforms.Normalize((0.5, 0.5, 0.5),  # Normalize the image pixel values
#                          (0.5, 0.5, 0.5))
# ])

# # Load and transform the image
# image = Image.open(image_path).convert('RGB')
# to = transforms.ToTensor()
# im = to(image)
# print(im.shape)
# print(image.size)
# transformed_image = transform(image)
# print(transformed_image.shape, 'da')




model = SAXSViT()

summary(
    model,
    input_size=(1,3, 224,224),
    col_names=["input_size", "output_size", "num_params", "trainable"],
    col_width=20,
    row_settings=["var_names"]
)

# train_saxs_batches, test_saxs_batches, saxs_phases = \
#     data_setup.create_data_batches_from_dataset_files(path=os.path.join(PACKAGE_PATH, 'cache/small_joined_phases.npz'),
#                                                     transforms=saxs_model.data_transforms,
#                                                     batch_size=32,
#                                                     num_workers=0
#                                                     )

# print('finish')
# a ,b = next(iter(train_saxs_batches))
# # plt.imshow(a[0][0,:,:].numpy())
# # print(torch.abs(torch.diag(a[0][0,:,:])).numpy())
# for x in range(10,14):
#     plt.plot(torch.diag(a[x][0,:,:]).numpy(), label=''.join(saxs_phases[b[x]]))
# # plt.plot(torch.sqrt(torch.diag(a[0][0,:,:])).numpy())
# plt.legend()
# plt.show()

# from saxs.saxs_model.phase_prediction import prediction

# prediction(None, 'res/075775_treated_xye.csv', None, None, 230)




# plt.plot(a[2])
# print(saxs_phases[b[2]])

# for x in train_saxs_batches:
#     # print(x['input'])
#     # print(*x['target'])
#     print(x)



# optimizer = torch.optim.Adam(params=saxs_model.parameters(),
#                              lr=1e-3)
# loss_fn = torch.nn.CrossEntropyLoss()

# pretrained_vit_results = engine.train(saxs_model=saxs_model,
#                                       train_dataloader=train_saxs_batches,
#                                       test_dataloader=test_saxs_batches,
#                                       optimizer=optimizer,
#                                       loss_fn=loss_fn,
#                                       epochs=1,
#                                       device=DEVICE)
#
#
#
# phase_prediction.prediction(saxs_model, saxs_phases, 'data/dot/train/Im3m/075773_treated_xye.png')
