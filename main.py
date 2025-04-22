import sys, logging  # noqa E401
from PySide6.QtWidgets import QApplication
from windows import HolySight
from resources import icons  # noqa: F401

logging.basicConfig(
    filename="logs.txt",
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - Line %(lineno)d - %(message)s'
)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HolySight()
    sys.exit(app.exec())
