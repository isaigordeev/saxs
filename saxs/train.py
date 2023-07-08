import saxs_data_setup
from saxs.model import SAXSViT
from saxs.settings import TRAIN_DIR, TEST_DIR
import phase_prediction

saxs = SAXSViT()

train_saxs_batches, test_saxs_batches, saxs_phases = saxs_data_setup.create_data_batches(train_data_dir=TRAIN_DIR,
                                                                                          test_data_dir=TEST_DIR,
                                                                                          transforms=saxs.data_transforms,
                                                                                          batch_size=32,
                                                                                          num_workers=0
                                                                                          )

print(train_saxs_batches)
print(len(train_saxs_batches))
print(saxs_phases)

img, label = next(iter(train_saxs_batches))

phase_prediction.prediction(saxs, saxs_phases, 'data/dot/train/Im3m/1.png')

# print(saxs(img))

