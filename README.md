# ChessBot

A neural network-based chess bot that plays on Lichess. The bot uses a 3D CNN trained on PGN game data to predict moves and plays via the Lichess Board API.

## Project Structure

```
chessbot/
├── main.py                 # Entry point — game loop and bot logic
├── converter.py            # FEN-to-tensor and UCI move indexing
├── network/                # Neural network
│   ├── net.py              # 3D CNN architecture (Conv3d → FC → 4672 moves)
│   ├── bot.py              # Inference wrapper (loads weights, returns move probabilities)
│   └── train.py            # Training on PGN data
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
└── requirements.txt
```

## Architecture

### Neural Network

The network (`network/net.py`) is a 3D CNN that takes a board representation as input and outputs probabilities over 4672 possible moves:

- **Input**: `(1, 17, 8, 8)` tensor — 12 piece planes (6 white + 6 black), 4 castling rights planes, 1 en passant plane
- **Layers**: 3x Conv3d + BatchNorm + MaxPool → FC(512) → Dropout(0.7) → FC(4672)
- **Output**: probability distribution over all possible UCI moves (64x64 base moves + promotions)

The converter (`converter.py`) handles FEN → tensor conversion and UCI move → index mapping.

### Game Loop

1. Create a game against Stockfish AI via `/api/challenge/ai`
2. Stream game state via `/api/board/game/stream/{id}`
3. On each turn: convert FEN to tensor → get move probabilities → mask illegal moves → sample move → send via `/api/board/game/{id}/move/{move}`

Currently the bot only plays as white.

### Lichess Integration

Uses the Lichess **Board API** (for regular accounts, Rapid+ time controls). Key endpoints:
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

### Play against Stockfish

```bash
python main.py
```

Settings in `main.py`:
- `OPPONENT` — `"stockfish"` or a bot username
- `STOCKFISH_LEVEL` — 1 to 8
- `CLOCK_LIMIT` — time in seconds (minimum 480 for Board API)
- `WEIGHTS_FILE` — weights file name from `network/weights/`

### Train on PGN data

```bash
python -m network.train
```

Edit `network/train.py` to set the PGN file path and training parameters (epochs, batch size, learning rate).

## Dependencies

- **python-chess** — chess logic and move validation
- **torch** — neural network (3D CNN)
- **numpy** — tensor operations
- **requests** — Lichess API client
- **python-dotenv** — environment variable loading
- **playwright** — Chess.com browser automation (optional)

## License

MIT License
