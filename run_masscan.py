import logging, subprocess, glob, os

def start_masscan(mass_format):
    """The main function for masscan. This one in particular simply runs masscan and then calls the formatter for the output."""
    #TODO: Have the data be fed directly into a database.
    #TODO: Format the data before it writes to file somehow, not sure what the best way to do this would be yet.
    #Maybe split this function so this is more of a runner and calls a seperate function that "starts" masscan.
    try:
        logging.debug("Beggining Masscan Scan Using the Following Command: %s" % mass_format)
        #For some reason subprocess doesn't like single strings for its commands and you need to split each flag into seperate strings.
        #TODO: Maybe have the formatter put the data into a list from the start so this little for loop isn't necessary.
        subprocess.run([i for i in mass_format.split(' ')])
        logging.debug("Masscan Scan Finished")
        logging.debug("Formatting Masscan Output")
        format_mass_out()
        logging.debug("Finished Formatting Masscan Output")

    except Exception as error:
        logging.critical("Error when trying to run the masscan command.\nError: %s" % error)

def format_mass_out():
    try:
        #Since there will likely be multiple masscan files, this will search for the latest one so we can format it.
        #This whole thing might be pointless if I can manage to format the output before it is written to a file.
        file_list = glob.glob('./results/masscan/mass_results_*')
        latest_file = max(file_list, key=os.path.getctime)
        print(latest_file)
        with open(latest_file, "r") as file:
            lines = file.read().splitlines()
        print(lines)

    except Exception as error:
        logging.critical("Error in formatting masscan output: %s" % error)
        exit()