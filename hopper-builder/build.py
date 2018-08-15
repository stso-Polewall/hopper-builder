#!/usr/bin/env python3

from Typing import Dict

import logging
import os
import shutil
import yaml

logger = logging.getLogger(__name__)

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
        logger.info("Creating config")

        class_dict = {}
        default_path = os.path.dirname(os.path.realpath(__file__)) + "/default_conf.yml"
        user_path = os.path.expanduser("~/.config/builder.yml")

        # Create Default user config if missing
        if not os.path.isfile(user_path):
                    logger.debug("Adding default user config")
                    shutil.copyfile(default_path, user_path)

        # Open and create user dictonary
        try:
            with open(user_path, "r") as yaml_file:
                logger.debug("Creating user_dict")
                user_dict = yaml.load(yaml_file)
        except FileNotFoundError:
            logger.error("Missing user config: {}".format(user_path), exc_info=True)

        # Open and create project dictonary if it exists
        project_path = os.path.expanduser(user_dict['settings']['config'])
        if os.path.isfile(project_path):
            with open(project_path, "r") as yaml_file:
                logger.debug("Creating project_dict")
                project_dict = yaml.load(yaml_file)
        else:
            logger.warning("Missing project config: {}".format(project_path))

        # Merge user and project into class dictoanry
        class_dict['settings'] = user_dict['settings']

        # Add modules from project
        if "modules" in project_dict:
            for module in project_dict.iterkeys():
                for item in module.iterkeys():
                    logger.debug("project_dict['modules']['{}']: {}".format(module, item))
                    class_dict['modules'][module][item] = project_dict['modules'][module][item]

        # Add/Update modules from user
        if "modules" in user_dict:
            for module in user_dict.iterkeys():
                for item in module.iterkeys():
                    logger.debug("user_dict['modules']['{}']: {}".format(module, item))
                    class_dict['modules'][module][item] = user_dict['modules'][module][item]

        
        if "modules" in class_dict:
            logger.info("Done")
            return class_dict
        else:
            # Modules missing, pointless to continue
            logger.error("Missing modules in config.  Quiting!")
            quit()


class Sw(Build):
    pass


class Hw(Build):
    pass
