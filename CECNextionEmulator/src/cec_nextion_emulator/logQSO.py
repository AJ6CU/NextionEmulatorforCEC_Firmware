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
from datetime import datetime, UTC, timezone
from QSOLogger import QSOLogger
import os
from VirtualNumericKeyboard import VirtualNumericKeyboard
from VirtualKeyboard import VirtualKeyboard
from tkinter import messagebox
import re

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
        if gv.NUMBER_DELIMITER == ",":
            self.lowFreqDigits.set(",000")
        else:
            self.lowFreqDigits.set(".000")

        self.bandName_VAR.set(self._calculate_band_from_freq(self.frequency_VAR.get().replace(",",".")))

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


    def callsign_Entered_CB(self, event=None):
        self.callsign_save = self.callsign_VAR.get()
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vKeyboard = VirtualKeyboard(self, self.callSign_VAR, self.callSign_Vkeyboard_Validate, 12)


    def callsign_Validate_CB(self, p_entry_value, v_condition):
        return self.is_valid_lotw_callsign(p_entry_value)

    def callsign_Vkeyboard_Validate(self):
        if not self.is_valid_lotw_callsign(self.callsign_VAR.get()):
            self.callsign_VAR.set()

    def callsign_Invalid_CB(self, p_entry_value=None, v_condition=None):

        messagebox.showinfo("Error - Invalid Callsign",
                            "callsign is empty, exceeds 20 characters, includes an illegal character" +
                            " (something other than A-Z, 0-9, /) or bad format." +
                            " Input ignored, resetting to prior value", parent=self)
        self.callsign_VAR.set(self.callsign_save)


    def is_valid_lotw_callsign(self, callsign):
        # 1. Clean the input: remove whitespace and convert to uppercase
        call = callsign.strip().upper()

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



    def frequency_Entered_CB(self, event=None):
        self.frequency_save = self.frequency_VAR.get()
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vNumericPad = VirtualNumericKeyboard(self, self.frequency_VAR, self.frequency_Vkeyboard_Validate, 7, True)

    def frequency_Validate_CB(self, p_entry_value, v_condition):
        return self.is_valid_frequency(p_entry_value)

    def frequency_Vkeyboard_Validate(self):
        if not self.is_valid_frequency(self.frequency_VAR.get()):
            self.frequency_Invalid_CB()

    def frequency_Invalid_CB(self, p_entry_value=None, v_condition=None):
        messagebox.showinfo("Error - Frequency is invalid",
                            "Entered frequency exceeds 60mHZ. Resetting to prior value",
                            parent=self)
        self.frequency_VAR.set(self.frequency_save)

    def is_valid_frequency(self, f):
        if int(gv.unformatFrequency(f)) <= round(gv.FREQ_BOUNDS['HIGH'] / 1000):
            return True
        else:
            return False



    def utcDateYYYY_Entered_CB(self, event=None):
        self.utcDateYYYY_save = self.utcDateYYYY_VAR.get()
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vNumericPad = VirtualNumericKeyboard(self, self.utcDateYYYY_VAR, self.utcDateYYYY_Vkeyboard_Validate, 7, False)

    def utcDateYYYY_Validate_CB(self, p_entry_value, v_condition):
        if self.is_valid_year(p_entry_value):
            self.updateLocalDateTime()
            return True
        else:
            return False

    def utcDateYYYY_Vkeyboard_Validate(self):
        if self.is_valid_year(self.utcDateYYYY_VAR.get()):
            self.updateLocalDateTime()
        else:
            self.utcDateYYYY_Invalid_CB()

    def utcDateYYYY_Invalid_CB(self, p_entry_value=None, v_condition=None):
        messagebox.showinfo("Error - Illegal Year",
                            "Entered year not in the range of 2026 - 2050. Resetting to prior value",
                            parent=self)
        self.utcDateYYYY_VAR.set(self.utcDateYYYY_save)

    def is_valid_year(self, year):
        if gv.validateNumber(int(year), 2026, 2050):
            return True
        else:
            return False




    def utcDateMM_Entered_CB(self, event=None):
        self.utcDateMM_save = self.utcDateMM_VAR.get()
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vNumericPad = VirtualNumericKeyboard(self, self.utcDateMM_VAR, self.utcDateMM_Vkeyboard_Validate,
                                                      2, False)

    def utcDateMM_Validate_CB(self, p_entry_value, v_condition):
        if self.is_valid_month(p_entry_value):
            self.updateLocalDateTime()
            return True
        else:
            return False

    def utcDateMM_Vkeyboard_Validate(self):
        if self.is_valid_month(self.utcDateMM_VAR.get()):
            self.updateLocalDateTime()
        else:
            self.utcDateMM_Invalid_CB()

    def utcDateMM_Invalid_CB(self, p_entry_value=None, v_condition=None):
        messagebox.showinfo("Error - Illegal Month",
                            "Entered month not in the range of 1-12. Resetting to prior value",
                            parent=self)
        self.utcDateMM_VAR.set(self.utcDateMM_save)

    def is_valid_month(self, month):
        if gv.validateNumber(int(month), 1, 12):
            return True
        else:
            return False



    def utcDateDD_Entered_CB(self, event=None):
        self.utcDateDD_save = self.utcDateDD_VAR.get()
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vNumericPad = VirtualNumericKeyboard(self, self.utcDateDD_VAR, self.utcDateDD_Vkeyboard_Validate,
                                                      2, False)

    def utcDateDD_Validate_CB(self, p_entry_value, v_condition):
        if self.is_valid_day(self.utcDateYYYY_VAR.get(), self.utcDateMM_VAR.get(), p_entry_value):
            self.updateLocalDateTime()
            return True
        else:
            return False

    def utcDateDD_Vkeyboard_Validate(self):
        if self.is_valid_day(self.utcDateYYYY_VAR.get(), self.utcDateMM_VAR.get(), p_entry_value):
            self.updateLocalDateTime()
        else:
            self.utcDateDD_Invalid_CB()

    def utcDateDD_Invalid_CB(self, p_entry_value=None, v_condition=None):
        messagebox.showinfo("Error - Illegal Day",
                            "Entered day is not valid for Year and Month. Resetting to prior value",
                            parent=self)
        self.utcDateDD_VAR.set(self.utcDateDD_save)


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



    def utcTimeHH_Entered_CB(self, event=None):
        self.utcTimeHH_save = self.utcTimeHH_VAR.get()
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vNumericPad = VirtualNumericKeyboard(self, self.utcTimeHH_VAR, self.utcTimeHH_Vkeyboard_Validate,
                                                      2, False)

    def utcTimeHH_Validate_CB(self, p_entry_value, v_condition):
        if self.is_valid_hour(p_entry_value):
            self.updateLocalDateTime()
            return True
        else:
            return False

    def utcTimeHH_Vkeyboard_Validate(self):
        if self.is_valid_hour(self.utcTimeHH_VAR.get()):
            self.updateLocalDateTime()
        else:
            self.utcTimeHH_Invalid_CB()

    def utcTimeHH_Invalid_CB(self, p_entry_value=None, v_condition=None):
        messagebox.showinfo("Error - Illegal Time",
                            "Entered hour is not in range 0-23. Resetting to prior value",
                            parent=self)
        self.utcTimeHH_VAR.set(self.utcTimeHH_save)

    def is_valid_hour(self, hour):
        if gv.validateNumber(int(hour), 0, 23):
            return True
        else:
            return False




    def utcTimeMM_Entered_CB(self, event=None):
        self.utcTimeMM_save = self.utcTimeMM_VAR.get()
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vNumericPad = VirtualNumericKeyboard(self, self.utcTimeMM_VAR, self.utcTimeMM_Vkeyboard_Validate,
                                                      2, False)

    def utcTimeMM_Validate_CB(self, p_entry_value, v_condition):
        if self.is_valid_minutes(p_entry_value):
            self.updateLocalDateTime()
            return True
        else:
            return False


    def utcTimeMM_Vkeyboard_Validate(self):
        if self.is_valid_minutes(self.utcTimeMM_VAR.get()):
            self.updateLocalDateTime()
        else:
            self.utcTimeMM_Invalid_CB()

    def utcTimeMM_Invalid_CB(self, p_entry_value=None, v_condition=None):
        messagebox.showinfo("Error - Illegal Time",
                            "Entered minutes is not in range 0-59. Resetting to prior value",
                            parent=self)
        self.utcTimeMM_VAR.set(self.utcTimeMM_save)

    def is_valid_minutes(self, minutes):
        if gv.validateNumber(int(minutes), 0, 59):
            return True
        else:
            return False





    def updateLocalDateTime(self):
        print("in update", self.utcDateYYYY_VAR.get())
        utc_string = (self.utcDateYYYY_VAR.get() + "-" + self.utcDateMM_VAR.get() + "-" + self.utcDateDD_VAR.get() +
                      "T" + self.utcTimeHH_VAR.get() +":" + self.utcTimeMM_VAR.get() +":00Z")

        utc_obj = datetime.fromisoformat(utc_string)
        # Convert to local time zone
        local_obj = utc_obj.astimezone()

        self.localDate_VAR.set(local_obj.strftime("%Y-%m-%d"))
        self.localTime_VAR.set(local_obj.strftime("%H:%M"))



    def rstSend_Entered_CB(self, event=None):
        self.rstSend_save = self.rstSend_VAR.get()
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vKeyboard = VirtualKeyboard(self, self.rstSend_VAR, self.rstSend_Vkeyboard_Validate, 8)

    def rstSend_Validate_CB(self, p_entry_value, v_condition):
        if self.is_valid_rst(p_entry_value):
            return True
        else:
            return False

    def rstSend_Vkeyboard_Validate(self):
        if not self.is_valid_rst(self.rstSend_VAR.get()):
            self.rstSend_Invalid_CB()

    def rstSend_Invalid_CB(self, p_entry_value=None, v_condition=None):
        messagebox.showinfo("Error - RST Sent",
                            "Entered RST Sent has length of either 0 or more than 8 characters. Resetting to prior value",
                            parent=self)
        self.rstSend_VAR.set(self.rstSend_save)




    def rstReceived_Entered_CB(self, event=None):
        print("Entered RST Received")
        self.rstReceived_save = self.rstReceived_VAR.get()
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vKeyboard = VirtualKeyboard(self, self.rstReceived_VAR, self.rstReceived_Vkeyboard_Validate, 8)

    def rstReceived_Validate_CB(self, p_entry_value, v_condition):
        if self.is_valid_rst(p_entry_value):
            return True
        else:
            return False

    def rstReceived_Vkeyboard_Validate(self):
        if not self.is_valid_rst(self.rstReceived_VAR.get()):
            self.rstReceived_Invalid_CB()


    def rstReceived_Invalid_CB(self, p_entry_value=None, v_condition=None):
        messagebox.showinfo("Error - RST Received",
                            "Entered RST Received has length of either 0 or more than 8 characters. Resetting to prior value",
                            parent=self)
        self.rstReceived_VAR.set(self.rstReceived_save)

    def is_valid_rst(self,rst):
        if 3<= len(rst) <= 8:
            return True
        else:
            return False




    def logQSO_CB(self):
        qso={}
        qso['call'] = self.callsign_VAR.get()
        qso['mode'] = self.commType_VAR.get()
        qso['qso_date'] = self.utcDateYYYY_VAR.get()+self.utcDateMM_VAR.get()+self.utcDateDD_VAR.get()
        qso['time_on'] = self.utcTimeHH_VAR.get()+self.utcTimeMM_VAR.get()
        qso['freq'] = self.frequency_VAR.get()
        qso['band'] = self.bandName_VAR.get()
        qso['rst_sent'] = self.rstSend_VAR_VAR.get()
        qso['rst_rcvd'] = self.rstReceived_VAR.get()

        'call', 'mode', 'qso_date', 'time_on', 'freq', 'rst_sent', 'rst_rcvd'
        self.mainWindow.QSOLogger_Object.append_qso(qso)
        self.popup.destroy()

    def cancel_CB(self):
        self.popup.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = logQSO(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
