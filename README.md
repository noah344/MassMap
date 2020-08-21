# MassMap
## Description
A tool that combines the comprehensive scanning capabilities of Nmap with the speed of masscan.  This tool is designed to provide fast and accurate port and vulnerability scanning data for large networks (think thousands to tens of thousands of IPs).

## Motivation
This project was created initially in an environment which I no longer have access to.  Having worked for several months on the project, I chose to create a new open-source version from scratch with various improvements.  The beginning goal of this project was to provide data similar to what can be found on shodan.io, but for IP's not accessible directly from the Internet (i.e. Internal private network IP addresses).  

More or less, the project was meant to be able to quickly find devices with critical unpatched vulnerabilities on extremely large networks to help provide a high-level overview of the overall security of the network.  Vulnerabilities such as ms17-010 demonstrated how essential it is for every single machine on a network to be patched, and this tool can help with that.

As I continued development however, the purpose of the tool somewhat split.  On one hand, system/network administrators can use the tool to discover critical vulnerabilities lurking on their network, and patch them.  On the other, those conducting penetration tests can use this tool to massively cut down on the scanning phase of the tests, allowing them more time to attempt to exploit discovered vulnerabilities and ultimately providing customers witha  more comprehensive and useful penetration test report.

With the split in goals came two major design decisions.  Those less tech-savvy would likely want a GUI environment to not only setup the scans but also to view the results of the scans.  So far I have implemented a GUI to run the scan.  The second major design decision was to make the tool more of a suite of tools combining many useful penetration tools into one.  Currently MassMap combines not only masscan and nmap, but also web vulnerability scanning tools such as nikto and gobuster.  Eventually I would like to add more capabilities.

Whew, that was a little long-winded.  Sorry about that, who cares about that nonsense, let's get into the nitty gritty.

## Technical Details

MassMap is now meant to be a framework that will provide an automated method of scanning large networks with a variety of tools.

To begin the explanation, let's start with what exactly a vulnerabilty/port scanner is.

### Port Scanners
All networked computers have ports, 65,536 to be exact.  Applications on your computer use these ports to communicate across the Internet.  Typically ports start off as closed meaning that data cannot pass through them, afterall more open ports means more potential attack vectors for a malicious actor.  For example, when connecting to a website over the Internet, you are actually connecting to a computer's port via your browser.  The standard web port without security is port 80.  There are a number of "well known" ports throughout the range of 65,536, but I won't go into detail about that here.

Port scanners are simply tools that are able to check whether or not individual ports are open or closed.  Below is a sample of results from a scanner called Nmap, pulled from the website of nixCraft.

![Nmap Results Example](https://www.cyberciti.biz/media/new/cms/2012/11/Practical-Examples-of-NMAP-Commands-for-Linux-System.png)

We can see above that Nmap managed to find a total of four open ports.  22, 53, 80, and 443.  We can also see what service is likely running on those ports, ssh, domain, http, and https.

Based on these results a penetration tester can determine that the device is likely a web server due to port 80 (http) and port 443 (https) being open.  With this information the pentester can navigate to the website and potentially exploit a vulnerability there.

I won't get into the more technical aspects about how these scanners work, but more or less they send out data in the form of packets over the network.  These packets eventually return with information about the status of the ports.

### Scanners Used in MassMap

#### Masscan
Masscan, though not as well known as some other scanners, is an amazing feat of programming that essentially has created the fastest port scanner available.  The github page for it can be found [here](https://github.com/robertdavidgraham/masscan).

This scanner spews out packets at an extremely fast rate which, in theory, will provide you with port scan results much faster.  In the end this scanner is only limited by the hardware running it and, if not configured properly, will flood the network its running on with data and cause some major issues.  By design, this scanner simply provides information about the open/closed status of the port with no additional information.  Other scanners provide much more useful data, but none provide data as quickly as masscan.

#### Nmap
Nmap has essentially become synonymous with vulnerability/port scanning.  It is the de-facto tool used by penetration testers and system administrators around the world.  The github page for nmap can be found [here](https://github.com/nmap/nmap) and the official nmap website can be found [here](nmap.org).

Nmap not only provides open/closed results similar to masscan, but it also provides extensive application and version detection capabilities.  Instead of just saying that a port is open, masscan can provide you with what service is running on a specific port, and the particular version of the service.  This information is invaluable when doing a penetration test and helps to prioritize where efforts should be primarily made.  An older version of a program may have more vulnerabilities than an older version for instance.

On top of all of this, nmap possesses a powerful scripting engine called NSE.  NSE essentially is used to provide even more extensive data about individual processes as well as information about the device itself.  Some such scripts can be used to immediately verify whether or not a specific service running on a specific port is vulnerable to a specific exploit.

The major downside of Nmap is that, to get a truly comprehensive scan you need to scan every single port with service and version detection scans enabled.  On smaller networks these scans aren't a huge deal, typically taking an hour or two.  On larger networks however, ones consisting of thousands to tens of thousands of devices, nmap struggles and can take days to scan everything.

### MassMap = Nmap + Masscan
As stated previously, the primary goal of this project is to combine the speed of masscan with the capabilities of Nmap to provide detailed scan results as quickly as possible.  Let's explain this with an example.

You need to a scan a single device for vulnerabilities.  You know nothing about this device other than the fact that there should be some open ports.  You run nmap against all 65,535 ports with nse scripts, service detection, and version detection against the host.  The scan takes roughly 30 minutes and discovers 3 open ports.

Now, instead of running Nmap first, lets use MassMap.  You configure MassMap to scan all ports on the device, with nse scripts enabled, service detection, and version detection.  The IP is fed directly into Massmap which tells you that there are three open ports on the device within 30 seconds.  Now we send those ports over to nmap.  Nmap now only has to scan 3 ports rather than all 65,535.  Nmap now finishes its scans in 3 minutes essentially providing the exact same results in roughly 3.5 minutes.

Though this example isn't exact by any means, it illustrates what MassMap can do in large scale networks.

## Installation
All of this needs to be tested on other distros.  Should work properly on debian and CentOS.
Pip modules will be installed when running the setup.py file.  Nmap and masscan need to be installed manually.  
As of right now this project only works on Linux (as far as I know, I havn't tested it on Windows).  Below are the dependencies:

CLI
- Python 3: Program is written in Python 3.
- Nmap 7.80: The standard version installed appears to be 7.70, need to figure out easiest process for getting 7.80.  Comprehensive scanner.

CentOS 8<br/>
wget https://nmap.org/dist/nmap-7.80-1.x86_64.rpm<br/>
rpm -ivh --nodeps ./nmap-7.80-1.x86_64.rpm<br/>

- Masscan 1.05:  Fast scanner.
- python-libnmap Pip Module:  Used to run nmap scans directly from python.
- selenium Pip Module:  Web testing.
- tqdm Pip Module:  Progressbar.
- gobuster:  Web directory bruteforcing.
- nikto:  Web vulnerability detection.

GUI
All of the above and:
- pyqt5 Pip module:  GUI programmed using pyqt5 framework.
- qdarkstyle:  Darker version of pyqt5.

# WILL ADD MORE AS TIME GOES ON BLAH BLAH
