import torch
from torch import nn

from saxs.saxs_model.model import PatchEmbedding


class TranSaxs(nn.Module):
    def __init__(self,
                 encoder: nn.Module,
                 decoder: nn.Module,
                 img_size: int = IMAGE_DIM,
                 in_channels: int = COLOR_CHANNELS,
                 patch_size: int = PATCH_SIZE,
                 num_transformer_layers: int = ATTENTION_BLOCKS,
                 embedding_dim: int = EMBEDDING_DIM,
                 mlp_size: int = 3072,
                 num_heads: int = 12,
                 attn_dropout: float = 0,
                 mlp_dropout: float = 0.1,
                 embedding_dropout: float = 0.1,
                 num_classes: int = 3):
        super().__init__()

        self.encoder = encoder
        self.decoder = decoder


    def forward(self, x):

        peaks_embeddings = self.encoder(x[0])
        output = self.decoder(x[1], peaks_embeddings)

        return output