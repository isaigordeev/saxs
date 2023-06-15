from model import SASXTransformer
from torchsummary import summary

modelx = SASXTransformer()


summary(model=modelx,
        input_size=(32,1, 224,224),
        )
