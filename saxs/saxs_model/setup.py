from pathlib import Path

import torch

SET_DIR = 'test_processing_data/'
SET_DIR = Path(SET_DIR)

SEED = 42
NUM_EPOCHS = 1
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
SAVE_MODEL_DIR = 'models/'
