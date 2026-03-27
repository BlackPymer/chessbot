import chess
from .game import ChessGame


class GameClient:
    """Client for managing chess game."""

    def __init__(self):
        self.game = ChessGame()

    def new_game(self, fen: str = None):
        """Start a new game."""
        self.game.new_game(fen)

    def is_valid_move(self, move_uci: str) -> bool:
        """Check if move is valid."""
        return self.game.is_valid_move(move_uci)

    def make_move(self, move_uci: str) -> bool:
        """Make a move."""
        return self.game.make_move(move_uci)

    def get_turn(self) -> str:
        """Get current turn."""
        return self.game.get_turn()

    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self.game.is_game_over()

    def get_result(self) -> str:
        """Get game result."""
        return self.game.get_game_result()

    def get_fen(self) -> str:
        """Get current position (FEN)."""
        return self.game.get_fen()

    def get_legal_moves(self) -> list:
        """Get list of legal moves."""
        return self.game.get_legal_moves()

    def is_check(self) -> bool:
        """Check if in check."""
        return self.game.is_check()

    def get_pgn(self) -> str:
        """Get game in PGN format."""
        return self.game.get_pgn()

    def get_board(self) -> chess.Board:
        """Get board object."""
        return self.game.get_board()

    def is_valid_san_move(self, san_move: str) -> bool:
        """Check if move in SAN format is valid."""
        return self.game.is_valid_san_move(san_move)

    def make_san_move(self, san_move: str) -> bool:
        """Make a move in SAN format."""
        return self.game.make_san_move(san_move)

    def get_uci_move(self, san_move: str) -> str:
        """Convert SAN move to UCI format."""
        return self.game.get_uci_move(san_move)
