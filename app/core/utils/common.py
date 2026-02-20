import logging


def setup_logging() -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        f"[%(levelname)s] %(asctime)s | %(name)s | Ln. %(lineno)d %(funcName)s -> %(message)s",
        "%Y-%m-%d %I:%M:%S %p"
    )

    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(console_handler)