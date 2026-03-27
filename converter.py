from numpy import ndarray
import numpy as np


def convert_fen_to_network(fen: str) -> ndarray:
    res = np.zeros((17, 8, 8))
    k = 0

    for i in range(8):
        j = 0
        while j < 8 and k < len(fen):
            if fen[k].isdigit():
                j += int(fen[k])
                k += 1
            elif fen[k] == "/":
                k += 1
            elif fen[k] == "P":
                res[0][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "p":
                res[6][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "R":
                res[1][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "N":
                res[2][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "B":
                res[3][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "Q":
                res[4][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "K":
                res[5][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "r":
                res[7][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "n":
                res[8][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "b":
                res[9][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "q":
                res[10][i][j] = 1
                k += 1
                j += 1
            elif fen[k] == "k":
                res[11][i][j] = 1
                k += 1
                j += 1
            else:
                k += 1

    while k < len(fen) and fen[k] != " ":
        k += 1
    k += 1

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

    for i in range(8):
        for j in range(8):
            res[12][i][j] = KR
            res[13][i][j] = QR
            res[14][i][j] = kR
            res[15][i][j] = qR

    while k < len(fen) and fen[k] != " ":
        k += 1
    k += 1

    if k < len(fen) and fen[k] != "-" and k + 1 < len(fen):
        file_char = fen[k]
        rank_char = fen[k + 1]

        if "a" <= file_char <= "h" and "1" <= rank_char <= "8":
            file_idx = ord(file_char) - ord("a")
            rank_idx = int(rank_char) - 1
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
