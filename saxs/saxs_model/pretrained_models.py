

from .model import SAXSViT10

from torchinfo import summary #optional

from .model_settings import IMAGE_DIM, COLOR_CHANNELS, PATCH_SIZE, ATTENTION_BLOCKS, EMBEDDING_DIM

mod = SAXSViT10(IMAGE_DIM, COLOR_CHANNELS, PATCH_SIZE, ATTENTION_BLOCKS, EMBEDDING_DIM, 3072, 12, 0.1, 0, 0.1, 3)



summary(mod,
        input_size=(1, 3, 498, 498),  # (batch_size, color_channels, height, width)
        col_names=["input_size", "output_size", "num_params", "trainable"],
        col_width=20,
        row_settings=["var_names"]
        )





