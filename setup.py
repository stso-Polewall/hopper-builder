#!/usr/bin/env python3

from setuptools import setup

setup(name="Hopper-Builder",
      version="0.0.1",
      description="Automate Vivado build of hopper",
      author="Stian Solli",
      url="https://github.com/stso-Polewall/hopper-builder",
      license="Other/Proprietary",
      scripts=["bin/builder"],
      packages=["builder"],
      python_requires=">=3.5",
      install_requires=[
          "PyYAML >= 3.13",
          "progressbar2 >= 3.38",
      ],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: Other/Proprietary License",
          "Natural Language :: English",
          "Environment :: Console",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Software Development :: Build Tools",
      ],)
