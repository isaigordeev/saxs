import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


COLOR_CHANNELS = 3
IMAGE_DIM = 500 # len of q,I,dI
EMBEDDING_DIM = 3*IMAGE_DIM
HEADS = 12
ATTENTION_BLOCKS = 3
PATCH_SIZE = 16
PHASES_NUMBER = 3