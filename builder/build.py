#!/usr/bin/env python3

from typing import Dict, Any

import logging
import os
import shlex
import subprocess
import shutil
import yaml

logger = logging.getLogger(__name__)


class Build(object):
    config = {}

    def __init__(self, module):
        self.module = module

        # Set config if empty
        if not self.config:
            self.config = self._set_config()

        self._cwd_to_base()

    def _cwd_to_base(self):
        os.chdir(os.path.expanduser(self.config['settings']['project']))
        logger.debug("Setting cwd to {}".format(os.getcwd()))

    def _proc_start(self, cmd) -> None:
        """Runs command with subprocess

        Raises
        ------
        subprocess.CalledProcessError
            If process returns a non zero value
        """
        logger.debug("Running {}".format(cmd))

        # NOTE: Default false to limit as cpulimit always returns 0
        if "limit" in self.config['settings']:
            if self.config['settings']['limit']:
                limit = True
            else:
                limit = False
        else:
            limit = False

        logger.debug("Limit: {}".format(limit))

        try:
            if not limit:
                subprocess.run(shlex.split(cmd), check=True)
            else:
                subprocess.run(["cpulimit", "-l 75", "-m", "-z", "-f", "--"] + shlex.split(cmd), check=True)
        except subprocess.CalledProcessError:
             logger.error("\"{}\" subprocess failed!".format(cmd), exc_info=True)

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
            # logger.error("Missing modules in config.  Quiting!")
            quit()


class Hw(Build):
    def __init__(self, module):
        super().__init__(module)

    def build_hw(self) -> None:
        logger.info("Starting Hardware Build")
        # Change directory to hwpath
        os.chdir(self.config['modules'][self.module]['hwpath'])
        logger.debug("Setting cwd to {}".format(os.getcwd()))

        # Set enviroment path
        self._set_env()

        logger.debug("Building HW")
        self._proc_start("vivado -mode tcl -source makeHW_All.tcl")
        #try:
        #    if 'ERROR: [' in open('vivado.log').read():
        #        raise subprocess.CalledProcessError
        #except subprocess.CalledProcessError:
        #    logger.error("\"vivado -mode tcl -source makeHW_All.tcl\" subprocess failed!", exc_info=True) 
        self._cwd_to_base()
        logger.info("Finished Hardware Build")

    def _set_env(self) -> None:
        """Adds Vivado to PATH"""
        logger.debug("Setting envirotment PATH")
        os.environ["PATH"] = subprocess.check_output(
                             shlex.split("bash settings64_Vivado_Linux.sh")).decode().split("\n")[1]
        logger.debug(os.environ["PATH"])


class Sw(Build):
    def __init__(self, module):
        super().__init__(module)

    def build_sw(self):
        logger.info("Starting Software Build")
        os.chdir(self.config['modules'][self.module]['swpath'])
        logger.debug("Setting cwd to {}".format(os.getcwd()))
        logger.debug("Building SW")
        self._proc_start("bash buildAll")
        self._cwd_to_base()
        logger.info("Finished Software Build")
