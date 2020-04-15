import logging
import urllib3
from subprocess import Popen, PIPE, DEVNULL, run
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def take_screenshots(list):
    """Responsible for taking screenshots of discovered webpages."""
    logging.debug("Setting up Screenshot Options")
    #Sets up an options variable that we can modify.
    driver_options = Options()
    #Makes sure that selenium runs headless.
    driver_options.headless = True
    #Sets up the selenium webdriver.
    driver = webdriver.Firefox(executable_path="./deps/geckodriver", options=driver_options)
    logging.debug("Finished Setting up Screenshot Options")

    for i in list:
        try:
            logging.debug("Taking Screenshot of %s" % i)
            #Tells the driver to go to the specified webpage.
            driver.get("http://%s" % i)
            #Takes a screenshot of the discovered webpage.
            driver.save_screenshot("./results/nmap_http/screenshots/%s.png" % i)
            logging.debug("Finished Taking Screenshot of %s" % i)
        except Exception as error:
            logging.warning("Issue with taking screenshot of %s.\nError: %s" % (i, error))
            pass
    #Closes the driver.
    driver.close()

def pull_html(list):
    """Pulls the html source code from discovered web page."""
    #Sets up urllib to start the pulls.
    http = urllib3.PoolManager()

    #Loops through the list of web pages.
    for i in list:
        try:
            #Uses GET to get the web page.
            response = http.request('GET', "http://%s" % i)
            #Saves the html to a file.
            with open("./results/nmap_http/html/%s.html" % i, "wb") as file:
                file.write(response.data)

        except Exception as error:
            logging.warning("Issue with pulling HTML of %s.\nError: %s" % (i, error))

def run_gobuster(list, wordlist):
    """Runs gobuster against discovered web pages."""
    #TODO Add this to formats.json.
    #Sets up a list that will hold our formatted html.
    full_output = ['<h1 align="center">Gobuster Output</h1>']
    #Loops through each webpage.
    for i in list:
        try:
            logging.debug("Running Gobuster on %s" % i)
            #Sets up the gobuster command.
            cmd = "gobuster dir -u http://%s -w %s -q -e -t 5" % (i, wordlist)
            #Appends more data to our formatted html data.
            full_output.append('<h2>Results for <a href="http://%s">http://%s</a></h2>' % (i, i))
            #Runs gobuster.
            process = Popen([i for i in cmd.split(" ")], stdout=PIPE)
            #Adds the gobuster output to the file.
            full_output.extend([i for i in process.communicate()[0].decode(encoding="utf-8").split("\n")])
            logging.debug("Finished Running Gobuster on %s" % i)
        except Exception as error:
            logging.warning("Failed to complete gobuster scan against %s.\nError: %s" % (i, error))

    logging.debug("Formatting Gobuster Output")
    #Removes empty values from our list.
    while "" in full_output:
        full_output.remove("")
    #Formats the rest of the output into html links.
    for i in range(len(full_output)):
        if "<" not in full_output[i]:
            full_output[i] = '<p><a href="%s">%s</a></p>' % (full_output[i][0:full_output[i].index(" ")], full_output[i][0:full_output[i].index(" ")])
    logging.debug("Finished Formatting Gobuster Output")

    logging.debug("Writing Formatted Gobuster Output to File")
    #Writes the output to a file.
    with open("./results/nmap_http/gobuster/latest_gobuster.html", "w") as file:
        for i in full_output:
            file.write("%s\n" % i)
    logging.debug("Finished Writing Formatted Gobuster Output to File")

def run_nikto(list):
    """Runs nikto on the discovered web pages."""
    for i in list:
        try:
            logging.debug("Running Nikto on %s" % i)
            #Sets up the nikto command.
            cmd = "nikto -nointeractive -output ./results/nmap_http/nikto/nikto_%s.html -Format htm -host http://%s" % (i,i)
            #Runs the nikto command.
            run([i for i in cmd.split(" ")], stdout=DEVNULL)
            logging.debug("Finished Running Nikto on %s" % i)
        except Exception as error:
            logging.warning("Error when running Nikto on %s.\nError: %s" % (i, error))
        


    

