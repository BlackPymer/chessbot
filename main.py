import time
import numpy as np
from dotenv import load_dotenv
from game_services.lichess.service import LichessService
from game_brain.client import GameClient
from network.bot import Bot
from converter import move_to_index

OPPONENT = "stockfish"
STOCKFISH_LEVEL = 1
WEIGHTS_FILE = "weights_epoch_100.pth"
CLOCK_LIMIT = 600
CLOCK_INCREMENT = 0


class ChessBot:
    def __init__(
        self,
        service: LichessService,
        bot: Bot,
        opponent: str = "stockfish",
        level: int = 1,
    ):
        self.service = service
        self.bot = bot
        self.game = GameClient()
        self.game_id = None
        self.opponent = opponent
        self.level = level

    def run(self):
        if self.opponent == "stockfish":
            self._challenge_stockfish()
        else:
            self._challenge_rated_bot()
            self._wait_for_game()
        self.service.start_streaming(self.game_id)
        self._game_loop()

    def _challenge_stockfish(self):
        game = self.service.challenge_stockfish(
            level=self.level,
            clock_limit=CLOCK_LIMIT,
            clock_increment=CLOCK_INCREMENT,
        )
        self.game_id = game["id"]
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

    def _game_loop(self):
        while True:
            state = self.service.get_game_state()
            if not state:
                break

            fen = state["fen"]
            if state["status"] != "started":
                break

            self.game.new_game(fen)

            if self.game.is_game_over():
                print(f"Game over! Result: {self.game.get_result()}")
                break

            current_turn = self.game.get_turn()
            if current_turn == "white":
                move = self._make_decision()
                if move:
                    print(f"Playing: {move}")
                    self.service.make_move(move)
                    self.game.make_move(move)
            else:
                time.sleep(1)

    def _make_decision(self):
        pos = self._get_position_tensor()
        probs = self.bot.get_move_probs(pos)

        legal_moves = self.game.get_legal_moves()
        legal_indices = [move_to_index(m) for m in legal_moves]

        masked_probs = np.zeros_like(probs)
        for idx in legal_indices:
            masked_probs[idx] = probs[idx]

        if masked_probs.sum() == 0:
            return legal_moves[0] if legal_moves else None

        masked_probs = masked_probs / masked_probs.sum()

        move_idx = np.random.choice(len(masked_probs), p=masked_probs)
        move_uci = legal_moves[legal_indices.index(move_idx)]

        return move_uci

    def _get_position_tensor(self):
        fen = self.game.get_fen()
        return self._fen_to_array(fen)

    def _fen_to_array(self, fen: str) -> np.ndarray:
        from converter import convert_fen_to_network

        return convert_fen_to_network(fen)


def main():
    load_dotenv()
    service = LichessService()
    bot = Bot(WEIGHTS_FILE)
    chess_bot = ChessBot(service, bot, opponent=OPPONENT, level=STOCKFISH_LEVEL)
    chess_bot.run()


if __name__ == "__main__":
    main()
