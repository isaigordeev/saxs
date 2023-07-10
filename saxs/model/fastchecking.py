from model import *

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

summary(tiny_model, input_size=[1,3,64,64])