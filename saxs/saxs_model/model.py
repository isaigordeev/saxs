import torch
import torchvision
from torch import nn

from .model_settings import EMBEDDING_DIM, PATCH_SIZE, COLOR_CHANNELS, ATTENTION_BLOCKS, IMAGE_DIM, DEVICE, PHASES_NUMBER





class SAXSpy(nn.Module):
    def __init__(self, input_shape: int, hidden_units: int, output_shape=3) -> None:
        super().__init__()
        self.efficientnet = None #TODO
        self.block1 = nn.Sequential(
            nn.Conv2d(input_shape,
                      hidden_units,
                      kernel_size=3, padding=1),
            nn.Linear(in_features=hidden_units,
                      out_features=output_shape),
        )

    def forward(self, x: torch.Tensor):
        return self.block1(x)

class SAXSConv(nn.Module):
    def __init__(self, input_shape, hidden_units, output_shape):
        super().__init__()

        self.block_1 = nn.Sequential(
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
        self.block_2 = nn.Sequential(
            nn.Conv2d(hidden_units, hidden_units, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(hidden_units, hidden_units, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_features=hidden_units * 7 * 7,
                      out_features=output_shape)
        )

    def forward(self, x):
        x = self.block_1(x)
        x = self.block_2(x)
        return self.classifier(x)




class PatchEmbedding(nn.Module):

    def __init__(self,
                 in_channels: int = COLOR_CHANNELS,
                 patch_size: int = PATCH_SIZE,
                 embedding_dim: int = EMBEDDING_DIM):
        super().__init__()
        self.patch_size = patch_size

        self.patcher = nn.Conv2d(in_channels=in_channels,
                                 out_channels=embedding_dim,
                                 kernel_size=self.patch_size,
                                 stride=patch_size,
                                 padding=0)

        self.flatten = nn.Flatten(start_dim=2,
                                  end_dim=3)

    def forward(self, x):
        image_resolution = x.shape[-1]
        assert image_resolution % self.patch_size == 0, f"Input image size must be divisble by patch size, image shape: {image_resolution}, patch size: {patch_size}"

        x_patched = self.patcher(x)
        x_flattened = self.flatten(x_patched)
        return x_flattened.permute(0, 2, 1)


class OriginalViT(nn.Module):
    def __init__(self,
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

        assert img_size % patch_size == 0, f"Image size must be divisible by patch size, image size: {img_size}, patch size: {patch_size}."
        print(embedding_dim)
        self.num_patches = (img_size * img_size) // patch_size ** 2

        self.class_embedding = nn.Parameter(data=torch.randn(1, 1, embedding_dim),
                                            requires_grad=True)

        self.position_embedding = nn.Parameter(data=torch.randn(1, self.num_patches + 1, embedding_dim),
                                               requires_grad=True)

        self.embedding_dropout = nn.Dropout(p=embedding_dropout)

        self.patch_embedding = PatchEmbedding(in_channels=in_channels,
                                              patch_size=patch_size,
                                              embedding_dim=embedding_dim)

        self.transformer_encoder = nn.Sequential(*[nn.TransformerEncoderLayer(d_model=embedding_dim,
                                                                              nhead=num_heads,
                                                                              dim_feedforward=mlp_size,
                                                                              dropout=attn_dropout,
                                                                              activation="gelu",
                                                                              batch_first=True,
                                                                              norm_first=True) for _ in
                                                   range(num_transformer_layers)])

        self.classifier = nn.Sequential(
            nn.LayerNorm(normalized_shape=embedding_dim),
            nn.Linear(in_features=embedding_dim,
                      out_features=embedding_dim),
            nn.GELU(),
            nn.Linear(in_features=embedding_dim,
                      out_features=num_classes)
        )

    def forward(self, x):
        batch_size = x.shape[0]

        class_token = self.class_embedding.expand(batch_size, -1, -1)

        x = self.patch_embedding(x)

        x = torch.cat((class_token, x), dim=1)

        x = self.position_embedding + x

        x = self.embedding_dropout(x)

        x = self.transformer_encoder(x)

        x = self.classifier(x[:, 0])

        return x


class SAXSViT10(OriginalViT):
    def __init__(self, img_size, in_channels, patch_size, num_transformer_layers, embedding_dim, mlp_size, num_heads,
                 attn_dropout, mlp_dropout, embedding_dropout, num_classes):

        super().__init__(img_size, in_channels, patch_size, num_transformer_layers, embedding_dim, mlp_size, num_heads,
                         attn_dropout, mlp_dropout, embedding_dropout, num_classes)



class SAXSViT(nn.Module):
    def __init__(self, pretrained=False):
        super().__init__()

        self.data_transforms = None



        if pretrained:
            self.pretrained_vit_weights = torchvision.models.ViT_B_16_Weights.DEFAULT
        else: 
            self.pretrained_vit_weights = None

        self.vit_pretrained = torchvision.models.vit_b_16(self.pretrained_vit_weights).to(DEVICE)
             

        for layer in self.vit_pretrained.parameters():
            layer.requires_grad = False

        # self.vit_pretrained.heads = nn.Sequential(nn.Linear(in_features=768, out_features=PHASES_NUMBER).to(DEVICE))

        self.vit_pretrained.heads = nn.Sequential(
          nn.Linear(in_features=768, out_features=256).to(DEVICE),
          nn.Tanh(),
          nn.Linear(in_features=256, out_features=PHASES_NUMBER).to(DEVICE),
        ) 
        


        # self.get_pretrained_vit()

        # self.classifier = nn.Linear(in_features=768, out_features=PHASES_NUMBER).to(DEVICE) 


    def get_pretrained_vit(self):
        self.pretrained_vit_weights = torchvision.models.ViT_B_16_Weights.DEFAULT

        self.vit_pretrained = torchvision.models.vit_b_16(weights=self.pretrained_vit_weights).to(DEVICE)

        for layer in self.vit_pretrained.parameters():
            layer.requires_grad = False

        self.vit_pretrained.heads = nn.Linear(in_features=768, out_features=PHASES_NUMBER).to(DEVICE)  # FIRSTLY

        self.data_transforms = self.pretrained_vit_weights.transforms()
        print(self.data_transforms)

    def forward(self, x):
        x = self.vit_pretrained(x)
        # x = self.classifier(x)
        return x

