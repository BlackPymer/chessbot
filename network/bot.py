import os
import torch
import torch.nn as nn
import torch.optim as optim
from network.net import Net
import numpy as np
from numpy import ndarray

WEIGHTS_DIR = "network/weights"


class Bot:
    def __init__(self, weights_filename: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net = Net(None)
        self.net.to(self.device)

        try:
            weights = self.load_weights(weights_filename)
            if weights is not None:
                self.net.load_state_dict(weights)
        except:
            print("Weights loading error")

    def load_weights(self, filename: str) -> dict:
        filepath = os.path.join(WEIGHTS_DIR, filename)
        if os.path.exists(filepath):
            print(f"Loading weights from {filepath}")
            return torch.load(filepath, map_location=self.device, weights_only=True)
        else:
            print(f"Weights file not found: {filepath}")
            return None

    def get_move_probs(self, pos: ndarray) -> ndarray:
        """Get move probabilities as numpy array."""
        input_tensor = torch.tensor(pos, dtype=torch.float32, device=self.device)
        input_tensor = input_tensor.unsqueeze(0).unsqueeze(0)  # (1, 1, 17, 8, 8)

        with torch.no_grad():
            self.net.eval()
            _, probs = self.net(input_tensor)
            probs = probs.squeeze(0).cpu().numpy()

        return probs
