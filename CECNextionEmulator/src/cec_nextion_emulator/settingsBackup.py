#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk


import settingsBackupui as baseui
from configuration import configuration
import globalvars as gv
from time import sleep

from tkinter import messagebox


#
# Manual user code
#



class settingsBackup(baseui.settingsBackupUI):
    def __init__(self, master=None,mainWindow=None, **kw):
        super().__init__(master, **kw)

        self.master= master
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
        #   Update all the fields in the dialog. These are the easy ones as they are preloaded
        #
        self.ConfigFile_Master_Cal_VAR.set(self.get_ConfigFile_Master_Cal())
        self.ConfigFile_SSB_BFO_VAR.set(self.get_ConfigFile_SSB_BFO())
        self.ConfigFIle_CW_BFO_VAR.set(self.get_ConfigFile_CW_BFO())
        self.ConfigFile_CW_Keytype_VAR.set(self.get_ConfigFile_CW_Keytype())
        self.ConfigFIle_CW_Speed_VAR.set(self.get_ConfigFile_CW_Speed())
        self.ConfigFile_CW_Sidetone_VAR.set(self.get_ConfigFile_CW_Tone())
        self.ConfigFile_CW_Delay_Before_TX_VAR.set(self.get_ConfigFile_CW_Delay_Before_TX())
        self.ConfigFIle_CW_Delay_Returning_To_RX_VAR.set(self.get_ConfigFile_CW_Delay_Returning_To_RX())

        gv.formatCombobox(self.from_Combobox, "Arial", "18", "bold")
        gv.formatCombobox(self.to_Combobox, "Arial", "18", "bold")

        self.from_Combobox_VAR.set("Select")
        self.to_Combobox_VAR.set("Select")
        #
        #   The following are know values and we just need to load the ones that currently exist
        #
        self.EEPROM_Current_CW_Keytype_VAR.set(self.get_Current_CW_Keytype())
        self.EEPROM_Current_CW_Speed_VAR.set(self.get_Current_CW_Speed())
        self.EEPROM_Current_CW_Sidetone_VAR.set(self.get_Current_CW_Tone())
        self.EEPROM_Current_CW_Delay_Before_TX_VAR.set(self.get_Current_CW_Delay_Before_TX())
        self.EEPROM_Current_CW_Delay_Returning_To_RX_Label_VAR.set(self.get_Current_CW_Delay_Returning_To_RX())

        #
        #   Following a little complex as we have to request that the radio perform EEPROM Memory reads
        #

        self.mainWindow.theRadio.Req_Master_Cal(self.load_Current_Master_Cal)
        self.mainWindow.theRadio.Req_SSB_BFO(self.load_Current_SSB_BFO)
        self.mainWindow.theRadio.Req_CW_BFO(self.load_Current_CW_BFO)

        self.mainWindow.theRadio.Req_Factory_Master_Cal(self.load_Factory_Master_Cal)
        self.mainWindow.theRadio.Req_Factory_SSB_BFO(self.load_Factory_SSB_BFO)
        self.mainWindow.theRadio.Req_Factory_CW_Speed(self.load_Factory_CW_Speed)
        self.mainWindow.theRadio.Req_Factory_CW_Sidetone(self.load_Factory_CW_Tone)

        self.reboot = False                 # Some settings require a reboot to take effect
        sleep(.5)                           # give the MCU some time to respond

        #
        #   Can now kickoff the UX
        #
        self.initUX()

    def initUX(self):
        self.popup.title("Backup Key Radio Settings")
        self.popup.geometry("850x675")
        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)
        gv.trimAndLocateWindow(self.popup, 0, 0)


    #
    #   Master Cal getters/setters
    #

    #       Current Master Cal getters/setters
    def load_Current_Master_Cal(self, value):
        self.EEPROM_Current_Master_Cal_VAR.set(value)

    def get_Current_Master_Cal(self):
        return self.EEPROM_Current_Master_Cal_VAR.get()

    def set_Current_Master_Cal(self,value):

        if gv.validateNumber(value, gv.MASTER_CAL_BOUNDS['LOW'], gv.MASTER_CAL_BOUNDS['HIGH'], "Master Cal", self):
            self.mainWindow.theRadio.Set_Master_Cal(value)
            self.reboot = True


    #       ConfigFile Master Cal getters/setters
    def get_ConfigFile_Master_Cal(self):
        return gv.config.get_Master_Cal()

    def set_ConfigFile_Master_Cal(self, value):
        gv.config.set_Master_Cal(value)



    #
    #   SSB_BFO getters/setters
    #

    #       Current SSB_BFO Cal getters/setters
    def load_Current_SSB_BFO(self, value):
        self.EEPROM_Current_SSB_BFO_VAR.set(value)

    def get_Current_SSB_BFO(self):
        return self.EEPROM_Current_SSB_BFO_VAR.get()

    def set_Current_SSB_BFO(self,value):

        if gv.validateNumber(value, gv.BFO_CAL_BOUNDS['LOW'], gv.BFO_CAL_BOUNDS['HIGH'], "SSB BFO", self):
            self.mainWindow.theRadio.Set_SSB_BFO(value)
            self.reboot = True

    #       ConfigFile SSB_BFO Cal getters/setters
    def get_ConfigFile_SSB_BFO(self):
        return gv.config.get_SSB_BFO()

    def set_ConfigFile_SSB_BFO(self, value):
        gv.config.set_SSB_BFO(value)


    #
    #   CW_BFO getters/setters
    #

    #       Current CW_BFO Cal getters/setters
    def load_Current_CW_BFO(self, value):
        self.EEPROM_Current_CW_BFO_VAR.set(value)

    def get_Current_CW_BFO(self):
        return self.EEPROM_Current_CW_BFO_VAR.get()

    def set_Current_CW_BFO(self,value):
        if gv.validateNumber(value, gv.CW_CAL_BOUNDS['LOW'], gv.CW_CAL_BOUNDS['HIGH'], "CW BFO", self):
            self.mainWindow.theRadio.Set_CW_BFO(value)
            self.reboot = True


    #       ConfigFile CW_BFO Cal getters/setters
    def get_ConfigFile_CW_BFO(self):
        return gv.config.get_CW_BFO()

    def set_ConfigFile_CW_BFO(self,value):
        return gv.config.set_CW_BFO(value)


    #
    #   CW Key Type getters/setters
    #

    #       Current Key_type getters/setters
    def get_Current_CW_Keytype(self):
        return self.mainWindow.key_type_value_VAR.get()

    def set_Current_CW_Keytype(self, value):
        if gv.validateKeyInDict(gv.CW_KeyValue, value, "CW Keytype", self):
            self.mainWindow.theRadio.Set_CW_Keytype(value)

    #       ConfigFile Key_Type getters/setters
    def get_ConfigFile_CW_Keytype(self):
        return gv.config.get_Keytype()

    def set_ConfigFile_CW_Keytype(self, value):
        gv.config.set_Keytype(value)


    #
    #   Factory: Master Cal getters
    #
    def load_Factory_Master_Cal(self, value):
        self.EEPROM_Factory_Master_Cal_VAR.set(value)

    def get_Factory_Master_Cal(self):
        return self.EEPROM_Factory_Master_Cal_VAR.get()

    #
    #   Factory SSB_BFO getters
    #
    def load_Factory_SSB_BFO(self, value):
        self.EEPROM_Factory_SSB_BFO_VAR.set(value)

    def get_Factory_SSB_BFO(self):
        return self.EEPROM_Factory_SSB_BFO_VAR.get()

    #
    #   Factory CW Speed getters
    #
    def load_Factory_CW_Speed(self, value):
        self.EEPROM_Factory_CW_Speed_VAR.set(value)

    def get_Factory_CW_Speed(self):
        return self.EEPROM_Factory_CW_Speed_VAR.get()

    #
    #   CW_Speed getters/setters
    #


    def get_Current_CW_Speed(self):
        return self.mainWindow.key_speed_value_VAR.get()

    def set_Current_CW_Speed(self,value):
        if gv.validateNumber(value, gv.CW_SPEED_WPM_BOUNDS['LOW'], gv.CW_SPEED_WPM_BOUNDS['HIGH'], "CW WPM", self):
            self.mainWindow.theRadio.Set_CW_Speed(value)


    def get_ConfigFile_CW_Speed(self):
        return gv.config.get_CW_Speed()

    def set_ConfigFile_CW_Speed(self,value):
        gv.config.set_CW_Speed(value)

    #
    #   Factory CW Sidetone getters
    #
    def load_Factory_CW_Tone(self, value):
        self.EEPROM_Factory_CW_Sidetone_VAR.set(value)

    def get_Factory_CW_Tone(self):
        return self.EEPROM_Factory_CW_Sidetone_VAR.get()

    #
    #   CW_Speed getters/setters
    #

    #       Current CW_Sidetone getters/setters
    def get_Current_CW_Tone(self):
        return self.mainWindow.tone_value_VAR.get()

    def set_Current_CW_Tone(self, value):
        if gv.validateNumber(value, gv.CW_TONE_BOUNDS['LOW'], gv.CW_TONE_BOUNDS['HIGH'], "CW Sidetone", self):
            self.mainWindow.theRadio.Set_CW_Tone(value)
            self.reboot = True

    #       ConfigFile CW_Sidetone getters/setters
    def get_ConfigFile_CW_Tone(self):
        return gv.config.get_CW_Tone()

    def set_ConfigFile_CW_Tone(self, value):
        gv.config.set_CW_Tone(value)


    #
    #   Delay_Before_TX_Value getters/setters
    #

    #       Current Delay_Before_TX_Value getters/setters
    def get_Current_CW_Delay_Before_TX(self):
        return self.mainWindow.delay_starting_tx_value_VAR.get()

    def set_Current_CW_Delay_Before_TX(self, value):
        if gv.validateNumber(value, gv.CW_START_TX_BOUNDS['LOW'], gv.CW_START_TX_BOUNDS['HIGH'], "Delay->TX", self):
            self.mainWindow.theRadio.Set_CW_Delay_Starting_TX(value)
            self.reboot = True

    #       ConfigFile Delay_Before_TX_Value getters/setters
    def get_ConfigFile_CW_Delay_Before_TX(self):
        return gv.config.get_CW_Delay_Before_TX()

    def set_ConfigFile_CW_Delay_Before_TX(self, value):
        gv.config.set_CW_Delay_Before_TX(value)

    #
    #   Delay_Returning_To_RX_Value getters/setters
    #

    #       Current Delay_Returning_To_RX_Value getters/setters
    def get_Current_CW_Delay_Returning_To_RX(self):
        return self.mainWindow.delay_returning_to_rx_value_VAR.get()

    def set_Current_CW_Delay_Returning_To_RX(self, value):
        if gv.validateNumber(value, gv.CW_DELAY_Return_RX_BOUNDS['LOW'], gv.CW_DELAY_Return_RX_BOUNDS['HIGH'], "Delay->RX", self):
            self.mainWindow.theRadio.Set_CW_Delay_Returning_To_RX(value)
            self.reboot = True

    #       ConfigFile Delay_Returning_To_RX_Value getters/setters
    def get_ConfigFile_CW_Delay_Returning_To_RX(self):
        return gv.config.get_CW_Delay_Returning_to_RX()

    def set_ConfigFile_CW_Delay_Returning_To_RX(self, value):
        gv.config.set_CW_Delay_Returning_to_RX(value)



    def select_All_Checkbutton_CB(self):
        if self.select_All_Checked_VAR.get() == "1":
            self.Master_Cal_Checked_VAR.set("1")
            self.SSB_BFO_Checked_VAR.set("1")
            self.CW_BFO_Checked_VAR.set("1")
            self.CW_Keytype_Checked_VAR.set("1")
            self.CW_Speed_Checked_VAR.set("1")
            self.CW_Sidetone_Checked_VAR.set("1")
            self.CW_Delay_Before_TX_Checked_VAR.set("1")
            self.CW_Delay_Returning_To_RX_Checked_VAR.set("1")

            self.select_All_Checked_Text_VAR.set("Uncheck to Deselect All")


        else:
            self.Master_Cal_Checked_VAR.set("0")
            self.SSB_BFO_Checked_VAR.set("0")
            self.CW_BFO_Checked_VAR.set("0")
            self.CW_Keytype_Checked_VAR.set("0")
            self.CW_Speed_Checked_VAR.set("0")
            self.CW_Sidetone_Checked_VAR.set("0")
            self.CW_Delay_Before_TX_Checked_VAR.set("0")
            self.CW_Delay_Returning_To_RX_Checked_VAR.set("0")

            self.select_All_Checked_Text_VAR.set("Select All")







    def copy_CB(self):

        if self.from_Combobox_VAR.get() == "Select":
            messagebox.showinfo(message="Must select a source for the copy", parent=self)
            return
        elif self.to_Combobox_VAR.get() == "Select":
            messagebox.showinfo(message="Must select a destination for the copy", parent=self)
            return
        elif self.from_Combobox_VAR.get() == self.to_Combobox_VAR.get():
            messagebox.showinfo(message="Source and Destination must be different", parent=self)
            return


        #
        #   Build dictionary of source,destination
        #
        selectedValues = {}

        source = self.from_Combobox_VAR.get()
        destination = self.to_Combobox_VAR.get()

        #
        #   Process each line that is checked assigning read/writing file using the infamous "getattr" magic
        #
        if self.Master_Cal_Checked_VAR.get() == "1":
            readFunction = getattr(self, "get_"+source+"_Master_Cal", None)
            writeFunction = getattr(self, "set_"+destination+"_Master_Cal", None)

            if readFunction != None and writeFunction != None:
                selectedValues["Master_Cal"] = [writeFunction, readFunction]

        if self.SSB_BFO_Checked_VAR.get() == "1":
            readFunction = getattr(self, "get_"+source+"_SSB_BFO", None)
            writeFunction = getattr(self, "set_"+destination+"_SSB_BFO", None)

            if readFunction != None and writeFunction != None:
                selectedValues["SSB_BFO"] = [writeFunction, readFunction]


        if self.CW_BFO_Checked_VAR.get() == "1":
            readFunction = getattr(self, "get_"+source+"_CW_BFO", None)
            writeFunction = getattr(self, "set_"+destination+"_CW_BFO", None)

            if readFunction != None and writeFunction != None:
                selectedValues["CW_BFO"] = [writeFunction, readFunction]

            if readFunction == None:     # Only happens if source is "Factory"
                messagebox.showinfo(message=source + " is not a valid source for CW BFO\nRequested update ignored", parent=self)


        if self.CW_Keytype_Checked_VAR.get() == "1":
            readFunction = getattr(self, "get_"+source+"_CW_Keytype", None)
            writeFunction = getattr(self, "set_"+destination+"_CW_Keytype", None)

            if readFunction != None and writeFunction != None:
                selectedValues["CW_Keytype"] = [writeFunction, readFunction]

            if readFunction == None:      # Only happens if source is "Factory"
                messagebox.showinfo(message=source + " is not a valid source for CW Keytype\nRequested update ignored", parent=self)


        if self.CW_Speed_Checked_VAR.get() == "1":
            readFunction = getattr(self, "get_"+source+"_CW_Speed", None)
            writeFunction = getattr(self, "set_"+destination+"_CW_Speed", None)

            if readFunction != None and writeFunction != None:
                selectedValues["CW_Speed"] = [writeFunction, readFunction]


        if self.CW_Sidetone_Checked_VAR.get() == "1":
            readFunction = getattr(self, "get_"+source+"_CW_Tone", None)
            writeFunction = getattr(self, "set_"+destination+"_CW_Tone", None)



            if readFunction != None and writeFunction != None:
                selectedValues["CW_Tone"] = [writeFunction, readFunction]


        if self.CW_Delay_Before_TX_Checked_VAR.get() == "1":
            readFunction = getattr(self, "get_" + source + "_CW_Delay_Before_TX", None)
            writeFunction = getattr(self, "set_" + destination + "_CW_Delay_Before_TX", None)

            if readFunction != None and writeFunction != None:
                selectedValues["CW_Delay_Before_TX"] = [writeFunction, readFunction]


            if readFunction == None:       # Only happens if source is "Factory"
                messagebox.showinfo(message=source + " is not a valid source for Delay->TX\nRequested update ignored", parent=self)


        if self.CW_Delay_Returning_To_RX_Checked_VAR.get() == "1":
            readFunction = getattr(self, "get_" + source + "_CW_Delay_Returning_To_RX", None)
            writeFunction = getattr(self, "set_" + destination + "_CW_Delay_Returning_To_RX", None)


            if readFunction != None and writeFunction != None:
                selectedValues["CW_Delay_Returning_To_RX"] = [writeFunction, readFunction]

            if readFunction == None:       # Only happens if source is "Factory"
                messagebox.showinfo(message=source + " is not a valid source for Delay->RX\nRequested update ignored", parent=self)



        if len(selectedValues) == 0:
            messagebox.showinfo(message="No Valid Selections to Copy\n\n"+
                                "Did you forget to check what you wanted to backup?", parent=self)
            return

        warningMessage = "The following Settings in " + destination + " will be overwritten by values from the " + source + " settings:\n\n"
        for key in selectedValues:
            warningMessage = warningMessage +  key  + "\n"

        if(messagebox.askokcancel(title="Confirm Copy", message=warningMessage, parent=self, icon="warning")):
            for key in selectedValues:
                selectedValues[key][0](selectedValues[key][1]())

        if self.reboot:
            if (messagebox.askyesno("Reboot Required", "One or more changes require a reboot to take effect.\n\n"+
                                                           "Do you want to reboot now?",
                                                            parent=self, icon="warning")
            ):
                    self.mainWindow.theRadio.rebootRadio()

        self.popup.destroy()

    def cancel_CB(self):
        self.popup.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsBackup(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
