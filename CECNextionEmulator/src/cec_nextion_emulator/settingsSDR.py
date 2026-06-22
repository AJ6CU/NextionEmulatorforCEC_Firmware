#!/usr/bin/python3
"""
settingsSDR

Used to save of machines

UI source file: settingsSDR.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import settingsSDRui as baseui
import globalvars as gv


#
# Manual user code
#

class settingsSDR(baseui.settingsSDRUI):
    def __init__(self, master=None, mainWindow=None, **kw):
        self.master = master
        self.mainWindow = mainWindow
        #
        #   Create a toplevel window to contain the settings popup
        #
        self.popup = tk.Toplevel(self.master)
        super().__init__(self.popup, **kw)

        self.initUX()

    def initUX(self):
        self.popup.title("SDR Settings")
        self.popup.geometry(gv.POPUP_WINDOW_OFFSET)

        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsSDR(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
