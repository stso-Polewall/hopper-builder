#!/usr/bin/env python3

from typing import Any

import argparse


def parse_args() -> Any:
    """parses arguments

    Returns
    -------
    Args
        Object contaning argument variables
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-clean', action="store_true")
    parser.add_argument('--no-pull', action="store_true")
    parser.add_argument('module')
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()


if __name__ == "__main__":
    main()
