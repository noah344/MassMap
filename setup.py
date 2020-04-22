#!/usr/bin/env python3

from subprocess import run, DEVNULL
from main import setup_logging
import logging

to_install = ["qdarkstyle", "pyqt5", "tqdm", "python-libnmap", "selenium"]
setup_logging()
logging.getLogger().setLevel(logging.DEBUG)
logging.info("Beggining Installation of Dependencies")
for i in to_install:
    try:
        logging.debug("Attempting to install %s." % i)
        run(["pip3", "install", i], stdout=DEVNULL)
        logging.debug("Finished installing %s." % i)
    except Exception as error:
        logging.critical("Error installing %s.\nError: %s" % (i, error))
logging.info("Finished Installing Dependencies")