from PySide6.QtCore import Signal, QObject
from app.core.services import ConfigService


class CrosshairModel(QObject):
    colorChanged = Signal(str)
    sizeChanged = Signal(int)
    opacityChanged = Signal(float)
    imageChanged = Signal(str)
    positionChanged = Signal(tuple)

    moveModeChanged = Signal(bool)
    visibilityChanged = Signal(bool)

    def __init__(self, config_service: ConfigService) -> None:
        super().__init__()
        self.service = config_service

        self._color: str
        self._size: int
        self._opacity: float
        self._image: str
        self._pos: tuple

        self._is_movable: bool = False
        self._is_hidden: bool = False

    def load_config(self) -> None:
        config_data = self.service.load_config_data()
        self._color = config_data["ch_color"]
        self._size = config_data["ch_size"]
        self._opacity = config_data["ch_opacity"]
        self._image = config_data["ch_image"]
        self._pos = tuple(config_data["ch_pos"])

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, color: str) -> None:
        self._color = color
        self.colorChanged.emit(color)

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, size: int) -> None:
        self._size = size
        self.sizeChanged.emit(size)

    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    def opacity(self, opacity: int) -> None:
        op = opacity / 10.0
        self._opacity = op
        self.opacityChanged.emit(op)

    @property
    def image(self) -> str:
        return self._image

    @image.setter
    def image(self, image: str) -> None:
        self._image = image
        self.imageChanged.emit(image)

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, pos: tuple[int, int]) -> None:
        self._pos = pos
        self.positionChanged.emit(pos)

    @property
    def movable(self) -> bool:
        return self._is_movable

    @movable.setter
    def movable(self, movable: bool) -> None:
        self._is_movable = movable
        self.moveModeChanged.emit(movable)

    @property
    def hidden(self) -> bool:
        return self._is_hidden

    @hidden.setter
    def hidden(self, hidden: bool) -> None:
        self._is_hidden = hidden
        self.visibilityChanged.emit(hidden)
