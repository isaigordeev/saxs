from torch import nn
import torch
from setup import data, SEED, train_loader

device = 'cuda' if torch.cuda.is_available() else 'cpu'

class TinyVGG(nn.Module):

    def __init__(self, input_shape: int, hidden_units: int, output_shape: int) -> None:
        super().__init__()
        self.conv_block_1 = nn.Sequential(
            nn.Conv2d(in_channels=input_shape,
                      out_channels=hidden_units,
                      kernel_size=3,
                      stride=1,
                      padding=1),
            nn.ReLU(),
            nn.Conv2d(in_channels=hidden_units,
                      out_channels=hidden_units,
                      kernel_size=3,
                      stride=1,
                      padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2,
                         stride=2)
        )
        self.conv_block_2 = nn.Sequential(
            nn.Conv2d(hidden_units, hidden_units, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(hidden_units, hidden_units, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_features=hidden_units*16*16,
                      out_features=output_shape)
        )

    def forward(self, x: torch.Tensor):
        x = self.conv_block_1(x)
        x = self.conv_block_2(x)
        return self.classifier(x)

torch.manual_seed(SEED)

tiny_model = TinyVGG(input_shape=3, 
                     hidden_units=10,
                     output_shape=len(data.classes)).to(device)

print(tiny_model)

img, label = next(iter(train_loader))

# img = img[0].unsqueeze(dim=0)

tiny_model.eval()
print(img.shape)

with torch.inference_mode():
    pred = tiny_model(img)

print(torch.softmax(pred, dim=1))


