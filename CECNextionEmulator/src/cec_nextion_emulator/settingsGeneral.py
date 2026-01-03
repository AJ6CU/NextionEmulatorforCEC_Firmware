#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk

import tkinter.font as font
import tkinter.font as tkFont

import settingsGeneralui as baseui
from configuration import configuration
import globalvars as gv


#
# Manual user code
#


class settingsGeneral(baseui.settingsGeneralUI):
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

        gv.formatCombobox( self.Number_Delimiter_Combobox, "Arial", "24", "bold")
        gv.formatCombobox( self.Virtual_Keyboard_Combobox, "Arial", "24", "bold")
        gv.formatCombobox(self.VFO_Touch_Optimized_Combobox, "Arial", "24", "bold")
        gv.formatCombobox(self.Time_On_Freq_Combobox, "Arial", "24", "bold")

        self.saveNUMBER_DELIMITER = gv.config.get_NUMBER_DELIMITER()
        self.NUMBER_DELIMITER_VAR.set(self.saveNUMBER_DELIMITER)

        self.saveVFO_Touch_Optimized = gv.config.get_VFO_Touch_Optimized()
        self.VFO_Touch_Optimized_VAR.set(self.saveVFO_Touch_Optimized)

        self.saveVirtual_Keyboard = gv.config.get_Virtual_Keyboard_Switch()
        self.Virtual_Keyboard_VAR.set(self.saveVirtual_Keyboard)

        self.saveTime_On_Freq = str(int(int(gv.config.get_Scan_On_Station_Time())/1000))
        self.Time_On_Freq_VAR.set(self.saveTime_On_Freq)
        #
        #   Can now kickoff the UX
        #

        self.initUX()


    def initUX(self):
        self.popup.title("General Settings")
        self.popup.geometry("450x450")
        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)
        gv.trimAndLocateWindow(self.popup, 0, 0)

    def apply_CB(self):

        if self.NUMBER_DELIMITER_VAR.get() != self.saveNUMBER_DELIMITER:
            gv.config.set_NUMBER_DELIMITER(self.NUMBER_DELIMITER_VAR.get())

        if self.Virtual_Keyboard_VAR.get() != self.saveVirtual_Keyboard:
            gv.config.set_Virtual_Keyboard_Switch(self.Virtual_Keyboard_VAR.get())

        if self.VFO_Touch_Optimized_VAR.get() != self.saveVFO_Touch_Optimized:
            gv.config.set_VFO_Touch_Optimized(self.VFO_Touch_Optimized_VAR.get())

        if self.Time_On_Freq_VAR.get() != self.saveTime_On_Freq:
            gv.config.set_Scan_On_Station_Time(str(int(int(self.Time_On_Freq_VAR.get())*1000)))

        self.popup.destroy()

    def cancel_CB(self):
        self.popup.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsMisc(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
