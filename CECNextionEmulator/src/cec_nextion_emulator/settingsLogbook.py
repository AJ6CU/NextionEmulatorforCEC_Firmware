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
from QSOLogger import QSOLogger
import os


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

        self.initUX()

    def initUX(self):
        self.popup.title("Logbook Settings")

        self.logbookSwitch_VAR.set(gv.config.get_logbook_Switch())
        self.logbookSwitchSave = gv.config.get_logbook_Switch()

        self.logbookType_VAR.set(gv.config.get_logbook_Type())
        self.logbookTypeSave = gv.config.get_logbook_Type()

        self.logbookName_VAR.set(gv.config.get_logbook_Name())
        self.logbookNameSave = gv.config.get_logbook_Name()

        self.logbookLocation_Text.insert("1.0",gv.config.get_logbook_Location())
        self.logbookLocationSave = gv.config.get_logbook_Location()

        self.logbookLocation_Text.configure(state="disabled")

        if self.logbookSwitch_VAR.get() == "False":
            self.logbookType_Menubutton.configure(state="disabled")
            self.logbookFileSelectorButton.configure(state="disabled")


        self.popup.geometry(gv.POPUP_WINDOW_OFFSET)

        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)

    def selectLogbookOn_CB(self):
        self.logbookSwitch_VAR.set("True")
        self.logbookType_Menubutton.configure(state="normal")
        self.logbookFileSelectorButton.configure(state="normal")


    def selectLogbookOff_CB(self):
        self.logbookSwitch_VAR.set("False")

        self.logbookType_Menubutton.configure(state="disabled")
        self.logbookFileSelectorButton.configure(state="disabled")



    def selectLogbookType_CSV_CB(self):
        self.logbookType_VAR.set("csv")


    def selectLogbookType_ADI_CB(self):
        self.logbookType_VAR.set("adi")


    def newLogbookLocation_CB(self, event=None):
        newpath = self.logbookFileSelectorButton.cget('path')
        self.logbookLocation_Text.configure(state="normal")
        self.logbookLocation_Text.delete("1.0", tk.END)
        self.logbookLocation_Text.insert("1.0",newpath)
        self.logbookLocation_Text.configure(state="disabled")


    def apply_CB(self):

        newType = False
        newName = False

        if self.logbookSwitchSave != self.logbookSwitch_VAR.get():
            gv.config.set_logbook_Switch(self.logbookSwitch_VAR.get())

        if self.logbookTypeSave != self.logbookType_VAR.get():
            gv.config.set_logbook_Type(self.logbookType_VAR.get())
            newType = True

        if self.logbookNameSave != self.logbookName_VAR.get():
            gv.config.set_logbook_Name(self.logbookName_VAR.get())
            newName = True

        if self.logbookLocationSave != self.logbookLocation_Text.get("1.0", "end-1c"):
            gv.config.set_logbook_Location(self.logbookLocation_Text.get("1.0", "end-1c"))
            newName = True

        if (self.logbookSwitch_VAR.get() == "False"):
            if (self.mainWindow.QSOLogger_Object != None):  # If turnoff logger, destroy the object
                self.mainWindow.QSOLogger_Object = None

        else:
            theLogbook = os.path.expanduser(os.path.join(gv.config.get_logbook_Location(), self.logbookName_VAR.get()))

            if self.mainWindow.QSOLogger_Object == None:           # Create new object
                self.mainWindow.QSOLogger_Object = QSOLogger(self.logbookType_VAR.get(), theLogbook)
            else:
                if newType:
                    self.mainWindow.QSOLogger_Object.change_format(self.logbookType_VAR.get())
                if newName:
                    self.mainWindow.QSOLogger_Object.set_filename(theLogbook)

        self.popup.destroy()

    def cancel_CB(self):
        self.popup.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsLogbook(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
