# Load model directly
from transformers import AutoTokenizer, AutoModel
import torch #Import Pytorch
import torch.nn as nn #Import nn, all neural network modules
import torch.optim as optim #optimiers in torch
from torch.utils.data import Dataset, DataLoader #Dataset related
from torch.optim.lr_scheduler import ReduceLROnPlateau
import timm 
import matplotlib.pyplot as plt # For data viz import pandas as pd import numpy as np + Codit + Markdown CC
import pandas as pd

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class CESMDataset(Dataset):
    def __init__(self, data_dir, max_len=60):
        self.data_dir = data_dir
        self.tokenizer = AutoTokenizer.from_pretrained("climatebert/distilroberta-base-climate-f")
        self.data = pd.read_csv(data_dir)
        self.text = self.data["x"].tolist()
        self.y = self.data["y"].tolist()
        self.labels = self.y
        self.label2id = {l:i for i,l in enumerate(sorted(set(self.labels)))}
        self.id2label = {i:l for l,i in self.label2id.items()}    
        self.max_len = max_len    

    def __len__(self):
        return len(self.text)
    
    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.text[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )
        item = {k:v.squeeze(0) for k, v in enc.items()}   # remove batch dim
        item["labels"] = torch.tensor(self.label2id[self.labels[idx]])
        return item
    
    @property
    def num_classes(self):
        return len(self.label2id)


data_dir = "TrainingSet/cesm_training_set.csv"

dataset = CESMDataset(data_dir)

dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

class CESMBert(nn.Module):
    def __init__(self, num_classes):
        #Define all parts of model
        super().__init__()
        self.base_model = AutoModel.from_pretrained("climatebert/distilroberta-base-climate-f")
        self.classifier = nn.Linear(self.base_model.config.hidden_size, num_classes)
   
    def forward(self, input_ids, attention_mask):
        #connect these parts and return output
         # 1. run transformer
        last_hidden = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask
        ).last_hidden_state                              # [B, L, H]

        # 2. meanÇæpool over the real tokens (ignore PADs)
        mask = attention_mask.unsqueeze(-1).type_as(last_hidden)  # [B, L, 1]
        summed = (last_hidden * mask).sum(dim=1)         # [B, H]
        counts = mask.sum(dim=1).clamp(min=1e-9)         # [B, 1]  avoid /0
        pooled = summed / counts                         # [B, H]

        # 3. classify
        logits = self.classifier(pooled)                 # [B, num_classes]
        return logits

model = CESMBert(num_classes=len(dataset.label2id))
model.to(device)





#Training
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-5)
scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)

num_epoch = 50
train_losses = []

for epoch in range(num_epoch):
    #set model to train mode
    model.train()
    #initialize running loss
    running_loss = 0.0
    #iterate over data
    for batch in dataloader:
        input_ids      = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels         = batch["labels"].to(device)

        optimizer.zero_grad()
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * input_ids.size(0)
        
    train_loss = running_loss / len(dataloader.dataset)
    train_losses.append(train_loss)
    
    # Step the scheduler
    scheduler.step(train_loss)
    
    print(f"Epoch {epoch+1}/{num_epoch}, Loss: {train_loss:.4f}, LR: {optimizer.param_groups[0]['lr']:.2e}")

# Calculate final accuracy
print("\nCalculating final accuracy...")
model.eval()
correct = 0
total = 0

with torch.no_grad():
    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        _, predicted = torch.max(outputs.data, 1)
        
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

accuracy = 100 * correct / total
print(f"Final Accuracy: {accuracy:.2f}% ({correct}/{total})")

# Save the trained model and related files
print("Saving model...")
torch.save(model.state_dict(), 'models/cesm_model.pth')
torch.save(dataset.label2id, 'models/label2id.pth')
torch.save(dataset.id2label, 'models/id2label.pth')

# Save tokenizer
dataset.tokenizer.save_pretrained('models/cesm_tokenizer')

# Save training losses for plotting
import json
with open('training/training_losses.json', 'w') as f:
    json.dump(train_losses, f)

print("Model saved successfully!")
print("Files saved:")
print("- models/cesm_model.pth (model weights)")
print("- models/label2id.pth (label to ID mapping)")
print("- models/id2label.pth (ID to label mapping)")
print("- models/cesm_tokenizer/ (tokenizer files)")
print("- training/training_losses.json (training losses)")

# Plot training losses
plt.figure(figsize=(10, 6))
plt.plot(train_losses, label='Training Loss')
plt.title('Training Loss Over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)
plt.savefig('training/training_loss_plot.png')
plt.show()

# Save training info
training_info = {
    "num_epochs": num_epoch,
    "final_accuracy": accuracy,
    "final_loss": train_losses[-1] if train_losses else None,
    "num_classes": len(dataset.label2id),
    "total_samples": len(dataloader.dataset)
}

with open('training/training_info.json', 'w') as f:
    json.dump(training_info, f, indent=2)

print("- training/training_loss_plot.png (training loss plot)")
print("- training/training_info.json (training information)")

#
