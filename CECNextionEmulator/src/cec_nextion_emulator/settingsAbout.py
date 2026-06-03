#!/usr/bin/python3
"""
settingsAbout

Used to save general settings

UI source file: settingsAbout.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import settingsAboutui as baseui
import globalvars as gv
import os


#
# Manual user code
#

class settingsAbout(baseui.settingsAboutUI):

    def __init__(self, master=None, mainWindow=None, **kw):
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
        self.popup.protocol("WM_DELETE_WINDOW", self.close_CB)

        super().__init__(self.master, **kw)

        self.initUX()

    def initUX(self):
        self.popup.title("About CECNextionEmulator")

        self.popup.geometry(gv.POPUP_WINDOW_OFFSET)

        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)

        self.versionID_VAR.set(gv.APPVERSION)
        self.releaseDate_VAR.set(gv.APPDATE)
        self.configurationFileLocation_VAR.set(os.path.expanduser(os.path.join("~", ".CECNextionEmulator.ini")))
        self.logFileLocation_VAR.set(os.path.expanduser(os.path.join("~", ".CECNextionEmulator.log")))


        self.pack(expand=tk.YES, fill=tk.BOTH)


    def close_CB(self):
        self.popup.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsAbout(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
