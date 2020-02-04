import logging, subprocess, glob, os

def start_masscan(mass_format):
    """The main function for masscan. This one in particular simply runs masscan and then calls the formatter for the output."""
    #TODO: Have the data be fed directly into a database.
    #TODO: Format the data before it writes to file somehow, not sure what the best way to do this would be yet.
    #Maybe split this function so this is more of a runner and calls a seperate function that "starts" masscan.
    try:
        logging.debug("Beginning Masscan Scan Using the Following Command: %s" % mass_format)
        #For some reason subprocess doesn't like single strings for its commands and you need to split each flag into seperate strings.
        #TODO: Maybe have the formatter put the data into a list from the start so this little for loop isn't necessary.
        subprocess.run([i for i in mass_format.split(' ')])
        logging.debug("Masscan Scan Finished")
        logging.debug("Formatting Masscan Output")

        return(format_mass_out())

    except Exception as error:
        logging.critical("Error when trying to run the masscan command.\nError: %s" % error)

def format_mass_out():
    try:
        #Since there will likely be multiple masscan files, this will search for the latest one so we can format it.
        #This whole thing might be pointless if I can manage to format the output before it is written to a file.
        file_list = glob.glob('./results/masscan/mass_results_*')
        latest_file = max(file_list, key=os.path.getctime)
        logging.debug("Reading Data from %s" % latest_file)
        ip_port_list = []
        with open(latest_file, "r") as file:
            lines = file.read().splitlines()
        for i in lines:
            #We don't want lines starting with # as they are comments.
            if "#" not in i:   
                ip_port = i.split(" ")[2:4]
                ip_port_list.append("%s:%s" % (ip_port[1], ip_port[0]))

        #Opens a new file starting with formatted and writes the formatted output to it.  This is mostly just for the user in case they want to read it.
        #Actual data is sent back to main where it will eventually be fed to nmap.
        with open ("%sformatted_%s" % (latest_file[0:latest_file.index("mass_results")], latest_file[latest_file.index("mass_results"):]), "w") as file:
            logging.debug("Writing Formatted Data to %s" % file.name)
            for i in ip_port_list:
                file.write("%s\n" % i)

        logging.debug("Finished Formatting Masscan Output")
        return(ip_port_list)

    except Exception as error:
        logging.critical("Error in formatting masscan output: %s" % error)
        exit()