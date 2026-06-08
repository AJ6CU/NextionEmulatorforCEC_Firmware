#!/usr/bin/python3
"""
settingsLogbook

Manages the settings for the logbook function

UI source file: settingsLogbook.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import settingsLogbookui as baseui
import globalvars as gv


#
# Manual user code
#

class settingsLogbook(baseui.settingsLogbookUI):
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
        self.popup.protocol("WM_DELETE_WINDOW", self.cancel_CB)
        #
        #
        #   Magic code to get a handle on the current font of the default item and propagate it to the list...
        #

        # self.saveNUMBER_DELIMITER = gv.config.get_NUMBER_DELIMITER()
        # self.NUMBER_DELIMITER_VAR.set(self.saveNUMBER_DELIMITER)
        #
        # self.saveVFO_Touch_Optimized = gv.config.get_VFO_Touch_Optimized()
        # self.VFO_Touch_Optimized_VAR.set(self.saveVFO_Touch_Optimized)
        #
        # self.saveVirtual_Keyboard = gv.config.get_Virtual_Keyboard_Switch()
        # self.Virtual_Keyboard_VAR.set(self.saveVirtual_Keyboard)
        #
        # self.saveTime_On_Freq = str(int(int(gv.config.get_Scan_On_Station_Time()) / 1000))
        # self.Time_On_Freq_VAR.set(self.saveTime_On_Freq)
        #
        #   Can now kickoff the UX
        #

        self.initUX()

    def initUX(self):
        self.popup.title("Logbook Settings")
        self.popup.geometry(gv.POPUP_WINDOW_OFFSET)

        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsLogbook(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
