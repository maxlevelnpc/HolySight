import logging


def setup_logging(log_file: str) -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s | %(name)s | Ln. %(lineno)d %(funcName)s -> %(message)s",
        "%Y-%m-%d %I:%M:%S %p",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(console_handler)
