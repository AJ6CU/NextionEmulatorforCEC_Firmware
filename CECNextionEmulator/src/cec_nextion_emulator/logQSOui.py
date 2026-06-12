#!/usr/bin/python3
"""
Log QSO

Completes the logging of a QSO

UI source file: logQSO.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.simpletooltip import Tooltip


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
class logQSOUI(ttk.Labelframe):
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

        self.logData_Frame = ttk.Frame(self, name="logdata_frame")
        self.logData_Frame.configure(
            height=200, style="NormalOutline.TFrame", width=200)
        # First object created
        on_first_object_cb(self.logData_Frame)

        self.callsign_Frame = ttk.Frame(
            self.logData_Frame, name="callsign_frame")
        self.callsign_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.callsign_Label = ttk.Label(
            self.callsign_Frame, name="callsign_label")
        self.callsign_Label.configure(
            style="Heading2b.TLabel", text='Callsign')
        self.callsign_Tooltip = Tooltip(self.callsign_Label)
        self.callsign_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Enter the call sign of the station you QSOed with.',
            wraplength=300)
        self.callsign_Label.pack(pady="0 5")
        self.callsign_Entry = ttk.Entry(
            self.callsign_Frame, name="callsign_entry")
        self.callsign_VAR = tk.StringVar()
        self.callsign_Entry.configure(
            font="{Arial} 20 {}",
            style="Entry2b.TEntry",
            textvariable=self.callsign_VAR,
            validate="focusout",
            width=12)
        self.callsign_Entry.pack()
        _validatecmd = (
            self.callsign_Entry.register(
                self.callsign_Validate_CB), "%P", "%V")
        self.callsign_Entry.configure(validatecommand=_validatecmd)
        _validatecmd = (
            self.callsign_Entry.register(
                self.callsign_Invalid_CB), "%P", "%V")
        self.callsign_Entry.configure(invalidcommand=_validatecmd)
        self.callsign_Entry.bind("<Button>", self.callsign_Entered_CB, add="+")
        self.callsign_Frame.grid(column=0, padx=10, pady="10 30", row=0)
        self.freq_Frame = ttk.Frame(self.logData_Frame, name="freq_frame")
        self.freq_Frame.configure(height=200, style="Normal.TFrame", width=200)
        self.band_Label = ttk.Label(self.freq_Frame, name="band_label")
        self.band_Label.configure(style="Heading2b.TLabel", text='Band')
        self.band_Label.grid(column=0, padx="0 15", row=0)
        self.frequency_Label = ttk.Label(
            self.freq_Frame, name="frequency_label")
        self.frequency_Label.configure(
            style="Heading2b.TLabel", text='Frequency')
        self.frequency_Tooltip = Tooltip(self.frequency_Label)
        self.frequency_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Enter the frequency of the QSO to nearest 1kHZ.',
            wraplength=300)
        self.frequency_Label.grid(column=1, row=0)
        self.mode_Label = ttk.Label(self.freq_Frame, name="mode_label")
        self.mode_Label.configure(style="Heading2b.TLabel", text='Mode')
        self.mode_Tooltip = Tooltip(self.mode_Label)
        self.mode_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Select from the drop down the type of communication.',
            wraplength=300)
        self.mode_Label.grid(column=3, row=0)
        self.imputedBand_Label = ttk.Label(
            self.freq_Frame, name="imputedband_label")
        self.bandName_VAR = tk.StringVar(value='40m')
        self.imputedBand_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='40m',
            textvariable=self.bandName_VAR)
        self.imputedBand_Label.grid(column=0, padx="0 20", row=1, sticky="n")
        self.frequency_entry = ttk.Entry(
            self.freq_Frame, name="frequency_entry")
        self.frequency_VAR = tk.StringVar(value='14.032')
        self.frequency_entry.configure(
            font="{Arial} 20 {}",
            justify="right",
            style="Entry2b.TEntry",
            textvariable=self.frequency_VAR,
            validate="focusout",
            width=7)
        _text_ = '14.032'
        self.frequency_entry.delete("0", "end")
        self.frequency_entry.insert("0", _text_)
        self.frequency_entry.grid(column=1, row=1, sticky="n")
        _validatecmd = (
            self.frequency_entry.register(
                self.frequency_Validate_CB), "%P", "%V")
        self.frequency_entry.configure(validatecommand=_validatecmd)
        _validatecmd = (
            self.frequency_entry.register(
                self.frequency_Invalid_CB), "%P", "%V")
        self.frequency_entry.configure(invalidcommand=_validatecmd)
        self.frequency_entry.bind(
            "<Button>", self.frequency_Entered_CB, add="+")
        self.frequency_ext = ttk.Label(self.freq_Frame, name="frequency_ext")
        self.lowFreqDigits = tk.StringVar(value='.000')
        self.frequency_ext.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='.000',
            textvariable=self.lowFreqDigits)
        self.frequency_ext.grid(
            column=2,
            ipadx=10,
            padx="0 15",
            row=1,
            sticky="n")
        self.mode_Menubutton = ttk.Menubutton(
            self.freq_Frame, name="mode_menubutton")
        self.commType_VAR = tk.StringVar()
        self.mode_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.commType_VAR,
            width=6)
        self.mode_Menu = tk.Menu(self.mode_Menubutton, name="mode_menu")
        self.mode_Menu.configure(tearoff=False)
        def SSB_cmd(itemid="SSB"): self.selectMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=SSB_cmd,
            font="{Arial} 24 {}",
            label='SSB',
            state="normal")

        def CW_cmd(itemid="CW"): self.selectMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=CW_cmd,
            font="{Arial} 24 {}",
            label='CW',
            state="normal")

        def FT8_cmd(itemid="FT8"): self.selectMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=FT8_cmd,
            font="{Arial} 24 {}",
            label='FT8',
            state="normal")

        def FT4_cmd(itemid="FT4"): self.selectMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=FT4_cmd,
            font="{Arial} 24 {}",
            label='FT4',
            state="normal")

        def FT2_cmd(itemid="FT2"): self.selectMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=FT2_cmd,
            font="{Arial} 24 {}",
            label='FT2',
            state="normal")

        def AM_cmd(itemid="AM"): self.selectMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=AM_cmd,
            font="{Arial} 24 {}",
            label='AM',
            state="normal")

        def FM_cmd(itemid="FM"): self.selectMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=FM_cmd,
            font="{Arial} 24 {}",
            label='FM',
            state="normal")

        def RTTY_cmd(itemid="RTTY"): self.selectMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=RTTY_cmd,
            font="{Arial} 24 {}",
            label='RTTY',
            state="normal")

        def PSK31_cmd(itemid="PSK31"): self.selectMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=PSK31_cmd,
            font="{Arial} 24 {}",
            label='PSK31',
            state="normal")
        self.mode_Menubutton.configure(menu=self.mode_Menu)
        self.mode_Menubutton.grid(column=3, row=1)
        self.freq_Frame.grid(padx=10, pady="0 30", row=1)
        self.timeDate_Frame = ttk.Frame(
            self.logData_Frame, name="timedate_frame")
        self.timeDate_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.qsoDate_Label = ttk.Label(
            self.timeDate_Frame, name="qsodate_label")
        self.qsoDate_Label.configure(style="Heading2b.TLabel", text='Date')
        self.qsoDate_Label.grid(column=1, pady="0 5", row=0)
        self.qsoTime_Label = ttk.Label(
            self.timeDate_Frame, name="qsotime_label")
        self.qsoTime_Label.configure(style="Heading2b.TLabel", text='Time')
        self.qsoTime_Label.grid(column=2, pady="0 5", row=0)
        self.utc_Label = ttk.Label(self.timeDate_Frame, name="utc_label")
        self.utc_Label.configure(style="Heading2b.TLabel", text='UTC:')
        self.utc_Label.grid(column=0, row=1)
        self.utcDate_Frame = ttk.Frame(
            self.timeDate_Frame, name="utcdate_frame")
        self.utcDate_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.utcYYYY_Entry = ttk.Entry(
            self.utcDate_Frame, name="utcyyyy_entry")
        self.utcDateYYYY_VAR = tk.StringVar(value='2026')
        self.utcYYYY_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.utcDateYYYY_VAR,
            validate="focusout",
            width=4)
        _text_ = '2026'
        self.utcYYYY_Entry.delete("0", "end")
        self.utcYYYY_Entry.insert("0", _text_)
        self.utcYYYY_Entry.grid(column=1, row=0)
        _validatecmd = (self.utcYYYY_Entry.register(
            self.utcDateYYYY_Validate_CB), "%P", "%V")
        self.utcYYYY_Entry.configure(validatecommand=_validatecmd)
        _validatecmd = (self.utcYYYY_Entry.register(
            self.utcDateYYYY_Invalid_CB), "%P", "%V")
        self.utcYYYY_Entry.configure(invalidcommand=_validatecmd)
        self.utcYYYY_Entry.bind(
            "<Button>",
            self.utcDateYYYY_Entered_CB,
            add="+")
        self.slash1_label = ttk.Label(self.utcDate_Frame, name="slash1_label")
        self.slash1_label.configure(style="Heading1b.TLabel", text='-')
        self.slash1_label.grid(column=2, row=0)
        self.utcMM_Entry = ttk.Entry(self.utcDate_Frame, name="utcmm_entry")
        self.utcDateMM_VAR = tk.StringVar(value='12')
        self.utcMM_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.utcDateMM_VAR,
            validate="focusout",
            width=2)
        _text_ = '12'
        self.utcMM_Entry.delete("0", "end")
        self.utcMM_Entry.insert("0", _text_)
        self.utcMM_Entry.grid(column=3, row=0)
        _validatecmd = (
            self.utcMM_Entry.register(
                self.utcDateMM_Validate_CB),
            "%P",
            "%V")
        self.utcMM_Entry.configure(validatecommand=_validatecmd)
        _validatecmd = (
            self.utcMM_Entry.register(
                self.utcDateMM_Invalid_CB),
            "%P",
            "%V")
        self.utcMM_Entry.configure(invalidcommand=_validatecmd)
        self.utcMM_Entry.bind("<Button>", self.utcDateMM_Entered_CB, add="+")
        self.slash2_Label = ttk.Label(self.utcDate_Frame, name="slash2_label")
        self.slash2_Label.configure(style="Heading1b.TLabel", text='-')
        self.slash2_Label.grid(column=4, row=0)
        self.utc_DD_Entry = ttk.Entry(self.utcDate_Frame, name="utc_dd_entry")
        self.utcDateDD_VAR = tk.StringVar(value='28')
        self.utc_DD_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.utcDateDD_VAR,
            validate="focusout",
            width=2)
        _text_ = '28'
        self.utc_DD_Entry.delete("0", "end")
        self.utc_DD_Entry.insert("0", _text_)
        self.utc_DD_Entry.grid(column=5, row=0)
        _validatecmd = (self.utc_DD_Entry.register(
            self.utcDateDD_Validate_CB), "%P", "%V")
        self.utc_DD_Entry.configure(validatecommand=_validatecmd)
        _validatecmd = (self.utc_DD_Entry.register(
            self.utcDateDD_Invalid_CB), "%P", "%V")
        self.utc_DD_Entry.configure(invalidcommand=_validatecmd)
        self.utc_DD_Entry.bind(
            "<ButtonPress>",
            self.utcDateDD_Entered_CB,
            add="+")
        self.utcDate_Frame.grid(column=1, row=1, sticky="w")
        self.utcTime_Frame = ttk.Frame(
            self.timeDate_Frame, name="utctime_frame")
        self.utcTime_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.utcTimeHH_Entry = ttk.Entry(
            self.utcTime_Frame, name="utctimehh_entry")
        self.utcTimeHH_VAR = tk.StringVar(value='23')
        self.utcTimeHH_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.utcTimeHH_VAR,
            validate="focusout",
            width=2)
        _text_ = '23'
        self.utcTimeHH_Entry.delete("0", "end")
        self.utcTimeHH_Entry.insert("0", _text_)
        self.utcTimeHH_Entry.grid(column=1, row=0)
        _validatecmd = (
            self.utcTimeHH_Entry.register(
                self.utcTimeHH_Validate_CB), "%P", "%V")
        self.utcTimeHH_Entry.configure(validatecommand=_validatecmd)
        _validatecmd = (
            self.utcTimeHH_Entry.register(
                self.utcTimeHH_Invalid_CB), "%P", "%V")
        self.utcTimeHH_Entry.configure(invalidcommand=_validatecmd)
        self.utcTimeHH_Entry.bind(
            "<Button>", self.utcTimeHH_Entered_CB, add="+")
        self.colon1_Label = ttk.Label(self.utcTime_Frame, name="colon1_label")
        self.colon1_Label.configure(style="Heading1b.TLabel", text=':')
        self.colon1_Label.grid(column=2, row=0)
        self.entry5 = ttk.Entry(self.utcTime_Frame, name="entry5")
        self.utcTimeMM_VAR = tk.StringVar(value='12')
        self.entry5.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.utcTimeMM_VAR,
            validate="focusout",
            width=2)
        _text_ = '12'
        self.entry5.delete("0", "end")
        self.entry5.insert("0", _text_)
        self.entry5.grid(column=3, row=0)
        _validatecmd = (
            self.entry5.register(
                self.utcTimeMM_Validate_CB),
            "%P",
            "%V")
        self.entry5.configure(validatecommand=_validatecmd)
        _validatecmd = (
            self.entry5.register(
                self.utcTimeMM_Invalid_CB),
            "%P",
            "%V")
        self.entry5.configure(invalidcommand=_validatecmd)
        self.entry5.bind("<Button>", self.utcTimeMM_Entered_CB, add="+")
        self.utcTime_Frame.grid(column=2, padx=30, row=1, sticky="w")
        self.dateClue_Frame = ttk.Frame(
            self.timeDate_Frame, name="dateclue_frame")
        self.dateClue_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.label10 = ttk.Label(self.dateClue_Frame, name="label10")
        self.label10.configure(style="Heading2b.TLabel", text='YYYY')
        self.label10.grid(column=2, padx="7 0", row=1)
        self.label11 = ttk.Label(self.dateClue_Frame, name="label11")
        self.label11.configure(style="Heading2b.TLabel", text='MM')
        self.label11.grid(column=3, padx="21 0", row=1)
        self.label12 = ttk.Label(self.dateClue_Frame, name="label12")
        self.label12.configure(style="Heading2b.TLabel", text='DD')
        self.label12.grid(column=5, padx="18 0", row=1)
        self.dateClue_Frame.grid(column=1, pady="0 15", row=2, sticky="w")
        self.timeClue_Frame = ttk.Frame(
            self.timeDate_Frame, name="timeclue_frame")
        self.timeClue_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.timeClue_HH_Label = ttk.Label(
            self.timeClue_Frame, name="timeclue_hh_label")
        self.timeClue_HH_Label.configure(style="Heading2b.TLabel", text='HH')
        self.timeClue_HH_Label.grid(column=2, padx="5 0", row=1)
        self.timeClue_MM = ttk.Label(self.timeClue_Frame, name="timeclue_mm")
        self.timeClue_MM.configure(style="Heading2b.TLabel", text='MM')
        self.timeClue_MM.grid(column=3, padx="15 0", row=1)
        self.timeClue_Frame.grid(
            column=2,
            padx=30,
            pady="0 15",
            row=2,
            sticky="w")
        self.localLabel = ttk.Label(self.timeDate_Frame, name="locallabel")
        self.localLabel.configure(style="Heading2b.TLabel", text='Local:')
        self.localLabel.grid(
            column=0,
            padx="0 10",
            pady="0 10",
            row=4,
            sticky="e")
        self.local_date_Label = ttk.Label(
            self.timeDate_Frame, name="local_date_label")
        self.localDate_VAR = tk.StringVar(value='2026-12-28')
        self.local_date_Label.configure(
            style="Heading2b.TLabel",
            text='2026-12-28',
            textvariable=self.localDate_VAR)
        self.local_date_Label.grid(column=1, padx=15, pady="0 10", row=4)
        self.label2 = ttk.Label(self.timeDate_Frame, name="label2")
        self.localTime_VAR = tk.StringVar(value='23:12')
        self.label2.configure(
            style="Heading2b.TLabel",
            text='23:12',
            textvariable=self.localTime_VAR)
        self.label2.grid(column=2, padx=30, pady="0 10", row=4)
        self.timeDate_Frame.grid(column=0, padx=10, pady="0 30", row=10)
        self.signalReport_Frame = ttk.Frame(
            self.logData_Frame, name="signalreport_frame")
        self.signalReport_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.rstSend_Label = ttk.Label(
            self.signalReport_Frame, name="rstsend_label")
        self.rstSend_Label.configure(style="Heading2b.TLabel", text='RST Sent')
        self.rstSend_Tooltip = Tooltip(self.rstSend_Label)
        self.rstSend_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Enter the signal report of the signal you received from the other party (in the appropriate format for your communication mode) ',
            wraplength=300)
        self.rstSend_Label.grid(column=0, padx="0 20", pady="0 5", row=0)
        self.rstRcvd_Label = ttk.Label(
            self.signalReport_Frame, name="rstrcvd_label")
        self.rstRcvd_Label.configure(style="Heading2b.TLabel", text='RST Rcvd')
        self.rstRcvd_Tooltip = Tooltip(self.rstRcvd_Label)
        self.rstRcvd_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Enter the signal report that the other party sent you on the quality of your signal. (in the appropriate format for your communication mode) \n',
            wraplength=300)
        self.rstRcvd_Label.grid(column=1, pady="0 5", row=0)
        self.rstSend_Entry = ttk.Entry(
            self.signalReport_Frame, name="rstsend_entry")
        self.rstSend_VAR = tk.StringVar(value='599')
        self.rstSend_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.rstSend_VAR,
            validate="focusout",
            width=8)
        _text_ = '599'
        self.rstSend_Entry.delete("0", "end")
        self.rstSend_Entry.insert("0", _text_)
        self.rstSend_Entry.grid(column=0, padx="0 20", row=1)
        _validatecmd = (
            self.rstSend_Entry.register(
                self.rstSend_Validate_CB), "%P", "%V")
        self.rstSend_Entry.configure(validatecommand=_validatecmd)
        _validatecmd = (
            self.rstSend_Entry.register(
                self.rstSend_Invalid_CB), "%P", "%V")
        self.rstSend_Entry.configure(invalidcommand=_validatecmd)
        self.rstSend_Entry.bind("<Button>", self.rstSend_Entered_CB, add="+")
        self.rstRcvd_Entry = ttk.Entry(
            self.signalReport_Frame, name="rstrcvd_entry")
        self.rstReceived_VAR = tk.StringVar(value='599')
        self.rstRcvd_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.rstReceived_VAR,
            validate="focusout",
            width=8)
        _text_ = '599'
        self.rstRcvd_Entry.delete("0", "end")
        self.rstRcvd_Entry.insert("0", _text_)
        self.rstRcvd_Entry.grid(column=1, row=1)
        _validatecmd = (self.rstRcvd_Entry.register(
            self.rstReceived_Validate_CB), "%P", "%V")
        self.rstRcvd_Entry.configure(validatecommand=_validatecmd)
        _validatecmd = (self.rstRcvd_Entry.register(
            self.rstReceived_Invalid_CB), "%P", "%V")
        self.rstRcvd_Entry.configure(invalidcommand=_validatecmd)
        self.rstRcvd_Entry.bind(
            "<Button>",
            self.rstReceived_Entered_CB,
            add="+")
        self.signalReport_Frame.grid(column=0, padx=10, pady="0 30", row=11)
        self.logData_Frame.pack(padx=20, side="top")
        self.closingFrame = ttk.Frame(self, name="closingframe")
        self.closingFrame.configure(style="Normal.TFrame")
        self.logQSO_Button = ttk.Button(
            self.closingFrame, name="logqso_button")
        self.startStopSpectrum_VAR = tk.StringVar(value='Log')
        self.logQSO_Button.configure(
            style="Button2b.TButton",
            text='Log',
            textvariable=self.startStopSpectrum_VAR,
            width=10)
        self.logQSO_Button.grid(padx="0 15", row=0)
        self.logQSO_Button.configure(command=self.logQSO_CB)
        self.cancel_Button = ttk.Button(
            self.closingFrame, name="cancel_button")
        self.cancel_Button.configure(
            style="Button2b.TButton", text='Cancel', width=10)
        self.cancel_Button.grid(column=3, row=0)
        self.cancel_Button.configure(command=self.cancel_CB)
        self.closingFrame.pack(pady="20 15", side="top")
        self.closingFrame.grid_anchor("center")
        self.configure(
            height=200,
            style="Heading2.TLabelframe",
            text='Log QSO\n',
            width=200)
        # Layout for 'logQSO_Labelframe' skipped in custom widget template.

    def callsign_Validate_CB(self, p_entry_value, v_condition):
        pass

    def callsign_Invalid_CB(self, p_entry_value, v_condition):
        pass

    def callsign_Entered_CB(self, event=None):
        pass

    def frequency_Validate_CB(self, p_entry_value, v_condition):
        pass

    def frequency_Invalid_CB(self, p_entry_value, v_condition):
        pass

    def frequency_Entered_CB(self, event=None):
        pass

    def selectMode_CB(self, itemid):
        pass

    def utcDateYYYY_Validate_CB(self, p_entry_value, v_condition):
        pass

    def utcDateYYYY_Invalid_CB(self, p_entry_value, v_condition):
        pass

    def utcDateYYYY_Entered_CB(self, event=None):
        pass

    def utcDateMM_Validate_CB(self, p_entry_value, v_condition):
        pass

    def utcDateMM_Invalid_CB(self, p_entry_value, v_condition):
        pass

    def utcDateMM_Entered_CB(self, event=None):
        pass

    def utcDateDD_Validate_CB(self, p_entry_value, v_condition):
        pass

    def utcDateDD_Invalid_CB(self, p_entry_value, v_condition):
        pass

    def utcDateDD_Entered_CB(self, event=None):
        pass

    def utcTimeHH_Validate_CB(self, p_entry_value, v_condition):
        pass

    def utcTimeHH_Invalid_CB(self, p_entry_value, v_condition):
        pass

    def utcTimeHH_Entered_CB(self, event=None):
        pass

    def utcTimeMM_Validate_CB(self, p_entry_value, v_condition):
        pass

    def utcTimeMM_Invalid_CB(self, p_entry_value, v_condition):
        pass

    def utcTimeMM_Entered_CB(self, event=None):
        pass

    def rstSend_Validate_CB(self, p_entry_value, v_condition):
        pass

    def rstSend_Invalid_CB(self, p_entry_value, v_condition):
        pass

    def rstSend_Entered_CB(self, event=None):
        pass

    def rstReceived_Validate_CB(self, p_entry_value, v_condition):
        pass

    def rstReceived_Invalid_CB(self, p_entry_value, v_condition):
        pass

    def rstReceived_Entered_CB(self, event=None):
        pass

    def logQSO_CB(self):
        pass

    def cancel_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = logQSOUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
