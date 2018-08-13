#!/usr/bin/env python3

from typing import Dict, Any
import os
from pathlib import Path
import shutil
import argparse
import yaml

import pprint

DEFAULT_CONF_PATH = os.path.expanduser("~/.config/builder.yml")
DEFAULT_CONF_FILE = os.path.dirname(os.path.realpath(__file__)) + "/default_conf.yml"


def get_conf() -> Dict:
    """Returns a settings dictonary

    It gets user and project settings and combine them.
    If user is empty a default file is copied to user folder.

    Returns
    -------
    dict
        A dictonary contaning settings
    """
    if not os.path.isfile(DEFAULT_CONF_PATH):
        shutil.copyfile(DEFAULT_CONF_FILE, DEFAULT_CONF_PATH)

    with open(DEFAULT_CONF_PATH, "r") as yaml_file:
        user_dict = yaml.load(yaml_file)

    if os.path.isfile(os.path.expanduser(user_dict['settings']['config'])):
        with open(os.path.expanduser(user_dict['settings']['config'])) as yaml_file:
            project_dict = yaml.load(yaml_file)
            # NOTE Adding and removing DELETE to modules is a bodge!
            if user_dict["modules"] == None:
                user_dict["modules"] = {"DELETE": None}
            user_dict["modules"] = {**project_dict["modules"], **user_dict["modules"]}
            if "DELETE" in user_dict["modules"]:
                user_dict["modules"].pop("DELETE")

    return user_dict


def parse_args() -> Any:
    """parses arguments

    Returns
    -------
    Args
        Object contaning argument variables
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean', action="store_true")
    parser.add_argument('--pull', action="store_true")
    parser.add_argument('module')
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    pprint.pprint(get_conf())


if __name__ == "__main__":
    main()
