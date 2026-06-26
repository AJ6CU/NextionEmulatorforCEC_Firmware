#!/usr/bin/python3
"""
sdrDashboard

A small window that pops up when a sdr is connected

UI source file: sdrDashboard.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.hideableframe import HideableFrame
from pygubu.widgets.scrolledframe import ScrolledFrame


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
class sdrDashboardUI(ttk.Frame):
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

        self.liveTelemetry_Frame = ttk.Labelframe(
            self, name="livetelemetry_frame")
        self.liveTelemetry_Frame.configure(
            style="Normal.TLabelframe",
            text=' Live Telemetry Tracker Panel ')
        # First object created
        on_first_object_cb(self.liveTelemetry_Frame)

        frame7 = ttk.Frame(self.liveTelemetry_Frame)
        frame7.configure(height=200, style="Normal.TFrame", width=200)
        label1 = ttk.Label(frame7)
        label1.configure(style="Heading4.TLabel", text='Active VFO Frequency:')
        label1.pack(padx="42 10", side="left")
        self.label_val_freq = ttk.Label(frame7, name="label_val_freq")
        self.label_val_freq.configure(
            font="TkFixedFont",
            style="Heading4.TLabel",
            text='000.0000 MHz')
        self.label_val_freq.pack(side="left")
        label4 = ttk.Label(frame7)
        label4.configure(style="Heading4.TLabel", text='Mode:')
        label4.pack(padx="40 10", side="left")
        self.label_val_mode = ttk.Label(frame7, name="label_val_mode")
        self.label_val_mode.configure(style="Heading4.TLabel", text='UNKNOWN')
        self.label_val_mode.pack(side="left")
        frame7.pack(anchor="center", expand=True, fill="x", pady=5, side="top")
        frame9 = ttk.Frame(self.liveTelemetry_Frame)
        frame9.configure(height=200, style="Normal.TFrame", width=200)
        label6 = ttk.Label(frame9)
        label6.configure(
            style="Heading4.TLabel",
            text='Signal Strength (dBFS):')
        label6.pack(anchor="center", padx="40 0", side="left")
        frame8 = ttk.Frame(frame9)
        frame8.configure(style="Normal.TFrame")
        self.label_smeter_ticks = ttk.Label(frame8, name="label_smeter_ticks")
        self.label_smeter_ticks.configure(
            background="gray",
            font="TkFixedFont",
            foreground="white",
            text='S1 . S3 . S5 . S7 . S9 . +10 . +30')
        self.label_smeter_ticks.pack(anchor="w", side="top")
        self.smeter_Progressbar = ttk.Progressbar(
            frame8, name="smeter_progressbar")
        self.smeter_Progressbar.configure(
            length=210, maximum=100, mode="determinate")
        self.smeter_Progressbar.pack(fill="x", pady=4, side="top")
        self.label_smeter_val = ttk.Label(frame8, name="label_smeter_val")
        self.label_smeter_val.configure(
            background="gray",
            font="TkFixedFont",
            foreground="white",
            text='-00.0 dBFS')
        self.label_smeter_val.pack(anchor="w", pady=2, side="top")
        frame8.pack(padx=10, side="left")
        frame9.pack(expand=True, fill="x", pady=5)
        frame5 = ttk.Frame(self.liveTelemetry_Frame)
        frame5.configure(height=200, style="Normal.TFrame", width=200)
        lbl_volume_txt = ttk.Label(frame5)
        lbl_volume_txt.configure(
            style="Heading4.TLabel",
            text='Audio Volume (0-100):')
        lbl_volume_txt.pack(padx="50 0", side="left")
        self.volume_scale = ttk.Scale(frame5, name="volume_scale")
        self.volume_scale.configure(
            from_=0, length=150, orient="horizontal", to=100)
        self.volume_scale.pack(padx=10, side="left")
        self.volume_scale.bind(
            "<B1-Motion>",
            self.action_on_volume_slider_move,
            add="+")
        self.volume_scale.bind(
            "<ButtonRelease-1>",
            self.action_on_volume_slider_move,
            add="+")
        self.label_volume_val = ttk.Label(frame5, name="label_volume_val")
        self.label_volume_val.configure(
            font="TkFixedFont",
            style="Heading4.TLabel",
            text='50%')
        self.label_volume_val.pack(side="left")
        self.button_mute_toggle = ttk.Button(frame5, name="button_mute_toggle")
        self.button_mute_toggle.configure(
            style="Button3Sunken.TButton", text='🔊 Mute Audio')
        self.button_mute_toggle.pack(padx=10, side="left")
        self.button_mute_toggle.configure(command=self.action_toggle_mute)
        frame5.pack(anchor="center", expand=True, fill="x", pady=5, side="top")
        self.liveTelemetry_Frame.pack(anchor="n", side="top")
        self.sdrCommands_ScrolledFrame = ScrolledFrame(
            self, scrolltype="both", name="sdrcommands_scrolledframe")
        self.sdrCommands_ScrolledFrame.innerframe.configure(
            style="Normal.TFrame")
        self.sdrCommands_ScrolledFrame.configure(usemousewheel=False)
        self.band_all_Frame = ttk.Frame(
            self.sdrCommands_ScrolledFrame.innerframe,
            name="band_all_frame")
        self.band_all_Frame.configure(style="Normal.TFrame")
        self.bands_Frame = ttk.Frame(self.band_all_Frame, name="bands_frame")
        self.bands_Frame.configure(height=200, style="Normal.TFrame")
        self.bandsToggle_Button = ttk.Button(
            self.bands_Frame, name="bandstoggle_button")
        self.bandsToggle_Button.configure(
            state="normal", style="Custom.Toolbutton", text='Bands')
        self.bandsToggle_Button.pack(expand=False, side="left")
        self.bandsToggle_Button.configure(command=self.toggleBands_CB)
        self.bands_Frame.grid(column=0, row=0, sticky="nw")
        self.bandsAccordion_Frame = HideableFrame(
            self.band_all_Frame, name="bandsaccordion_frame")
        self.bandsAccordion_Frame.configure(style="Normal.TFrame")
        self.quickHamBandSelect_Labelframe = ttk.Labelframe(
            self.bandsAccordion_Frame, name="quickhambandselect_labelframe")
        self.quickHamBandSelect_Labelframe.configure(
            style="Normal.TLabelframe", text=' Ham Radio Bands')
        self.ham_band_160m = ttk.Button(
            self.quickHamBandSelect_Labelframe,
            name="ham_band_160m")
        self.ham_band_160m.configure(
            style="Button3Raised.TButton", text='160M')
        self.ham_band_160m.grid(column=0, padx=5, pady=5, row=0)
        def ham_band_160m_cmd_(): self.action_quick_band("ham_band_160m")

        self.ham_band_160m.configure(command=ham_band_160m_cmd_)
        self.ham_band_80m = ttk.Button(
            self.quickHamBandSelect_Labelframe,
            name="ham_band_80m")
        self.ham_band_80m.configure(style="Button3Raised.TButton", text='80M')
        self.ham_band_80m.grid(column=1, padx=5, pady=5, row=0)
        def ham_band_80m_cmd_(): self.action_quick_band("ham_band_80m")

        self.ham_band_80m.configure(command=ham_band_80m_cmd_)
        self.ham_band_40m = ttk.Button(
            self.quickHamBandSelect_Labelframe,
            name="ham_band_40m")
        self.ham_band_40m.configure(style="Button3Raised.TButton", text='40M')
        self.ham_band_40m.grid(column=2, padx=5, pady=5, row=0)
        def ham_band_40m_cmd_(): self.action_quick_band("ham_band_40m")

        self.ham_band_40m.configure(command=ham_band_40m_cmd_)
        self.ham_band_30m = ttk.Button(
            self.quickHamBandSelect_Labelframe,
            name="ham_band_30m")
        self.ham_band_30m.configure(style="Button3Raised.TButton", text='30M')
        self.ham_band_30m.grid(column=0, padx=5, pady=5, row=1)
        def ham_band_30m_cmd_(): self.action_quick_band("ham_band_30m")

        self.ham_band_30m.configure(command=ham_band_30m_cmd_)
        self.ham_band_20m = ttk.Button(
            self.quickHamBandSelect_Labelframe,
            name="ham_band_20m")
        self.ham_band_20m.configure(style="Button3Raised.TButton", text='20M')
        self.ham_band_20m.grid(column=1, padx=5, pady=5, row=1)
        def ham_band_20m_cmd_(): self.action_quick_band("ham_band_20m")

        self.ham_band_20m.configure(command=ham_band_20m_cmd_)
        self.ham_band_17m = ttk.Button(
            self.quickHamBandSelect_Labelframe,
            name="ham_band_17m")
        self.ham_band_17m.configure(style="Button3Raised.TButton", text='17M')
        self.ham_band_17m.grid(column=2, padx=5, pady=5, row=1)
        def ham_band_17m_cmd_(): self.action_quick_band("ham_band_17m")

        self.ham_band_17m.configure(command=ham_band_17m_cmd_)
        self.ham_band_15m = ttk.Button(
            self.quickHamBandSelect_Labelframe,
            name="ham_band_15m")
        self.ham_band_15m.configure(style="Button3Raised.TButton", text='15M')
        self.ham_band_15m.grid(column=0, padx=5, pady=5, row=2)
        def ham_band_15m_cmd_(): self.action_quick_band("ham_band_15m")

        self.ham_band_15m.configure(command=ham_band_15m_cmd_)
        self.ham_band_12m = ttk.Button(
            self.quickHamBandSelect_Labelframe,
            name="ham_band_12m")
        self.ham_band_12m.configure(style="Button3Raised.TButton", text='12M')
        self.ham_band_12m.grid(column=1, padx=5, pady=5, row=2)
        def ham_band_12m_cmd_(): self.action_quick_band("ham_band_12m")

        self.ham_band_12m.configure(command=ham_band_12m_cmd_)
        self.ham_band_10m = ttk.Button(
            self.quickHamBandSelect_Labelframe,
            name="ham_band_10m")
        self.ham_band_10m.configure(style="Button3Raised.TButton", text='10m')
        self.ham_band_10m.grid(column=2, padx=5, pady=5, row=2)
        def ham_band_10m_cmd_(): self.action_quick_band("ham_band_10m")

        self.ham_band_10m.configure(command=ham_band_10m_cmd_)
        self.quickHamBandSelect_Labelframe.pack(
            anchor="w", padx=10, side="top")
        self.quickHamBandSelect_Labelframe.grid_anchor("w")
        self.modeChange_Labelframe = ttk.Labelframe(
            self.bandsAccordion_Frame, name="modechange_labelframe")
        self.modeChange_Labelframe.configure(
            style="Normal.TLabelframe", text='Mode')
        self.modeLSB_Button = ttk.Button(
            self.modeChange_Labelframe,
            name="modelsb_button")
        self.modeLSB_Button.configure(
            style="Button3Raised.TButton", text='LSB')
        self.modeLSB_Button.grid(column=0, padx=5, pady=5, row=0)
        def modeLSB_Button_cmd_(): self.action_quick_mode("modeLSB_Button")

        self.modeLSB_Button.configure(command=modeLSB_Button_cmd_)
        self.modeUSB_Button = ttk.Button(
            self.modeChange_Labelframe,
            name="modeusb_button")
        self.modeUSB_Button.configure(
            style="Button3Raised.TButton", text='USB')
        self.modeUSB_Button.grid(column=1, padx=5, pady=5, row=0)
        def modeUSB_Button_cmd_(): self.action_quick_mode("modeUSB_Button")

        self.modeUSB_Button.configure(command=modeUSB_Button_cmd_)
        self.modeCWL_Button = ttk.Button(
            self.modeChange_Labelframe,
            name="modecwl_button")
        self.modeCWL_Button.configure(
            style="Button3Raised.TButton", text='CWL')
        self.modeCWL_Button.grid(column=2, padx=5, pady=5, row=0)
        def modeCWL_Button_cmd_(): self.action_quick_mode("modeCWL_Button")

        self.modeCWL_Button.configure(command=modeCWL_Button_cmd_)
        self.modeCWU_Button = ttk.Button(
            self.modeChange_Labelframe,
            name="modecwu_button")
        self.modeCWU_Button.configure(
            style="Button3Raised.TButton", text='CWU')
        self.modeCWU_Button.grid(column=3, padx=5, pady=5, row=0)
        def modeCWU_Button_cmd_(): self.action_quick_mode("modeCWU_Button")

        self.modeCWU_Button.configure(command=modeCWU_Button_cmd_)
        self.modeChange_Labelframe.pack(anchor="w", padx=10)
        self.modeChange_Labelframe.grid_anchor("w")
        self.bandwidthManagement_Labelframe = ttk.Labelframe(
            self.bandsAccordion_Frame, name="bandwidthmanagement_labelframe")
        self.bandwidthManagement_Labelframe.configure(
            style="Normal.TLabelframe", text='IF Filter')
        frame1 = ttk.Frame(self.bandwidthManagement_Labelframe)
        frame1.configure(height=200, style="Normal.TFrame", width=200)
        self.widenFilter_Button = ttk.Button(frame1, name="widenfilter_button")
        self.widenFilter_Button.configure(
            style="Button3Raised.TButton", text='Widen')
        self.widenFilter_Button.pack(padx=5, pady=5, side="left")
        self.widenFilter_Button.configure(command=self.action_filter_widen)
        self.narrowFilter_Button = ttk.Button(
            frame1, name="narrowfilter_button")
        self.narrowFilter_Button.configure(
            style="Button3Raised.TButton", text='Narrow')
        self.narrowFilter_Button.pack(padx=5, pady=5, side="left")
        self.narrowFilter_Button.configure(command=self.action_filter_narrow)
        self.resetFilter_Button = ttk.Button(frame1, name="resetfilter_button")
        self.resetFilter_Button.configure(
            style="Button3Raised.TButton", text='Reset')
        self.resetFilter_Button.pack(padx=5, pady=5, side="left")
        self.resetFilter_Button.configure(command=self.action_filter_reset)
        self.filterWidth_Label = ttk.Label(frame1, name="filterwidth_label")
        self.filterWidth_Label.configure(
            style="Heading4.TLabel", text='Filter:')
        self.filterWidth_Label.pack(padx=20, pady=5, side="left")
        self.currentFilterWidth_Label = ttk.Label(
            frame1, name="currentfilterwidth_label")
        self.currentFilterWidth_VAR = tk.StringVar()
        self.currentFilterWidth_Label.configure(
            style="Heading4.TLabel",
            textvariable=self.currentFilterWidth_VAR)
        self.currentFilterWidth_Label.pack(side="left")
        self.filterWidthHZ_Label = ttk.Label(
            frame1, name="filterwidthhz_label")
        self.filterWidthHZ_Label.configure(style="Heading4.TLabel", text='HZ')
        self.filterWidthHZ_Label.pack(padx=5, pady=5, side="left")
        frame1.grid(column=0, row=0, sticky="ew")
        frame2 = ttk.Frame(self.bandwidthManagement_Labelframe)
        frame2.configure(height=200, style="Normal.TFrame", width=200)
        self.forceFilterBandwidth_Label = ttk.Label(
            frame2, name="forcefilterbandwidth_label")
        self.forceFilterBandwidth_Label.configure(
            style="Heading4.TLabel", text='Force BW (Hz):')
        self.forceFilterBandwidth_Label.pack(padx="30 0", pady=5, side="left")
        self.entry_force_bw = ttk.Entry(frame2, name="entry_force_bw")
        self.entry_force_bw.configure(width=6)
        self.entry_force_bw.pack(padx=5, pady=5, side="left")
        self.forceFilterBandwidth_Button = ttk.Button(
            frame2, name="forcefilterbandwidth_button")
        self.forceFilterBandwidth_Button.configure(
            style="Button3Raised.TButton", text='Force Override')
        self.forceFilterBandwidth_Button.pack(padx=30, pady=5, side="left")
        self.forceFilterBandwidth_Button.configure(
            command=self.action_master_force_bw)
        frame2.grid(column=0, pady=10, row=2, sticky="ew")
        self.bandwidthManagement_Labelframe.pack(anchor="w", padx=10)
        self.bandwidthManagement_Labelframe.grid_anchor("w")
        self.bandsAccordion_Frame.grid(column=0, row=1)
        self.band_all_Frame.pack(
            anchor="n",
            expand=True,
            fill="both",
            padx=5,
            pady=5,
            side="top")
        self.band_all_Frame.grid_anchor("nw")
        self.channels_all = ttk.Frame(
            self.sdrCommands_ScrolledFrame.innerframe,
            name="channels_all")
        self.channels_all.configure(style="Normal.TFrame")
        self.channels_Frame = ttk.Frame(
            self.channels_all, name="channels_frame")
        self.channels_Frame.configure(height=200, style="Normal.TFrame")
        self.channelsToggle_Button = ttk.Button(
            self.channels_Frame, name="channelstoggle_button")
        self.channelsToggle_Button.configure(
            state="normal", style="Custom.Toolbutton", text='Channels')
        self.channelsToggle_Button.pack(expand=True, fill="x", side="left")
        self.channelsToggle_Button.configure(command=self.toggleChannels_CB)
        self.channels_Frame.grid(column=0, row=0, sticky="nw")
        self.channelsAccordion_Frame = HideableFrame(
            self.channels_all, name="channelsaccordion_frame")
        self.channelsAccordion_Frame.configure(style="Normal.TFrame")
        frame4 = ttk.Frame(self.channelsAccordion_Frame)
        frame4.configure(height=200, style="Normal.TFrame", width=200)
        grid_wrapper = ttk.Frame(frame4)
        grid_wrapper.configure(style="Normal.TFrame")
        self.treeChannels = ttk.Treeview(grid_wrapper, name="treechannels")
        self.treeChannels.configure(
            height=10, selectmode="browse", show="headings")
        self.treeChannels.pack(expand=True, fill="both", side="left")
        self.treeChannels.bind(
            "<<TreeviewSelect>>",
            self.action_on_channel_row_click,
            add="+")
        self.treeScrollbar = ttk.Scrollbar(grid_wrapper, name="treescrollbar")
        self.treeScrollbar.configure(orient="vertical")
        self.treeScrollbar.pack(fill="y", side="right")
        grid_wrapper.pack(side="left")
        self.channelSearch_Labelframe = ttk.Labelframe(
            frame4, name="channelsearch_labelframe")
        self.channelSearch_Labelframe.configure(
            style="Normal.TLabelframe", text='Search')
        self.channelLookup_Entry = ttk.Entry(
            self.channelSearch_Labelframe,
            name="channellookup_entry")
        self.channelLookup_Entry.grid(
            column=0, padx=5, pady=5, row=0, sticky="ew")
        self.channelLookup_Entry.bind(
            "<KeyRelease>", self.action_filter_search_grid, add="+")
        self.channelSearch_Labelframe.pack(anchor="center", side="right")
        frame4.pack()
        self.channelEdit_Labelframe = ttk.Labelframe(
            self.channelsAccordion_Frame, name="channeledit_labelframe")
        self.channelEdit_Labelframe.configure(
            height=200,
            style="Normal.TLabelframe",
            text='Channel Edit',
            width=200)
        self.addChanneltoBank_Button = ttk.Button(
            self.channelEdit_Labelframe, name="addchanneltobank_button")
        self.addChanneltoBank_Button.configure(
            style="Button3Raised.TButton", text='Copy to\nSource')
        self.addChanneltoBank_Button.grid(column=0, padx=10, pady=10, row=0)
        self.addChanneltoBank_Button.configure(
            command=self.action_copy_row_to_target_bank)
        self.deleteChannel_Button = ttk.Button(
            self.channelEdit_Labelframe, name="deletechannel_button")
        self.deleteChannel_Button.configure(
            style="Button3Raised.TButton", text='Erase')
        self.deleteChannel_Button.grid(column=0, padx=10, pady=10, row=1)
        self.deleteChannel_Button.configure(command=self.action_del_ch)
        self.newChannelFromVFO_Labelframe = ttk.Labelframe(
            self.channelEdit_Labelframe, name="newchannelfromvfo_labelframe")
        self.newChannelFromVFO_Labelframe.configure(
            height=200, style="Normal.TLabelframe", text='Save VFO to Channel', width=200)
        self.newVFOHeader_Frame = ttk.Frame(
            self.newChannelFromVFO_Labelframe,
            name="newvfoheader_frame")
        self.newVFOHeader_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.channelName_Label = ttk.Label(
            self.newVFOHeader_Frame, name="channelname_label")
        self.channelName_Label.configure(
            style="Heading4.TLabel", text='Label:')
        self.channelName_Label.grid(
            column=0, padx=10, pady=10, row=0, sticky="e")
        self.newChannel_Label = ttk.Entry(
            self.newVFOHeader_Frame, name="newchannel_label")
        self.newChannel_Label.configure(width=10)
        self.newChannel_Label.grid(column=1, pady=10, row=0, sticky="w")
        self.channelStation_Label = ttk.Label(
            self.newVFOHeader_Frame, name="channelstation_label")
        self.channelStation_Label.configure(
            style="Heading4.TLabel", text='Desccription:')
        self.channelStation_Label.grid(
            column=0, padx=10, pady=10, row=1, sticky="e")
        self.customStationName_Entry = ttk.Entry(
            self.newVFOHeader_Frame, name="customstationname_entry")
        self.customStationName_Entry.configure(width=15)
        self.customStationName_Entry.grid(
            column=1, padx="0 15", pady=10, row=1, sticky="w")
        self.newVFOHeader_Frame.pack()
        self.addNewChannel_Button = ttk.Button(
            self.newChannelFromVFO_Labelframe,
            name="addnewchannel_button")
        self.addNewChannel_Button.configure(
            style="Button3Raised.TButton", text='Save')
        self.addNewChannel_Button.pack(pady=10)
        self.addNewChannel_Button.configure(
            command=self.action_capture_live_vfo_to_channel)
        self.newChannelFromVFO_Labelframe.grid(
            column=1, padx=40, pady=10, row=0, rowspan=2, sticky="ns")
        self.channelEdit_Labelframe.pack(anchor="w", padx="20 10", side="top")
        self.bankRouting_Labelframe = ttk.Labelframe(
            self.channelsAccordion_Frame, name="bankrouting_labelframe")
        self.bankRouting_Labelframe.configure(
            style="Normal.TLabelframe",
            text='Channel Bank Management')
        self.channelControl_Frame = ttk.Frame(
            self.bankRouting_Labelframe,
            name="channelcontrol_frame")
        self.channelControl_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.bankCloneButton = ttk.Button(
            self.channelControl_Frame, name="bankclonebutton")
        self.bankCloneButton.configure(
            style="Button3Raised.TButton", text='Clone')
        self.bankCloneButton.grid(column=0, padx=15, pady=10, row=1)
        self.bankCloneButton.configure(
            command=self.action_bulk_clone_source_to_target)
        self.bankDelete_Button = ttk.Button(
            self.channelControl_Frame, name="bankdelete_button")
        self.bankDelete_Button.configure(
            style="Button3Raised.TButton", text='Delete')
        self.bankDelete_Button.grid(column=0, padx=10, pady=10, row=2)
        self.bankDelete_Button.configure(
            command=self.action_delete_source_bank_profile)
        self.newChannelBank_Button = ttk.Button(
            self.channelControl_Frame, name="newchannelbank_button")
        self.newChannelBank_Button.configure(
            style="Button3Raised.TButton", text='New')
        self.newChannelBank_Button.grid(column=0, padx=15, pady=10, row=0)
        self.newChannelBank_Button.configure(
            command=self.action_create_brand_new_bank)
        self.channelControl_Frame.grid(
            column=1,
            columnspan=3,
            padx=40,
            pady=10,
            row=0,
            sticky="ew")
        self.sourceTargetLabelframe = ttk.Labelframe(
            self.bankRouting_Labelframe, name="sourcetargetlabelframe")
        self.sourceTargetLabelframe.configure(
            height=200,
            style="Normal.TLabelframe",
            text='Select Banks',
            width=200)
        lbl_src_bank = ttk.Label(self.sourceTargetLabelframe)
        lbl_src_bank.configure(style="Heading4.TLabel", text='Source:')
        lbl_src_bank.pack(pady="15 0")
        self.sourceBank_Combobox = ttk.Combobox(
            self.sourceTargetLabelframe, name="sourcebank_combobox")
        self.sourceBank_Combobox.pack(padx=10)
        self.sourceBank_Combobox.bind(
            "<<ComboboxSelected>>",
            self.action_on_set_dropdown_change,
            add="+")
        lbl_tgt_bank = ttk.Label(self.sourceTargetLabelframe)
        lbl_tgt_bank.configure(style="Heading4.TLabel", text='Target:')
        lbl_tgt_bank.pack(pady="15 0")
        self.targetBank_Combobox = ttk.Combobox(
            self.sourceTargetLabelframe, name="targetbank_combobox")
        self.targetBank_Combobox.pack(padx=10, pady="0 10")
        self.sourceTargetLabelframe.grid(column=0, row=0)
        self.bankRouting_Labelframe.pack(anchor="w", padx=10, pady="20 10")
        self.channelsAccordion_Frame.grid(row=1)
        self.channels_all.pack(
            anchor="n",
            expand=True,
            fill="both",
            padx=5,
            pady=5,
            side="top")
        self.channels_all.grid_anchor("nw")
        self.scan_all = ttk.Frame(
            self.sdrCommands_ScrolledFrame.innerframe,
            name="scan_all")
        self.scan_all.configure(style="Normal.TFrame")
        self.scan_Frame = ttk.Frame(self.scan_all, name="scan_frame")
        self.scan_Frame.configure(style="Normal.TFrame")
        self.scanToggle_Button = ttk.Button(
            self.scan_Frame, name="scantoggle_button")
        self.scanToggle_Button.configure(
            state="normal", style="Custom.Toolbutton", text='Scan')
        self.scanToggle_Button.pack(expand=False, side="left")
        self.scanToggle_Button.configure(command=self.toggleScan_CB)
        self.scan_Frame.grid(column=0, row=0, sticky="nw")
        self.scanAccordion_Frame = HideableFrame(
            self.scan_all, name="scanaccordion_frame")
        self.scanAccordion_Frame.configure(style="Normal.TFrame")
        self.scanParameters_Labelframe = ttk.Labelframe(
            self.scanAccordion_Frame, name="scanparameters_labelframe")
        self.scanParameters_Labelframe.configure(
            style="Normal.TLabelframe", text='Settings')
        lbl_delay = ttk.Label(self.scanParameters_Labelframe)
        lbl_delay.configure(
            style="Heading4.TLabel",
            text='Scan Delay Period (ms):')
        lbl_delay.grid(column=0, padx=5, pady=10, row=0)
        self.entry_scan_time = ttk.Entry(
            self.scanParameters_Labelframe,
            name="entry_scan_time")
        self.entry_scan_time.configure(width=6)
        self.entry_scan_time.grid(column=1, padx=5, pady=10, row=0, sticky="w")
        self.scanBankSelect_Label = ttk.Label(
            self.scanParameters_Labelframe,
            name="scanbankselect_label")
        self.scanBankSelect_Label.configure(
            style="Heading4.TLabel", text='Source Bank:')
        self.scanBankSelect_Label.grid(
            column=0, padx=5, pady=2, row=1, sticky="w")
        self.scanBankSelect_Combobox = ttk.Combobox(
            self.scanParameters_Labelframe, name="scanbankselect_combobox")
        self.scanBankSelect_Combobox.grid(
            column=1, padx=5, pady=2, row=1, sticky="w")
        self.scanBankSelect_Combobox.bind(
            "<<ComboboxSelected>>",
            self.action_on_set_dropdown_change,
            add="+")
        self.scanParameters_Labelframe.pack(padx=10)
        self.scanControl_Labelframe = ttk.Labelframe(
            self.scanAccordion_Frame, name="scancontrol_labelframe")
        self.scanControl_Labelframe.configure(
            style="Normal.TLabelframe", text='Control')
        self.scanStart_Button = ttk.Button(
            self.scanControl_Labelframe,
            name="scanstart_button")
        self.scanStart_Button.configure(
            style="Button3Raised.TButton",
            text='▶ Start Scan ')
        self.scanStart_Button.grid(column=0, padx=5, pady=5, row=0)
        self.scanStart_Button.configure(command=self.action_start_scan)
        self.scanStop_Button = ttk.Button(
            self.scanControl_Labelframe,
            name="scanstop_button")
        self.scanStop_Button.configure(
            style="Button3Raised.TButton",
            text='⏹ Stop Scan')
        self.scanStop_Button.grid(column=1, padx=5, pady=5, row=0)
        self.scanStop_Button.configure(command=self.stop_scan)
        self.scanControl_Labelframe.pack(anchor="w", padx=10, pady=10)
        self.scanAccordion_Frame.grid(row=1)
        self.scan_all.pack(
            anchor="n",
            expand=True,
            fill="both",
            padx=5,
            pady=5,
            side="top")
        self.scan_all.grid_anchor("nw")
        self.sdrCommands_ScrolledFrame.pack(
            anchor="n", expand=True, fill="both", side="top")
        self.connectionStatus_Frame = ttk.Labelframe(
            self, name="connectionstatus_frame")
        self.connectionStatus_Frame.configure(
            style="Normal.TLabelframe", text='Status')
        self.ipAddress_Label = ttk.Label(
            self.connectionStatus_Frame,
            name="ipaddress_label")
        self.ipAddress_Label.configure(
            style="Heading4.TLabel",
            text='SDR IP Address:')
        self.ipAddress_Label.grid(
            column=0, padx="40 10", pady=5, row=0, sticky="e")
        self.portLabel = ttk.Label(
            self.connectionStatus_Frame,
            name="portlabel")
        self.portLabel.configure(
            style="Heading4.TLabel",
            text='TCP Socket Port:')
        self.portLabel.grid(column=2, padx="20 10", pady=5, row=0)
        self.sdrStatus_Label = ttk.Label(
            self.connectionStatus_Frame,
            name="sdrstatus_label")
        self.sdrStatus_Label.configure(
            style="Heading4.TLabel", text='SDR Status:')
        self.sdrStatus_Label.grid(column=0, row=2, sticky="e")
        self.linkStatus_Label = ttk.Label(
            self.connectionStatus_Frame,
            name="linkstatus_label")
        self.linkStatus_VAR = tk.StringVar(value='Disconnected')
        self.linkStatus_Label.configure(
            style="RedLED3.TLabel",
            takefocus=False,
            text='Disconnected',
            textvariable=self.linkStatus_VAR)
        self.linkStatus_Label.grid(column=1, row=2)
        self.reconnect_Button = ttk.Button(
            self.connectionStatus_Frame,
            name="reconnect_button")
        self.reconnect_Button.configure(
            style="Button3Raised.TButton", text='Reconnect')
        self.reconnect_Button.grid(column=2, columnspan=2, pady=5, row=2)
        self.reconnect_Button.configure(command=self.action_connect)
        self.sdrIPAddress_Label = ttk.Label(
            self.connectionStatus_Frame,
            name="sdripaddress_label")
        self.sdrIPAddress_VAR = tk.StringVar(value='0.0.0.0\t')
        self.sdrIPAddress_Label.configure(
            state="normal",
            style="Heading4.TLabel",
            text='0.0.0.0\t',
            textvariable=self.sdrIPAddress_VAR)
        self.sdrIPAddress_Label.grid(column=1, row=0, sticky="w")
        self.sdrPortNumber_Label = ttk.Label(
            self.connectionStatus_Frame,
            name="sdrportnumber_label")
        self.sdrPortNumber_VAR = tk.StringVar(value='8000')
        self.sdrPortNumber_Label.configure(
            style="Heading4.TLabel",
            text='8000',
            textvariable=self.sdrPortNumber_VAR)
        self.sdrPortNumber_Label.grid(column=3, row=0)
        self.connectionStatus_Frame.pack(anchor="s", side="bottom")
        self.connectionStatus_Frame.grid_anchor("s")
        self.configure(height=800, style="Normal.TFrame", width=600)
        # Layout for 'primaryFrame' skipped in custom widget template.

    def action_on_volume_slider_move(self, event=None):
        pass

    def action_toggle_mute(self):
        pass

    def toggleBands_CB(self):
        pass

    def action_quick_band(self, widget_id):
        pass

    def action_quick_mode(self, widget_id):
        pass

    def action_filter_widen(self):
        pass

    def action_filter_narrow(self):
        pass

    def action_filter_reset(self):
        pass

    def action_master_force_bw(self):
        pass

    def toggleChannels_CB(self):
        pass

    def action_on_channel_row_click(self, event=None):
        pass

    def action_filter_search_grid(self, event=None):
        pass

    def action_copy_row_to_target_bank(self):
        pass

    def action_del_ch(self):
        pass

    def action_capture_live_vfo_to_channel(self):
        pass

    def action_bulk_clone_source_to_target(self):
        pass

    def action_delete_source_bank_profile(self):
        pass

    def action_create_brand_new_bank(self):
        pass

    def action_on_set_dropdown_change(self, event=None):
        pass

    def toggleScan_CB(self):
        pass

    def action_start_scan(self):
        pass

    def stop_scan(self):
        pass

    def action_connect(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = sdrDashboardUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
