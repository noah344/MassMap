import logging, argparse, re, json, time
from os import system, path, getcwd, remove, makedirs
from netaddr import IPNetwork, iter_iprange, IPAddress
from netaddr.core import AddrFormatError

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

def get_args():
    """Provides an argument parser to collect options from the user."""
    #Sets up the parser and provides it with a description.
    parser = argparse.ArgumentParser(description="Scans a set of IPs quickly and provides detailed output using nmap and masscan.")
    #Sets up a mutually exclusive group of arguments meaning that only one can be selected, verbose or quiet.
    verbosity = parser.add_mutually_exclusive_group()
    #Sets up additional groups to make the help output pretty.
    mass_args = parser.add_argument_group("Masscan Arguments")
    req_args = parser.add_argument_group("Required Arguments")

    #Adds verbosity arguments to make more output visible if needed or to quiet the output.
    verbosity.add_argument("-v", "--verbose", action="store_true", help="Increases verbosity of the program.", default=False, required=False)
    verbosity.add_argument("-q", "--quiet", action="store_true", help="Decreases the verbosity of the program.", default=False, required=False)
    
    #Provides an argument that the user can set to change the rate that masscan will send out packets.
    mass_args.add_argument("-mr", "--mass_rate", type=int, help="Tells masscan the packet rate you wish for it to use. Default is 20000.", default=20000, required=False)
    #Provides an argument that the user can set to change the ports that masscan will scan.
    mass_args.add_argument("-mp", "--mass_ports", type=str, help="Tells masscan what ports you wish for it to scan. Default is 1-65535.", default="1-65535", required=False)

    #Adds a required argument that has the user provide either a comma separated list of IPs or a file that contains a list of IP addresses.
    req_args.add_argument("IPs", type=str, help="Provide the full location of an IP file or a comma seperated list of IPs. Can be formatted in any of the following ways: \
        192.168.1.1, 192.168.1.2-192.168.1.5, 192.168.1.0/24.")

    #Returns the argument parser with the parsed arguments to main.
    return verify_args(parser.parse_args())

def verify_args(arg_list):
    """Responsible for verifying various arguments to make sure they won't cause errors further down the line."""
    #Checks if the user wants verbose output.
    if arg_list.verbose:
        #If they do, this line modifies the logger to set the logging level to debug, which provides more output to the user.
        logging.getLogger().setLevel(logging.DEBUG)
    #Checks if the user wants quiet output.
    elif arg_list.quiet:
        #If they do, this line modifies the logger to set the logging level to warning, so only warning and critical messages will show up.
        logging.getLogger().setLevel(logging.WARNING)
    logging.debug("Verifying Arguments")
    #After calling various functions that verify that ports and ips are formatted correctly, this will send back all of the arguments in one line.
    return arg_list, verify_ips(arg_list.IPs), verify_ports(arg_list.mass_ports)

def verify_ips(to_verify):
    """Responsible for verifying that IP addresses are formatted properly."""
    logging.debug("Verifying IPs")
    #Error catching in case the IPs are improperly formatted.
    try:
        #A list that will hold all IP addresses.
        addresses = []
        #More error catching.
        try:
            #Tries to interpret the user input as a file and open it.  If it fails it will error out and assume the user has instead sent in a list of IPs directly.
            with open(to_verify) as file:
                #If it works, the ips will be read from the file and put into a list.
                lines = file.read().splitlines()
        #If the file read errors out, this will split the line by commas.  Placing the results into a list.
        except FileNotFoundError:
            lines = to_verify.split(",")

        #Loops through each item int he list created above.
        for i in lines:
            #Checks to see if the item is using CIDR addressing.
            if "/" in i:
                #If it is, it will verify that the formatting is correct (IPNetwork(i) will error out and get caught by the except lower down if the format is incorrect),
                #and then will use the IPNetwork thing from the netaddr module imported earlier to parse out all the IPs in that range of ips and place them into the addresses list.
                for j in IPNetwork(i):
                    #The str is necessary because otherwise it will include data structure stuff that we don't want.
                    addresses.append(str(j))
            #If instead there is a -, that indicates that the user supplied a range of IP addresses.
            elif "-" in i:
                #This splits the values at the -.
                ip_range = i.split('-')
                #This line will use the iter_iprange function from the netaddr module and will create an iterable using the two IPs made by splitting above.
                #This will error out if either of the supplied IPs end up being invalid for whatever reason.
                for i in list(iter_iprange(ip_range[0], ip_range[1])):
                    #Again, the str part is necessary to ensure that the value doesn't include data structure information.
                    addresses.append(str(i))
            #Lastly, if it doesn't include a / or -, it must just simply be a single IP address.
            else:
                #This will attempt to convert the string into an IPAddress using netaddr's IPAddress function which will error out if the format is incorrect.
                addresses.append(str(IPAddress(i)))
        logging.debug("Finished Verifying IPs")

        logging.debug("Setting Up Directories")
        make_dirs()
        logging.debug("Finished Setting Up Directories")

        #This calls the write_ips function from below that's responsible for writing the IPs to a file for masscan to use.
        write_ips(addresses)
        #Returns the list of addresses.
        return addresses

    #Catches errors that indicate there was some sort of formatting issue.
    except AddrFormatError as err:
        logging.critical("Error with verifying IPs. Exiting Program.\nError: %s" % err)
        exit()

def verify_ports(to_verify):
    """Will attempt to verify the ports selected by the user."""
    logging.debug("Verifying Ports")
    #A string that will hold the ports.
    ports = ""
    #Loops through the values retrieved after splitting the user input by ,.
    for i in to_verify.split(","):
        #Checks to see if it is a range of ports.
        if "-" in i:
            #Will verify that each of the ports supplied are valid by calling check_ports.
            for j in i.split("-"):
                check_ports(j)
            #Adds the port range to the ports string.
            ports += "%s," % i
        #Otherwise it will be just a singular port.  This will call the check_ports function which will error out if it is invalid.
        elif check_ports(i):
            #Adds the port to the ports string.
            ports += "%s," % i
    logging.debug("Finished Verifying Ports")
    #Returns the ports, the -1 is to make sure the last comma is excluded from the string when its returned.
    return ports[:-1]

def check_ports(to_check):
    """Checks ports to ensure they are within acceptable values."""
    #Error catching.
    try:
        #Checks to see if the port supplied is between 1 and 65535.  Will error out and exit if it is not.
        if not 1 <= int(to_check) <= 65535:
            logging.crticial("Error with verifying ports. Exiting Program.\nError: Port values must be between 1 and 65535.")
            exit()
        #Otherwise it returns True.
        else:
            return True

    #Error catching indicating that the user did not provide valid numbers.
    except ValueError as err:
        logging.critical("Error with verifying ports. Exiting Program.\nError: %s" % err)
        exit()

def make_dirs():
    to_make = ["./results", "./results/masscan", "./results/nmap"]
    for i in to_make:
        if not path.exists(i):
            logging.debug("Making %s Directory" % i)
            makedirs(i)
        else:
            logging.debug("Directory %s Already Exists - Skipping" % i)
    
def write_ips(addresses):
    """Writes provided ips to a file for use by masscan."""
    #Checks if the file exists already.  If it does it deletes it.
    if path.isfile("./results/masscan/mass_ips.txt"):
        remove("./results/masscan/mass_ips.txt")
    #Otherwise it will open the file, write all lines to it, then close it.
    with open("./results/masscan/mass_ips.txt", "w") as file:
        for i in addresses:
            file.write("%s\n" % i)

def get_formats(args):
    """Will get the formats for all scanners used in this program from a json file located in ./deps/formats.json."""
    logging.debug("Importing Formats",)
    #A dictionary that will hold all loaded formats.
    formats = {}
    #Opens the ./deps/formats.json file in read only mode.
    with open("./deps/formats.json", "r") as file:
        #Uses the json module to laod the json data directly into a json object that we can then sort through.
        data = json.load(file)
        #Loops through the "scanners", a list within the json object that contains the formats for all of the scanners.
        for i in data["scanners"]:
            #Gets the name of the scanner.
            scanner = i["scanner"]
            logging.debug("Importing %s Format" % scanner)
            #Adds the scanner to the formats dictionary after calling the add_scanner function.
            formats[scanner] = add_scanner(i)
            logging.debug("Finished Importing %s Format" % scanner)
    #Calls the format_mass function which will format the format to the proper format WHEEE
    logging.debug("Formatting Masscan With Arguments")
    formats['masscan'] = format_mass(formats['masscan'], args)
    logging.debug("Finished Formatting Masscan With Arguments")
    logging.debug("Finished Importing Formats")
    #Returns the formats dictionary.
    return formats

def add_scanner(scanner_to_add):
    """Interprets a scanner dictionary and converts it to a string that we can further modify later."""
    #Sets up a string to hold our data.
    formatted_scanner = ""
    #Pops of the scanner value because we don't need it.
    scanner_to_add.pop('scanner')
    #Loops through the keys of the scanner dictionary
    for i in scanner_to_add.keys():
        #Adds the values associated with each key to the formatted_scanner string.
        formatted_scanner += "%s " % scanner_to_add[i]
    #Returns the formatted string.
    return formatted_scanner[:-1]

def format_mass(to_format, args):
    """Will format the format with the user provided and/or default options."""
    return to_format % (args.mass_ports, "./results/masscan/mass_ips.txt", args.mass_rate, "./results/masscan/mass_results_" + time.strftime("%Y:%m:%d-%H:%M"))





