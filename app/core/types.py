from typing import TypedDict


class ConfigData(TypedDict):
    ch_color: str
    ch_size: int
    ch_opacity: float
    ch_image: str
    ch_pos: tuple[int, int]
