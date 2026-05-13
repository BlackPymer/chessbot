import asyncio
import json
import numpy as np
from dotenv import load_dotenv
from game_services.lichess.service import LichessService
from game_brain.client import GameClient
from network.bot import Bot
from converter import move_to_index, flip_move, convert_fen_to_network

OPPONENT = "stockfish"
STOCKFISH_LEVEL = 5
WEIGHTS_FILE = "weights_epoch_100.pth"
CLOCK_LIMIT = 600
CLOCK_INCREMENT = 0
COLOR = "random"  # "white", "black", or "random"


class ChessBot:
    def __init__(
        self,
        service: LichessService,
        bot: Bot,
        opponent: str = "stockfish",
        level: int = 1,
        color: str = "white",
    ):
        self.service = service
        self.bot = bot
        self.game = GameClient()
        self.game_id = None
        self.opponent = opponent
        self.level = level
        self.color = color
        self.our_color = None

    async def run(self):
        loop = asyncio.get_event_loop()
        if self.opponent == "stockfish":
            await loop.run_in_executor(None, self._challenge_stockfish)
        else:
            await loop.run_in_executor(None, self._challenge_rated_bot)
            await loop.run_in_executor(None, self._wait_for_game)
        await loop.run_in_executor(None, self.service.start_streaming, self.game_id)
        return await self._game_loop()

    def _challenge_stockfish(self):
        game = self.service.challenge_stockfish(
            level=self.level,
            clock_limit=CLOCK_LIMIT,
            clock_increment=CLOCK_INCREMENT,
            color=self.color,
        )
        self.game_id = game["id"]
        self.our_color = None
        print(f"Game started vs Stockfish Level {self.level}! ID: {self.game_id}")
        print(f"Watch: https://lichess.org/{self.game_id}")

    def _challenge_rated_bot(self):
        self.service.challenge_rated_bot(
            bot_username=self.opponent,
            rated=False,
            clock_limit=CLOCK_LIMIT,
            clock_increment=CLOCK_INCREMENT,
        )
        print(f"Challenge sent to {self.opponent}")

    def _wait_for_game(self):
        print("Waiting for game to start...")
        game = self.service.wait_for_game_start()
        self.game_id = game["id"]
        print(f"Game started! ID: {self.game_id}")
        print(f"Watch: https://lichess.org/{self.game_id}")

    async def _game_loop(self):
        loop = asyncio.get_event_loop()
        moves = []
        result = None
        while True:
            state = await loop.run_in_executor(None, self.service.get_game_state)
            if not state:
                break

            if self.our_color is None and "our_color" in state:
                self.our_color = state["our_color"]
                print(f"Playing as: {self.our_color}")

            fen = state["fen"]
            if state["status"] != "started":
                result = state["status"]
                break

            self.game.new_game(fen)

            if self.game.is_game_over():
                result = self.game.get_result()
                print(f"Game over! Result: {result}")
                break

            current_turn = self.game.get_turn()
            if current_turn == self.our_color:
                move = self._make_decision()
                if move:
                    print(f"Playing: {move}")
                    await loop.run_in_executor(None, self.service.make_move, move)
                    self.game.make_move(move)
                    moves.append(move)
            else:
                await asyncio.sleep(1)

        pgn = None
        winner = None
        try:
            pgn = await loop.run_in_executor(None, self.service.get_game_pgn)
            pgn_data = json.loads(pgn)
            winner = pgn_data.get("winner")
        except Exception as e:
            print(f"Failed to fetch PGN: {e}")

        return {
            "result": result,
            "winner": winner,
            "moves": moves,
            "our_color": self.our_color,
            "game_id": self.game_id,
            "pgn": pgn,
        }

    def _make_decision(self):
        flip = self.our_color == "black"
        fen = self.game.get_fen()
        pos = convert_fen_to_network(fen, flip=flip)
        probs = self.bot.get_move_probs(pos)

        legal_moves = self.game.get_legal_moves()
        # If flipped, convert legal moves to "white perspective" for index lookup
        network_moves = [flip_move(m) for m in legal_moves] if flip else legal_moves
        legal_indices = [move_to_index(m) for m in network_moves]

        masked_probs = np.zeros_like(probs)
        for idx in legal_indices:
            masked_probs[idx] = probs[idx]

        if masked_probs.sum() == 0:
            return legal_moves[0] if legal_moves else None

        masked_probs = masked_probs / masked_probs.sum()

        move_idx = np.random.choice(len(masked_probs), p=masked_probs)
        move_uci = legal_moves[legal_indices.index(move_idx)]

        return move_uci


async def main(level: int = STOCKFISH_LEVEL, color: str = COLOR):
    load_dotenv()
    service = LichessService()
    bot = Bot(WEIGHTS_FILE)
    chess_bot = ChessBot(
        service, bot, opponent=OPPONENT, level=level, color=color
    )
    result = await chess_bot.run()
    print(f"\nGame result: {result}")
    return result


if __name__ == "__main__":
    _ = asyncio.run(main())
