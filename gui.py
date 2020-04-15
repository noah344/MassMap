#!/usr/bin/env python3

import sys
from subprocess import run, DEVNULL
from os import getcwd, path
import qdarkstyle
from PyQt5 import QtWidgets
from netaddr import IPNetwork, iter_iprange, IPAddress
from netaddr.core import AddrFormatError

from PyQt5.QtWidgets import (QApplication as app, QLabel as label, QWidget as widget,
    QGridLayout as grid_layout, QCheckBox as checkbox, QComboBox as combobox, QGroupBox as groupbox,
    QLineEdit as textbox, QToolTip as tooltip, QFileDialog as filedialog, QPushButton as button, QDesktopWidget)
from PyQt5.QtGui import (QFont as font, QDesktopServices)
from PyQt5.QtCore import QUrl, Qt

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setup_main_window()
        self.set_window_layout()
    
    def setup_main_window(self):
        qtRectangle = self.frameGeometry()
        centerpoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerpoint)
        self.move(qtRectangle.topLeft())
            
        self.setFixedSize(800,470)
        self.centralwidget = widget()
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle("MassMap")
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

    def set_window_layout(self):
        self.layout = grid_layout()
        self.centralwidget.setLayout(self.layout)

        #Labels
        self.ip_label = self.setup_label("IPs to Scan:", self.layout, 0, 0, "Start by selecting either IP File or List of IPs.\nThen either enter a comma-separated list of IPs \n(i.e. x.x.x.x, x.x.x.x-x.x.x.x, x.x.x.x/24),\nor use the file dialog box to select a file with IPs in it.")
        self.verbosity_label = self.setup_label("Set Verbosity", self.layout, 1, 2, "Verbose Output will provide the most information.\nInfo Output will only output informational data.\nQuiet Output will quiet most of the output.")
        self.verbosity_label.setAlignment(Qt.AlignCenter)
        self.ports_label = self.setup_label("Ports to Scan:", self.layout, 1, 0, "Select ports to scan through for each selected host.\ni.e. 1-100, 120, 300")
        self.rate_label = self.setup_label("Masscan Rate:", self.layout, 2, 0, "Select the rate that you want to run the\nscan at, be carefule with your choice.")
        self.threads_label = self.setup_label("Nmap Threads:", self.layout, 3, 0, "Select the number of threads you want nmap to use.")
        self.extra_label = self.setup_label("Do Extra Scans?", self.layout, 4, 0, "Select this if you want to run NSE\nscript scans against detected ports.")
        self.sshot_label = self.setup_label("Take Screenshots?", self.layout, 5, 0, "Select this if you want to take screenshots\nof discovered http web pages.")
        self.ppull_label = self.setup_label("Pull HTML?", self.layout, 6, 0, "Select this if you want to pull down web page raw\nhtml data for offline analysis.")
        self.gobust_label = self.setup_label("Run Gobuster?", self.layout, 7, 0, "Select this if you want to run gobuster against\ndetected http web pages.")
        self.nikto_label = self.setup_label("Run Nikto?", self.layout, 8, 0, "Select this if you want to run nikto against\ndetected http web pages.")
        self.error_label = self.setup_label("ERROR", self.layout, 9, 0)
        self.error_label.setStyleSheet("color: red;")
        self.error_label.hide()
        self.results_label = self.setup_label('<a href="file:///root/Desktop/MassMap/results/html/">View Results</a>', self.layout, 10, 0)
        self.results_label.linkActivated.connect(self.results_clicked)
        self.results_label.hide()

        #Checkboxes
        self.extra_scans_chk = self.setup_checkbox(self.layout, 4, 1, True)
        self.take_sshot_chk = self.setup_checkbox(self.layout, 5, 1, True)
        self.page_pulls_chk = self.setup_checkbox(self.layout, 6, 1, True)
        self.run_gobust_chk = self.setup_checkbox(self.layout, 7, 1, True)
        self.run_nikto_chk = self.setup_checkbox(self.layout, 8, 1, True)

        #Comboboxes
        self.type_of_ips_combo = self.setup_combo(["List of IPs", "IP File"], self.layout, 0, 1)
        self.type_of_ips_combo.currentTextChanged.connect(self.ip_combo_changed)
        self.verbosity_combo = self.setup_combo(["Verbose", "Info", "Quiet"], self.layout, 2, 2)
        self.gob_wordlist_combo = self.setup_combo(["/dirb/common.txt", "/dirb/small.txt", "/dirb/big.txt", "/dirbuster/directory-list-2.3-small.txt", "/dirbuster/directory-list-2.3-medium.txt"], self.layout, 7, 2)

        #Textboxes
        self.ports_textbox = self.setup_textbox("1-65535", self.layout, 1, 1)
        self.rate_textbox = self.setup_textbox("100000", self.layout, 2, 1)
        self.ips_textbox = self.setup_textbox("", self.layout, 0, 2)
        self.threads_textbox = self.setup_textbox("20", self.layout, 3, 1)

        #Buttons
        self.file_button = self.setup_button("Select\nFile", self.layout, 0, 4)
        self.file_button.setFont(font("Arial", 15))
        self.file_button.hide()
        self.file_button.clicked.connect(self.select_file)

        self.done_button = self.setup_button("Start Scan", self.layout, 9, 1)
        self.done_button.clicked.connect(self.check_opts)

        self.exit_button = self.setup_button("Exit", self.layout, 9, 2)
        self.exit_button.clicked.connect(exit)

    def setup_label(self, text, layout, row, column, *tooltip):
        tmp = label(text)
        if tooltip:
            tmp.setToolTip(tooltip[0])
        self.add_to_layout(layout, tmp, row, column)
        return tmp

    def setup_checkbox(self, layout, row, column, checked):
        tmp = checkbox()
        self.add_to_layout(layout, tmp, row, column)
        tmp.setChecked(checked)
        return tmp

    def setup_combo(self, items, layout, row, column):
        tmp = combobox()
        tmp.addItems(items)
        self.add_to_layout(layout, tmp, row, column)
        return tmp

    def setup_textbox(self, text, layout, row, column):
        tmp = textbox()
        tmp.setText(text)
        self.add_to_layout(layout, tmp, row, column)
        return tmp

    def setup_button(self, text, layout, row, column):
        tmp = button(text)
        self.add_to_layout(layout, tmp, row, column)
        return tmp

    def add_to_layout(self, layout, widget, row, column):
        layout.addWidget(widget, row, column)

    def ip_combo_changed(self):
        if str(self.type_of_ips_combo.currentText()) == "IP File":
            self.file_button.show()
        else:
            self.file_button.hide()
            self.ips_textbox.setText("")

    def select_file(self):
        self.select_file_diag = filedialog().getOpenFileName(self, 'Select IP File', getcwd(), "Text files (*.txt)")
        self.ips_textbox.setText(self.select_file_diag[0])
        return(self.select_file_diag[0])

    def check_opts(self):
        valid_ports = self.verify_ports(self.ports_textbox.text())
        valid_ips = self.verify_ips(self.ips_textbox.text())
        valid_threads = self.verify_ips(self.threads_textbox.text())
        valid_rate = self.verify_ips(self.rate_textbox.text())
        
        if not valid_ports:
            self.ports_textbox.setStyleSheet("background-color: red;")
            self.error_label.show()
        else:
            self.ports_textbox.setStyleSheet("background-color: #19232D;")
        
        if not valid_ips:
            self.ips_textbox.setStyleSheet("background-color: red;")
            self.error_label.show()
        else:
            self.ips_textbox.setStyleSheet("background-color: #19232D;")

        if not valid_threads:
            self.threads_textbox.setStyleSheet("background-color: red;")
            self.error_label.show()
        else:
            self.threads_textbox.setStyleSheet("background-color: #19232D;")
        
        if not valid_rate:
            self.rate_textbox.setStyleSheet("background-color: red;")
            self.error_label.show()
        else:
            self.rate_textbox.setStyleSheet("background-color: #19232D;")

        if valid_ports and valid_ips and valid_threads and valid_rate:
            self.error_label.hide()
            self.start_it()

    def start_it(self):
        command = "./main.py %s -mR %s -mP %s" % (self.ips_textbox.text(), self.rate_textbox.text(), self.ports_textbox.text())
        if not self.extra_scans_chk.isChecked():
            command = command + " -nE"
        if self.take_sshot_chk.isChecked():
            command = command + " -sS"
        if self.page_pulls_chk.isChecked():
            command = command + " -pP"
        if self.run_gobust_chk.isChecked():
            command = command + " -gB /usr/share/wordlists%s" % self.gob_wordlist_combo.currentText()
        if self.run_nikto_chk.isChecked():
            command = command + " -rN"

        verbosity = self.verbosity_combo.currentText()
        if verbosity == "Verbose":
            command = command + " -v"
        elif verbosity == "Quiet":
            command = command + " -q" 
        
        run([i for i in command.split(' ')])
        self.results_label.show()

    def check_numb(self, to_verify):
        try:
            int(to_verify)
            return True
        except ValueError:
            return False

    def verify_ips(self, to_verify):
        try:
            addresses = []
            try:
                with open(to_verify) as file:
                    lines = file.read().splitlines()
            except FileNotFoundError:
                lines = to_verify.split(",")

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

            return True

        except AddrFormatError:
            return False

    def verify_ports(self, to_verify):
        ports = ""
        for i in to_verify.split(","):
            if "-" in i:
                for j in i.split("-"):
                    if not self.check_ports(j):
                        return False
                ports += "%s," % i
            elif self.check_ports(i):
                ports += "%s," % i
            else:
                return False
        return True

    def check_ports(self, to_check):
        try:
            if not 1 <= int(to_check) <= 65535:
                return False
            else:
                return True

        except ValueError:
            return False

    def results_clicked(self, linkStr):
        run(["sensible-browser", "--new-window", "file:///root/Desktop/MassMap/results/nmap_http/"], stdout=DEVNULL, stderr=DEVNULL)

if __name__ == '__main__':
    my_app = QtWidgets.QApplication([])
    bigger_font = font("Arial", 20, font.Bold)
    my_app.setFont(bigger_font)
    window = MainWindow()
    window.show()

    sys.exit(my_app.exec())