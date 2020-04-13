import logging, time, threading, subprocess
from os import getcwd, listdir
from tqdm import tqdm
from libnmap.process import NmapProcess as nmap
from libnmap.parser import NmapParser as nmap_parser
from multiprocessing import Pool, Manager
from functools import partial
from user_functions import bcolors
from extras import take_screenshots, pull_html, run_gobuster

def start_nmap(nmap_format, extra_nmap_format, mass_data, args):
    """Used to set up multithreading and call the individual masscan processes."""
    try:
        #Sets up a threadpool with user-entered threads value.
        pool = Pool(args.nmap_threads)
        manager = Manager()
        shared_list = manager.list()
        #Sets up the progress bar.  Pretty complicated, worth googling.
        pbar = tqdm(pool.imap_unordered(partial(nmap_runner, nmap_format, extra_nmap_format, args.no_extra_scans, shared_list), mass_data), total=len(mass_data), desc=bcolors.OKGREEN + "Nmap Progressbar" + bcolors.ENDC)
        for _ in pbar:
            pass

        #Terminates the threadpool and joins the threads back to the main process.
        pool.terminate()
        pool.join()
        #Terminates the progresbar.
        pbar.close()

        conv_to_html()
        logging.info("Finished Nmap")
 
    except Exception as error:
        logging.critical("Error when trying to run Nmap.\nError: %s" % error)

    if args.screenshot:
        try:
            logging.info("Taking Screenshots")
            take_screenshots(shared_list)
            logging.info("Finished Taking Screenshots") 

        except Exception as error:
            logging.critical("Error when trying to take screenshots.\nError: %s" % error)

    if args.page_pulls:
        try:
            logging.info("Pulling HTML")
            pull_html(shared_list)
            logging.info("Finished Pulling HTML")
        
        except Exception as error:
            logging.critical("Error when trying to pull HTML.\nError: %s" % error)

    if args.gobuster:
        try:
            logging.info("Running Gobuster")
            run_gobuster(shared_list, args.gobuster)
            logging.info("Finished Running Gobuster")

        except Exception as error:
            logging.critical("Error when trying to run Gobuster.\nError: %s" % error)


def nmap_runner(nmap_format, extra_nmap_format, no_extra_scans, shared_list, ip_port):
    """Runs the actual nmap scans."""
    ip,port = ip_port.split(":")
    #Calls the libnmap modules nmapprocess and runs it.
    nm_process = nmap(targets=ip, options=format_nmap(nmap_format, port), safe_mode=False)
    #Makes sure the process runs in the background.
    nm_process.run_background()

    while nm_process.is_running():
        time.sleep(2)

    #Gets the output of the scan.
    scan_out = nm_process.stdout
    #If the scan includes the text "state="filtered"" or "tcpwrapped" that indicates that the port is firewalled off and theres no point in keeping it.
    if 'state="filtered"' in scan_out or 'tcpwrapped' in scan_out:
        #TODO:  Change that filtered/tcpwrapped will still have output.  Need to check for this but don't have the data to set up the code right now.
        pass

    else:
        file_name = "./results/nmap/nmap_reg_%s_%s_" % (ip, port) + time.strftime("%Y:%m:%d-%H:%M") + ".xml"
        #Writes the output of the original scan to a file.
        with open(file_name, "w") as file:
            file.write(scan_out)

        if 'portid="80"' in scan_out or 'service name="http"' in scan_out:
            shared_list.append("%s:%s" % (ip, port))

        #Will only run if the user didn't specify that they didn't want extra scans to be run.
        if not no_extra_scans:
            output = ""
            #Checks for ftp-anonymous login.
            if 'portid="21"' in scan_out or 'service name="ftp"' in scan_out:
                output = extra_nmap_runner(extra_nmap_format, "ftp-anon", ip, port)
            #Checks for world-readable/writeable nfs mounts.
            elif 'portid="111"' in scan_out or 'service name"rpcbind' in scan_out:
                output = extra_nmap_runner(extra_nmap_format, "nfs-showmount", ip, port)

            #Will only write to the file if there is data in the output variable.
            if output:
                with open(file_name.replace("reg", "xtra"), "w") as file:
                    file.write(output)


def extra_nmap_runner(extra_nmap_format, script_name, ip, port):
    """Runs the extra nmap scans.  See above."""
    xtra_process = nmap(targets=ip, options=format_extra(extra_nmap_format, script_name, port), safe_mode=False)
    xtra_process.run_background()

    while xtra_process.is_running():
        time.sleep(2)
    
    return xtra_process.stdout

def format_nmap(nmap_format, port):
    """Formats the nmap command to include the port."""
    return nmap_format % port

def format_extra(extra_nmap_format, script, port):
    """Formats the extra nmap command to include the script and port."""
    return extra_nmap_format % (port, script) 

def conv_to_html():
    """Converts the nmap xml files to html files viewable in a web browser."""
    logging.debug("Converting XML Files to HTML")
    html_dir = getcwd() + "/results/nmap_http/"
    nmap_dir = getcwd() + "/results/nmap/"

    files = listdir(nmap_dir)
    for i in files:
        command = ["xsltproc", nmap_dir + i, "-o", html_dir + i[0:len(i)-3] + "html"]
        subprocess.run(command)
    logging.debug("Done Converting XML Files to HTML")