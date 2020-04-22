#!/usr/bin/env python3

from subprocess import run, DEVNULL
import logging

class bcolors:
    """Used to provide color to logging output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

to_install = ["qdarkstyle", "pyqt5", "tqdm", "python-libnmap", "selenium"]

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ])

logging.getLogger().setLevel(logging.DEBUG)

logging.addLevelName(logging.WARNING, bcolors.WARNING + bcolors.BOLD + logging.getLevelName(logging.WARNING) + bcolors.ENDC)
logging.addLevelName(logging.CRITICAL, bcolors.FAIL + bcolors.BOLD + bcolors.UNDERLINE + logging.getLevelName(logging.CRITICAL) + bcolors.ENDC)
logging.addLevelName(logging.INFO, bcolors.BOLD + bcolors.OKGREEN + logging.getLevelName(logging.INFO) + bcolors.ENDC)
logging.addLevelName(logging.DEBUG, bcolors.OKBLUE + logging.getLevelName(logging.DEBUG) + bcolors.ENDC)

logging.info("Beginning Installation of Dependencies")
for i in to_install:
    try:
        logging.debug("Attempting to install %s." % i)
        run(["pip3", "install", i], stdout=DEVNULL)
        logging.debug("Finished installing %s." % i)
    except Exception as error:
        logging.critical("Error installing %s.\nError: %s" % (i, error))
logging.info("Finished Installing Dependencies")