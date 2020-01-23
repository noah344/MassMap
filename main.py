#!/usr/bin/env python3
import logging
from user_functions import get_args, get_formats, make_dirs, bcolors
from run_masscan import start_masscan

def main():
    setup_logging()
    logging.info("Initializing Program")
    args, addresses, ports = get_args()
    logging.debug("Finished Verifying Arguments")
    formats = get_formats(args)
    logging.info("Finished Initializing Program")

    logging.info("Starting Masscan")
    logging.debug("Starting Masscan Scan")
    start_masscan(formats['masscan'])
    logging.info("Finished Masscan")


def setup_logging():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.addLevelName(logging.WARNING, bcolors.WARNING + bcolors.BOLD + logging.getLevelName(logging.WARNING) + bcolors.ENDC)
    logging.addLevelName(logging.CRITICAL, bcolors.FAIL + bcolors.BOLD + bcolors.UNDERLINE + logging.getLevelName(logging.CRITICAL) + bcolors.ENDC)
    logging.addLevelName(logging.INFO, bcolors.BOLD + bcolors.OKGREEN + logging.getLevelName(logging.INFO) + bcolors.ENDC)
    logging.addLevelName(logging.DEBUG, bcolors.OKBLUE + logging.getLevelName(logging.DEBUG) + bcolors.ENDC)
    
if __name__ == '__main__':
    main()