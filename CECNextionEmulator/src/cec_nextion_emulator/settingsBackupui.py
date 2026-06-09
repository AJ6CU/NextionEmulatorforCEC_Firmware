#!/usr/bin/python3
"""
settingsBackup

used to bachup and restore critical values

UI source file: settingsBackup.ui
"""
import tkinter as tk
import tkinter.ttk as ttk


def safe_i18n_translator(value):
    """i18n - Setup translator in derived class file"""
    return value


def safe_fo_callback(widget):
    """on first objec callback - Setup callback in derived class file."""
    pass


def safe_image_loader(master, image_name: str):
    """Image loader - Setup image_loader in derived class file."""
    img = None
    try:
        img = tk.PhotoImage(file=image_name, master=master)
    except tk.TclError:
        pass
    return img


#
# Base class definition
#
class settingsBackupUI(ttk.Labelframe):
    def __init__(
        self,
        master=None,
        *,
        translator=None,
        on_first_object_cb=None,
        data_pool=None,
        image_loader=None,
        **kw
    ):
        if translator is None:
            translator = safe_i18n_translator
        _ = translator  # i18n string marker.
        if image_loader is None:
            image_loader = safe_image_loader
        if on_first_object_cb is None:
            on_first_object_cb = safe_fo_callback

        super().__init__(master, **kw)

        frame1 = ttk.Frame(self)
        frame1.configure(height=200, style="Normal.TFrame", width=200)
        # First object created
        on_first_object_cb(frame1)

        self.backupSettings_Frame = ttk.Frame(
            frame1, name="backupsettings_frame")
        self.backupSettings_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.label29 = ttk.Label(self.backupSettings_Frame, name="label29")
        self.label29.configure(
            anchor="w",
            justify="right",
            style="Heading1b.TLabel",
            text='Select')
        self.label29.grid(column=0, padx=5, row=0, sticky="w")
        self.label14 = ttk.Label(self.backupSettings_Frame, name="label14")
        self.label14.configure(
            anchor="w",
            justify="right",
            style="Heading1b.TLabel",
            text='Setting')
        self.label14.grid(column=1, padx=5, row=0, sticky="w")
        self.label15 = ttk.Label(self.backupSettings_Frame, name="label15")
        self.label15.configure(
            anchor="e",
            justify="center",
            style="Heading1b.TLabel",
            text='Factory\nValue')
        self.label15.grid(column=2, row=0, sticky="ew")
        self.label16 = ttk.Label(self.backupSettings_Frame, name="label16")
        self.label16.configure(
            anchor="e",
            justify="center",
            style="Heading1b.TLabel",
            text='Current\nValue')
        self.label16.grid(column=3, row=0, sticky="ew")
        self.label17 = ttk.Label(self.backupSettings_Frame, name="label17")
        self.label17.configure(
            anchor="e",
            justify="center",
            style="Heading1b.TLabel",
            text='Config\nFile')
        self.label17.grid(column=4, row=0, sticky="ew")
        frame2 = ttk.Frame(self.backupSettings_Frame)
        frame2.configure(height=200, width=200)
        separator1 = ttk.Separator(frame2)
        separator1.configure(orient="horizontal")
        separator1.pack(expand=True, fill="x", side="top")
        frame2.grid(column=0, columnspan=5, row=1, sticky="ew")
        self.Master_Cal = ttk.Button(
            self.backupSettings_Frame, name="master_cal")
        self.Master_Cal_VAR = tk.StringVar(value='No')
        self.Master_Cal.configure(
            style="Button2Raised.TButton",
            text='No',
            textvariable=self.Master_Cal_VAR,
            width=5)
        self.Master_Cal.grid(column=0, pady=15, row=3)
        def Master_Cal_cmd_(): self.selectSetting_CB("Master_Cal")

        self.Master_Cal.configure(command=Master_Cal_cmd_)
        self.Master_Cal_Heading_Label = ttk.Label(
            self.backupSettings_Frame, name="master_cal_heading_label")
        self.Master_Cal_Heading_Label.configure(
            anchor="w", style="Heading1b.TLabel", text='Master Cal', width=10)
        self.Master_Cal_Heading_Label.grid(column=1, padx=5, pady=5, row=3)
        self.EEPROM_Factory_Master_Cal_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_factory_master_cal_label")
        self.EEPROM_Factory_Master_Cal_VAR = tk.StringVar(value='label3')
        self.EEPROM_Factory_Master_Cal_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label3',
            textvariable=self.EEPROM_Factory_Master_Cal_VAR,
            width=10)
        self.EEPROM_Factory_Master_Cal_Label.grid(
            column=2, padx="0 5", pady=5, row=3, sticky="e")
        self.EEPROM_Current_Master_Cal_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_current_master_cal_label")
        self.EEPROM_Current_Master_Cal_VAR = tk.StringVar(value='label4')
        self.EEPROM_Current_Master_Cal_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.EEPROM_Current_Master_Cal_VAR,
            width=10)
        self.EEPROM_Current_Master_Cal_Label.grid(
            column=3, padx="0 5", pady=5, row=3, sticky="e")
        self.ConfigFile_Master_Cal_Label = ttk.Label(
            self.backupSettings_Frame, name="configfile_master_cal_label")
        self.ConfigFile_Master_Cal_VAR = tk.StringVar(value='label4')
        self.ConfigFile_Master_Cal_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.ConfigFile_Master_Cal_VAR,
            width=10)
        self.ConfigFile_Master_Cal_Label.grid(
            column=4, padx="0 5", pady=5, row=3, sticky="e")
        self.SSB_BFO = ttk.Button(self.backupSettings_Frame, name="ssb_bfo")
        self.SSB_BFO_VAR = tk.StringVar(value='No')
        self.SSB_BFO.configure(
            cursor="arrow",
            style="Button2Raised.TButton",
            text='No',
            textvariable=self.SSB_BFO_VAR,
            width=5)
        self.SSB_BFO.grid(column=0, pady="0 15", row=4)
        def SSB_BFO_cmd_(): self.selectSetting_CB("SSB_BFO")

        self.SSB_BFO.configure(command=SSB_BFO_cmd_)
        self.SSB_BFO_Heading_Label = ttk.Label(
            self.backupSettings_Frame, name="ssb_bfo_heading_label")
        self.SSB_BFO_Heading_Label.configure(
            anchor="w", style="Heading1b.TLabel", text='SSB BFO', width=10)
        self.SSB_BFO_Heading_Label.grid(column=1, padx=5, pady="0 5", row=4)
        self.EEPROM_Factory_SSB_BFO_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_factory_ssb_bfo_label")
        self.EEPROM_Factory_SSB_BFO_VAR = tk.StringVar(value='label3')
        self.EEPROM_Factory_SSB_BFO_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label3',
            textvariable=self.EEPROM_Factory_SSB_BFO_VAR,
            width=10)
        self.EEPROM_Factory_SSB_BFO_Label.grid(
            column=2, padx="0 5", pady="0 5", row=4, sticky="e")
        self.EEPROM_Current_SSB_BFO_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_current_ssb_bfo_label")
        self.EEPROM_Current_SSB_BFO_VAR = tk.StringVar(value='label4')
        self.EEPROM_Current_SSB_BFO_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.EEPROM_Current_SSB_BFO_VAR,
            width=10)
        self.EEPROM_Current_SSB_BFO_Label.grid(
            column=3, padx="0 5", pady="0 5", row=4, sticky="e")
        self.ConfigFile_SSB_BFO_Label = ttk.Label(
            self.backupSettings_Frame, name="configfile_ssb_bfo_label")
        self.ConfigFile_SSB_BFO_VAR = tk.StringVar(value='label4')
        self.ConfigFile_SSB_BFO_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.ConfigFile_SSB_BFO_VAR,
            width=10)
        self.ConfigFile_SSB_BFO_Label.grid(
            column=4, padx="0 5", pady="0 5", row=4, sticky="e")
        self.CW_BFO = ttk.Button(self.backupSettings_Frame, name="cw_bfo")
        self.CW_BFO_VAR = tk.StringVar(value='No')
        self.CW_BFO.configure(
            cursor="arrow",
            style="Button2Raised.TButton",
            text='No',
            textvariable=self.CW_BFO_VAR,
            width=5)
        self.CW_BFO.grid(column=0, pady="0 15", row=5)
        def CW_BFO_cmd_(): self.selectSetting_CB("CW_BFO")

        self.CW_BFO.configure(command=CW_BFO_cmd_)
        self.CW_BFO_Heading_Label = ttk.Label(
            self.backupSettings_Frame, name="cw_bfo_heading_label")
        self.CW_BFO_Heading_Label.configure(
            anchor="w", style="Heading1b.TLabel", text='CW BFO', width=10)
        self.CW_BFO_Heading_Label.grid(column=1, padx=5, pady="0 5", row=5)
        self.EEPROM_Factory_CW_BFO_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_factory_cw_bfo_label")
        self.EEPROM_Factory_CW_BFO_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='N/A',
            width=10)
        self.EEPROM_Factory_CW_BFO_Label.grid(
            column=2, padx="0 5", pady="0 5", row=5, sticky="e")
        self.EEPROM_Current_CW_BFO_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_current_cw_bfo_label")
        self.EEPROM_Current_CW_BFO_VAR = tk.StringVar(value='label4')
        self.EEPROM_Current_CW_BFO_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.EEPROM_Current_CW_BFO_VAR,
            width=10)
        self.EEPROM_Current_CW_BFO_Label.grid(
            column=3, padx="0 5", pady="0 5", row=5, sticky="e")
        self.ConfigFIle_CW_BFO_Label = ttk.Label(
            self.backupSettings_Frame, name="configfile_cw_bfo_label")
        self.ConfigFIle_CW_BFO_VAR = tk.StringVar(value='label4')
        self.ConfigFIle_CW_BFO_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.ConfigFIle_CW_BFO_VAR,
            width=10)
        self.ConfigFIle_CW_BFO_Label.grid(
            column=4, padx="0 5", pady="0 5", row=5, sticky="e")
        self.CW_Keytype = ttk.Button(
            self.backupSettings_Frame, name="cw_keytype")
        self.CW_Keytype_VAR = tk.StringVar(value='No')
        self.CW_Keytype.configure(
            style="Button2Raised.TButton",
            text='No',
            textvariable=self.CW_Keytype_VAR,
            width=5)
        self.CW_Keytype.grid(column=0, pady="0 15", row=6)
        def CW_Keytype_cmd_(): self.selectSetting_CB("CW_Keytype")

        self.CW_Keytype.configure(command=CW_Keytype_cmd_)
        self.CW_Keytype_Heading_Label = ttk.Label(
            self.backupSettings_Frame, name="cw_keytype_heading_label")
        self.CW_Keytype_Heading_Label.configure(
            anchor="w", style="Heading1b.TLabel", text='Keytype', width=10)
        self.CW_Keytype_Heading_Label.grid(column=1, padx=5, pady="0 5", row=6)
        self.EEPROM_Factory_CW_Keytype_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_factory_cw_keytype_label")
        self.EEPROM_Factory_CW_Keytype_Label.configure(
            anchor="e", justify="right", style="Heading1Std.TLabel", text='N/A', width=10)
        self.EEPROM_Factory_CW_Keytype_Label.grid(
            column=2, padx="0 5", pady="0 5", row=6, sticky="e")
        self.EEPROM_Current_CW_Keytype_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_current_cw_keytype_label")
        self.EEPROM_Current_CW_Keytype_VAR = tk.StringVar(value='label4')
        self.EEPROM_Current_CW_Keytype_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.EEPROM_Current_CW_Keytype_VAR,
            width=10)
        self.EEPROM_Current_CW_Keytype_Label.grid(
            column=3, padx="0 5", pady="0 5", row=6, sticky="e")
        self.ConfigFile_CW_Keytype_Label = ttk.Label(
            self.backupSettings_Frame, name="configfile_cw_keytype_label")
        self.ConfigFile_CW_Keytype_VAR = tk.StringVar(value='label4')
        self.ConfigFile_CW_Keytype_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.ConfigFile_CW_Keytype_VAR,
            width=10)
        self.ConfigFile_CW_Keytype_Label.grid(
            column=4, padx="0 5", pady="0 5", row=6, sticky="e")
        self.CW_Speed = ttk.Button(self.backupSettings_Frame, name="cw_speed")
        self.CW_Speed_VAR = tk.StringVar(value='No')
        self.CW_Speed.configure(
            cursor="arrow",
            style="Button2Raised.TButton",
            text='No',
            textvariable=self.CW_Speed_VAR,
            width=5)
        self.CW_Speed.grid(column=0, pady="0 15", row=7)
        def CW_Speed_cmd_(): self.selectSetting_CB("CW_Speed")

        self.CW_Speed.configure(command=CW_Speed_cmd_)
        self.CW_Speed_Heading_Label = ttk.Label(
            self.backupSettings_Frame, name="cw_speed_heading_label")
        self.CW_Speed_Heading_Label.configure(
            anchor="w", style="Heading1b.TLabel", text='CW Speed', width=10)
        self.CW_Speed_Heading_Label.grid(column=1, padx=5, pady="0 5", row=7)
        self.EEPROM_Factory_CW_Speed_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_factory_cw_speed_label")
        self.EEPROM_Factory_CW_Speed_VAR = tk.StringVar(value='label6')
        self.EEPROM_Factory_CW_Speed_Label.configure(
            anchor="e",
            style="Heading1Std.TLabel",
            text='label6',
            textvariable=self.EEPROM_Factory_CW_Speed_VAR,
            width=10)
        self.EEPROM_Factory_CW_Speed_Label.grid(
            column=2, padx="0 5", pady="0 5", row=7, sticky="e")
        self.EEPROM_Current_CW_Speed_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_current_cw_speed_label")
        self.EEPROM_Current_CW_Speed_VAR = tk.StringVar(value='label4')
        self.EEPROM_Current_CW_Speed_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.EEPROM_Current_CW_Speed_VAR,
            width=10)
        self.EEPROM_Current_CW_Speed_Label.grid(
            column=3, padx="0 5", pady="0 5", row=7, sticky="e")
        self.ConfigFile_CW_Speed_Label = ttk.Label(
            self.backupSettings_Frame, name="configfile_cw_speed_label")
        self.ConfigFIle_CW_Speed_VAR = tk.StringVar(value='label4')
        self.ConfigFile_CW_Speed_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.ConfigFIle_CW_Speed_VAR,
            width=10)
        self.ConfigFile_CW_Speed_Label.grid(
            column=4, padx="0 5", pady="0 5", row=7, sticky="e")
        self.CW_Sidetone = ttk.Button(
            self.backupSettings_Frame, name="cw_sidetone")
        self.CW_Sidetone_VAR = tk.StringVar(value='No')
        self.CW_Sidetone.configure(
            cursor="arrow",
            style="Button2Raised.TButton",
            text='No',
            textvariable=self.CW_Sidetone_VAR,
            width=5)
        self.CW_Sidetone.grid(column=0, pady="0 15", row=8)
        def CW_Sidetone_cmd_(): self.selectSetting_CB("CW_Sidetone")

        self.CW_Sidetone.configure(command=CW_Sidetone_cmd_)
        self.CW_Sidetone_Heading_Label = ttk.Label(
            self.backupSettings_Frame, name="cw_sidetone_heading_label")
        self.CW_Sidetone_Heading_Label.configure(
            anchor="w", style="Heading1b.TLabel", text='Sidetone', width=10)
        self.CW_Sidetone_Heading_Label.grid(
            column=1, padx=5, pady="0 5", row=8)
        self.EEPROM_Factory_CW_Sidetone_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_factory_cw_sidetone_label")
        self.EEPROM_Factory_CW_Sidetone_VAR = tk.StringVar(value='label10')
        self.EEPROM_Factory_CW_Sidetone_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label10',
            textvariable=self.EEPROM_Factory_CW_Sidetone_VAR,
            width=10)
        self.EEPROM_Factory_CW_Sidetone_Label.grid(
            column=2, padx="0 5", pady="0 5", row=8, sticky="e")
        self.EEPROM_Current_CW_Sidetone_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_current_cw_sidetone_label")
        self.EEPROM_Current_CW_Sidetone_VAR = tk.StringVar(value='label4')
        self.EEPROM_Current_CW_Sidetone_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.EEPROM_Current_CW_Sidetone_VAR,
            width=10)
        self.EEPROM_Current_CW_Sidetone_Label.grid(
            column=3, padx="0 5", pady="0 5", row=8, sticky="e")
        self.ConfigFile_CW_Sidetone_Label = ttk.Label(
            self.backupSettings_Frame, name="configfile_cw_sidetone_label")
        self.ConfigFile_CW_Sidetone_VAR = tk.StringVar(value='label4')
        self.ConfigFile_CW_Sidetone_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.ConfigFile_CW_Sidetone_VAR,
            width=10)
        self.ConfigFile_CW_Sidetone_Label.grid(
            column=4, padx="0 5", pady="0 5", row=8, sticky="e")
        self.CW_Delay_Before_TX = ttk.Button(
            self.backupSettings_Frame, name="cw_delay_before_tx")
        self.CW_Delay_Before_TX_VAR = tk.StringVar(value='No')
        self.CW_Delay_Before_TX.configure(
            cursor="arrow",
            style="Button2Raised.TButton",
            text='No',
            textvariable=self.CW_Delay_Before_TX_VAR,
            width=5)
        self.CW_Delay_Before_TX.grid(column=0, pady="0 15", row=9)
        def CW_Delay_Before_TX_cmd_(): self.selectSetting_CB("CW_Delay_Before_TX")

        self.CW_Delay_Before_TX.configure(command=CW_Delay_Before_TX_cmd_)
        self.CW_Delay_Before_TX_Heading_Label = ttk.Label(
            self.backupSettings_Frame, name="cw_delay_before_tx_heading_label")
        self.CW_Delay_Before_TX_Heading_Label.configure(
            anchor="w", style="Heading1b.TLabel", text='Delay->TX', width=10)
        self.CW_Delay_Before_TX_Heading_Label.grid(
            column=1, padx=5, pady="0 5", row=9)
        self.EEPROM_Factory_CW_Delay_Before_TX = ttk.Label(
            self.backupSettings_Frame, name="eeprom_factory_cw_delay_before_tx")
        self.EEPROM_Factory_CW_Delay_Before_TX.configure(
            anchor="e", justify="right", style="Heading1Std.TLabel", text='N/A', width=10)
        self.EEPROM_Factory_CW_Delay_Before_TX.grid(
            column=2, padx="0 5", pady="0 5", row=9, sticky="e")
        self.EEPROM_Current_CW_Delay_Before_TX = ttk.Label(
            self.backupSettings_Frame, name="eeprom_current_cw_delay_before_tx")
        self.EEPROM_Current_CW_Delay_Before_TX_VAR = tk.StringVar(
            value='label4')
        self.EEPROM_Current_CW_Delay_Before_TX.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.EEPROM_Current_CW_Delay_Before_TX_VAR,
            width=10)
        self.EEPROM_Current_CW_Delay_Before_TX.grid(
            column=3, padx="0 5", pady="0 5", row=9, sticky="e")
        self.ConfigFile_CW_Delay_Before_TX_Label = ttk.Label(
            self.backupSettings_Frame, name="configfile_cw_delay_before_tx_label")
        self.ConfigFile_CW_Delay_Before_TX_VAR = tk.StringVar(value='label4')
        self.ConfigFile_CW_Delay_Before_TX_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.ConfigFile_CW_Delay_Before_TX_VAR,
            width=10)
        self.ConfigFile_CW_Delay_Before_TX_Label.grid(
            column=4, padx="0 5", pady="0 5", row=9, sticky="e")
        self.CW_Delay_Before_RX = ttk.Button(
            self.backupSettings_Frame, name="cw_delay_before_rx")
        self.CW_Delay_Before_RX_VAR = tk.StringVar(value='No')
        self.CW_Delay_Before_RX.configure(
            cursor="arrow",
            style="Button2Raised.TButton",
            text='No',
            textvariable=self.CW_Delay_Before_RX_VAR,
            width=5)
        self.CW_Delay_Before_RX.grid(column=0, pady="0 15", row=10)
        def CW_Delay_Before_RX_cmd_(): self.selectSetting_CB("CW_Delay_Before_RX")

        self.CW_Delay_Before_RX.configure(command=CW_Delay_Before_RX_cmd_)
        self.CW_Delay_Returning_To_RX_Heading_Label = ttk.Label(
            self.backupSettings_Frame, name="cw_delay_returning_to_rx_heading_label")
        self.CW_Delay_Returning_To_RX_Heading_Label.configure(
            anchor="w", style="Heading1b.TLabel", text='Delay->RX', width=10)
        self.CW_Delay_Returning_To_RX_Heading_Label.grid(
            column=1, padx=5, pady="0 5", row=10)
        self.EEPROM_Factory_CW_Delay_Returning_To_RX_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_factory_cw_delay_returning_to_rx_label")
        self.EEPROM_Factory_CW_Delay_Returning_To_RX_VAR = tk.StringVar(
            value='N/A')
        self.EEPROM_Factory_CW_Delay_Returning_To_RX_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='N/A',
            textvariable=self.EEPROM_Factory_CW_Delay_Returning_To_RX_VAR,
            width=10)
        self.EEPROM_Factory_CW_Delay_Returning_To_RX_Label.grid(
            column=2, padx="0 5", pady="0 5", row=10, sticky="e")
        self.EEPROM_Current_CW_Delay_Returning_To_RX_Label = ttk.Label(
            self.backupSettings_Frame, name="eeprom_current_cw_delay_returning_to_rx_label")
        self.EEPROM_Current_CW_Delay_Returning_To_RX_Label_VAR = tk.StringVar(
            value='label4')
        self.EEPROM_Current_CW_Delay_Returning_To_RX_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.EEPROM_Current_CW_Delay_Returning_To_RX_Label_VAR,
            width=10)
        self.EEPROM_Current_CW_Delay_Returning_To_RX_Label.grid(
            column=3, padx="0 5", pady="0 5", row=10, sticky="e")
        self.ConfigFIle_CW_Delay_Returning_To_RX_Label = ttk.Label(
            self.backupSettings_Frame, name="configfile_cw_delay_returning_to_rx_label")
        self.ConfigFIle_CW_Delay_Returning_To_RX_VAR = tk.StringVar(
            value='label4')
        self.ConfigFIle_CW_Delay_Returning_To_RX_Label.configure(
            anchor="e",
            justify="right",
            style="Heading1Std.TLabel",
            text='label4',
            textvariable=self.ConfigFIle_CW_Delay_Returning_To_RX_VAR,
            width=10)
        self.ConfigFIle_CW_Delay_Returning_To_RX_Label.grid(
            column=4, padx="0 5", pady="0 5", row=10, sticky="e")
        frame3 = ttk.Frame(self.backupSettings_Frame)
        frame3.configure(height=200, width=200)
        separator2 = ttk.Separator(frame3)
        separator2.configure(orient="horizontal")
        separator2.pack(expand=True, fill="x", side="top")
        frame3.grid(column=0, columnspan=5, row=11, sticky="ew")
        frame5 = ttk.Frame(self.backupSettings_Frame)
        frame5.configure(height=200, style="Normal.TFrame", width=200)
        self.select_All = ttk.Button(frame5, name="select_all")
        self.select_All_VAR = tk.StringVar(value='Select All')
        self.select_All.configure(
            style="Button2Raised.TButton",
            text='Select All',
            textvariable=self.select_All_VAR,
            width=10)
        self.select_All.pack(pady=15)
        self.select_All.configure(command=self.select_All_Checkbutton_CB)
        frame5.grid(column=0, columnspan=4, row=12, sticky="w")
        self.backupSettings_Frame.pack(
            anchor="center", expand=True, fill="x", side="top")
        self.backupSettings_Frame.grid_anchor("center")
        self.action_Frame = ttk.Frame(frame1, name="action_frame")
        self.action_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.from_Label = ttk.Label(self.action_Frame, name="from_label")
        self.from_Label.configure(style="Heading1b.TLabel", text='Source:')
        self.from_Label.grid(column=2, padx="10 0", row=0)
        self.to_Label = ttk.Label(self.action_Frame, name="to_label")
        self.to_Label.configure(style="Heading1b.TLabel", text='Destination:')
        self.to_Label.grid(column=4, padx="40 0", row=0)
        self.from_Menubutton = ttk.Menubutton(
            self.action_Frame, name="from_menubutton")
        self.from_Source_VAR = tk.StringVar(value='Select')
        self.from_Menubutton.configure(
            style="Heading0.TMenubutton",
            text='Select',
            textvariable=self.from_Source_VAR,
            width=10)
        self.from_Menu = tk.Menu(self.from_Menubutton, name="from_menu")
        self.from_Menu.configure(tearoff=False)
        self.from_Menu.add(
            "command",
            command=self.selectFrom_Factory_CB,
            font="{Arial} 24 {}",
            label='Factory',
            state="normal")
        self.from_Menu.add(
            "command",
            command=self.selectFrom_Current_CB,
            font="{Arial} 24 {}",
            label='Current',
            state="normal")
        self.from_Menu.add(
            "command",
            command=self.selectFrom_ConfigFile_CB,
            font="{Arial} 24 {}",
            label='ConfigFile',
            state="normal")
        self.from_Menubutton.configure(menu=self.from_Menu)
        self.from_Menubutton.grid(
            column=3,
            padx="15 5",
            pady=10,
            row=0,
            sticky="w")
        self.to_Menubutton = ttk.Menubutton(
            self.action_Frame, name="to_menubutton")
        self.to_Source_VAR = tk.StringVar(value='Select')
        self.to_Menubutton.configure(
            style="Heading0.TMenubutton",
            text='Select',
            textvariable=self.to_Source_VAR,
            width=10)
        self.to_Menu = tk.Menu(self.to_Menubutton, name="to_menu")
        self.to_Menu.configure(tearoff=False)
        self.to_Menu.add(
            "command",
            command=self.selectTo_Current_CB,
            font="{Arial} 24 {}",
            label='Current',
            state="normal")
        self.to_Menu.add(
            "command",
            command=self.selectTo_ConfigFile_CB,
            font="{Arial} 24 {}",
            label='ConfigFile',
            state="normal")
        self.to_Menubutton.configure(menu=self.to_Menu)
        self.to_Menubutton.grid(
            column=5,
            padx="15 10",
            pady=10,
            row=0,
            sticky="w")
        self.action_Frame.pack(
            anchor="center",
            expand=True,
            fill="x",
            pady="10 0",
            side="top")
        self.action_Frame.grid_anchor("center")
        self.closingFrame = ttk.Frame(frame1, name="closingframe")
        self.closingFrame.configure(
            height=50, style="Normal.TFrame", width=200)
        self.apply_Button = ttk.Button(self.closingFrame, name="apply_button")
        self.apply_Button.configure(style="Button2b.TButton", text='Copy')
        self.apply_Button.pack(padx=10, side="left")
        self.apply_Button.configure(command=self.copy_CB)
        self.cancel_Buttom = ttk.Button(
            self.closingFrame, name="cancel_buttom")
        self.cancel_Buttom.configure(style="Button2b.TButton", text='Cancel')
        self.cancel_Buttom.pack(padx=10, side="left")
        self.cancel_Buttom.configure(command=self.cancel_CB)
        self.closingFrame.pack(
            anchor="center",
            expand=False,
            pady=20,
            side="top")
        frame1.pack(anchor="center", expand=True, fill="both", side="top")
        self.configure(
            height=400,
            style="Heading2.TLabelframe",
            text='Radio Backup',
            width=600)
        # Layout for 'labelframe1' skipped in custom widget template.

    def selectSetting_CB(self, widget_id):
        pass

    def select_All_Checkbutton_CB(self):
        pass

    def selectFrom_Factory_CB(self):
        pass

    def selectFrom_Current_CB(self):
        pass

    def selectFrom_ConfigFile_CB(self):
        pass

    def selectTo_Current_CB(self):
        pass

    def selectTo_ConfigFile_CB(self):
        pass

    def copy_CB(self):
        pass

    def cancel_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsBackupUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
