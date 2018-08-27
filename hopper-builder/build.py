#!/usr/bin/env python3

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
    def _set_config():
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

        stmv = 'modules'
        class_dict[stmv] = {}
        # Add modules from project
        if stmv in project_dict:
            for module, _ in project_dict[stmv].items():
                for key, value in project_dict[stmv][module].items():
                    logger.debug("project_dict[{}]['{}']: {}".format(stmv, module, key))
                    class_dict[stmv][module] = project_dict[stmv][module]

        # Add/Update modules from user
        if stmv in user_dict and user_dict[stmv]:
            for module, _ in user_dict[stmv].items():
                for key, _ in user_dict[stmv][module].items():
                    logger.debug("user_dict[{}]['{}']: {}".format(stmv, module, key))
                    class_dict[stmv][module] = user_dict[stmv][module]

        if class_dict[stmv]:
            logger.info("Done")
            logger.debug("Returning: {}".format(class_dict))
            return class_dict
        else:
            # Modules missing, pointless to continue
            logger.error("Missing modules in config.  Quiting!")
            quit()


class Sw(Build):
    pass


class Hw(Build):
    pass
