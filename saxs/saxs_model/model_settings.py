import torch
from torchvision import transforms

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


COLOR_CHANNELS = 3
IMAGE_DIM = 448  #len of q,I,dI
EMBEDDING_DIM = 3*IMAGE_DIM
HEADS = 12
ATTENTION_BLOCKS = 3
PATCH_SIZE = 166
PHASES_NUMBER = 3

DEFAULT_IMAGE_CLASS_TRANSFORMS = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

TRAIN_DIR = 'test_processing_data/dot/train'
TEST_DIR = 'test_processing_data/dot/test'

