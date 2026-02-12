#!/usr/bin/python3
import pathlib
import sys, os

import tkinter as tk
import tkinter.ttk as ttk
import pygubu
from time import sleep


# import piCEC_UXui as baseui
from mainScreen import mainScreen
from piRadio import piRadio
from configuration import configuration
from comportManager import comportManager
import globalvars as gv

from tkinter import messagebox


root = None
mainWindow = None
radioPort = None
myRadio = None


#
#   once a valid port is found, then we can start the main window.
#
def startMainWindow(radioPortName, radioPortHandle):

    radioPort.place_forget()

    radioPort.place(relx=0.80, rely=1, anchor="s")

    gv.config.setRadioPort(radioPortName)  # update the config file if necessary because of comport selection
    # print(" radio:", comPortName)
    # comPort.setComPort(comPortName)
    myRadio = piRadio(radioPortName, radioPortHandle, mainWindow)  # Initialize the Radio object with selected port



    mainWindow.attachRadio(myRadio)         # tell the mainWindow how to talk to the radio

    myRadio.rebootRadio()                   # We reboot the radio because it sends a bunch of initialization values on startup
                                            # to the Nextion screen. We need to capture them

    myRadio.readALLValues()                 # Now after reboot, read in the initialization values


    mainWindow.initUX()                     # With the initialization values read in, we can perform some initialization functions
                                            # like setting up tuning rate

    myRadio.updateData()  # This process read any data available, but dont schedule followup


#
#   Main program and loop
#
root = tk.Tk()

root.geometry("400x275+5+30")           # necessary because latest Tixie put new windows in center
root.title("CECNextionEmulator - A Nextion Emulator for CEC Firmware running on the uBITX")


gv.config = configuration(root)                    # Read in config data, if missing preload with defaults
                                                # Root is passed to allow popup error messages

mainWindow = mainScreen(root)

radioPort = comportManager(root, startMainWindow)


if not radioPort.getComPort():
    #
    #   Handles the case where the com port is not valid or not in .ini file.
    #   Have to open up  selection window.
    #
    radioPort.pack()

    root.geometry(gv.trimAndLocateWindow(radioPort, 5, 30))

    root.after(500, radioPort.retry())           # If we failed to get a comport the easy way, try again

root.mainloop()
