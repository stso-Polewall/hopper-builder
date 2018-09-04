#!/usr/bin/env python3

from typing import Dict, Any

import logging
import os
import shlex
import subprocess
import shutil
import yaml
from pprint import pformat

logger = logging.getLogger(__name__)


class Build(object):
    config = {}

    def __init__(self, module, verbose=False):
        self.module = module.lower()
        self.verbose = verbose

        # Set config if empty
        if not self.config:
            Build.config = self._set_config()

        # Check if module exist
        if self.module not in self.config['modules']:
            logger.critical("Missing module: {}!".format(self.module))
            self._list_modules()
            exit(1)

        self._cwd_to_base()

    def _list_modules(self):
        modules = [*self.config['modules']]
        modules.sort()
        print("Available modules: {}".format(", ".join(modules).lower()))


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
        if self.verbose:
            stdout = None
        else:
            logger.debug("Opening stdout to /dev/null")
            stdout = open(os.devnull, 'w')

        logger.debug("Running {}".format(cmd))
        try:
            subprocess.run(shlex.split(cmd), check=True, stdout=stdout)
        except subprocess.CalledProcessError:
            logger.error("\"{}\" subprocess failed!".format(cmd), exc_info=True)
 
        if stdout:
            logger.debug("Closing stdout")
            stdout.close

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
        logger.debug("Creating config")

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
                    class_dict[stmv][module.lower()] = project_dict[stmv][module]

        # Add/Update modules from user
        if stmv in user_dict and user_dict[stmv]:
            for module, _ in user_dict[stmv].items():
                for key, _ in user_dict[stmv][module].items():
                    logger.debug("user_dict[{}]['{}']: {}".format(stmv, module, key))
                    class_dict[stmv][module.lower()] = user_dict[stmv][module]

        if class_dict[stmv]:
            logger.debug("Config done")
            logger.debug("Returning: {}".format('\n' + pformat(class_dict)))
            return class_dict
        else:
            # Modules missing, pointless to continue
            # logger.error("Missing modules in config.  Quiting!")
            quit()


class Hw(Build):
    def __init__(self, module, verbose=False):
        super().__init__(module, verbose)

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

    def is_enabled(self) -> bool:
        """Should this be run based on current configs

        Returns
        -------
        bool
            Returns True if class should be used in build
        """
        if self.config['modules'][self.module]['hw']:
            return True
        else:
            return False

    def _set_env(self) -> None:
        """Adds Vivado to PATH
        echo $PATH needs to be last line of settings64_Vivado_Linux.sh
        """
        logger.debug("Setting envirotment PATH")
        os.environ["PATH"] = subprocess.check_output(
                             shlex.split("bash settings64_Vivado_Linux.sh")).decode().split("\n")[1]
        logger.debug(os.environ["PATH"])


class Sw(Build):
    def __init__(self, module, verbose=False):
        super().__init__(module, verbose)

    def build_sw(self):
        logger.info("Starting Software Build")
        os.chdir(self.config['modules'][self.module]['swpath'])
        logger.debug("Setting cwd to {}".format(os.getcwd()))
        logger.debug("Building SW")
        self._proc_start("bash buildAll")
        self._cwd_to_base()
        logger.info("Finished Software Build")

    def is_enabled(self) -> bool:
        """Should this be run based on current configs

        Returns
        -------
        bool
            Returns True if class should be used in build
        """
        if self.config['modules'][self.module]['sw']:
            return True
        else:
            return False
