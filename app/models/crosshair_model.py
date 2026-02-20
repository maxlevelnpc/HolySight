from PySide6.QtCore import Signal, QObject
from app.core.services import ConfigService


class CrosshairModel(QObject):
    colorChanged = Signal(object)
    sizeChanged = Signal(int)
    opacityChanged = Signal(float)
    imageChanged = Signal(str, object)
    borderColorChanged = Signal(object)
    borderSizeChanged = Signal(object)
    positionChanged = Signal(tuple)

    def __init__(self, config_service: ConfigService) -> None:        
        super().__init__()
        self.service = config_service

        self._color: str
        self._size: int
        self._opacity: float
        self._image: str
        self._bcolor: str
        self._bsize: int
        self._pos: tuple
    
    def load_config(self) -> None:
        config_data = self.service.load_config_data()
        self._color = config_data["ch_color"]
        self._size = config_data["ch_size"] 
        self._opacity = config_data["ch_opacity"]
        self._image = config_data["ch_image"]
        self._bcolor = config_data["ch_bcolor"]
        self._bsize = config_data["ch_bsize"]
        self._pos = tuple(config_data["ch_pos"])
    
    def get_style_req(self) -> tuple[str, int, str, int]:
        return self._color, self._size, self._bcolor, self._bsize 
    
    @property
    def color(self) -> str:
        return self._color
    
    @color.setter
    def color(self, color: str) -> None:
        self._color = color
        self.colorChanged.emit(self.get_style_req)

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
    def opacity(self, opacity: float) -> None:
        op = opacity / 255
        self._opacity = op
        self.opacityChanged.emit(op)

    @property
    def image(self) -> str:
        return self._image
    
    @image.setter
    def image(self, image: str) -> None:
        self._image = image
        self.imageChanged.emit(image, self.get_style_req)

    @property
    def bcolor(self) -> str:
        return self._bcolor
    
    @bcolor.setter
    def bcolor(self, bcolor: str) -> None:
        self._bcolor = bcolor
        self.borderColorChanged.emit(self.get_style_req)

    @property
    def bsize(self) -> int:
        return self._bsize
    
    @bsize.setter
    def bsize(self, bsize: int) -> None:
        self._bsize = bsize
        self.borderSizeChanged.emit(self.get_style_req)

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos
    
    @pos.setter
    def pos(self, pos: tuple[int, int]) -> None:
        self._pos = pos
        self.positionChanged.emit(pos)
