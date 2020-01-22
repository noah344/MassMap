import logging, argparse
from os import system, path, getcwd
from netaddr import IPNetwork, iter_iprange, IPAddress
from netaddr.core import AddrFormatError

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_args():
    parser = argparse.ArgumentParser(description="Scans a set of IPs quickly and provides detailed output using nmap and masscan.")
    verbosity = parser.add_mutually_exclusive_group()
    mass_args = parser.add_argument_group("Masscan Arguments")
    req_args = parser.add_argument_group("Required Arguments")

    verbosity.add_argument("-v", "--verbose", action="store_true", help="Increases verbosity of the program.", default=False, required=False)
    verbosity.add_argument("-q", "--quiet", action="store_true", help="Decreases the verbosity of the program.", default=False, required=False)
    
    mass_args.add_argument("-r", "--mass_rate", type=int, help="Tells masscan the packet rate you wish for it to use. Default is 20000.", default=20000, required=False)
    mass_args.add_argument("-p", "--mass_ports", type=str, help="Tells masscan what ports you wish for it to scan. Default is 1-65535.", default="1-65535", required=False)

    req_args.add_argument("IPs", type=str, help="Provide the full location of an IP file or a comma seperated list of IPs. Can be formatted in any of the following ways: \
        192.168.1.1, 192.168.1.2-192.168.1.5, 192.168.1.0/24.")

    return verify_args(parser.parse_args())

def verify_args(arg_list):
    if arg_list.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif arg_list.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    logging.info("Verifying Arguments")
    return arg_list, verify_ips(arg_list.IPs), verify_ports(arg_list.mass_ports)

def verify_ips(to_verify):
    try:
        addresses = []
        try:
            with open(to_verify) as file:
                lines = file.read().splitlines()
        except FileNotFoundError:
            lines = to_verify.replace(" ","").split(",")

        for i in lines:
            if "/" in i:
                for j in IPNetwork(i):
                    addresses.append(str(j))
            elif "-" in i:
                ip_range = i.split('-')
                for i in list(iter_iprange(ip_range[0], ip_range[1])):
                    addresses.append(str(i))
            else:
                addresses.append(str(IPAddress(i)))
        logging.debug("IPs Verfied")
        return addresses

    except AddrFormatError as err:
        logging.critical("Error with verifying IPs. Exiting Program.\nError: %s" % err)
        exit()

def verify_ports(to_verify):
    try:
        ports = ""
        for i in to_verify.split(","):
            if "-" in i:
                for j in i.split("-"):
                    int(j)
                ports += "%s," % i
            elif int(i):
                ports += "%s," % i
        logging.debug("Ports Verified")
        return ports[:-1]

    except ValueError as err:
        logging.critical("Error with verifying ports. Exiting Program.\nError: %s" % err)
        exit()