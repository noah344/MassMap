import logging
import urllib3
from subprocess import Popen, PIPE
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def take_screenshots(list):
    logging.debug("Setting up Screenshot Options")
    driver_options = Options()
    driver_options.headless = True
    driver = webdriver.Firefox(executable_path="./deps/geckodriver", firefox_options=driver_options)
    logging.debug("Finished Setting up Screenshot Options")

    for i in list:
        try:
            logging.debug("Taking Screenshot of %s" % i)
            driver.get("http://%s" % i)
            driver.save_screenshot("./results/nmap_http/screenshots/%s.png" % i)
            logging.debug("Finished Taking Screenshot of %s" % i)
        except Exception as error:
            logging.warning("Issue with taking screenshot of %s.\nError: %s" % (i, error))
            pass
    
    driver.close()

def pull_html(list):
    http = urllib3.PoolManager()

    for i in list:
        try:
            response = http.request('GET', "http://%s" % i)
            with open("./results/nmap_http/html/%s.html" % i, "wb") as file:
                file.write(response.data)

        except Exception as error:
            logging.warning("Issue with pulling HTML of %s.\nError: %s" % (i, error))

def run_gobuster(list, wordlist):
    #TODO Add this to formats.json.
    full_output = ['<h1 align="center">Gobuster Output</h1>']
    for i in list:
        try:
            logging.debug("Running Gobuster on %s" % i)
            cmd = "gobuster dir -u http://%s -w %s -q -e -t 5" % (i, wordlist)
            full_output.append('<h2>Results for <a href="http://%s">http://%s</a></h2>' % (i, i))
            process = Popen([i for i in cmd.split(" ")], stdout=PIPE)
            full_output.extend([i for i in process.communicate()[0].decode(encoding="utf-8").split("\n")])
            logging.debug("Finished Running Gobuster on %s" % i)
        except Exception as error:
            logging.warning("Failed to complete gobuster scan against %s.\nError: %s" % (i, error))
    logging.debug("Formatting Gobuster Output")
    while "" in full_output:
        full_output.remove("")
    for i in range(len(full_output)):
        if "<" not in full_output[i]:
            full_output[i] = '<p><a href="%s">%s</a></p>' % (full_output[i][0:full_output[i].index(" ")], full_output[i][0:full_output[i].index(" ")])
    logging.debug("Finished Formatting Gobuster Output")

    logging.debug("Writing Formatted Gobuster Output to File")
    with open("./results/nmap_http/gobuster/latest_gobuster.html", "w") as file:
        for i in full_output:
            file.write("%s\n" % i)
    logging.debug("Finished Writing Formatted Gobuster Output to File")

    
    

