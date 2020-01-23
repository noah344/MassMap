import logging, subprocess, glob, os

def start_masscan(mass_format):
    try:
        logging.debug("Beggining Masscan Scan Using the Following Command: %s" % mass_format)
        subprocess.run([i for i in mass_format.split(' ')])
        logging.debug("Masscan Scan Finished")
        logging.debug("Formatting Masscan Output")
        format_mass_out()
        logging.debug("Finished Formatting Masscan Output")

    except Exception as error:
        logging.critical("Error when trying to run the masscan command.\nError: %s" % error)

def format_mass_out():
    try:
        file_list = glob.glob('./results/masscan/mass_results_*')
        latest_file = max(file_list, key=os.path.getctime)
        print(latest_file)
        with open(latest_file, "r") as file:
            lines = file.read().splitlines()
        print(lines)

    except Exception as error:
        logging.critical("Error in formatting masscan output: %s" % error)
        exit()