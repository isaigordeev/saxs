import torch

from tqdm.auto import tqdm
from torch import nn 


device = 'cpu'

def train_step(model: torch.nn.Module, 
               dataloader: torch.utils.data.DataLoader,
               loss_fn: torch.nn.Module,
               optimizer: torch.optim.Optimizer):
    model.train()

    train_loss, train_acc = 0, 0

    for batch, (img, label) in enumerate(dataloader):
        img, label = img.to(device), label.to(device)

        label_pred = model(img)

        loss = loss_fn(label_pred, label)
        train_loss += loss.item()

        optimizer.zero_grad()
        loss.backward()

        optimizer.step()

        label_pred_class = torch.argmax(torch.softmax(label_pred, dim=1), dim=1)
        train_acc += ((label_pred_class == label).sum().item()/len(label_pred))


    train_loss = train_loss/ len(dataloader)
    train_acc = train_acc/ len(dataloader)
    return train_loss, train_acc


def test_step(model: torch.nn.Module, 
               dataloader: torch.utils.data.DataLoader,
               loss_fn: torch.nn.Module,):
    model.eval()

    with torch.inference_mode():
        for batch, (img, label) in enumerate(dataloader):

            test_label_pred = model(img)

            loss = loss_fn(test_label_pred, label)
            test_loss += loss.item()


            test_label_pred_class = torch.argmax(torch.softmax(test_label_pred, dim=1), dim=1)
            test_acc += ((test_label_pred_class == label).sum().item()/len(test_label_pred))


    test_loss = test_loss/ len(dataloader)
    test_acc = test_acc/ len(dataloader)

    return test_loss, test_acc



def train(model:torch.nn.Module,
          train_dataloader: torch.utils.data.DataLoader,
          test_dataloader: torch.utils.data.DataLoader,
          optimizer: torch.optim.Optimizer,
          loss_fn: torch.nn.Module = nn.CrossEntropyLoss(),
          epochs: int = 5):
    
    results = {'train_loss': [],
               'train_acc': [],
               'test_loss': [],
               'test_acc': []}

    for epoch in tqdm(range(epochs)):
        train_loss, train_acc = train_step(model=model,
                                          dataloader = train_dataloader,
                                          loss_fn=loss_fn,
                                          optimizer=optimizer
                                          )
        
        test_loss, test_acc = test_step(model=model,
                                        dataloader=test_dataloader,
                                        loss_fn=loss_fn)
        
        print(
            f"Epoch: {epoch+1} | "
            f"train_loss: {train_loss:.4f} | "
            f"train_acc: {train_acc:.4f} | "
            f"test_loss: {test_loss:.4f} | "
            f"test_acc: {test_acc:.4f}"
        )

        results["train_loss"].append(train_loss)
        results["train_acc"].append(train_acc)
        results["test_loss"].append(test_loss)
        results["test_acc"].append(test_acc)

    return results