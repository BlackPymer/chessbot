import torch
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):

    def __init__(self, weight=None, input_size=(17, 8, 8)):
        super(Net, self).__init__()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.conv1 = nn.Conv3d(1, 32, kernel_size=(3, 3, 3), padding=1)
        self.conv2 = nn.Conv3d(32, 64, kernel_size=(3, 3, 3), padding=1)
        self.conv3 = nn.Conv3d(64, 128, kernel_size=(3, 3, 3), padding=1)

        self.bn1 = nn.BatchNorm3d(32)
        self.bn2 = nn.BatchNorm3d(64)
        self.bn3 = nn.BatchNorm3d(128)

        self.pool = nn.MaxPool3d((1, 2, 2))

        self._to_linear = None

        self.fc2 = nn.Linear(512, 4672)
        self.dropout = nn.Dropout(0.7)

        self.to(self.device)

        self._calculate_linear_size(input_size)

        self.fc1 = nn.Linear(self._to_linear, 512).to(self.device)

        if weight is not None:
            self.load_state_dict(weight)

    def _calculate_linear_size(self, input_size):
        self.eval()
        with torch.no_grad():
            x = torch.zeros(1, 1, *input_size, device=self.device)
            x = self.pool(F.relu(self.bn1(self.conv1(x))))
            x = self.pool(F.relu(self.bn2(self.conv2(x))))
            x = self.pool(F.relu(self.bn3(self.conv3(x))))
            self._to_linear = x.view(1, -1).size(1)
        self.train()

    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))

        flattened = x.view(x.size(0), -1)
        fc1_out = F.relu(self.fc1(flattened))
        fc1_out = self.dropout(fc1_out)

        output = self.fc2(fc1_out)
        probabilities = F.softmax(output, dim=1)

        return output, probabilities
