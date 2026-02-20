import logging

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream

log = logging.getLogger(__name__)


def reposition_window(window, center=True):
    screen = QApplication.primaryScreen().availableGeometry()
    frame = window.frameGeometry()

    if center:
        frame.moveCenter(screen.center())
        window.move(frame.topLeft())
    else:
        # half right center
        half_width = screen.width() // 2
        x = screen.left() + half_width + (half_width - frame.width()) // 2
        y = screen.top() + (screen.height() - frame.height()) // 2 - 60
        window.move(x, y)

def load_style(*paths: str) -> str:
    """
    :returns: combined styles.
    """
    style = ""

    for path in paths:
        file = QFile(path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            style += stream.readAll() + f"\n\n"
            file.close()
        else:
            log.critical(f"{file.errorString()} -> `{path}`")

    return style
