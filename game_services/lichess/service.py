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

    def challenge_bot(
        self,
        bot_username: str,
        rated: bool = False,
        clock_limit: int = 60,
        clock_increment: int = 0,
    ):
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

    def get_game_state(self):
        """Get current game state."""
        if not self.game_stream:
            return None

        for state in self.game_stream:
            if state:
                return state
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
