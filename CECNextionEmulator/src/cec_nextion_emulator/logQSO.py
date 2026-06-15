#!/usr/bin/python3
"""
Log QSO

Completes the logging of a QSO

UI source file: logQSO.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from multiprocessing.process import parent_process

import logQSOui as baseui
import globalvars as gv
from datetime import datetime, UTC, timezone
from QSOLogger import QSOLogger
import os
from VirtualNumericKeyboard import VirtualNumericKeyboard
from VirtualKeyboard import VirtualKeyboard
from tkinter import messagebox
import re
from entryFieldHandler import entryFieldHandler

#
# Manual user code
#


class logQSO(baseui.logQSOUI):
    def __init__(self, parent=None, mainWindow = None, **kw):
        self.parent = parent
        self.mainWindow = mainWindow

        self.popup = tk.Toplevel(self.parent)

        super().__init__(self.popup, **kw)

        self.popup.protocol("WM_DELETE_WINDOW", self.cancel_CB)

        self.initUX()  # This deals with any initiation that needs to be done after the Object is fully
        # instantiated.

    def initUX(self):
        #
        #   Make sure a log exists
        #


        if self.mainWindow.QSOLogger_Object == None:  # Create new object
            theLogbook = os.path.expanduser(
                os.path.join(gv.config.get_Logbook_Location(), gv.config.get_Logbook_Name()))
            self.mainWindow.QSOLogger_Object = QSOLogger(gv.config.get_Logbook_Type(), theLogbook)
            self.mainWindow.QSOLogger_Object.set_backup_interval(int(gv.config.get_Logbook_Backup_Interval()))

        # self.frequency_VAR.set(self.mainWindow.theVFO_Object.getFormattedPrimaryVFO()[:-3].rstrip("\r\n"))
        self.frequency_VAR.set(self.mainWindow.theVFO_Object.getFormattedPrimaryVFO()[:-4])
        if gv.config.get_NUMBER_DELIMITER() == ",":
            self.lowFreqDigits.set(",000")
        else:
            self.lowFreqDigits.set(".000")


        self.localDate_VAR.set(datetime.now().strftime("%Y-%m-%d"))
        self.localTime_VAR.set(datetime.now().strftime("%H:%M"))

        self.utcDateYYYY_VAR.set(datetime.now(UTC).strftime("%Y"))
        self.utcDateMM_VAR.set(datetime.now(UTC).strftime("%m"))
        self.utcDateDD_VAR.set(datetime.now(UTC).strftime("%d"))

        self.utcTimeHH_VAR.set(datetime.now(UTC).strftime("%H"))
        self.utcTimeMM_VAR.set(datetime.now(UTC).strftime("%M"))


        if self.mainWindow.primary_Mode_VAR.get() == "CWL" or self.mainWindow.primary_Mode_VAR.get() == "CWU":
            self.commType_VAR.set("CW")
        else:
            self.commType_VAR.set("SSB")
        #
        #   Create a handler for each entry field
        #
        #   (self, parent, widget_name, fieldWidth, vkeyboard, nextWidget=None, **kw)
        self.callsign_Object =      entryFieldHandler(self, "callsign", 20, VirtualKeyboard, self.logQSO_Button)
        self.frequency_Object =     entryFieldHandler(self, "frequency", 6, VirtualNumericKeyboard, self.popup) #sself.logQSO_Button) # self.logQSO_Button)
        self.utcDateYYYY_Object =   entryFieldHandler(self, "utcDateYYYY", 4, VirtualNumericKeyboard, self.popup) #s self.utcDateMM_Entry)
        self.utcDateMM_Object =     entryFieldHandler(self, "utcDateMM", 2, VirtualNumericKeyboard,  self.popup) #sself.utcDateDD_Entry)
        self.utcDateDD_Object =     entryFieldHandler(self, "utcDateDD", 2, VirtualNumericKeyboard,  self.popup) #sself.utcTimeHH_Entry)
        self.utcTimeHH_Object =     entryFieldHandler(self, "utcTimeHH", 2, VirtualNumericKeyboard,  self.popup) #sself.utcTimeMM_Entry)
        self.utcTimeMM_Object =     entryFieldHandler(self, "utcTimeMM", 2, VirtualNumericKeyboard,  self.popup) #sself.logQSO_Button)
        self.rstSend_Object =       entryFieldHandler(self, "rstSend", 8, VirtualKeyboard,  self.popup) #sself.rstRcvd_Entry)
        self.rstRcvd_Object =       entryFieldHandler(self, "rstRcvd", 8, VirtualKeyboard, self.popup) #sself.logQSO_Button)


        self.popup.geometry(gv.POPUP_WINDOW_OFFSET)
        self.popup.title("Log QSO")

        self.popup.wait_visibility()  # required on Linux

        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)

    #
    #   Callsign processing routines
    #


    def callsign_validation(self):
        if self.is_valid_lotw_callsign(self.callsign_VAR.get()):
            return True
        else:
            return False

    def callsign_errorHandler(self):

        messagebox.showinfo("Error - Invalid Callsign",
                            "Callsign is empty, exceeds 20 characters, includes an illegal character" +
                            " (something other than A-Z, 0-9, /) or bad format." +
                            " Input ignored, resetting to prior value", parent=self)

    def callsign_preProcessor(self):
        return self.callsign_VAR.get()

    def callsign_postProcessor(self):
        self.callsign_VAR.set(self.callsign_VAR.get().upper())

    #
    #   Callsign validation
    #

    def is_valid_lotw_callsign(self, callsign):
        # 1. Clean the input: remove whitespace and convert to uppercase
        call = callsign.strip().upper()
        if (len(call) == 0):        # special case of empty callsign when log window appears.
            return True             # If the user tries to log with an empty callsign, caught at logging stage

        # 2. Check length constraint (LoTW minimum is 3, maximum is 20)
        if not (3 <= len(call) <= 20):
            return False

        # 3. Check character rules: letters, digits, and exactly one slash separator
        # Cannot start or end with a slash, and no consecutive slashes
        if call.startswith('/') or call.endswith('/') or '//' in call:
            return False

        # 4. Enforce valid characters (A-Z, 0-9, /)
        if not re.match(r'^[A-Z0-9/]+$', call):
            return False

        # 5. Check prefix exceptions: Base callsign cannot start with digit 0 or 1
        # We split by '/' to evaluate the main base callsign blocks
        parts = call.split('/')
        for part in parts:
            if part and part[0] in ('0', '1'):
                # Only valid if it's an exceptional prefix like 1A, 1M, 1S
                if not part.startswith(('1A', '1M', '1S')):
                    return False

        return True


    #
    #   frequency processing routines
    #

    def frequency_validation(self):
        if int(self.frequency_VAR.get()) <= round(gv.FREQ_BOUNDS['HIGH'] / 1000):
            return True
        else:
            return False

    def frequency_errorHandler(self):
        messagebox.showinfo("Error - Frequency is invalid",
                            "Entered frequency exceeds 60mHZ. Resetting to prior value",
                            parent=self)
    def frequency_preProcessor(self):
        return self.frequency_VAR.get().replace(",","").replace(".","")

    def frequency_postProcessor(self):
        freq = float(self.frequency_VAR.get())/1000
        self.frequency_VAR.set(f"{freq:.3f}")
        self.bandName_VAR.set(self._calculate_band_from_freq(self.frequency_VAR.get()))
        self.frequency_VAR.set(self.frequency_VAR.get().replace(".", gv.NUMBER_DELIMITER))

    #
    #   Frequency utilities
    #

    def _calculate_band_from_freq(self, freq_mhz):
        """Internal frequency-to-band string calculator."""
        freq_mhz_STD = freq_mhz.replace(",", ".")
        try:
            f = float(freq_mhz_STD)
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

    #
    #   General utilities used by date/time routines
    #
    def formatDateTime(self, dateOrTime):
        if len(dateOrTime) == 1:
            return "0"+dateOrTime
        else:
            return dateOrTime

    def updateLocalDateTime(self):
        # print("in update", self.utcDateYYYY_VAR.get())
        utc_string = (self.utcDateYYYY_VAR.get() + "-" + self.utcDateMM_VAR.get() + "-" + self.utcDateDD_VAR.get() +
                      "T" + self.utcTimeHH_VAR.get() +":" + self.utcTimeMM_VAR.get() +":00Z")

        utc_obj = datetime.fromisoformat(utc_string)
        # Convert to local time zone
        local_obj = utc_obj.astimezone()

        self.localDate_VAR.set(local_obj.strftime("%Y-%m-%d"))
        self.localTime_VAR.set(local_obj.strftime("%H:%M"))


    #
    #   utcDateYYYY processing routines
    #

    def utcDateYYYY_validation(self):
        print("utcDateYYYY validation")
        print(self.utcDateYYYY_VAR.get())

        return self.is_valid_year(self.utcDateYYYY_VAR.get())


    def utcDateYYYY_errorHandler(self):
        print("utcDateYYYY errorHandler")
        print(self.utcDateYYYY_VAR.get())
        messagebox.showinfo("Error - Illegal Year",
                            "Entered year not in the range of 2026 - 2050. Resetting to prior value",
                            parent=self)

    def utcDateYYYY_preProcessor(self):
        return self.utcDateYYYY_VAR.get()

    def utcDateYYYY_postProcessor(self):
        print("utcDateYYYY postProcessor")
        print(self.utcDateYYYY_VAR.get())
        self.updateLocalDateTime()
    #
    #   utcDateYYYY validation routine
    #
    def is_valid_year(self, year):
        if gv.validateNumber(int(year), 2026, 2050):
            return True
        else:
            return False

    #
    #   utcDateMM processing routines
    #

    def utcDateMM_validation(self):
        print("utcDateMM validation")
        print(self.utcDateMM_VAR.get())
        return self.is_valid_month(self.utcDateMM_VAR.get())

    def utcDateMM_errorHandler(self):
        print("utcDateMM errorHandler")
        print(self.utcDateMM_VAR.get())
        messagebox.showinfo("Error - Illegal Month",
                            "Entered month not in the range of 1-12. Resetting to prior value",
                            parent=self)

    def utcDateMM_preProcessor(self):
        return self.utcDateMM_VAR.get()

    def utcDateMM_postProcessor(self):
        print("utcDateMM postProcessor")
        print(self.utcDateMM_VAR.get())
        self.utcDateMM_VAR.set(self.formatDateTime(self.utcDateMM_VAR.get()))   #   add leading zero if a single digit
        self.updateLocalDateTime()


    #
    #   utcMonth Validation routines
    #
    def is_valid_month(self, month):
        return gv.validateNumber(int(month), 1, 12)





    #
    #   utcDateDD processing routines
    #

    def utcDateDD_validation(self):
        print("utcDateDD validation")
        print(self.utcDateDD_VAR.get())
        return self.is_valid_day(self.utcDateYYYY_VAR.get(), self.utcDateMM_VAR.get(), self.utcDateDD_VAR.get())

    def utcDateDD_errorHandler(self):
        print("utcDateDD errorHandler")
        print(self.utcDateDD_VAR.get())
        messagebox.showinfo("Error - Illegal Day",
                            "Entered day is not valid for Year and Month. Resetting to prior value",
                            parent=self)

    def utcDateDD_preProcessor(self):
        return self.utcDateDD_VAR.get()

    def utcDateDD_postProcessor(self):
        print("utcDateDD postProcessor")
        print(self.utcDateDD_VAR.get())
        self.utcDateDD_VAR.set(self.formatDateTime(self.utcDateDD_VAR.get()))   #   add leading zero if a single digit
        self.updateLocalDateTime()

    #
    #   utcDate validation routine
    #
    def is_valid_day(self, year, month, day):
        def is_leap_year(year):
            return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

        imonth = int(month)
        iyear = int(year)
        iday = int(day)

        if imonth < 1 or imonth > 12:
            return False

        # Maps month index to days (February defaults to 28)
        days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # Adjusts February if it's a leap year
        if imonth == 2 and is_leap_year(iyear):
            max_days = 29
        else:
            max_days = days_in_months[imonth - 1]

        return 1 <= iday <= max_days
    #

    #
    #   utcTimeHH processing routines
    #

    def utcTimeHH_validation(self):
        print("utcTimeHH validation")
        print(self.utcTimeHH_VAR.get())
        return self.is_valid_hour(self.utcTimeHH_VAR.get())

    def utcTimeHH_errorHandler(self):
        print("utcTimeHH errorHandler")
        print(self.utcTimeHH_VAR.get())
        messagebox.showinfo("Error - Illegal Time",
                            "Entered hour is not in range 0-23. Resetting to prior value",
                            parent=self)


    def utcTimeHH_preProcessor(self):
        return self.utcTimeHH_VAR.get()

    def utcTimeHH_postProcessor(self):
        print("utcTimeHH postProcessor")
        print(self.utcTimeHH_VAR.get())
        self.utcTimeHH_VAR.set(self.formatDateTime(self.utcTimeHH_VAR.get()))  # add leading zero if a single digit
        self.updateLocalDateTime()

    #
    #   utcTimeHH validation routines
    #
    def is_valid_hour(self, hour):
        return gv.validateNumber(int(hour), 0, 23)

    #
    #   utcTimeMM processing routines
    #

    def utcTimeMM_validation(self):
        print("utcTimeMM validation")
        print(self.utcTimeMM_VAR.get())
        return True

    def utcTimeMM_errorHandler(self):
        print("utcTimeMM errorHandler")
        print(self.utcTimeMM_VAR.get())
        messagebox.showinfo("Error - Illegal Time",
                            "Entered hour is not in range 0-23. Resetting to prior value",
                            parent=self)

    def utcTimeMM_preProcessor(self):
        return self.utcTimeMM_VAR.get()

    def utcTimeMM_postProcessor(self):
        print("utcTimeMM postProcessor")
        print(self.utcTimeMM_VAR.get())
        self.utcTimeMM_VAR.set(self.formatDateTime(self.utcTimeMM_VAR.get()))  # add leading zero if a single digit
        self.updateLocalDateTime()

    #
    #   utcTime Validation Routine
    #
    def is_valid_minutes(self, minutes):
        return gv.validateNumber(int(minutes), 0, 59)

    #
    #   RST utilities used by both fields
    #
    def is_valid_rst(self,rst):
        if 3<= len(rst) <= 8:
            return True
        else:
            return False

    #
    #   rstSend processing routines
    #

    def rstSend_validation(self):
        print("rstSend validation")
        print(self.rstSend_VAR.get())
        return self.is_valid_rst(self.rstSend_VAR.get())

    def rstSend_errorHandler(self):
        print("rstSend errorHandler")
        print(self.rstSend_VAR.get())
        messagebox.showinfo("Error - RST Sent",
                            "Entered RST Sent has length of either 0 or more than 8 characters. Resetting to prior value",
                            parent=self)

    def rstSend_preProcessor(self):
        return self.rstSend_VAR.get()

    def rstSend_postProcessor(self):
        print("rstSend postProcessor")
        print(self.rstSend_VAR.get())
        return self.rstSend_VAR.get()

        #
        #   Callsign processing routines
        #

    def rstRcvd_validation(self):
        print("rstRecv validation")
        print(self.rstRcvd_VAR.get())
        return self.is_valid_rst(self.rstRcvd_VAR.get())

    def rstRcvd_errorHandler(self):
        print("rstRecv errorHandler")
        print(self.rstRcvd_VAR.get())
        messagebox.showinfo("Error - RST Received",
                            "Entered RST Received has length of either 0 or more than 8 characters. Resetting to prior value",
                            parent=self)

    def rstRcvd_preProcessor(self):
        return self.rstRcvd_VAR.get()

    def rstRcvd_postProcessor(self):
        return self.rstRcvd_VAR.get()




    #
    #   Rest of the callbacks
    #

    def selectMode_CB(self, itemid):
        self.commType_VAR.set(itemid)

    def logQSO_CB(self):
        if len(self.callsign_VAR.get()) == 0:
            messagebox.showinfo("Error - Empty callsign",
                                "No callsign entered. Please enter a valid callsign and try again",
                                parent=self)
            return
        else:
            qso={}
            qso['call'] = self.callsign_VAR.get()
            qso['mode'] = self.commType_VAR.get()
            qso['qso_date'] = self.utcDateYYYY_VAR.get()+self.utcDateMM_VAR.get()+self.utcDateDD_VAR.get()
            qso['time_on'] = self.utcTimeHH_VAR.get()+self.utcTimeMM_VAR.get()
            qso['freq'] = self.frequency_VAR.get().replace(",", ".")
            qso['band'] = self.bandName_VAR.get()
            qso['rst_sent'] = self.rstSend_VAR.get()
            qso['rst_rcvd'] = self.rstRcvd_VAR.get()

            self.mainWindow.QSOLogger_Object.append_qso(qso)
            self.popup.destroy()

    def cancel_CB(self):
        self.popup.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = logQSO(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
