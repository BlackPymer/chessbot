import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class LichessClient:
    BASE_URL = "https://lichess.org"

    def __init__(self):
        token = os.getenv("LICHESS_TOKEN")
        print(f"Lichess token: {token[:10]}..." if token else "No token!")
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        )

        retry = Retry(total=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)

    def get_account(self):
        response = self.session.get(f"{self.BASE_URL}/api/account")
        response.raise_for_status()
        return response.json()

    def get_online_bots(self):
        response = self.session.get(f"{self.BASE_URL}/api/bot/online")
        response.raise_for_status()

        bots = []
        for line in response.text.strip().split("\n"):
            if line:
                import json

                bots.append(json.loads(line))
        return bots

    def challenge_stockfish(
        self,
        level: int = 1,
        clock_limit: int = 60,
        clock_increment: int = 0,
        color: str = "white",
    ):
        """Challenge Stockfish AI at specified level (1-8)."""
        print(f"Challenging Stockfish AI level {level} as {color}")
        response = self.session.post(
            f"{self.BASE_URL}/api/challenge/ai",
            data={
                "level": level,
                "color": color,
                "clock.limit": clock_limit,
                "clock.increment": clock_increment,
            },
        )
        response.raise_for_status()
        return response.json()

    def challenge_bot(
        self,
        bot_username: str,
        rated: bool = False,
        clock_limit: int = 60,
        clock_increment: int = 0,
    ):
        response = self.session.post(
            f"{self.BASE_URL}/api/challenge/{bot_username}",
            data={
                "rated": str(rated).lower(),
                "clock.limit": clock_limit,
                "clock.increment": clock_increment,
            },
        )
        response.raise_for_status()
        return response.json()

    def accept_challenge(self, challenge_id: str):
        response = self.session.post(
            f"{self.BASE_URL}/api/challenge/{challenge_id}/accept"
        )
        response.raise_for_status()
        return response.ok

    def decline_challenge(self, challenge_id: str, reason: str = "later"):
        response = self.session.post(
            f"{self.BASE_URL}/api/challenge/{challenge_id}/decline",
            params={"reason": reason},
        )
        response.raise_for_status()
        return response.ok

    def stream_incoming_events(self):
        response = self.session.get(f"{self.BASE_URL}/api/stream/event", stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                import json

                yield json.loads(line.decode("utf-8"))

    def stream_game(self, game_id: str):
        response = self.session.get(
            f"{self.BASE_URL}/api/board/game/stream/{game_id}", stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                import json

                yield json.loads(line.decode("utf-8"))

    def make_move(self, game_id: str, move: str, offering_draw: bool = False):
        url = f"{self.BASE_URL}/api/board/game/{game_id}/move/{move}"
        if offering_draw:
            url += "?offeringDraw=true"
        response = self.session.post(url)
        if response.status_code == 400:
            print(f"Board API failed (400), response: {response.text}")
        response.raise_for_status()
        return response.ok

    def abort_game(self, game_id: str):
        response = self.session.post(f"{self.BASE_URL}/api/board/game/{game_id}/abort")
        response.raise_for_status()
        return response.ok

    def resign_game(self, game_id: str):
        response = self.session.post(f"{self.BASE_URL}/api/board/game/{game_id}/resign")
        response.raise_for_status()
        return response.ok

    def get_game_pgn(self, game_id: str):
        response = self.session.get(f"{self.BASE_URL}/game/export/{game_id}")
        response.raise_for_status()
        return response.text
