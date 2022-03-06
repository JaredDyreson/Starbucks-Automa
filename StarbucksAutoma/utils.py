"""A collection of scripts that can be used"""

import pathlib
import os


def source(path: pathlib.Path):
    """Load environment variables from plain text file"""

    with open(path, "r", encoding="utf-8") as fil_ptr:
        for line in fil_ptr.readlines():
            match line.split("="):
                case [name, value]:
                    os.environ[name] = value
                case _:
                    raise Exception(f"failed to parse: {line}")
