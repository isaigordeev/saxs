import timm
from torchinfo import summary

from model import SASXTransformer

model_vim = timm.create_model('vit_base_patch16_224', pretrained=True)

modelx = SASXTransformer()

# print(modelx.parameters)
# summary(model=modelx,
#         input_size=(32, 1, 224,224),
#         )

# summary(SASXTransformer(), 
#         input_size=(32, 3, 224,224), 
#         col_names=["input_size", "output_size", "num_params", "trainable"],
#         col_width=20,
#         row_settings=["var_names"])

summary(SASXTransformer(),
        input_size=(32, 3, 224,224), 
        col_names=["input_size", "output_size", "num_params", "trainable"],
        col_width=20,
        row_settings=["var_names"])
