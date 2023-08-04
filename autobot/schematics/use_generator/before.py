"""...as a list builder."""


def compute_squares(n: int) -> list[int]:
    squares: list[int] = [i * i for i in range(n)]
    return squares
