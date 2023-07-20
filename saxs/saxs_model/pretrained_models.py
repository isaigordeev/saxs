

from .model import SAXSViT

from torchinfo import summary #optional


mod = SAXSViT()


summary(mod,
        input_size=(1, 3, 224, 224),  # (batch_size, color_channels, height, width)
        col_names=["input_size", "output_size", "num_params", "trainable"],
        col_width=20,
        row_settings=["var_names"]
        )





