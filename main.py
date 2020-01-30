#!/usr/bin/env python3
import logging
from user_functions import get_args, get_formats, make_dirs, verify_versions, bcolors
from run_masscan import start_masscan
from run_nmap import start_nmap
def main():
    """The main function for the program.  This calls all other functions."""
    setup_logging()
    logging.info("Initializing Program")
    args, addresses, ports = get_args()
    logging.debug("Finished Verifying Arguments")
    formats = get_formats(args)
    verify_versions()
    logging.info("Finished Initializing Program")

    logging.info("Starting Masscan")
    logging.debug("Starting Masscan Scan")
    mass_data = start_masscan(formats['masscan'])
    logging.info("Finished Masscan")

    logging.info("Starting Nmap")
    start_nmap(formats['default_nmap'], mass_data, args)
    logging.info("Finished Nmap")

def setup_logging():
    """Responsible for setting up the logger to make output look nicer and to log to both the screen and a file."""
    #TODO: See if this can be moved to the user_functions module to make this module look better.
    #format sets up the logging messages to include the date/time of the message.
    #Level sets the level to INFO at the start, this will be modified shortly if the user provided -q or -v.
    #Handlers makes sure that the output is sent to both the screen and to the log file.
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s', 
        level=logging.INFO,
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ])
    logging.root.handlers[0].setLevel(logging.DEBUG)
    logging.debug("Setting Up Directories")
    make_dirs()
    logging.debug("Finished Setting Up Directories")

    #These just make the log output look nicer, could probably make this code clearner as well.
    logging.addLevelName(logging.WARNING, bcolors.WARNING + bcolors.BOLD + logging.getLevelName(logging.WARNING) + bcolors.ENDC)
    logging.addLevelName(logging.CRITICAL, bcolors.FAIL + bcolors.BOLD + bcolors.UNDERLINE + logging.getLevelName(logging.CRITICAL) + bcolors.ENDC)
    logging.addLevelName(logging.INFO, bcolors.BOLD + bcolors.OKGREEN + logging.getLevelName(logging.INFO) + bcolors.ENDC)
    logging.addLevelName(logging.DEBUG, bcolors.OKBLUE + logging.getLevelName(logging.DEBUG) + bcolors.ENDC)
    
if __name__ == '__main__':
    main()