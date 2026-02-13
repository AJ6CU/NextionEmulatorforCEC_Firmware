#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import comportManagerui as baseui

import serial.tools.list_ports              # Used to get a list of com ports

from tkinter import messagebox

from time import sleep
import globalvars as gv
from configuration import configuration

import os
import ipaddress


#
# Manual user code
#

class comportManager(baseui.comportManagerUI):

    def __init__(self, master=None, actionCallback=None, **kw):
        super().__init__(master, **kw)
        self.master = master
        self.actionCallback = actionCallback


        self.open_com_port = None
        self.selectionMade = False

        self.radioPortType = "ComPort"          # Default to ComPort


        gv.formatCombobox(self.connectionType_Combobox, "Arial", "12", "bold")
        #
        #   Determine existing type of connection in config file
        #
        if len(gv.config.getRadioPort()) > 3:
            if gv.config.getRadioPort()[:3]=="soc":
                self.setRadioPortType('Socket')

            else:
                self.setRadioPortType( 'ComPort')

        else:
            self.setRadioPortType(self, self.radioPortType)

        self.radioConnectionType_VAR.set(self.radioPortType)




    #
    #   this is how we get things started. Main program asks for a comPort, make the callback if found, else report failure
    #
    def getRadioPort(self):

        #
        #   Lets try the easy way first. Hopefully the comport in the configuration file will just work!
        #
        #
        configPort = gv.config.getRadioPort()
        #
        #   Handle ComPort differently than Socket
        #
        if self.radioPortType == "ComPort":
            if self.validateComPort(configPort):                #test if config port exists in list of ports
                if self.forceUseOfThisComPort(configPort):       #force it and try to open, if good, then we can start main
                    self.actionCallback(configPort, self.getRadioPortHandle())
                    # self.actionCallback(self.getSelectedComPort(), self.getComPortDesc())
                    return True
            return False

        else:       # Need to validate IP/Port address
            if self.validateWiFiSocket(configPort):
                if (self.forceUseOfThisSocket(configPort)):  # force it and try to open, if good, then we can start main
                    self.actionCallback(configPort, self.getRadioPortHandle())
                    return True
            return False

    #
    #   If we don't get the comport the easy way, this routing is called every 500ms. If a selection has been made, it is checked
    #   and if valid, we kick off the main window. Else, just try again in 500ms
    #
    #
    #   need to change state on Test button to disabled while trying to open up an ip port. Turn it to enabled if failed
    #   maybe with an error message popup like below
    #
    def retry(self):
        if self.selectionMade:
            port = self.getSelectedComPort()
            #
            #   Eliminate the common error selection of an illegal port
            #   (Works for ComPort and Socket)
            #
            if port in ["/dev/cu.Bluetooth-Incoming-Port",
                                            "/dev/cu.debug-console"
                                            ]:
                    messagebox.showerror(title="ERROR Incorrect CompPort Selected.", parent=self,
                                         detail=self.getSelectedComPort() + "\nIs not a uBITX!")
                    self.selectionMade = False
            else:
                if self.openSelectedComPort(port):
                    self.actionCallback(port, self.getRadioPortHandle())
                    return
                else:
                    self.wifi_Port_Test_Button.configure(state="normal")
                    self.selectionMade = False
        self.master.after(500,self.retry)


    def validateComPort(self, port):
        #
        #   if it is valid, it will be on list of updated comports
        #
        if (port in self.comPortList):
            return True
        else:
            return False



    def validateWiFiSocket(self, ip_port_str):
        """
        Validates if a string is a valid IP address and port number combination.

        Args:
            ip_port_str: The string to validate (e.g., "socket://192.168.1.1:9000")

        Returns:
            A boolean, True if valid, False otherwise.
        """
        try:
            # 1. Split the string into IP and Port parts
            if ":" not in ip_port_str or len(ip_port_str) < 18:
                return False  # Format incorrect: missing colon separator or not long enough, minimum is "socket://1.1.1.1:1"
            socket_prefix = ip_port_str[:9]
            socket_suffix = ip_port_str[9:]

            if socket_prefix != "socket://":
                return False  # not valid parameter to pyserial
            parts = socket_suffix.split(":")
            if len(parts) != 2:
                return False  # Format incorrect: too many or too few colons

            ip_str, port_str = parts

            # 2. Validate the IP address using the ipaddress module
            # This handles both IPv4 and IPv6 and raises a ValueError if invalid
            try:
                ipaddress.ip_address(ip_str)
            except ValueError as e:
                return False  # Not a valid ip string
            # 3. Validate the port number
            # Port must be a number between 0 and 65535
            try:
                port_num = int(port_str)
                if not (0 <= port_num <= 65535):
                    return False  # Invalid port number: must be between 0 and 65535
            except ValueError as e:
                return False  # Invalid port number: not a valid integer.
            return True

        except Exception as e:
            # Catch any other unexpected errors
            return False

    def forceUseOfThisComPort(self, port):
        savePort = self.availableComPorts_VAR.get()
        self.availableComPorts_VAR.set(port)
        if(self.openSelectedComPort(port)):
            return True
        else:
            #
            #   Reset selected port
            #
            self.availableComPorts_VAR.set(savePort)
            return False

    def forceUseOfThisSocket(self, port):
        # savePort = self.availableComPorts_VAR.get()
        # self.availableComPorts_VAR.set(port)
        if(self.openSelectedComPort(port)):
            return True
        else:
            return False


    def openSelectedComPort (self, port):

        try:
            if self.radioPortType == "ComPort":
                RS232 = serial.Serial(port, gv.BAUD, timeout=5, stopbits=1, parity=serial.PARITY_NONE, xonxoff=0,
                                      rtscts=0, write_timeout=1)
            else:
                RS232 = serial.serial_for_url(port, gv.BAUD, timeout=1)
            #
        except: # FileNotFoundError:
            return False
        else:
            #
            #   Port opened successfully, now need to cleanup UX
            #

            self.open_com_port = RS232

            if self.radioPortType == "ComPort":
                self.comPortsOptionMenu.configure(state="disabled")         # disable selection for life of run
                self.comPortListRefresh.configure(state="disabled")
            else:                   # Socket
                self.wifi_Port_Test_Button.pack_forget()        # success open means we can remove test button

            self.comportMessage_Frame.pack_forget()  # Close the top half of the select comport frame

            if port != gv.config.getRadioPort:       # This handles the case where the config file existed with the wrong comport
                gv.config.setRadioPort(port)
            return True




    def updateComPorts(self, *args):

        ports = serial.tools.list_ports.comports()          #Gets list of ports
        self.comPortList =[("Select Serial Port")]          #Seeds option list with Selection instructions

        for p in ports:                                 #this used to strip down to just the com port# or path
            self.comPortList.append(p.device)
        self.comPortsOptionMenu.set_menu(*self.comPortList)  # put found ports into the option menu


    def radioSerialPortSelected_CB(self, *args):                # callback specified by UX, connected to main
        self.selectionMade = True

    def test_Entered_IP_Address_CB (self):                      # ip address entered and user wants to try it
        self.selectionMade = True
        self.wifi_Port_Test_Button.configure(state="disabled")

    def getSelectedComPort(self):
        if self.radioPortType == "ComPort":
            return self.availableComPorts_VAR.get()
        else:
            return ("socket://"+self.IPv4_Octet1_VAR.get()+"."+self.IPv4_Octet2_VAR.get()+"."+self.IPv4_Octet3_VAR.get()+"."
                    +self.IPv4_Octet4_VAR.get()+":"+self.IPv4_Port_VAR.get())

    def getRadioPortHandle (self):
        return self.open_com_port

    def connectionTypeSelected_CB(self, event=None):
        self.setRadioPortType (self.radioConnectionType_VAR.get())


    def setRadioPortType(self, portType):
        self.radioPortType = portType

        if self.radioPortType == 'Socket':
            self.comPort_Frame.pack_forget()
            self.wifiPort_Frame.pack(
                expand=False,
                fill="x",
                padx=10,
                pady=10,
                side="top")
            self.ipAddress = gv.config.getRadioPort()
            ipParts = self.ipAddress.replace(":",".").replace("/","").split(".")

            self.IPv4_Octet1_VAR.set(ipParts[1])
            self.IPv4_Octet2_VAR.set(ipParts[2])
            self.IPv4_Octet3_VAR.set(ipParts[3])
            self.IPv4_Octet4_VAR.set(ipParts[4])
            self.IPv4_Port_VAR.set(ipParts[5])

        else:
            #
            #   Using get_image to isolate difference between a "package" and direct all
            #
            self.reloadicon = gv.get_image(gv.RELOADICON)

            self.wifiPort_Frame.pack_forget()
            self.comPort_Frame.pack(
                expand=False,
                fill="x",
                padx=10,
                pady=10,
                side="top")
            self.comPortListRefresh.configure(image=self.reloadicon)
            self.updateComPorts()  # preload the available com ports
            self.comPortsOptionMenu.configure(width=15)


