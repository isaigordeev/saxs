from engine import *
from model_build import *
from timeit import default_timer as timer

torch.manual_seed(SEED)

NUM_EPOCHS = 2

tiny_model = TinyVGG(input_shape=3, 
                     hidden_units=10,
                     output_shape=len(data.classes)).to(device)

loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(params=tiny_model.parameters(),
                             lr=0.001)


start_time = timer()

tiny_model_results = train(model=tiny_model,
                           train_dataloader=train_loader,
                           test_dataloader=test_loader,
                           optimizer=optimizer,
                           loss_fn=loss_fn,
                           epochs=NUM_EPOCHS
                           )

end_time = timer()
print(f'Taken: {end_time-start_time:.3f} s')