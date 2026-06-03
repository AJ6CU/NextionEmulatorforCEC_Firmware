#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import settingsui as baseui
import settingsMachine as sm
from cwSettings import cwSettings
from settingsMachine import settingsMachine
from settingsGeneral import settingsGeneral
from settingsBackup import settingsBackup
from settingsAbout import settingsAbout
from tkinter import messagebox
import globalvars as gv
from settingsAbout import settingsAbout


#
# Manual user code
#


class settings(baseui.settingsUI):
    def __init__(self, master=None, mainWindow = None,  **kw):
        #
        #   Save parameters for later use
        #
        self.master = master
        self.mainWindow = mainWindow

        #
        #   Create a toplevel window to contain the settings popup
        #
        self.popup = tk.Toplevel(self.master)

        super().__init__(self.popup, **kw)
        #
        #   Make sure that a close by the Window manager goes to the same close callback
        #
        self.popup.protocol("WM_DELETE_WINDOW", self.settingsClose_CB)

        #
        #   Initialize to none all the object pointers for the sub-settings windows
        #

        self.settingsMachineWindow = None
        self.settingsCWWindow = None
        self.settingsGeneralWindow = None              # This is the "general" settings
        self.settingsChannelsWindow = None
        self.settingsBackupWindow = None
        self.settingsFactoryResetWindow = None
        self.settingsRebootWindow = None
        self.settingsAboutWindow = None
        #
        #   Can now kickoff the UX
        #
        self.initUX()

        #
        #   This routine performs the house keeping for actually displaying the Settings
        #   Dialog box
        #

    def initUX(self):
        self.popup.title("PiCEC Software Settings")
        self.popup.geometry(gv.POPUP_WINDOW_OFFSET)

        # self.popup.geometry("600x425")
        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)
        # self.mainWindow.wait_window(self.popup)


        self.pack(expand=tk.YES, fill=tk.BOTH)
        # gv.trimAndLocateWindow(self.popup, 0, 0)

    #
    #   The following are the callbacks for the various buttons in the Settings Dialog
    #

    def settingsClose_CB(self):
        self.popup.destroy()
        # self.master.destroy()

    def SettingsMachine_CB(self):
        self.settingsMachineWindow = settingsMachine(self.master, self.mainWindow)

    def settingsCW_CB(self):
        self.settingsCWWindow = cwSettings(self.master, self.mainWindow)


    def settingsGeneral_CB(self):
        self.settingsGeneralWindow = settingsGeneral(self.master, self.mainWindow)

    def settingsBackup_CB(self):
        self.settingsBackupWindow = settingsBackup(self.master, self.mainWindow)

    def settingsReboot_CB(self):
        if messagebox.askokcancel("Reboot?", "Do you really want to reboot?", parent=self):
            self.mainWindow.theRadio.rebootRadio()

    def settingsAbout_CB(self):
        self.settingsAboutWindow = settingsAbout(self.master, self.mainWindow)




if __name__ == "__main__":
    root = tk.Tk()
    widget = settings(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
