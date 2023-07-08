from torch.nn import Linear
import torchvision
from settings import DEVICE, PHASES_NUMBER,EMBEDDING_DIM

from torchinfo import summary


pretrained_vit_weights = torchvision.models.ViT_B_16_Weights.DEFAULT

pretrained_vit_B_16 = torchvision.models.vit_b_16(weights=pretrained_vit_weights).to(DEVICE)


for layer in pretrained_vit_B_16.parameters():
    layer.requires_grad = False

pretrained_vit_B_16.heads = Linear(in_features=768, out_features=PHASES_NUMBER).to(DEVICE)  # FIRSTLY



# summary(pretrained_vit_B_16,
#         input_size=(1, 3, 224, 224),  # (batch_size, color_channels, height, width)
#         col_names=["input_size", "output_size", "num_params", "trainable"],
#         col_width=20,
#         row_settings=["var_names"]
#         )





