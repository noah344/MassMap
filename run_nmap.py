import logging, time, threading
from tqdm import tqdm
from libnmap.process import NmapProcess as nmap
from libnmap.parser import NmapParser as nmap_parser
from multiprocessing import Pool
from functools import partial
from user_functions import bcolors

def start_nmap(nmap_format, extra_nmap_format, mass_data, args):
    """Used to set up multithreading and call the individual masscan processes."""
    try:
        #Sets up a threadpool with user-entered threads value.
        pool = Pool(args.nmap_threads)
        #Sets up the progress bar.  Pretty complicated, worth googling.
        pbar = tqdm(pool.imap_unordered(partial(nmap_runner, nmap_format, extra_nmap_format, args.no_extra_scans), mass_data), total=len(mass_data), desc=bcolors.OKGREEN + "Nmap Progressbar" + bcolors.ENDC)
        for _ in pbar:
            pass

        #Terminates the threadpool and joins the threads back to the main process.
        pool.terminate()
        pool.join()
        #Terminates the progresbar.
        pbar.close()
 
    except Exception as error:
        logging.critical("Error when trying to run Nmap.\nError: %s" % error)

def nmap_runner(nmap_format, extra_nmap_format, no_extra_scans, ip_port):
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