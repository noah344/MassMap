import logging, time, threading
from libnmap.process import NmapProcess as nmap
from multiprocessing import Pool
from functools import partial

def start_nmap(nmap_format, mass_data, args):
    """Used to set up multithreading and call the individual masscan processes."""
    try:
        #Sets up a threadpool with user-entered threads value. Then runs the scans from the pool.
        pool = Pool(args.nmap_threads)
        for _ in pool.imap_unordered(partial(nmap_runner, nmap_format), mass_data):
            pass

        if not args.no_extra_scans:
            print("Yay more scans!")

    except Exception as error:
        logging.critical("Error when trying to run Nmap.\nError: %s" % error)

def nmap_runner(nmap_format, ip_port):
    """Runs the actual nmap scans."""
    ip,port = ip_port.split(":")
    #Calls the libnmap modules nmapprocess and runs it.
    nm_process = nmap(targets=ip, options=format_nmap(nmap_format, ip, port), safe_mode=False)
    #Makes sure the process runs in the background.
    nm_process.run_background()
    while nm_process.is_running():
        time.sleep(2)

def format_nmap(nmap_format, ip, port):
    """Formats the nmap file and saves the data to it."""
    file_name = "./results/nmap/nmap_reg_%s_%s_" % (ip, port)
    file_name += time.strftime("%Y:%m:%d-%H:%M")
    nmap_opts = nmap_format % (port, file_name)
    return nmap_opts