from numpy import ndarray
import numpy as np


def convert_fen_to_network(fen: str, flip: bool = False) -> ndarray:
    """Convert FEN to network input tensor (17, 8, 8).

    If flip=True, the board is mirrored vertically and piece colors are swapped,
    so the network always sees the position from white's perspective.

    Planes 0-5:  "our" pieces (P, R, N, B, Q, K)
    Planes 6-11: "their" pieces (p, r, n, b, q, k)
    Planes 12-13: our castling rights (K-side, Q-side)
    Planes 14-15: their castling rights (k-side, q-side)
    Plane 16: en passant
    """
    res = np.zeros((17, 8, 8))
    k = 0

    # Piece plane mapping: FEN char -> plane index
    piece_to_plane = {
        "P": 0, "R": 1, "N": 2, "B": 3, "Q": 4, "K": 5,
        "p": 6, "r": 7, "n": 8, "b": 9, "q": 10, "k": 11,
    }

    if flip:
        # Swap white/black planes
        piece_to_plane = {
            "p": 0, "r": 1, "n": 2, "b": 3, "q": 4, "k": 5,
            "P": 6, "R": 7, "N": 8, "B": 9, "Q": 10, "K": 11,
        }

    for i in range(8):
        row = (7 - i) if flip else i
        j = 0
        while j < 8 and k < len(fen):
            if fen[k].isdigit():
                j += int(fen[k])
                k += 1
            elif fen[k] == "/":
                k += 1
            elif fen[k] in piece_to_plane:
                res[piece_to_plane[fen[k]]][row][j] = 1
                k += 1
                j += 1
            else:
                k += 1

    # Skip to castling section
    while k < len(fen) and fen[k] != " ":
        k += 1
    k += 1  # skip space
    # Skip active color
    while k < len(fen) and fen[k] != " ":
        k += 1
    k += 1  # skip space

    KR = QR = kR = qR = 0
    while k < len(fen) and fen[k] != " ":
        if fen[k] == "K":
            KR = 1
        elif fen[k] == "Q":
            QR = 1
        elif fen[k] == "k":
            kR = 1
        elif fen[k] == "q":
            qR = 1
        k += 1

    if flip:
        KR, kR = kR, KR
        QR, qR = qR, QR

    for i in range(8):
        for j in range(8):
            res[12][i][j] = KR
            res[13][i][j] = QR
            res[14][i][j] = kR
            res[15][i][j] = qR

    # Skip space
    k += 1

    if k < len(fen) and fen[k] != "-" and k + 1 < len(fen):
        file_char = fen[k]
        rank_char = fen[k + 1]

        if "a" <= file_char <= "h" and "1" <= rank_char <= "8":
            file_idx = ord(file_char) - ord("a")
            rank_idx = int(rank_char) - 1
            if flip:
                rank_idx = 7 - rank_idx
            res[16][rank_idx][file_idx] = 1

    return res


def move_to_index(move: str) -> int:
    from_sq = move[:2]
    to_sq = move[2:4]
    promotion = move[4] if len(move) > 4 else None

    from_file = ord(from_sq[0]) - ord("a")
    from_rank = int(from_sq[1]) - 1
    from_idx = from_rank * 8 + from_file

    to_file = ord(to_sq[0]) - ord("a")
    to_rank = int(to_sq[1]) - 1
    to_idx = to_rank * 8 + to_file

    base_idx = from_idx * 64 + to_idx

    if promotion:
        promo_map = {"q": 0, "r": 1, "b": 2, "n": 3, "Q": 0, "R": 1, "B": 2, "N": 3}
        promo_idx = promo_map.get(promotion, 0)
        return 4096 + promo_idx * 64 + from_idx

    return base_idx


def flip_move(move: str) -> str:
    """Flip a UCI move vertically (e.g. e2e4 -> e7e5)."""
    from_sq = move[:2]
    to_sq = move[2:4]
    promotion = move[4:] if len(move) > 4 else ""

    from_flipped = from_sq[0] + str(9 - int(from_sq[1]))
    to_flipped = to_sq[0] + str(9 - int(to_sq[1]))

    return from_flipped + to_flipped + promotion
