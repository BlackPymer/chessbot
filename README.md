# ChessBot

A neural network-based chess bot that plays on Lichess. The bot uses a 3D CNN trained on PGN game data to predict moves and plays via the Lichess Board API. Includes an auto-training system that progressively levels up against Stockfish (levels 1-8), learning from its losses.

## Project Structure

```
chessbot/
├── main.py                 # Entry point — async game loop and bot logic
├── autotrain.py            # Auto-training — play, learn from losses, level up
├── converter.py            # FEN-to-tensor and UCI move indexing
├── network/                # Neural network
│   ├── net.py              # 3D CNN architecture (Conv3d → FC → 4672 moves)
│   ├── bot.py              # Inference wrapper (loads weights, returns move probabilities)
│   └── train.py            # Training on PGN data (sync + async)
├── game_services/          # Platform integrations
│   ├── service.py          # Base service interface
│   ├── lichess/            # Lichess integration (Board API)
│   │   ├── client.py       # Low-level HTTP client
│   │   └── service.py      # High-level game service
│   └── chesscom/           # Chess.com integration (Playwright)
│       └── service.py
├── game_brain/             # Chess logic
│   ├── game.py             # Core game class (python-chess)
│   └── client.py           # Game client wrapper
├── games/                  # Auto-generated loss PGNs per Stockfish level
└── requirements.txt
```

## Architecture

### Neural Network

The network (`network/net.py`) is a 3D CNN that takes a board representation as input and outputs probabilities over 4672 possible moves:

- **Input**: `(1, 17, 8, 8)` tensor — 12 piece planes (6 white + 6 black), 4 castling rights planes, 1 en passant plane
- **Layers**: 3x Conv3d + BatchNorm + MaxPool → FC(512) → Dropout(0.7) → FC(4672)
- **Output**: probability distribution over all possible UCI moves (64x64 base moves + promotions)

The converter (`converter.py`) handles FEN → tensor conversion and UCI move → index mapping. When playing as black, the board and moves are flipped to white's perspective for the network.

### Game Loop

1. Create a game against Stockfish AI via `/api/challenge/ai`
2. Stream game state via `/api/board/game/stream/{id}`
3. Detect our color from the `gameFull` stream event
4. On each turn: convert FEN to tensor → get move probabilities → mask illegal moves → sample move → send via API
5. Return game result, moves, and PGN

The game loop is fully async, allowing parallel operations (e.g. training during games).

### Auto-Training (`autotrain.py`)

A progressive training system that plays against Stockfish levels 2-8:

1. Play games against the current Stockfish level
2. On each loss, save the PGN to `games/stockfish_level_N.pgn`
3. After accumulating enough losses (default: 5), retrain the network on:
   - Base PGN file (your own games, all moves)
   - Loss PGNs for the current level (winner's moves only — learn to play like the opponent that beat you)
4. When you win a game, advance to the next level and reset
5. Previous level loss files are no longer used for training

Training runs in parallel with games via asyncio.

### Lichess Integration

Uses the Lichess **Board API** (for bot accounts). Key endpoints:
- `POST /api/challenge/ai` — start a game vs Stockfish (levels 1-8)
- `GET /api/board/game/stream/{id}` — stream game events
- `POST /api/board/game/{id}/move/{move}` — make a move

## Installation

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
LICHESS_TOKEN=your_lichess_token
```

### Getting a Lichess Token

1. Go to https://lichess.org/account/oauth/token
2. Create a token with permissions: `board:play`, `challenge:read`, `challenge:write`

## Usage

### Play a single game

```bash
python main.py
```

Settings in `main.py`:
- `OPPONENT` — `"stockfish"` or a bot username
- `STOCKFISH_LEVEL` — 1 to 8
- `CLOCK_LIMIT` — time in seconds (minimum 480 for Board API)
- `COLOR` — `"white"`, `"black"`, or `"random"`
- `WEIGHTS_FILE` — weights file name from `network/weights/`

### Auto-train against Stockfish

```bash
python autotrain.py
```

Settings in `autotrain.py`:
- `START_LEVEL` — starting Stockfish level (default: 2)
- `MAX_LEVEL` — maximum level to reach (default: 8)
- `MIN_LOSSES_TO_TRAIN` — losses needed before retraining (default: 5)
- `RETRAIN_EPOCHES` — epochs per training round (default: 20)
- `BASE_PGN` — base PGN file always included in training

### Train on PGN data manually

```bash
python -m network.train
```

## Dependencies

- **python-chess** — chess logic and move validation
- **torch** — neural network (3D CNN)
- **numpy** — tensor operations
- **requests** — Lichess API client
- **python-dotenv** — environment variable loading
- **playwright** — Chess.com browser automation (optional)

## License

MIT License
