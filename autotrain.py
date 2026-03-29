import asyncio
import os
import numpy as np
import torch
from dotenv import load_dotenv
from main import main as play_game
from network.train import gen_batches, Trainer

RETRAIN_EPOCHES = 20
MIN_LOSSES_TO_TRAIN = 5
BASE_PGN = "lichess_BalckPymer_2026-03-26.pgn"
LOSSES_DIR = "games"
START_LEVEL = 3
MAX_LEVEL = 8
WEIGHTS_FILE = "weights_epoch_100.pth"

losses_count = 0
training_needed = asyncio.Event()


def loss_file(level: int) -> str:
    return os.path.join(LOSSES_DIR, f"stockfish_level_{level}.pgn")


def save_loss_pgn(level: int, pgn: str):
    global losses_count
    os.makedirs(LOSSES_DIR, exist_ok=True)
    filepath = loss_file(level)
    with open(filepath, "a") as f:
        f.write(pgn + "\n\n")
    losses_count += 1
    print(f"Loss #{losses_count} saved to {filepath}")
    if losses_count >= MIN_LOSSES_TO_TRAIN:
        training_needed.set()


async def play(level: int) -> bool:
    print(f"\n{'='*40}")
    print(f"Playing vs Stockfish Level {level}")
    print(f"{'='*40}")

    result = await play_game(level=level)
    winner = result.get("winner")
    our_color = result["our_color"]
    pgn = result.get("pgn")

    print(f"Result: {result['result']}, winner: {winner}, our color: {our_color}")

    if winner == our_color:
        print(f"WON vs Stockfish Level {level}!")
        return True

    if winner and winner != our_color and pgn:
        save_loss_pgn(level, pgn)
    else:
        print("Draw or no PGN — not saving")

    return False


async def train_loop(level_ref: list):
    global losses_count
    while True:
        await training_needed.wait()
        training_needed.clear()

        current_level = level_ref[0]
        print(f"\n--- Training on base + stockfish level {current_level} losses ---")

        base_inputs, base_outputs = gen_batches([BASE_PGN], winner_only=False)
        loss_inputs, loss_outputs = gen_batches(
            [loss_file(current_level)], winner_only=True
        )

        all_inputs = base_inputs + loss_inputs
        all_outputs = base_outputs + loss_outputs

        if len(all_inputs) == 0:
            print("No training data!")
            continue

        input_batch = np.array(all_inputs)
        output_batch = torch.tensor(all_outputs, dtype=torch.long)
        print(
            f"Training samples: {len(all_inputs)} (base: {len(base_inputs)}, losses: {len(loss_inputs)})"
        )

        global WEIGHTS_FILE
        tr = Trainer(weights_filename=WEIGHTS_FILE)
        await tr.train_async(input_batch, output_batch, epoches=RETRAIN_EPOCHES)
        WEIGHTS_FILE = f"weights_epoch_{RETRAIN_EPOCHES}.pth"
        losses_count = 0
        print(f"--- Training complete, weights: {WEIGHTS_FILE} ---\n")


def count_existing_losses(level: int) -> int:
    filepath = loss_file(level)
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r") as f:
        content = f.read()
    return content.count('"winner"')


async def run():
    global losses_count
    load_dotenv()
    level = START_LEVEL
    level_ref = [level]

    existing = count_existing_losses(level)
    if existing > 0:
        losses_count = existing
        print(f"Found {existing} existing losses for level {level}")
        if existing >= MIN_LOSSES_TO_TRAIN:
            training_needed.set()

    train_task = asyncio.create_task(train_loop(level_ref))

    while level <= MAX_LEVEL:
        won = await play(level)
        if won:
            print(f"\nLevel {level} beaten! Moving to level {level + 1}")
            level += 1
            level_ref[0] = level
            losses_count_reset()
        await asyncio.sleep(2)

    print(f"\nAll levels beaten up to {MAX_LEVEL}!")
    train_task.cancel()


def losses_count_reset():
    global losses_count
    losses_count = 0
    training_needed.clear()


if __name__ == "__main__":
    asyncio.run(run())
