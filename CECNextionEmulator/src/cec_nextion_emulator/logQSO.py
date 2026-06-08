#!/usr/bin/python3
"""
Log QSO

Completes the logging of a QSO

UI source file: logQSO.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import logQSOui as baseui
import globalvars as gv


#
# Manual user code
#

class logQSO(baseui.logQSOUI):
    def __init__(self, master=None, mainWindow = None, **kw):
        self.master = master
        self.mainWindow = mainWindow

        self.popup = tk.Toplevel(self.master)

        super().__init__(self.popup, **kw)

        # self.protocol("WM_DELETE_WINDOW", self.close_CB)

        self.initUX()  # This deals with any initiation that needs to be done after the Object is fully
        # instantiated.

    def initUX(self):
        self.popup.geometry(gv.POPUP_WINDOW_OFFSET)
        self.popup.title("Log QSO")

        self.popup.wait_visibility()  # required on Linux

        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)


if __name__ == "__main__":
    root = tk.Tk()
    widget = logQSO(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
