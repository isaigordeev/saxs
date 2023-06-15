from model import SASXTransformer
from torchinfo import summary

from saxs.model import PatchEmbedding

modelx = SASXTransformer()

# print(modelx.parameters)
# summary(model=modelx,
#         input_size=(32, 1, 224,224),
#         )

summary(PatchEmbedding(), 
        input_size=(32, 3, 224,224), 
        col_names=["input_size", "output_size", "num_params", "trainable"],
        col_width=20,
        row_settings=["var_names"])
