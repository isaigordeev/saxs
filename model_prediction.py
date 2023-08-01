from saxs.saxs_model.phase_prediction import prediction_from_csv, prediction_from_npy
from saxs.saxs_model.model import SAXSViT10
import torch, os
from saxs.saxs_model.model_settings import DEVICE
import json


with open('model_train_config.json') as file:
    config = json.load(file)


model = SAXSViT10(**config).to(DEVICE)

state_dict = torch.load('model0.pth')

model.load_state_dict(state_dict)

# prediction_from_csv(model, 'without_back_res/075775_treated_xye.csv')
prediction_from_npy(model, 'saxs/data_generation/Synthetic_Processed/Im3m_cubic_processed.npy')

# for x in os.listdir('without_back_res/'):
#     prediction_from_csv(model, 'without_back_res/{}'.format(str(x)))