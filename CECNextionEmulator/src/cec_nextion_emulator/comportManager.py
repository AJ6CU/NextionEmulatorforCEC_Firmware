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


#
# Manual user code
#

class comportManager(baseui.comportManagerUI):




    def __init__(self, master=None, actionCallback=None, **kw):
        super().__init__(master, **kw)
        self.master = master
        self.actionCallback = actionCallback
        #
        #   Using get_image to isolate difference between a "package" and direct all
        #
        self.reloadicon = gv.get_image(gv.RELOADICON)
        self.comPortListRefresh.configure(image=self.reloadicon)

        self.open_com_port = None
        self.selectionMade = False

        self.updateComPorts()               #preload the available com ports
        self.comPortsOptionMenu.configure(width=15)


    #
    #   this is how we get things started. Main program asks for a comPort, make the callback if found, else report failure
    #
    def getComPort(self):

        #
        #   Lets try the easy way first. Hopefully the comport in the configuration file will just work!
        #
        #
        # if self.validateComPort(gv.config.getComPort()):                #test if config port exists in list of ports
        #     if (self.forceUseOfThisPort(gv.config.getComPort())):       #force it and try to open, if good, then we can start main
        #         self.actionCallback(self.getSelectedComPort(),self.getComPortDesc())
        #         return True
        #
        # return False
        self.open_com_port = serial.serial_for_url('socket://192.168.21.1:9000', baudrate=9600, timeout=1)
        self.actionCallback("testsocket", self.getComPortDesc())
        gv.COMPORT = self.getComPortDesc()
        return True
    #
    #   If we don't get the comport the easy way, this routing is called every 500ms. If a selection has been made, it is checked
    #   and if valid, we kick off the main window. Else, just try again in 500ms
    #

    def retry(self):
        if self.selectionMade:
            if self.getSelectedComPort() in ["/dev/cu.Bluetooth-Incoming-Port",
                                            "/dev/cu.debug-console"
                                            ]:
                    messagebox.showerror(title="ERROR Incorrect CompPort Selected.", parent=self,
                                         detail=self.getSelectedComPort() + "\nIs not a uBITX!")
                    self.selectionMade = False
            else:
                if self.openSelectedComPort():
                    self.actionCallback(self.getSelectedComPort(), self.getComPortDesc())
                    return
        self.master.after(500,self.retry)


    def validateComPort(self, port):
        #
        #   if it is valid, it will be on list of updated comports
        #
        if (port in self.comPortList):
            return True
        else:
            return False

    def forceUseOfThisPort(self, port):
        savePort = self.availableComPorts_VAR.get()
        self.availableComPorts_VAR.set(port)
        if(self.openSelectedComPort()):
            return True
        else:
            #
            #   Reset selected port
            #
            self.availableComPorts_VAR.set(savePort)
            return False


    def openSelectedComPort (self):
        comPort = self.getSelectedComPort()                    # get the selected com port

        try:
            RS232 = serial.Serial(comPort, gv.BAUD, timeout=5, stopbits=1, parity=serial.PARITY_NONE, xonxoff=0, rtscts=0, write_timeout=1)
        except: # FileNotFoundError:
            return False
        else:
            #
            #   Needs to confirm that there is data on the port
            #

            self.open_com_port = RS232

            self.comPortsOptionMenu.configure(state="disabled")         # disable selection for life of run
            self.comPortListRefresh.configure(state="disabled")
            self.comportMessage_Frame.pack_forget()  # Close the top half of the select comport frame

            if comPort != gv.config.getComPort:                     # This handles the case where the config file existed with the wrong comport
                gv.config.setComPort(comPort)
            return True




    def updateComPorts(self, *args):

        ports = serial.tools.list_ports.comports()          #Gets list of ports
        self.comPortList =[("Select Serial Port")]          #Seeds option list with Selection instructions

        for p in ports:                                 #this used to strip down to just the com port# or path
            self.comPortList.append(p.device)
        self.comPortsOptionMenu.set_menu(*self.comPortList)  # put found ports into the option menu


    def radioSerialPortSelected_CB(self, *args):                # callback specified by UX, connected to main
        self.selectionMade = True

    def getSelectedComPort(self):
        return self.availableComPorts_VAR.get()

    def getComPortDesc (self):
        return self.open_com_port


