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
from datetime import datetime, UTC


#
# Manual user code
#

class logQSO(baseui.logQSOUI):
    def __init__(self, master=None, mainWindow = None, **kw):
        self.master = master
        self.mainWindow = mainWindow

        self.popup = tk.Toplevel(self.master)

        super().__init__(self.popup, **kw)

        self.popup.protocol("WM_DELETE_WINDOW", self.cancel_CB)

        self.initUX()  # This deals with any initiation that needs to be done after the Object is fully
        # instantiated.

    def initUX(self):

        self.frequency_VAR.set(self.mainWindow.theVFO_Object.getFormattedPrimaryVFO()[:-4])
        if gv.NUMBER_DELIMITER == ",":
            self.lowFreqDigits.set(",000")
        else:
            self.lowFreqDigits.set(".000")

        self.bandName_VAR.set(self._calculate_band_from_freq(self.frequency_VAR.get().replace(",",".")))

        self.localDate_VAR.set(datetime.now().strftime("%Y-%m-%d"))
        self.localTime_VAR.set(datetime.now().strftime("%H:%M"))

        self.utcDate_VAR.set(datetime.now(UTC).strftime("%Y-%m-%d"))
        self.utcTime_VAR.set(datetime.now(UTC).strftime("%H:%M"))

        if self.mainWindow.primary_Mode_VAR.get() == "CWL" or self.mainWindow.primary_Mode_VAR.get() == "CWU":
            self.commType_VAR.set("CW")
        else:
            self.commType_VAR.set("SSB")


        self.popup.geometry(gv.POPUP_WINDOW_OFFSET)
        self.popup.title("Log QSO")

        self.popup.wait_visibility()  # required on Linux

        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)

    def _calculate_band_from_freq(self, freq_mhz):
        """Internal frequency-to-band string calculator."""
        try:
            f = float(freq_mhz)
            if 1.8 <= f <= 2.0:
                return "160m"
            elif 3.5 <= f <= 4.0:
                return "80m"
            elif 5.332 <= f <= 5.405:
                return "60m"
            elif 7.0 <= f <= 7.3:
                return "40m"
            elif 10.1 <= f <= 10.15:
                return "30m"
            elif 14.0 <= f <= 14.35:
                return "20m"
            elif 18.068 <= f <= 18.168:
                return "17m"
            elif 21.0 <= f <= 21.45:
                return "15m"
            elif 24.89 <= f <= 24.99:
                return "12m"
            elif 28.0 <= f <= 29.7:
                return "10m"
            elif 50.0 <= f <= 54.0:
                return "6m"
            elif 144.0 <= f <= 148.0:
                return "2m"
            elif 420.0 <= f <= 450.0:
                return "70cm"
            else:
                return "Custom"
        except (ValueError, TypeError):
            return "Unknown"

    def selectMode_CB(self, itemid):
        self.commType_VAR.set(itemid)

    def cancel_CB(self):
        self.popup.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = logQSO(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
