MAX_COMMITMENT_NODES: int

def pure_profiles(
    row: list[list[float]], column: list[list[float]], binary32: list[bool]
) -> list[tuple[int, int]]: ...
def commitment_choice(
    leader: list[list[float]], follower: list[list[float]]
) -> tuple[int, int]: ...
def mixed_profile(
    row: list[list[float]], column: list[list[float]]
) -> tuple[list[float], list[float]] | None: ...
