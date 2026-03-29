import chess
from .client import LichessClient
from ..service import Service


class LichessService(Service):
    def __init__(self):
        super().__init__()
        self.client = LichessClient()
        self.game_id = None
        self.game_stream = None
        self.board = chess.Board()

    def get_account(self):
        return self.client.get_account()

    def get_online_bots(self):
        return self.client.get_online_bots()

    def challenge_stockfish(
        self,
        level: int = 1,
        clock_limit: int = 60,
        clock_increment: int = 0,
        color: str = "white",
    ):
        """Challenge Stockfish AI at specified level (1-8)."""
        return self.client.challenge_stockfish(level, clock_limit, clock_increment, color)

    def challenge_rated_bot(
        self,
        bot_username: str,
        rated: bool = True,
        clock_limit: int = 60,
        clock_increment: int = 0,
    ):
        """Challenge a rated bot by username (e.g., 'maia1', 'WorstFish')."""
        return self.client.challenge_bot(
            bot_username, rated, clock_limit, clock_increment
        )

    def accept_challenge(self, challenge_id: str):
        return self.client.accept_challenge(challenge_id)

    def decline_challenge(self, challenge_id: str, reason: str = "later"):
        return self.client.decline_challenge(challenge_id, reason)

    def wait_for_game_start(self):
        """Wait for game to start. Automatically accepts challenges from our bot."""
        for event in self.client.stream_incoming_events():
            if event.get("type") == "challenge":
                challenge = event["challenge"]
                if (
                    challenge["challenger"]["name"]
                    == self.client.get_account()["username"]
                ):
                    self.accept_challenge(challenge["id"])
                    continue

            if event.get("type") == "gameStart":
                self.game_id = event["game"]["id"]
                self.game_stream = self.client.stream_game(self.game_id)
                return event["game"]

        return None

    def start_streaming(self, game_id: str):
        """Start streaming a game by ID."""
        self.game_id = game_id
        self.game_stream = self.client.stream_game(game_id)

    def get_game_state(self):
        """Get current game state from board stream.

        Handles both 'gameFull' (first event) and 'gameState' (subsequent) events.
        Computes FEN from the moves list since the stream doesn't provide it directly.
        """
        if not self.game_stream:
            return None

        for event in self.game_stream:
            if not event:
                continue

            if event.get("type") == "gameFull":
                state = event["state"]
                # Extract our color from gameFull event
                our_color = None
                white_info = event.get("white", {})
                black_info = event.get("black", {})
                if "aiLevel" in white_info or white_info.get("id") == "ai":
                    our_color = "black"
                elif "aiLevel" in black_info or black_info.get("id") == "ai":
                    our_color = "white"
                self._detected_color = our_color
                print(f"Stream gameFull: white={white_info}, black={black_info}")
            elif event.get("type") == "gameState":
                state = event
            else:
                continue

            board = chess.Board()
            moves = state.get("moves", "")
            if moves:
                for move in moves.split():
                    board.push_uci(move)

            result = {
                "fen": board.fen(),
                "status": state.get("status", "unknown"),
            }
            if hasattr(self, "_detected_color") and self._detected_color:
                result["our_color"] = self._detected_color
            return result

        return None

    def make_move(self, move: str, offering_draw: bool = False):
        """Make a move in UCI format (e.g., 'e2e4', 'e7e8q')."""
        if not self.game_id:
            raise Exception("No active game")
        return self.client.make_move(self.game_id, move, offering_draw)

    def get_board(self):
        """Get current position as chess.Board."""
        if not self.game_id:
            return None

        state = self.get_game_state()
        if not state:
            return None

        return chess.Board(state["fen"])

    def abort_game(self):
        if not self.game_id:
            raise Exception("No active game")
        return self.client.abort_game(self.game_id)

    def resign_game(self):
        if not self.game_id:
            raise Exception("No active game")
        return self.client.resign_game(self.game_id)

    def get_game_pgn(self):
        if not self.game_id:
            raise Exception("No active game")
        return self.client.get_game_pgn(self.game_id)

    def start_game(self):
        pass

    def get_board_pos(self):
        pass
