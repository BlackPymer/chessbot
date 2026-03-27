import chess


class ChessGame:
    def __init__(self):
        self.board = chess.Board()

    def new_game(self, fen: str = None):
        """Start a new game. Optionally set position via FEN."""
        if fen:
            self.board = chess.Board(fen)
        else:
            self.board = chess.Board()

    def is_valid_move(self, move_uci: str) -> bool:
        """Check if move is valid (UCI format: 'e2e4', 'e7e8q')."""
        try:
            move = chess.Move.from_uci(move_uci)
            return move in self.board.legal_moves
        except ValueError:
            return False

    def make_move(self, move_uci: str) -> bool:
        """Make a move. Returns True if successful."""
        if not self.is_valid_move(move_uci):
            return False

        move = chess.Move.from_uci(move_uci)
        self.board.push(move)
        return True

    def get_turn(self) -> str:
        """Get current turn: 'white' or 'black'."""
        return "white" if self.board.turn == chess.WHITE else "black"

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.board.is_game_over()

    def get_game_result(self) -> str:
        """
        Get game result:
        - 'ongoing' - game still in progress
        - 'white_won' - white won
        - 'black_won' - black won
        - 'draw' - draw
        """
        if not self.is_game_over():
            return "ongoing"

        if self.board.is_checkmate():
            return "black_won" if self.board.turn == chess.WHITE else "white_won"

        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return "draw"

        if self.board.is_fifty_moves() or self.board.is_repetition():
            return "draw"

        return "draw"

    def get_fen(self) -> str:
        """Get current position in FEN format."""
        return self.board.fen()

    def get_board(self) -> chess.Board:
        """Get board object."""
        return self.board

    def get_legal_moves(self) -> list:
        """Get list of legal moves in UCI format."""
        return [move.uci() for move in self.board.legal_moves]

    def is_check(self) -> bool:
        """Check if current player is in check."""
        return self.board.is_check()

    def get_pgn(self) -> str:
        """Get game in PGN format."""
        return self.board.pgn()

    def is_valid_san_move(self, san_move: str) -> bool:
        """Check if move in SAN format is valid (e.g., 'Qxd8', 'Nf3', 'e4')."""
        try:
            move = self.board.parse_san(san_move)
            return move in self.board.legal_moves
        except (ValueError, KeyError):
            return False

    def make_san_move(self, san_move: str) -> bool:
        """Make a move in SAN format. Returns True if successful."""
        if not self.is_valid_san_move(san_move):
            return False

        move = self.board.parse_san(san_move)
        self.board.push(move)
        return True

    def get_uci_move(self, san_move: str) -> str:
        """Convert SAN move to UCI format."""
        move = self.board.parse_san(san_move)
        return move.uci()
