import os
import json
import asyncio
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

            if (epoch + 1) % 10 == 0:
                self.save_weights(f"weights_epoch_{epoch + 1}.pth")

        self.save_weights(f"weights_epoch_{epoches}.pth")

    async def train_async(
        self, input_batch, output_batch, epoches=10, eval_every=1, batch_size=64
    ):
        """Async wrapper — runs training in a thread so it doesn't block the event loop."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, self.train, input_batch, output_batch, epoches, eval_every, batch_size
        )


def _parse_games_from_file(file_path: str):
    with open(file_path, "r") as f:
        content = f.read().strip()

    if not content:
        return []

    first_char = content.lstrip()[0] if content.lstrip() else ""
    if first_char == "{":
        return _parse_lichess_json(content)
    else:
        return _parse_pgn(content)


def _parse_lichess_json(content: str):
    games = []
    for line in content.split("\n"):
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            data = json.loads(line)
            moves_str = data.get("moves", "")
            winner = data.get("winner")
            if moves_str:
                moves = moves_str.split(" ")
                games.append({"moves": moves, "winner": winner})
        except json.JSONDecodeError:
            continue
    return games


def _parse_pgn(content: str):
    games = []
    lines = content.split("\n")
    winner_color = None
    for line in lines:
        if line.startswith("[Result "):
            result_val = line.split('"')[1]
            if result_val == "1-0":
                winner_color = "white"
            elif result_val == "0-1":
                winner_color = "black"
            else:
                winner_color = None
            continue

        if not line.startswith("1."):
            continue

        moves = []
        for token in line.split(" "):
            if token and not token[0].isdigit():
                moves.append(token)
        if moves:
            games.append({"moves": moves, "winner": winner_color})
        winner_color = None

    return games


def gen_batches(files: list, winner_only: bool = False):
    game = GameClient()
    input_batches = []
    output_batches = []
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"File not found, skipping: {file_path}")
            continue

        parsed_games = _parse_games_from_file(file_path)
        for parsed in parsed_games:
            moves = parsed["moves"]
            winner_color = parsed["winner"]
            game.new_game()

            for move in moves:
                turn = game.get_turn()
                if winner_only and winner_color and turn != winner_color:
                    try:
                        game.make_san_move(move)
                    except Exception:
                        pass
                    continue

                flip = turn == "black"
                pos = converter.convert_fen_to_network(game.get_fen(), flip=flip)
                input_batches.append(pos)

                try:
                    uci_move = game.get_uci_move(move)
                    network_move = converter.flip_move(uci_move) if flip else uci_move
                    label = converter.move_to_index(network_move)
                    output_batches.append(label)
                except Exception:
                    input_batches.pop()
                    continue

                game.make_san_move(move)

    return input_batches, output_batches


if __name__ == "__main__":
    file_path = "lichess_BalckPymer_2026-03-26.pgn"
    tr = Trainer()
    input_batches, output_batches = gen_batches([file_path])
    if len(input_batches) == 0:
        print("No training data collected!")
        exit(1)

    input_batches = np.array(input_batches)
    output_batches = torch.tensor(output_batches, dtype=torch.long)

    print(f"Input shape: {input_batches.shape}")
    print(f"Output shape: {output_batches.shape}")

    tr.train(input_batches, output_batches, epoches=100)
