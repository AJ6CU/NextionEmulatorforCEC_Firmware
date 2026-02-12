
import json
import os
import platform
import tkinter as tk
from tkinter import messagebox
import globalvars as gv


configuration_file = os.path.expanduser(os.path.join("~", ".CECNextionEmulator.ini"))

class configuration:

    def __init__(self, master=None, **kw):
        self.observers = {}
        try:
            config_file=open(configuration_file, 'r+')

            if (os.stat(configuration_file).st_size == 0):
                # top = tk.Toplevel(master)
                messagebox.showinfo("Information", "Empty configuration file was found\n" +
                                                    "Default values saved in" + configuration_file +
                                                    "\nReview and edit this file if needed",
                                                    parent=master)
                self.writeDefaults()
            else:
                self.config_data = json.load(config_file)
                config_file.close()
                self.distributeConfigData()  # Once config is read in, its values needs to be propagated to objects create prior
        except FileNotFoundError:
            # top = tk.Toplevel(master)
            messagebox.showinfo("Information", "No configuration file was found\n" +
                                                "Default values saved in" + configuration_file +
                                                "\nReview and edit this file if needed",
                                                parent=master)

            self.writeDefaults()
    def distributeConfigData(self):
        gv.NUMBER_DELIMITER = self.get_NUMBER_DELIMITER()
        # print("delimiter number is ", gv.NUMBER_DELIMITER)
        self.register_observer("NUMBER DELIMITER", gv.updateNUMBER_DELIMITER)


    def writeDefaults(self):
        if platform.system() == 'Windows':
            serialPort = "com6"

        elif platform.system() == 'Darwin':
            serialPort = "/dev/cu.usbserial-00000000"

        else:
            serialPort = "/dev/serial0"                     # for trixie+
            # serialPort = "/dev/ttyS0"                     # for bookbinder and below

        #
        #   The default for scanSet Settings is all "None"
        #
        self.config_data = {
                            "Serial Port": serialPort,

                            "Scan Set Settings": [
                                    [0,"None"], [1,"None"], [2, "None"], [3, "None"], [4, "None"],
                                    [5, "None"], [6, "None"], [7, "None"], [8, "None"], [9, "None"],
                                    [10, "None"], [11, "None"], [12, "None"], [13, "None"], [14, "None"],
                                    [15, "None"], [16, "None"], [17, "None"], [18, "None"], [19, "None"]],

                            "Scan On Station Time":1000,

                            "MCU Command Headroom": .09,        # in seconds
                            "MCU Update Period": 500,            # in ms
                            "NUMBER DELIMITER": ".",
                            "TXOffset": "EEPROM",
                            "VFO Touch Optimized": "True",
                            "Master Cal": "",
                            "SSB BFO": "",
                            "CW BFO": "",
                            "CW Tone": "600",
                            "CW Speed":"10",
                            "CW Key Type":"STRAIGHT",
                            "CW Delay Before TX":"500",
                            "CW Delay Returning to RX":"5000",
                            "Callsign":"",
                            "Virtual Keyboard Switch":"True"

                            }
        self.saveConfig()

    def getRadioPort(self):
        return self.config_data["Serial Port"]
    def setRadioPort(self, port):
        self.config_data ["Serial Port"] = port
        self.saveConfig()


    def get_ScanSet_Settings(self, channel):
        return self.config_data["Scan Set Settings"][channel][1]

    def set_ScanSet_Settings(self, channel, scanSet):
        self.config_data["Scan Set Settings"][channel][1] = scanSet
        self.saveConfig()


    def get_Scan_On_Station_Time(self):
        if self.config_data["Scan On Station Time"] < 1000:
            return "1000"           #defaults to 1 second
        return self.config_data["Scan On Station Time"]

    def set_Scan_On_Station_Time(self, time):
        self.config_data["Scan On Station Time"] = time
        self.saveConfig()

    def get_MCU_Command_Headroom(self):
        return self.config_data["MCU Command Headroom"]

    def set_MCU_Command_Headroom(self, value):
        self.config_data["MCU Command Headroom"] = value
        self._notify_observers("MCU Command Headroom", value)
        self.saveConfig()

    def get_MCU_Update_Period(self):
        return self.config_data["MCU Update Period"]

    def set_MCU_Update_Period(self, value):
        self.config_data["MCU Update Period"] = value
        self._notify_observers("MCU Update Period", value)
        self.saveConfig()


    def get_NUMBER_DELIMITER(self):
        return self.config_data["NUMBER DELIMITER"]

    def set_NUMBER_DELIMITER(self, value):
        self.config_data["NUMBER DELIMITER"] = value
        self._notify_observers("NUMBER DELIMITER", value)
        self.saveConfig()

    def get_VFO_Touch_Optimized(self):
        return self.config_data["VFO Touch Optimized"]

    def set_VFO_Touch_Optimized(self, value):
        self.config_data["VFO Touch Optimized"] = value
        self._notify_observers("VFO Touch Optimized", value)
        self.saveConfig()


    def get_Master_Cal(self):
        return self.config_data["Master Cal"]
    def set_Master_Cal(self,value):
        self.config_data ["Master Cal"] = value
        self.saveConfig()

    def get_SSB_BFO(self):
        return self.config_data["SSB BFO"]

    def set_SSB_BFO(self, value):
        self.config_data["SSB BFO"] = value
        self.saveConfig()

    def get_CW_BFO(self):
        return self.config_data["CW BFO"]

    def set_CW_BFO(self, value):
        self.config_data["CW BFO"] = value
        self.saveConfig()


    def get_CW_Tone(self):
        return self.config_data["CW Tone"]

    def set_CW_Tone(self, value):
        self.config_data["CW Tone"] = value
        self.saveConfig()


    def get_CW_Speed(self):
        return self.config_data["CW Speed"]

    def set_CW_Speed(self, value):
        self.config_data["CW Speed"] = value
        self.saveConfig()


    def get_Keytype(self):
        return self.config_data["CW Key Type"]

    def set_Keytype(self, value):
        self.config_data["CW Key Type"] = value
        self.saveConfig()


    def get_CW_Delay_Before_TX(self):
        return self.config_data["CW Delay Before TX"]

    def set_CW_Delay_Before_TX(self, value):
        self.config_data["CW Delay Before TX"] = value
        self.saveConfig()


    def get_CW_Delay_Returning_to_RX(self):
        return self.config_data["CW Delay Returning to RX"]

    def set_CW_Delay_Returning_to_RX(self, value):
        self.config_data["CW Delay Returning to RX"] = value
        self.saveConfig()

    def get_Virtual_Keyboard_Switch(self):
        return self.config_data["Virtual Keyboard Switch"]

    def set_Virtual_Keyboard_Switch(self, value):
        self.config_data["Virtual Keyboard Switch"] = value
        self.saveConfig()



    def saveConfig(self):
        config_file = open(configuration_file, 'w')
        json.dump(self.config_data, config_file)
        config_file.close()


    def register_observer(self, configParameter, observerMethod):
        if self.observers.get(configParameter) is not None:

            self.observers[configParameter].extend([observerMethod])
        else:
            self.observers[configParameter] = [observerMethod]


    def unregister_observer(self, configParameter, observerMethod):
        if self.observers.get(configParameter) is not None:
            if observerMethod in self.observers[configParameter]:
                self.observers[configParameter].remove(observerMethod)


    def _notify_observers(self, configParameter,value):
        if configParameter in self.observers:
            for observerMethod in self.observers[configParameter]:
                observerMethod(value)
