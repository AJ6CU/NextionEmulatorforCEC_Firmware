
import json
import os
import platform
import threading
import tkinter as tk
from tkinter import messagebox
import globalvars as gv
from defaultCECNextionEmulator import default_config_data




class ConfigurationManager:
    def __init__(self,Master=None):
        """
                Initializes the application configuration settings provider.
                Dynamically targets a hidden user-space config file in the user's home directory.
                """
        self.observers = {}
        # Targets: /home/username/.CECNextionEmulator.ini safely across Linux, Windows, and Mac
        self.configuration_file = os.path.expanduser(os.path.join("~", ".CECNextionEmulator.ini"))
        self.config_data = {}
        self.lock = threading.Lock()  # Thread-safe wrapper preventing race conditions
        self.loadConfig()

    def loadConfig(self):
        """Loads configuration from disk, falling back to Python dictionary defaults if missing/corrupt."""
        if os.path.exists(self.configuration_file):
            try:
                with open(self.configuration_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[-] Config parse error: {e}. Falling back to baseline defaults.")
                self.config_data = default_config_data.copy()
        else:
            print(f"[+] Creating fresh configuration profile at: {self.configuration_file}")
            self.config_data = default_config_data.copy()

            # Guarantee native fallback keys exist immediately on fresh profile creation
            if "Radio IP" not in self.config_data: self.config_data["Radio IP"] = "127.0.0.1"
            if "Radio Port" not in self.config_data: self.config_data["Radio Port"] = 4532

            self.saveConfig()

    def saveConfig(self):
        """Thread-safely serializes and flushes data pool to disk via JSON formatting."""
        with self.lock:
            try:
                with open(self.configuration_file, 'w', encoding='utf-8') as config_file:
                    json.dump(self.config_data, config_file, indent=4, sort_keys=True)
            except IOError as e:
                print(f"[-] Critical Error writing configuration profile to disk: {e}")

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
    #
    #
    # def get(self, key, fallback=None):
    #     """
    #     Safely fetches an item from the configuration memory array.
    #     Returns the specified fallback if the requested key does not exist.
    #     """
    #     return self.config_data.get(key, fallback)
    #
    #
    # def set(self, key, value):
    #     """
    #     Updates an app profile configuration parameter and immediately
    #     commits the update to disk cleanly.
    #     """
    #     self.config_data[key] = value
    #     self.saveConfig()  # Automatically triggers disk synchronization on value change

    def distributeConfigData(self):
        gv.NUMBER_DELIMITER = self.get_NUMBER_DELIMITER()
        # print("delimiter number is ", gv.NUMBER_DELIMITER)
        self.register_observer("NUMBER DELIMITER", gv.updateNUMBER_DELIMITER)


    def writeDefaults(self):
        #
        #   Use the defaults saved in defaultCECNextionEmulator.py
        #
        self.config_data = default_config_data
        #
        #   Make a guess on the serial port
        #
        if platform.system() == 'Windows':
            serialPort = "com6"

        elif platform.system() == 'Darwin':
            serialPort = "/dev/cu.usbserial-00000000"

        else:
            serialPort = "/dev/tty/USB0"                     # for trixie+
            # serialPort = "/dev/serial0"  # for trixie+
            # serialPort = "/dev/ttyS0"                     # for bookbinder and below

        self.config_data["Serial Port"] = serialPort

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

    def get_MCU_Read_Wait_Period(self):
        return self.config_data["MCU Read Wait Period"]

    def set_MCU_Read_Wait_Period(self, value):
        self.config_data["MCU Read Wait Period"] = value
        self.saveConfig()

        "PWR SWR"

    def get_PWR_SWR_Switch(self):
        if "PWR SWR" in self.config_data:
            return self.config_data["PWR SWR"]
        else:
            self.config_data["PWR SWR"] = "False"
            self.saveConfig()
            return self.config_data["PWR SWR"]

    def set_PWR_SWR_Switch(self, value):
        self.config_data["PWR SWR"] = value
        self.saveConfig()


    def get_SWR_Factor(self):
        if "SWR Factor" in self.config_data:
            return self.config_data["SWR Factor"]
        else:
            self.config_data["SWR Factor"] = "1.00"
            self.saveConfig()
            return self.config_data["SWR Factor"]

    def set_SWR_Factor(self, value):
        self.config_data["SWR Factor"] = value
        self.saveConfig()



    def get_PWR_Factor(self):
        if "PWR Factor" in self.config_data:
            return self.config_data["PWR Factor"]
        else:
            self.config_data["PWR Factor"] = "1.00"
            self.saveConfig()
            return self.config_data["PWR Factor"]

    def set_PWR_Factor(self, value):
        self.config_data["PWR Factor"] = value
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

    def get_VFOA_Copy(self):
        if "CW Copy VFOA to VFOB on Split" in self.config_data:
            return self.config_data["CW Copy VFOA to VFOB on Split"]
        else:
            self.config_data["CW Copy VFOA to VFOB on Split"] = "True"
            self.saveConfig()
            return self.config_data["CW Copy VFOA to VFOB on Split"]

    def set_VFOA_Copy(self, value):
        self.config_data["CW Copy VFOA to VFOB on Split"] = value
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

    def get_DSP_Switch(self):
        return self.config_data["DSP"]

    def set_DSP_Switch(self, value):
        self.config_data["DSP"] = value
        self.saveConfig()

    def get_Logbook_Switch(self):
        if "Logbook Switch" in self.config_data:
            return self.config_data["Logbook Switch"]
        else:
            self.config_data["Logbook Switch"] = "False"
            self.saveConfig()
            return self.config_data["Logbook Switch"]

    def set_Logbook_Switch(self, value):
        self.config_data["Logbook Switch"] = value
        self.saveConfig()


    def get_Logbook_Type(self):
        if "Logbook Type" in self.config_data:
            return self.config_data["Logbook Type"]
        else:
            self.config_data["Logbook Type"] = "ADI"
            self.saveConfig()
            return self.config_data["Logbook Type"]

    def set_Logbook_Type(self, value):
        self.config_data["Logbook Type"] = value
        self.saveConfig()

    def get_Logbook_Backup_Interval(self):
        if "Logbook Backup Interval" in self.config_data:
            return self.config_data["Logbook Backup Interval"]
        else:
            self.config_data["Logbook Backup Interval"] = "30"
            self.saveConfig()
            return self.config_data["Logbook Backup Interval"]

    def set_Logbook_Backup_Interval(self, value):
        self.config_data["Logbook Backup Interval"] = value
        self.saveConfig()


    def get_Logbook_Location(self):
        if "Logbook Location" in self.config_data:
            return self.config_data["Logbook Location"]
        else:
            self.config_data["Logbook Location"] = os.path.expanduser("~")
            self.saveConfig()
            return self.config_data["Logbook Location"]

    def set_Logbook_Location(self, value):
        self.config_data["Logbook Location"] = value
        self.saveConfig()


    def get_Logbook_Name(self):
        if "Logbook Name" in self.config_data:
            return self.config_data["Logbook Name"]
        else:
            self.config_data["Logbook Name"] = "Logbook"
            self.saveConfig()
            return self.config_data["Logbook Name"]

    def set_Logbook_Name(self, value):
        self.config_data["Logbook Name"] = value
        self.saveConfig()

    def get_sdr_server_ip(self) -> str:
        """Fetches the target transceiver host network string address."""
        return str(self.config_data.get("Radio IP", "127.0.0.1"))

    def set_sdr_server_ip(self, ip_str: str):
        """Sets target host network address and notifies observers."""
        self.config_data["Radio IP"] = str(ip_str).strip()
        self.saveConfig()
        self._notify_observers("Radio IP", ip_str)

    def get_sdr_tcp_port(self) -> int:
        """Fetches target system communication network socket connector port."""
        return int(self.config_data.get("Radio Port", 4532))

    def set_sdr_tcp_port(self, port_val: int):
        """Sets target transceiver communications loop connector port and notifies observers."""
        self.config_data["Radio Port"] = int(port_val)
        self.saveConfig()
        self._notify_observers("Radio Port", port_val)

    def get_scan_station_time_ms(self) -> int:
        """Fetches memory tracking channel stepping loop duration delay window."""
        return int(self.config_data.get("Scan On Station Time", 5000))

    def set_scan_station_time_ms(self, milliseconds: int):
        """Sets channel cycle loop timing threshold limits and notifies observers."""
        self.config_data["Scan On Station Time"] = int(milliseconds)
        self.saveConfig()
        self._notify_observers("Scan On Station Time", milliseconds)

    def get_last_active_frequency(self) -> int:
        """Fetches the previous successful runtime operational base tracking frequency."""
        return int(self.config_data.get("Last Active Frequency", 100100000))

    def set_last_active_frequency(self, freq_hz: int):
        """Saves current dial frequency parameter coordinates across sessions."""
        self.config_data["Last Active Frequency"] = int(freq_hz)
        self.saveConfig()
        self._notify_observers("Last Active Frequency", freq_hz)

    def get_scan_channels_registry(self) -> dict:
        """Extracts the entire multi-bank scanner registry stack."""
        data = self.config_data.get("Scan Channels Registry Queue", {})
        return data if isinstance(data, dict) else {"DEFAULT SET": []}

    def set_scan_channels_registry(self, registry_dict: dict):
        """Updates and serializes all scanner channel banks to persistent storage."""
        self.config_data["Scan Channels Registry Queue"] = dict(registry_dict)
        self.saveConfig()
        self._notify_observers("Scan Channels Registry Queue", registry_dict)

    def get_sdr_filter_width_hz(self) -> int:
        """Pulls stored bandwidth configuration specifications."""
        return int(self.config_data.get("SDR Filter Width HZ", 120000))

    def set_sdr_filter_width_hz(self, width_hz: int):
        """Commits software intermediate-frequency bandwidth limits to memory."""
        self.config_data["SDR Filter Width HZ"] = int(width_hz)
        self.saveConfig()
        self._notify_observers("SDR Filter Width HZ", width_hz)

    def get_sdr_current_mode(self) -> str:
        """Fetches current modulation footprint identifier selection tag."""
        return str(self.config_data.get("SDR Current Mode", "WFM"))

    def set_sdr_current_mode(self, mode_str: str):
        """Updates internal modulation type selection mapping criteria profiles."""
        self.config_data["SDR Current Mode"] = str(mode_str).strip()
        self.saveConfig()
        self._notify_observers("SDR Current Mode", mode_str)

    def get_audio_gain_level(self) -> int:
        """Pulls audio mixer output coefficient level bounds attributes."""
        return int(self.config_data.get("Audio Gain Volume Level", 50))

    def set_audio_gain_level(self, gain_val: int):
        """Saves operational software volume level settings constraints."""
        self.config_data["Audio Gain Volume Level"] = int(gain_val)
        self.saveConfig()
        self._notify_observers("Audio Gain Volume Level", gain_val)

    #
    #   following is a template on how add new parameters to configuration file
    #
    # def get_Template(self):
    #     if "Template" in self.config_data:
    #         return self.config_data["Template"]
    #     else:
    #         self.config_data["Template"] = "newdefault"
    #         self.saveConfig()
    #         return self.config_data["Template"]
    #
    # def set_Template(self, value):
    #     self.config_data["Template"] = value
    #     self.saveConfig()
