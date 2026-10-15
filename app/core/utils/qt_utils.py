import logging

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QFile, QTextStream

log = logging.getLogger(__name__)


def load_style(*paths: str) -> str:
    """
    :returns: combined stylesheet.
    """
    stylesheet = ""

    for path in paths:
        file = QFile(path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            stylesheet += stream.readAll() + "\n\n"
            file.close()
        else:
            log.critical(f"{file.errorString()} -> `{path}`")

    return stylesheet
