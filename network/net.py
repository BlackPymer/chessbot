import torch
import torch.nn as nn
import torch.nn.functional as F


class ResBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = out + residual
        return F.relu(out)


class Net(nn.Module):

    def __init__(self, weight=None, in_channels=17, num_res_blocks=5, channels=128):
        super().__init__()

        self.input_conv = nn.Sequential(
            nn.Conv2d(in_channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
        )

        self.res_blocks = nn.Sequential(
            *[ResBlock(channels) for _ in range(num_res_blocks)]
        )

        self.policy_head = nn.Sequential(
            nn.Conv2d(channels, 32, kernel_size=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(32 * 8 * 8, 4672),
        )

        self.dropout = nn.Dropout(0.25)

        if weight is not None:
            self.load_state_dict(weight)

    def forward(self, x):
        x = self.input_conv(x)
        x = self.res_blocks(x)
        x = self.dropout(x)
        output = self.policy_head(x)
        probabilities = F.softmax(output, dim=1)
        return output, probabilities
