import logging, time
from libnmap.process import NmapProcess as nmap

def start_nmap(nmap_format, mass_data):
    try:
        for i in mass_data:
            for j in mass_data[i]:
                nmap_runner(nmap_format, i, j)

    except Exception as error:
        logging.critical("Error when trying to run Nmap.\nError: %s" % error)

def nmap_runner(nmap_format, ip, port):
    nm_process = nmap(targets=ip, options=format_nmap(nmap_format, ip, port), safe_mode=False)
    nm_process.run_background()
    while nm_process.is_running():
        logging.debug("Nmap Scan Still Running: ETC: {0} DONE: {1}%".format(nm_process.etc, nm_process.progress))
        time.sleep(2)
    print(nm_process.rc)
    print(nm_process.state)

def format_nmap(nmap_format, ip, port):
    file_name = "./results/nmap/nmap_reg_%s_%s_" % (ip, port)
    file_name += time.strftime("%Y:%m:%d-%H:%M")
    nmap_opts = nmap_format % (port, file_name)
    return nmap_opts