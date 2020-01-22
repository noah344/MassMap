from os import system, path, getcwd
from netaddr import IPNetwork, iter_iprange, IPAddress

def clear():
    system("clear")
    
def get_ips():
    default = "%s/ips.txt" % getcwd()
    print("Provide the location of an ip file or provide a comma-seperated list of IPs.")
    choice = input(("The default points to %s: " % default))
    if not choice:
        choice = default
    return verify_ips(choice)
    

def verify_ips(to_verify):
    try:
        addresses = []
        if path.isfile(to_verify):
            with open(to_verify) as file:
                lines = file.read().splitlines()
        else:
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
    
        return addresses
    except:
        print("FAIL")