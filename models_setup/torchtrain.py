import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.metrics import f1_score
from tqdm import tqdm
import matplotlib.pyplot as plt
import os
from torch.optim.lr_scheduler import ReduceLROnPlateau
import efficientnet_pytorch as efn

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

seq_len = 200
EPOCHS = 2
NNBATCHSIZE = 64
LR = 0.0015

lam = np.load('Synthetic_Processed/lamellar.npy')
hex = np.load('Synthetic_Processed/hexagonal.npy')
p = np.load('Synthetic_Processed/P_cubic.npy')
g = np.load('Synthetic_Processed/G_cubic.npy')
d = np.load('Synthetic_Processed/D_cubic.npy')

x = np.vstack((lam,hex,p,g,d))
y = np.hstack(([0]*len(lam), [1]*len(hex), [2]*len(p), [3]*len(g), [4]*len(d)))

y = torch.tensor(y, dtype=torch.long)
y = nn.functional.one_hot(y, num_classes=5)

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

EFNS = [efn.EfficientNetB0, efn.EfficientNetB1, efn.EfficientNetB2, efn.EfficientNetB3,
        efn.EfficientNetB4, efn.EfficientNetB5, efn.EfficientNetB6]

class MyModel(nn.Module):
    def __init__(self, dim=200, ef=0):
        super(MyModel, self).__init__()
        self.base = EFNS[ef](pretrained='noisy-student')
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(self.base._fc.in_features, 5)

    def forward(self, x):
        x = self.base.extract_features(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

model = MyModel()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = ReduceLROnPlateau(optimizer, factor=0.5, patience=2)
criterion = nn.BCEWithLogitsLoss()

if torch.cuda.is_available():
    model.cuda()
    criterion = criterion.cuda()

def train(model, optimizer, criterion, train_loader):
    model.train()
    train_loss = 0
    for batch_idx, (data, target) in enumerate(train_loader):
        if torch.cuda.is_available():
            data, target = data.cuda(), target.cuda()

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target.float())
        loss.backward()
        optimizer.step()

        train_loss += loss.item()

    return train_loss / len(train_loader)

def evaluate(model, criterion, val_loader):
    model.eval()
    val_loss = 0
    with torch.no_grad():
        for data, target in val_loader:
            if torch.cuda.is_available():
                data, target = data.cuda(), target.cuda()

            output = model(data)
            loss = criterion(output, target.float())
            val_loss += loss.item()

    return val_loss / len(val_loader)

train_dataset = list(zip(X_train, y_train))
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=NNBATCHSIZE, shuffle=True)

optimizer = torch.optim.Adam(model.parameters(), lr=LR)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

for epoch in range(EPOCHS):
    running_loss = 0.0
    for i, data in enumerate(train_loader, 0):
        inputs, labels = data
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()

        outputs = model(inputs)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        if i % 10 == 9:
            print('[Epoch %d, Batch %5d] loss: %.3f' % (epoch + 1, i + 1, running_loss / 10))
            running_loss = 0.0

print('Finish')
