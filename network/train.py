import os
import torch
import torch.nn as nn
import torch.optim as optim
from network.net import Net
from game_brain.client import GameClient
import converter
import numpy as np

WEIGHTS_DIR = "network/weights"


class Trainer:
    def __init__(self, weights_filename: str = None, retrain: bool = False):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net = Net(None)
        self.net.to(self.device)

        if not retrain and weights_filename:
            weights = self.load_weights(weights_filename)
            if weights is not None:
                self.net.load_state_dict(weights)

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.net.parameters(), lr=0.001)

    def load_weights(self, filename: str) -> dict:
        filepath = os.path.join(WEIGHTS_DIR, filename)
        if os.path.exists(filepath):
            print(f"Loading weights from {filepath}")
            return torch.load(filepath, map_location=self.device, weights_only=True)
        else:
            print(f"Weights file not found: {filepath}")
            return None

    def save_weights(self, filename: str):
        os.makedirs(WEIGHTS_DIR, exist_ok=True)
        filepath = os.path.join(WEIGHTS_DIR, filename)
        torch.save(self.net.state_dict(), filepath)
        print(f"Weights saved to {filepath}")

    def train(self, input_batch, output_batch, epoches=10, eval_every=1, batch_size=64):
        self.net.train()

        n_samples = len(input_batch)
        n_batches = n_samples // batch_size

        for epoch in range(epoches):
            total_loss = 0
            indices = torch.randperm(n_samples)

            for i in range(n_batches):
                start_idx = i * batch_size
                end_idx = start_idx + batch_size
                batch_indices = indices[start_idx:end_idx]

                input_tensor = torch.tensor(
                    input_batch[batch_indices], dtype=torch.float32
                ).to(self.device)
                input_tensor = input_tensor.unsqueeze(1)
                output_tensor = output_batch[batch_indices].to(self.device)

                self.optimizer.zero_grad()
                output, _ = self.net(input_tensor)
                loss = self.criterion(output, output_tensor)
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()

            if epoch % eval_every == 0:
                avg_loss = total_loss / n_batches
                print(f"Epoch: {epoch}\tLoss: {avg_loss:.4f}")

        self.save_weights(f"weights_epoch_{epoches}.pth")


if __name__ == "__main__":
    file_path = "lichess_BalckPymer_2026-03-26.pgn"
    tr = Trainer("weights_epoch_100.pth")
    game = GameClient()
    content = None
    input_batches = []
    output_batches = []

    with open(file_path, "r") as file:
        content = file.read().split("\n")

    for line in content:
        if not line.startswith("1."):
            continue
        game.new_game()
        moves = line.split(" ")
        for move in moves:
            if move[0].isdigit():
                continue
            pos = converter.convert_fen_to_network(game.get_fen())
            input_batches.append(pos)

            try:
                uci_move = game.get_uci_move(move)
                label = converter.move_to_index(uci_move)
                output_batches.append(label)
            except Exception:
                input_batches.pop()
                continue

            game.make_san_move(move)

    if len(input_batches) == 0:
        print("No training data collected!")
        exit(1)

    input_batches = np.array(input_batches)
    output_batches = torch.tensor(output_batches, dtype=torch.long)

    print(f"Input shape: {input_batches.shape}")
    print(f"Output shape: {output_batches.shape}")

    tr.train(input_batches, output_batches, epoches=100)
