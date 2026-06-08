#!/usr/bin/python3
"""
Log QSO

Completes the logging of a QSO

UI source file: logQSO.ui
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
        self.callsign_Label.pack(pady="0 5")
        self.callsign_Entry = ttk.Entry(
            self.callsign_Frame, name="callsign_entry")
        self.callSign_VAR = tk.StringVar(value='AJ6CU/7')
        self.callsign_Entry.configure(
            font="{Arial} 20 {}",
            style="Entry2b.TEntry",
            textvariable=self.callSign_VAR,
            width=12)
        _text_ = 'AJ6CU/7'
        self.callsign_Entry.delete("0", "end")
        self.callsign_Entry.insert("0", _text_)
        self.callsign_Entry.pack()
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
        self.frequency_Label.grid(column=1, row=0)
        self.mode_Label = ttk.Label(self.freq_Frame, name="mode_label")
        self.mode_Label.configure(style="Heading2b.TLabel", text='Mode')
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
            width=7)
        _text_ = '14.032'
        self.frequency_entry.delete("0", "end")
        self.frequency_entry.insert("0", _text_)
        self.frequency_entry.grid(column=1, row=1, sticky="n")
        self.frequency_ext = ttk.Label(self.freq_Frame, name="frequency_ext")
        self.frequency_ext.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='.000')
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
            width=3)
        self.mode_Menu = tk.Menu(self.mode_Menubutton, name="mode_menu")
        self.mode_Menu.configure(tearoff=False)
        def SSB_cmd(itemid="SSB"): self.selecMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=SSB_cmd,
            font="{Arial} 36 {}",
            label='SSB',
            state="normal")

        def CW_cmd(itemid="CW"): self.selecMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=CW_cmd,
            font="{Arial} 36 {}",
            label='CW',
            state="normal")

        def FT8_cmd(itemid="FT8"): self.selecMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=FT8_cmd,
            font="{Arial} 36 {}",
            label='FT8',
            state="normal")

        def FT4_cmd(itemid="FT4"): self.selecMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=FT4_cmd,
            font="{Arial} 36 {}",
            label='FT4',
            state="normal")

        def FT2_cmd(itemid="FT2"): self.selecMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=FT2_cmd,
            font="{Arial} 36 {}",
            label='FT2',
            state="normal")

        def AM_cmd(itemid="AM"): self.selecMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=AM_cmd,
            font="{Arial} 36 {}",
            label='AM',
            state="normal")

        def FM_cmd(itemid="FM"): self.selecMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=FM_cmd,
            font="{Arial} 36 {}",
            label='FM',
            state="normal")

        def RTTY_cmd(itemid="RTTY"): self.selecMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=RTTY_cmd,
            font="{Arial} 36 {}",
            label='RTTY',
            state="normal")

        def PSK31_cmd(itemid="PSK31"): self.selecMode_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=PSK31_cmd,
            font="{Arial} 36 {}",
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
        self.localLabel = ttk.Label(self.timeDate_Frame, name="locallabel")
        self.localLabel.configure(style="Heading2b.TLabel", text='Local')
        self.localLabel.grid(column=0, padx="0 10", pady="0 10", row=1)
        self.qsoDateLocal_Entry = ttk.Entry(
            self.timeDate_Frame, name="qsodatelocal_entry")
        self.localDate_VAR = tk.StringVar(value='12/28/2026')
        self.qsoDateLocal_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.localDate_VAR,
            width=9)
        _text_ = '12/28/2026'
        self.qsoDateLocal_Entry.delete("0", "end")
        self.qsoDateLocal_Entry.insert("0", _text_)
        self.qsoDateLocal_Entry.grid(column=1, padx="0 15", pady="0 10", row=1)
        self.qsoTimeLocal_Entry = ttk.Entry(
            self.timeDate_Frame, name="qsotimelocal_entry")
        self.localTime_VAR = tk.StringVar(value='230520')
        self.qsoTimeLocal_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.localTime_VAR,
            width=8)
        _text_ = '230520'
        self.qsoTimeLocal_Entry.delete("0", "end")
        self.qsoTimeLocal_Entry.insert("0", _text_)
        self.qsoTimeLocal_Entry.grid(column=2, pady="0 10", row=1)
        self.utc_Label = ttk.Label(self.timeDate_Frame, name="utc_label")
        self.utc_Label.configure(style="Heading2b.TLabel", text='UTC:')
        self.utc_Label.grid(column=0, padx="0 10", row=2)
        self.qsoDateUTC_Entry = ttk.Entry(
            self.timeDate_Frame, name="qsodateutc_entry")
        self.utcDate_VAR = tk.StringVar(value='12/28/2026')
        self.qsoDateUTC_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.utcDate_VAR,
            width=9)
        _text_ = '12/28/2026'
        self.qsoDateUTC_Entry.delete("0", "end")
        self.qsoDateUTC_Entry.insert("0", _text_)
        self.qsoDateUTC_Entry.grid(column=1, padx="0 15", row=2)
        self.qsoTimeUTC_Entry = ttk.Entry(
            self.timeDate_Frame, name="qsotimeutc_entry")
        self.utcTime_VAR = tk.StringVar(value='230520')
        self.qsoTimeUTC_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.utcTime_VAR,
            width=8)
        _text_ = '230520'
        self.qsoTimeUTC_Entry.delete("0", "end")
        self.qsoTimeUTC_Entry.insert("0", _text_)
        self.qsoTimeUTC_Entry.grid(column=2, row=2)
        self.timeDate_Frame.grid(column=0, padx=10, pady="0 30", row=10)
        self.signalReport_Frame = ttk.Frame(
            self.logData_Frame, name="signalreport_frame")
        self.signalReport_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.rstSend_Label = ttk.Label(
            self.signalReport_Frame, name="rstsend_label")
        self.rstSend_Label.configure(style="Heading2b.TLabel", text='RST Sent')
        self.rstSend_Label.grid(column=0, padx="0 20", pady="0 5", row=0)
        self.rstRcvd_Label = ttk.Label(
            self.signalReport_Frame, name="rstrcvd_label")
        self.rstRcvd_Label.configure(style="Heading2b.TLabel", text='RST Rcvd')
        self.rstRcvd_Label.grid(column=1, pady="0 5", row=0)
        self.rstSend_Entry = ttk.Entry(
            self.signalReport_Frame, name="rstsend_entry")
        self.sentRST_VAR = tk.StringVar(value='599')
        self.rstSend_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.sentRST_VAR,
            width=4)
        _text_ = '599'
        self.rstSend_Entry.delete("0", "end")
        self.rstSend_Entry.insert("0", _text_)
        self.rstSend_Entry.grid(column=0, padx="0 20", row=1)
        self.rstRcvd_Entry = ttk.Entry(
            self.signalReport_Frame, name="rstrcvd_entry")
        self.rcvdRST_VAR = tk.StringVar(value='599')
        self.rstRcvd_Entry.configure(
            font="{Arial} 20 {}",
            justify="center",
            style="Entry2b.TEntry",
            textvariable=self.rcvdRST_VAR,
            width=4)
        _text_ = '599'
        self.rstRcvd_Entry.delete("0", "end")
        self.rstRcvd_Entry.insert("0", _text_)
        self.rstRcvd_Entry.grid(column=1, row=1)
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

    def selecMode_CB(self, itemid):
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
