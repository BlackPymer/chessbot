# ChessBot

A neural network-based chess bot for playing against online bots on Lichess and Chess.com. This project is designed for educational purposes to train and develop chess AI.

## Project Structure

```
chessbot/
├── game_services/          # Platform integration services
│   ├── service.py          # Base service interface
│   ├── chesscom/           # Chess.com integration (browser automation)
│   │   └── service.py
│   └── lichess/            # Lichess integration (API-based)
│       ├── service.py      # High-level game service
│       └── client.py       # Low-level API client
├── game_brain/             # Chess logic and game management
│   ├── game.py             # Core chess game class
│   └── client.py           # Game client wrapper
├── network/                # Neural network components
│   └── test.py
├── main.py                 # Entry point
└── requirements.txt        # Python dependencies
```

## Architecture

### Game Services Layer

The `game_services` module provides integration with chess platforms:

- **LichessService** - Uses Lichess Bot API for official bot gameplay
- **ChesscomService** - Uses browser automation (Playwright) for Chess.com

Both services inherit from the base `Service` class ensuring a consistent interface.

### Game Brain Layer

The `game_brain` module handles chess logic:

- **ChessGame** - Core game logic using `python-chess` library
- **GameClient** - High-level wrapper for game operations

Features:
- Move validation (UCI format: `e2e4`, `e7e8q`)
- Game state tracking (turn, check, game over)
- FEN/PGN export
- Legal moves generation

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for Chess.com)
playwright install
```

## Configuration

Create a `.env` file in the project root:

```env
# Lichess (required for bot gameplay)
LICHESS_TOKEN=your_lichess_bot_token

# Chess.com (optional, for browser automation)
CHESSCOM_LOGIN=your_email
CHESSCOM_PASSWORD=your_password
```

### Getting Lichess Bot Token

1. Upgrade your account to BOT at https://lichess.org/account/upgrade
2. Create a token at https://lichess.org/account/oauth/token
3. Select permissions: `bot:play`, `challenge:read`, `challenge:write`

## Usage

### Lichess Bot Integration

```python
from game_services.lichess.service import LichessService

service = LichessService()

# Get account info
account = service.get_account()
print(f"Account: {account['username']}")

# Get online bots
bots = service.get_online_bots()

# Challenge a bot
service.challenge_bot("StockfishLevel1", clock_limit=60)

# Wait for game to start
game = service.wait_for_game_start()

# Get current board position
board = service.get_board()

# Make a move (UCI format)
service.make_move("e2e4")
```

### Game Logic

```python
from game_brain.client import GameClient

client = GameClient()
client.new_game()

# Check if move is valid
if client.is_valid_move("e2e4"):
    client.make_move("e2e4")

# Get game state
print(f"Turn: {client.get_turn()}")
print(f"Game over: {client.is_game_over()}")
print(f"Result: {client.get_result()}")

# Get position
print(f"FEN: {client.get_fen()}")
print(f"Legal moves: {client.get_legal_moves()}")
```

## Dependencies

- **python-chess** - Chess logic and move validation
- **requests** - HTTP client for Lichess API
- **playwright** - Browser automation for Chess.com
- **torch** - Neural network framework (for future development)
- **numpy** - Numerical computations

## License

MIT License
