from torchinfo import summary #optional
from saxs.model.model import SAXSViT
from saxs.model.saxs_dataset import SAXSData



mod = SAXSViT()

data = SAXSData()


# summary(mod,
#         input_size=(1, 3, 224, 224),  # (batch_size, color_channels, height, width)
#         col_names=["input_size", "output_size", "num_params", "trainable"],
#         col_width=20,
#         row_settings=["var_names"]
#         )