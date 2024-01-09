import torch
import torch.nn as nn
import torch.nn.functional as F

class AnimalNeuralNetwork(nn.Module):
    def __init__(self, animal, input_size=8, hidden_size=16, output_size=2):
        super(AnimalNeuralNetwork, self).__init__()
        self.animal = animal
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

    def forward(self, x):
        x = F.sigmoid(self.fc1(x))
        x = F.sigmoid(self.fc2(x))
        return x