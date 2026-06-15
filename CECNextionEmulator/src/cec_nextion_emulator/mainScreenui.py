#!/usr/bin/python3
"""
pi_Nextion_UX

A Nextion GUI emulator for CEC

UI source file: mainScreen.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from JogwheelCustom import JogwheelCustom
from pygubu.widgets.simpletooltip import Tooltip
from theVFO import theVFO


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
class mainScreenUI(ttk.Frame):
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

        self.menuBar_Frame = ttk.Frame(self, name="menubar_frame")
        self.menuBar_Frame.configure(
            borderwidth=5,
            height=50,
            style="Normal.TFrame",
            width=1250)
        # First object created
        on_first_object_cb(self.menuBar_Frame)

        self.settings_Button = ttk.Button(
            self.menuBar_Frame, name="settings_button")
        self.settings_VAR = tk.StringVar(value='  \nSETTINGS\n  ')
        self.settings_Button.configure(
            style="Button2b.TButton",
            text='  \nSETTINGS\n  ',
            textvariable=self.settings_VAR,
            width=12)
        self.settings_Button_Tooltip = Tooltip(self.settings_Button)
        self.settings_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to bring up a menu of settings that allow you to tune this software.',
            wraplength=300)
        self.settings_Button.grid(column=0, padx="0 2", row=0, sticky="ns")
        self.settings_Button.configure(command=self.settings_CB)
        self.vfo_Button = ttk.Button(self.menuBar_Frame, name="vfo_button")
        self.vfo_VAR = tk.StringVar(value='\nVFO\n')
        self.vfo_Button.configure(
            state="normal",
            style="Button2b.TButton",
            text='\nVFO\n',
            textvariable=self.vfo_VAR,
            width=12)
        self.vfo_Button_Tooltip = Tooltip(self.vfo_Button)
        self.vfo_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to switch between VFO-A and VFO-B',
            wraplength=300)
        self.vfo_Button.grid(column=1, padx="0 2", row=0, sticky="ns")
        self.vfo_Button.configure(command=self.vfo_CB)
        self.mode_select_Menubutton = ttk.Menubutton(
            self.menuBar_Frame, name="mode_select_menubutton")
        self.primary_Mode_VAR = tk.StringVar(value=' \nMode\n')
        self.mode_select_Menubutton.configure(
            style="Heading2b.TMenubutton",
            text=' \nMode\n',
            textvariable=self.primary_Mode_VAR,
            width=9)
        menu1 = tk.Menu(self.mode_select_Menubutton)
        menu1.configure(tearoff=False)
        menu1.add(
            "command",
            command=self.mode_lsb_CB,
            font="{Arial} 24 {}",
            label='LSB',
            state="normal")
        menu1.add(
            "command",
            command=self.mode_usb_CB,
            font="{Arial} 24 {}",
            label='USB',
            state="normal")
        menu1.add(
            "command",
            command=self.mode_cwl_CB,
            font="{Arial} 24 {}",
            label='CWL',
            state="normal")
        menu1.add(
            "command",
            command=self.mode_cwu_CB,
            font="{Arial} 24 {}",
            label='CWU',
            state="normal")
        self.mode_select_Menubutton.configure(menu=menu1)
        self.mode_select_Menubutton.grid(
            column=2, padx="0 2", row=0, sticky="ns")
        self.band_up_Button = ttk.Button(
            self.menuBar_Frame, name="band_up_button")
        self.band_up_VAR = tk.StringVar(value='\nBAND UP\n')
        self.band_up_Button.configure(
            style="Button2b.TButton",
            text='\nBAND UP\n',
            textvariable=self.band_up_VAR,
            width=12)
        self.band_up_Tooltip = Tooltip(self.band_up_Button)
        self.band_up_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to move the VFO to the next higher band',
            wraplength=300)
        self.band_up_Button.grid(column=3, padx="0 2", row=0, sticky="ns")
        self.band_up_Button.configure(command=self.band_up_CB)
        self.band_down_Button = ttk.Button(
            self.menuBar_Frame, name="band_down_button")
        self.band_down_VAR = tk.StringVar(value='\nBAND DN\n')
        self.band_down_Button.configure(
            style="Button2b.TButton",
            text='\nBAND DN\n',
            textvariable=self.band_down_VAR,
            width=12)
        self.band_down_tooltip = Tooltip(self.band_down_Button)
        self.band_down_tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to move the VFO to the next lower band',
            wraplength=300)
        self.band_down_Button.grid(column=4, padx="0 2", row=0, sticky="ns")
        self.band_down_Button.configure(command=self.band_down_CB)
        self.lock_Button = ttk.Button(self.menuBar_Frame, name="lock_button")
        self.lock_VAR = tk.StringVar(value='\nLOCK\n')
        self.lock_Button.configure(
            style="Button2b.TButton",
            text='\nLOCK\n',
            textvariable=self.lock_VAR,
            width=12)
        self.lock_Button_Tooltip = Tooltip(self.lock_Button)
        self.lock_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to lock/unlock all the screen settings.',
            wraplength=300)
        self.lock_Button.grid(column=5, padx="0 2", row=0, sticky="ns")
        self.lock_Button.configure(command=self.lock_CB)
        self.speaker_Button = ttk.Button(
            self.menuBar_Frame, name="speaker_button")
        self.speaker_VAR = tk.StringVar(value='\nSPEAKER\n')
        self.speaker_Button.configure(
            style="Button2b.TButton",
            text='\nSPEAKER\n',
            textvariable=self.speaker_VAR,
            width=12)
        self.speaker_Button_Tooltip = Tooltip(self.speaker_Button)
        self.speaker_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to toggle between speaker output and mute',
            wraplength=300)
        self.speaker_Button.grid(column=6, row=0, sticky="ns")
        self.speaker_Button.configure(command=self.speaker_CB)
        self.menuBar_Frame.pack(anchor="n", expand=True, fill="x", side="top")
        frame2 = ttk.Frame(self)
        frame2.configure(
            height=200,
            relief="sunken",
            style="Normal.TFrame",
            width=1250)
        self.theVFO_Object = theVFO(frame2, name="thevfo_object")
        self.theVFO_Object.grid(column=0, pady="5 0", row=0)
        self.control_Meter_Tuning_Frame = ttk.Frame(
            frame2, name="control_meter_tuning_frame")
        self.control_Meter_Tuning_Frame.configure(
            borderwidth=0, height=200, style="Normal.TFrame", width=200)
        self.secondary_menu_Frame = ttk.Frame(
            self.control_Meter_Tuning_Frame,
            name="secondary_menu_frame")
        self.secondary_menu_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.signal_Control_Frame = ttk.Frame(
            self.secondary_menu_Frame, name="signal_control_frame")
        self.signal_Control_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.channels_Button = ttk.Button(
            self.signal_Control_Frame, name="channels_button")
        self.channels_Button.configure(
            style="Button2b.TButton",
            text='\nCHANNELS\n',
            width=11)
        self.channels_Button_Tooltip = Tooltip(self.channels_Button)
        self.channels_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to bring up the Channels window where you can edit your favorite frequencies and scan sets of channels.',
            wraplength=300)
        self.channels_Button.pack(anchor="nw", padx="0 10", side="left")
        self.channels_Button.configure(command=self.channels_CB)
        self.cwDecode_Button = ttk.Button(
            self.signal_Control_Frame, name="cwdecode_button")
        self.cwDecode_Button.configure(
            style="Button2b.TButton",
            text='\nCW DECODE\n',
            width=11)
        self.cwDecode_Button_Tooltip = Tooltip(self.cwDecode_Button)
        self.cwDecode_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to bring up a window that allows you to scan 240kHz and select an area to decode CW. This requires a second Nano.',
            wraplength=300)
        self.cwDecode_Button.pack(anchor="nw", padx="0 10", side="left")
        def cwDecode_Button_cmd_(): self.cwDecode_Button_CB("cwDecode_Button")

        self.cwDecode_Button.configure(command=cwDecode_Button_cmd_)
        self.spectrumScan_Button = ttk.Button(
            self.signal_Control_Frame, name="spectrumscan_button")
        self.spectrumScan_Button.configure(
            style="Button2b.TButton", text='\nSPECTRUM\n', width=11)
        self.spectrumScan_Tooltip = Tooltip(self.spectrumScan_Button)
        self.spectrumScan_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to bring up a window that allows you to scan 240kHZ of the band and look at average and peak signal levels.',
            wraplength=300)
        self.spectrumScan_Button.pack(anchor="nw", padx="0 10", side="left")
        def spectrumScan_Button_cmd_(): self.spectrumScan_Button_CB("spectrumScan_Button")

        self.spectrumScan_Button.configure(command=spectrumScan_Button_cmd_)
        self.bandScan_Button = ttk.Button(
            self.signal_Control_Frame, name="bandscan_button")
        self.bandScan_Button.configure(
            style="Button2b.TButton",
            text='\nBAND SCAN\n',
            width=11)
        self.bandScan_Button_Tooltip = Tooltip(self.bandScan_Button)
        self.bandScan_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to bring up a window that allows you to scan up to three sepeate bands for signals. ',
            wraplength=300)
        self.bandScan_Button.pack(anchor="nw", padx="0 10", side="left")
        def bandScan_Button_cmd_(): self.bandScan_Button_CB("bandScan_Button")

        self.bandScan_Button.configure(command=bandScan_Button_cmd_)
        self.split_Button = ttk.Button(
            self.signal_Control_Frame, name="split_button")
        self.split_Button.configure(
            style="Button2b.TButton",
            text='\nSPLIT\n',
            width=11)
        self.split_Button_Tooltip = Tooltip(self.split_Button)
        self.split_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to go into Split mode. ',
            wraplength=300)
        self.split_Button.pack(anchor="nw", padx="0 10", side="left")
        self.split_Button.configure(command=self.split_CB)
        self.rit_Button = ttk.Button(
            self.signal_Control_Frame, name="rit_button")
        self.rit_Button.configure(
            style="Button2b.TButton",
            text='\nRIT\n',
            width=11)
        self.rit_Button_Tooltip = Tooltip(self.rit_Button)
        self.rit_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to go enable RIT',
            wraplength=300)
        self.rit_Button.pack(anchor="nw", padx="0 10", side="left")
        self.rit_Button.configure(command=self.rit_CB)
        self.logQSO_Button = ttk.Button(
            self.signal_Control_Frame, name="logqso_button")
        self.logQSO_Button.configure(
            style="Button2b.TButton",
            text='\nLOG QSO\n',
            width=11)
        self.log_QSO_Tooltip = Tooltip(self.logQSO_Button)
        self.log_QSO_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to bring up a window to Log a QSO.',
            wraplength=300)
        self.logQSO_Button.pack(anchor="nw", padx="0 20", side="left")
        self.logQSO_Button.configure(command=self.logQSO_CB)
        self.signal_Control_Frame.grid(column=0, pady=10, row=0, sticky="n")
        self.secondary_menu_Frame.grid(column=0, padx=5, row=0)
        self.sMeter_Frame = ttk.Frame(
            self.control_Meter_Tuning_Frame,
            name="smeter_frame")
        self.sMeter_Frame.configure(
            height=70, style="Normal.TFrame", width=525)
        self.meter_Frame = ttk.Frame(self.sMeter_Frame, name="meter_frame")
        self.meter_Frame.configure(height=60, style="Normal.TFrame", width=425)
        label7 = ttk.Label(self.meter_Frame)
        label7.configure(
            style="Heading3b.TLabel",
            text=' ...................5................7..............8..........9........')
        label7.grid(column=1, row=0)
        self.s_meter_Label = ttk.Label(self.meter_Frame, name="s_meter_label")
        self.s_meter_Label.configure(style="Heading2b.TLabel", text='S/PO')
        self.s_meter_Label.grid(column=0, padx="0 10", row=1, sticky="w")
        self.s_meter_Progressbar = ttk.Progressbar(
            self.meter_Frame, name="s_meter_progressbar")
        self.s_meter_Progressbar_VAR = tk.StringVar(value='0')
        self.s_meter_Progressbar.configure(
            length=335,
            maximum=10,
            mode="determinate",
            orient="horizontal",
            style="Striped.Horizontal.TProgressbar",
            value=0,
            variable=self.s_meter_Progressbar_VAR)
        self.s_meter_Progressbar.grid(column=1, padx="5 0", row=1, sticky="w")
        self.meter_Frame.grid(column=0, row=0)
        self.meter_Frame.grid_propagate(0)
        self.SWR_PWR_Frame = ttk.Frame(self.sMeter_Frame, name="swr_pwr_frame")
        self.SWR_PWR_Frame.configure(
            height=60, style="NormalOutline.TFrame", width=95)
        self.SWR_Label = ttk.Label(self.SWR_PWR_Frame, name="swr_label")
        self.SWR_Label.configure(style="Heading3b.TLabel", text='SWR:')
        self.SWR_Label.grid(column=0, padx="5 0", pady=5, row=0)
        self.SWR_Value = ttk.Label(self.SWR_PWR_Frame, name="swr_value")
        self.SWR_Value_VAR = tk.StringVar()
        self.SWR_Value.configure(
            anchor="e",
            style="Heading4b.TLabel",
            textvariable=self.SWR_Value_VAR,
            width=4)
        self.SWR_Value.grid(column=1, padx="0 5", row=0, sticky="e")
        self.PWR_Label = ttk.Label(self.SWR_PWR_Frame, name="pwr_label")
        self.PWR_Label.configure(style="Heading3b.TLabel", text='PWR:')
        self.PWR_Label.grid(column=0, padx="5 0", pady="0 5", row=1)
        self.PWR_Value = ttk.Label(self.SWR_PWR_Frame, name="pwr_value")
        self.PWR_Value_VAR = tk.StringVar()
        self.PWR_Value.configure(
            anchor="e",
            style="Heading4b.TLabel",
            textvariable=self.PWR_Value_VAR,
            width=4)
        self.PWR_Value.grid(column=1, padx="0 5", row=1, sticky="e")
        self.SWR_PWR_Frame.grid(column=1, row=0, rowspan=2, sticky="se")
        self.SWR_PWR_Frame.grid_propagate(0)
        self.sMeter_Frame.grid(column=0, padx="20 0", row=1, sticky="w")
        self.sMeter_Frame.grid_propagate(0)
        self.cwDecodeFrame = ttk.Frame(
            self.control_Meter_Tuning_Frame,
            name="cwdecodeframe")
        self.cwDecodeFrame.configure(
            height=100, style="Normal.TFrame", width=400)
        self.decodedCWText = tk.Text(self.cwDecodeFrame, name="decodedcwtext")
        self.decodedCWText.configure(
            background="gray",
            borderwidth=2,
            font="{Courier New} 18 {}",
            foreground="white",
            height=3,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=1,
            relief="flat",
            spacing1=2,
            spacing2=5,
            spacing3=2,
            state="normal",
            width=25,
            wrap="char")
        self.decodedCWText.pack(expand=False, side="left")
        self.spectrumCanvas = tk.Canvas(
            self.cwDecodeFrame, name="spectrumcanvas")
        self.spectrumCanvas.configure(
            background="gray",
            height=100,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=1,
            relief="flat",
            width=200)
        self.spectrumCanvas.pack(
            anchor="sw",
            expand=False,
            padx="10 0",
            side="left")
        self.cwDecodeFrame.grid(
            column=0,
            padx="10 0",
            pady="10 0",
            row=2,
            sticky="nw")
        self.tuningArrow_Labelframe = ttk.Labelframe(
            self.control_Meter_Tuning_Frame, name="tuningarrow_labelframe")
        self.tuningArrow_Labelframe.configure(
            height=200, style="Heading3.TLabelframe", text='Tuning', width=200)
        self.downButton_Canvas = tk.Canvas(
            self.tuningArrow_Labelframe,
            name="downbutton_canvas")
        self.downButton_Canvas.configure(
            background="gray",
            borderwidth=0,
            height=140,
            highlightthickness=0,
            selectborderwidth=0,
            width=140)
        self.downButton_Canvas.pack(side="left")
        self.downButton_Canvas.bind(
            "<ButtonPress>",
            self.downButtonPressed_CB,
            add="+")
        self.downButton_Canvas.bind(
            "<ButtonRelease>",
            self.downButtonReleased_CB,
            add="")
        self.upButton_Canvas = tk.Canvas(
            self.tuningArrow_Labelframe,
            name="upbutton_canvas")
        self.upButton_Canvas.configure(
            background="gray",
            borderwidth=0,
            height=140,
            highlightthickness=0,
            selectborderwidth=0,
            width=140)
        self.upButton_Canvas.pack(side="left")
        self.upButton_Canvas.bind(
            "<ButtonPress>",
            self.upButtonPressed_CB,
            add="+")
        self.upButton_Canvas.bind(
            "<ButtonRelease>",
            self.upButtonReleased_CB,
            add="")
        self.tuning_Tooltip = Tooltip(self.tuningArrow_Labelframe)
        self.tuning_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click the up arrow to go up the current tuning factor. Down decreases the frequency by the tuning factor.',
            wraplength=300)
        self.tuningArrow_Labelframe.grid(
            column=0,
            columnspan=3,
            padx="650 0",
            pady=0,
            row=1,
            rowspan=3,
            sticky="sw")
        self.control_Meter_Tuning_Frame.grid(
            column=0, padx="5 0", row=1, sticky="nw")
        frame2.pack(
            anchor="n",
            expand=True,
            fill="x",
            ipadx=5,
            ipady=5,
            side="top")
        frame2.columnconfigure(0, weight=1)
        frame2.columnconfigure(1, weight=2)
        self.ATT_IFS_Adjust_Frame = ttk.Frame(
            self, name="att_ifs_adjust_frame")
        self.ATT_IFS_Adjust_Frame.configure(style="Normal.TFrame", width=1250)
        self.att_ifs_Frame = ttk.Frame(
            self.ATT_IFS_Adjust_Frame,
            name="att_ifs_frame")
        self.att_ifs_Frame.configure(
            height=200, style="Normal.TFrame", width=400)
        self.ATT_Frame = ttk.Frame(self.att_ifs_Frame, name="att_frame")
        self.ATT_Frame.configure(height=200, style="Normal.TFrame", width=200)
        self.ATT_Jogwheel = JogwheelCustom(
            self.ATT_Frame,
            start=0,
            end=255,
            divisions=10,
            radius=200,
            button_radius=25,
            value=70,
            scroll_steps=10,
            name="att_jogwheel")
        self.ATT_Jogwheel.configure(state="disabled", touchOptimized=False)
        self.ATT_Jogwheel.pack(anchor="center", padx="20 0", side="top")
        self.ATT_Jogwheel.configure(command=self.updateATTValue_CB)
        self.ATT_Jogwheel.bind(
            "<ButtonPress>",
            self.ATT_Jogwheel_ButtonPressed_CB,
            add="+")
        self.ATT_Jogwheel.bind(
            "<ButtonRelease>",
            self.ATT_Jogwheel_ButtonReleased_CB,
            add="+")
        self.ATT_Status_Label = ttk.Label(
            self.ATT_Frame, name="att_status_label")
        self.ATT_Status_VAR = tk.StringVar(value='ATT (OFF)')
        self.ATT_Status_Label.configure(
            style="Heading2b.TLabel",
            text='ATT (OFF)',
            textvariable=self.ATT_Status_VAR)
        self.ATT_Status_Label.pack(anchor="center", side="bottom")
        self.ATT_Tooltip = Tooltip(self.ATT_Frame)
        self.ATT_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Click to enable ATT. Move the dial to adjust the ATT. Click in plac to disable ATT.',
            wraplength=300)
        self.ATT_Frame.pack(padx=30, side="left")
        self.IFS_Frame = ttk.Frame(self.att_ifs_Frame, name="ifs_frame")
        self.IFS_Frame.configure(height=200, style="Normal.TFrame", width=200)
        self.IFS_Jogwheel = JogwheelCustom(
            self.IFS_Frame,
            start=-2000,
            end=2000,
            divisions=150,
            radius=200,
            button_radius=25,
            value=0,
            scroll_steps=150,
            name="ifs_jogwheel")
        self.IFS_Jogwheel.configure(state="disabled", touchOptimized=False)
        self.IFS_Jogwheel.pack(anchor="center", padx="20 0", side="top")
        self.IFS_Jogwheel.configure(command=self.updateIFSValue_CB)
        self.IFS_Jogwheel.bind(
            "<ButtonPress>",
            self.IFS_Jogwheel_ButtonPressed_CB,
            add="+")
        self.IFS_Jogwheel.bind(
            "<ButtonRelease>",
            self.IFS_Jogwheel_ButtonReleased_CB,
            add="+")
        self.IFS_Status_Label = ttk.Label(
            self.IFS_Frame, name="ifs_status_label")
        self.IFS_Status_VAR = tk.StringVar(value='IFS (OFF)')
        self.IFS_Status_Label.configure(
            style="Heading2b.TLabel",
            text='IFS (OFF)',
            textvariable=self.IFS_Status_VAR)
        self.IFS_Status_Label.pack(anchor="center", side="bottom")
        self.IFS_Tooltip = Tooltip(self.IFS_Frame)
        self.IFS_Tooltip.configure(
            justify="left",
            padx=8,
            relief="raised",
            text='Click to enable IFS. Move the dial to adjust the IFS. Click in plac to disable IFS.',
            wraplength=300)
        self.IFS_Frame.pack(side="left")
        self.att_ifs_Frame.pack(
            anchor="nw",
            expand=False,
            fill="x",
            padx=10,
            side="left")
        self.cwInfoFrame = ttk.Frame(
            self.ATT_IFS_Adjust_Frame,
            name="cwinfoframe")
        self.cwInfoFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.cw_Info_Frame = ttk.Frame(self.cwInfoFrame, name="cw_info_frame")
        self.cw_Info_Frame.configure(
            borderwidth=5,
            height=200,
            style="NormalOutline.TFrame",
            width=200)
        self.cw_settings_title_Label = ttk.Label(
            self.cw_Info_Frame, name="cw_settings_title_label")
        self.cw_settings_title_Label.configure(
            style="Heading2b.TLabel", text='CW Settings')
        self.cw_settings_title_Label.grid(column=0, columnspan=3, row=0)
        self.cw_settings_title_Label.bind("<1>", self.cwSettings_CB, add="")
        self.tone_Label = ttk.Label(self.cw_Info_Frame, name="tone_label")
        self.tone_Label.configure(style="Heading3b.TLabel", text='Tone')
        self.tone_Label.grid(column=0, row=1, sticky="w")
        self.tone_Label.bind("<1>", self.cwSettings_CB, add="")
        self.tone_value_Label = ttk.Label(
            self.cw_Info_Frame, name="tone_value_label")
        self.tone_value_VAR = tk.StringVar(value='799')
        self.tone_value_Label.configure(
            style="Heading3b.TLabel",
            text='799',
            textvariable=self.tone_value_VAR)
        self.tone_value_Label.grid(column=1, padx="0 2", row=1, sticky="w")
        self.tone_value_Label.bind("<1>", self.cwSettings_CB, add="")
        self.tone_units_Label = ttk.Label(
            self.cw_Info_Frame, name="tone_units_label")
        self.tone_units_Label.configure(style="Heading3b.TLabel", text='Hz')
        self.tone_units_Label.grid(column=2, row=1, sticky="w")
        self.tone_units_Label.bind("<1>", self.cwSettings_CB, add="")
        self.key_type_Label = ttk.Label(
            self.cw_Info_Frame, name="key_type_label")
        self.key_type_Label.configure(style="Heading3b.TLabel", text='Key')
        self.key_type_Label.grid(column=0, row=2, sticky="w")
        self.key_type_Label.bind("<1>", self.cwSettings_CB, add="")
        self.key_type_value_Label = ttk.Label(
            self.cw_Info_Frame, name="key_type_value_label")
        self.key_type_value_VAR = tk.StringVar(value='Straight')
        self.key_type_value_Label.configure(
            style="Heading3b.TLabel",
            text='Straight',
            textvariable=self.key_type_value_VAR)
        self.key_type_value_Label.grid(column=1, row=2, sticky="w")
        self.key_type_value_Label.bind("<1>", self.cwSettings_CB, add="")
        self.key_speed_label = ttk.Label(
            self.cw_Info_Frame, name="key_speed_label")
        self.key_speed_label.configure(style="Heading3b.TLabel", text='Speed')
        self.key_speed_label.grid(column=0, row=3, sticky="w")
        self.key_speed_label.bind("<1>", self.cwSettings_CB, add="")
        self.key_speed_value_Label = ttk.Label(
            self.cw_Info_Frame, name="key_speed_value_label")
        self.key_speed_value_VAR = tk.StringVar(value='1')
        self.key_speed_value_Label.configure(
            style="Heading3b.TLabel",
            text='1',
            textvariable=self.key_speed_value_VAR)
        self.key_speed_value_Label.grid(column=1, row=3, sticky="w")
        self.key_speed_value_Label.bind("<1>", self.cwSettings_CB, add="")
        self.key_speed_units_Label = ttk.Label(
            self.cw_Info_Frame, name="key_speed_units_label")
        self.key_speed_units_Label.configure(
            style="Heading3b.TLabel", text='wpm')
        self.key_speed_units_Label.grid(column=2, row=3, sticky="w")
        self.key_speed_units_Label.bind("<1>", self.cwSettings_CB, add="")
        self.delay_returning_to_rx_Label = ttk.Label(
            self.cw_Info_Frame, name="delay_returning_to_rx_label")
        self.delay_returning_to_rx_Label.configure(
            style="Heading3b.TLabel", text='Delay->RX')
        self.delay_returning_to_rx_Label.grid(
            column=0, padx="0 3", row=5, sticky="w")
        self.delay_returning_to_rx_Label.bind(
            "<1>", self.cwSettings_CB, add="")
        self.delay_returning_to_rx_value_Label = ttk.Label(
            self.cw_Info_Frame, name="delay_returning_to_rx_value_label")
        self.delay_returning_to_rx_value_VAR = tk.StringVar(value='199')
        self.delay_returning_to_rx_value_Label.configure(
            style="Heading3b.TLabel",
            text='199',
            textvariable=self.delay_returning_to_rx_value_VAR)
        self.delay_returning_to_rx_value_Label.grid(
            column=1, row=5, sticky="w")
        self.delay_returning_to_rx_value_Label.bind(
            "<1>", self.cwSettings_CB, add="")
        self.delay_returning_to_rx_units_Label = ttk.Label(
            self.cw_Info_Frame, name="delay_returning_to_rx_units_label")
        self.delay_returning_to_rx_units_Label.configure(
            style="Heading3b.TLabel", text='ms')
        self.delay_returning_to_rx_units_Label.grid(
            column=2, row=5, sticky="w")
        self.delay_returning_to_rx_units_Label.bind(
            "<1>", self.cwSettings_CB, add="")
        self.delay_starting_tx_Label = ttk.Label(
            self.cw_Info_Frame, name="delay_starting_tx_label")
        self.delay_starting_tx_Label.configure(
            style="Heading3b.TLabel", text='Delay->TX')
        self.delay_starting_tx_Label.grid(column=0, row=4, sticky="w")
        self.delay_starting_tx_Label.bind("<1>", self.cwSettings_CB, add="")
        self.delay_starting_tx_value_Label = ttk.Label(
            self.cw_Info_Frame, name="delay_starting_tx_value_label")
        self.delay_starting_tx_value_VAR = tk.StringVar(value='299')
        self.delay_starting_tx_value_Label.configure(
            style="Heading3b.TLabel",
            text='299',
            textvariable=self.delay_starting_tx_value_VAR)
        self.delay_starting_tx_value_Label.grid(column=1, row=4, sticky="w")
        self.delay_starting_tx_value_Label.bind(
            "<1>", self.cwSettings_CB, add="")
        self.delay_starting_tx_units_Label = ttk.Label(
            self.cw_Info_Frame, name="delay_starting_tx_units_label")
        self.delay_starting_tx_units_Label.configure(
            style="Heading3b.TLabel", text='ms')
        self.delay_starting_tx_units_Label.grid(column=2, row=4, sticky="w")
        self.delay_starting_tx_units_Label.bind(
            "<1>", self.cwSettings_CB, add="")
        self.cw_Settings_Frame_Tooltips = Tooltip(self.cw_Info_Frame)
        self.cw_Settings_Frame_Tooltips.configure(
            justify="left",
            padx=8,
            relief="raised",
            text='Current CW Settings. Click to go into the CW Settings Menu to edit them.',
            wraplength=300)
        self.cw_Info_Frame.pack(
            anchor="nw",
            expand=False,
            fill="x",
            pady="0 10",
            side="top")
        self.cw_Info_Frame.bind("<1>", self.cwSettings_CB, add="")
        self.cwInfoFrame.pack(padx="50 0", pady="15 0", side="top")
        self.ATT_IFS_Adjust_Frame.pack(
            anchor="w",
            expand=True,
            fill="both",
            pady="10 50",
            side="top")
        self.configure(
            borderwidth=5,
            height=900,
            style="Normal.TFrame",
            width=875)
        # Layout for 'main_window' skipped in custom widget template.

    def settings_CB(self):
        pass

    def vfo_CB(self):
        pass

    def mode_lsb_CB(self):
        pass

    def mode_usb_CB(self):
        pass

    def mode_cwl_CB(self):
        pass

    def mode_cwu_CB(self):
        pass

    def band_up_CB(self):
        pass

    def band_down_CB(self):
        pass

    def lock_CB(self):
        pass

    def speaker_CB(self):
        pass

    def channels_CB(self):
        pass

    def cwDecode_Button_CB(self, widget_id):
        pass

    def spectrumScan_Button_CB(self, widget_id):
        pass

    def bandScan_Button_CB(self, widget_id):
        pass

    def split_CB(self):
        pass

    def rit_CB(self):
        pass

    def logQSO_CB(self):
        pass

    def downButtonPressed_CB(self, event=None):
        pass

    def downButtonReleased_CB(self, event=None):
        pass

    def upButtonPressed_CB(self, event=None):
        pass

    def upButtonReleased_CB(self, event=None):
        pass

    def updateATTValue_CB(self):
        pass

    def ATT_Jogwheel_ButtonPressed_CB(self, event=None):
        pass

    def ATT_Jogwheel_ButtonReleased_CB(self, event=None):
        pass

    def updateIFSValue_CB(self):
        pass

    def IFS_Jogwheel_ButtonPressed_CB(self, event=None):
        pass

    def IFS_Jogwheel_ButtonReleased_CB(self, event=None):
        pass

    def cwSettings_CB(self, event=None):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = mainScreenUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
