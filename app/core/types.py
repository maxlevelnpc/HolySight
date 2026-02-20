from typing import TypedDict
from enum import Enum, auto


class CrosshairMode(Enum):
    GAME = auto()
    MOVE = auto()


class ConfigData(TypedDict):
    ch_color: str
    ch_size: int
    ch_opacity: float
    ch_image: str
    ch_bcolor: str
    ch_bsize: int
    ch_pos: tuple[int, int]
