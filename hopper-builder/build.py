#!/usr/bin/env python3

from Typing import Dict

import os
import shutil
import yaml


class Build(object):
    config = {}

    def __init__(self):
        # Set config if empty
        if not self.config:
            self.config = self._set_config()

    @staticmethod
    def _set_config() -> Dict:
        """Returns a settings dictonary

        It gets user and project settings and combine them.
        If user is empty a default file is copied to user folder.

        Returns
        -------
        dict
            A dictonary contaning settings
        """
        class_dict = {}
        default_path = os.path.dirname(os.path.realpath(__file__)) + "/default_conf.yml"
        user_path = os.path.expanduser("~/.config/builder.yml")

        # Create Default user config if missing
        if not os.path.isfile(user_path):
                    shutil.copyfile(default_path, user_path)

        # Open and create user dictonary
        if os.path.isfile(user_path):
            with open(user_path, "r") as yaml_file:
                user_dict = yaml.load(yaml_file)
        else:
            # user_path file does not exist
            raise FileNotFoundError

        # Open and create project dictonary if it exists
        project_path = os.path.expanduser(user_dict['settings']['config'])
        if os.path.isfile(project_path):
            with open(project_path, "r") as yaml_file:
                project_dict = yaml.load(yaml_file)
        else:
            raise FileNotFoundError

        # Merge user and project into class dictoanry
        class_dict['settings'] = user_dict['settings']

        # Add modules from project
        if "modules" in project_dict:
            for module in project_dict.iterkeys():
                for item in module.iterkeys():
                    class_dict['modules'][module][item] = project_dict['modules'][module][item]

        # Add/Update modules from user
        if "modules" in user_dict:
            for module in user_dict.iterkeys():
                for item in module.iterkeys():
                    class_dict['modules'][module][item] = user_dict['modules'][module][item]

        if "modules" in class_dict:
            return class_dict
        else:
            # Modules missing, pointless to continue
            raise ValueError


class Sw(Build):
    pass


class Hw(Build):
    pass
