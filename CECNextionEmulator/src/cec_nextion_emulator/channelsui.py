#!/usr/bin/python3
"""
CW Settings Window

Used to save cw settings

UI source file: channels.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from frequencyChannel import frequencyChannel
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
class channelsUI(ttk.Labelframe):
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
        frame1.configure(style="Normal.TFrame", width=750)
        # First object created
        on_first_object_cb(frame1)

        self.display_Current_VFO_Frame = ttk.Frame(
            frame1, name="display_current_vfo_frame")
        self.display_Current_VFO_Frame.configure(
            height=24, style="Normal.TFrame", width=450)
        self.current_VFO_Heading_Label = ttk.Label(
            self.display_Current_VFO_Frame,
            name="current_vfo_heading_label")
        self.current_VFO_Heading_Label.configure(
            style="Heading1b.TLabel", text='Current VFO:')
        self.current_VFO_Heading_Label.pack(
            anchor="center", padx="75 0", side="left")
        self.channel_Text_Label = ttk.Label(
            self.display_Current_VFO_Frame,
            name="channel_text_label")
        self.channel_Text_Label.configure(
            style="Heading2b.TLabel", text='Channel:')
        self.channel_Text_Label.pack(padx="10 0", side="left")
        self.current_Channel = ttk.Label(
            self.display_Current_VFO_Frame,
            name="current_channel")
        self.current_Channel_VAR = tk.StringVar(value='Not Saved')
        self.current_Channel.configure(
            style="Heading2bi.TLabel",
            text='Not Saved',
            textvariable=self.current_Channel_VAR,
            width=10)
        self.current_Channel.pack(padx="5 0", side="left")
        self.current_VFO_Label = ttk.Label(
            self.display_Current_VFO_Frame,
            name="current_vfo_label")
        self.current_VFO_VAR = tk.StringVar(value='99.999.99')
        self.current_VFO_Label.configure(
            style="Heading2b.TLabel",
            text='99.999.99',
            textvariable=self.current_VFO_VAR)
        self.current_VFO_Label.pack(padx="10 0", side="left")
        self.current_Mode_Label = ttk.Label(
            self.display_Current_VFO_Frame,
            name="current_mode_label")
        self.current_Mode_VAR = tk.StringVar(value='CWL')
        self.current_Mode_Label.configure(
            style="Heading2b.TLabel",
            text='CWL',
            textvariable=self.current_Mode_VAR)
        self.current_Mode_Label.pack(expand=False, padx="10 10", side="left")
        self.display_Current_VFO_Frame.pack(expand=True, fill="x", side="top")
        frame2 = ttk.Frame(frame1)
        frame2.configure(height=800, style="Normal.TFrame")
        self.header_Line_Frame = ttk.Frame(frame2, name="header_line_frame")
        self.header_Line_Frame.configure(
            height=24, style="Normal.TFrame", width=450)
        self.channel_header_Label = ttk.Label(
            self.header_Line_Frame, name="channel_header_label")
        self.channel_header_Label.configure(
            style="Heading2b.TLabel", text='Chan')
        self.channel_header_Label.grid(column=0, padx="10 0", row=0)
        self.name_Header_Label = ttk.Label(
            self.header_Line_Frame, name="name_header_label")
        self.name_Header_Label.configure(style="Heading2b.TLabel", text='Name')
        self.name_Header_Label.grid(column=1, padx="165 0", row=0)
        self.frequency_Header_Label = ttk.Label(
            self.header_Line_Frame, name="frequency_header_label")
        self.frequency_Header_Label.configure(
            style="Heading2b.TLabel", text='Freq')
        self.frequency_Header_Label.grid(column=2, padx="95 0", row=0)
        self.mode_Header_Label = ttk.Label(
            self.header_Line_Frame, name="mode_header_label")
        self.mode_Header_Label.configure(style="Heading2b.TLabel", text='Mode')
        self.mode_Header_Label.grid(column=4, padx="80 0", row=0)
        self.showLabel_Header_Label = ttk.Label(
            self.header_Line_Frame, name="showlabel_header_label")
        self.showLabel_Header_Label.configure(
            style="Heading2b.TLabel", text='Visible')
        self.showLabel_Header_Label.grid(column=5, padx="75 0", row=0)
        self.scan_Set_Label = ttk.Label(
            self.header_Line_Frame, name="scan_set_label")
        self.scan_Set_Label.configure(
            style="Heading2b.TLabel", text='Scan\nSet')
        self.scan_Set_Label.grid(column=6, padx="80 7", row=0)
        self.dirtyIndicator_Label = ttk.Label(
            self.header_Line_Frame, name="dirtyindicator_label")
        self.dirtyIndicator_Label.configure(
            style="Heading2b.TLabel", text='Saved')
        self.dirtyIndicator_Label.grid(column=7, padx=30, row=0)
        self.header_Line_Frame.pack(expand=True, fill="x")
        self.frameSizer = ttk.Frame(frame2, name="framesizer")
        self.frameSizer.configure(height=550, style="Normal.TFrame")
        self.scrolledChannelFrame = ScrolledFrame(
            self.frameSizer, scrolltype="vertical", name="scrolledchannelframe")
        self.scrolledChannelFrame.innerframe.configure(
            relief="flat", style="Normal.TFrame")
        self.scrolledChannelFrame.configure(usemousewheel=True)
        self.frequencyChannel1 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel1")
        self.frequencyChannel1.pack(
            anchor="w", expand=True, fill="x", side="top")
        self.frequencyChannel2 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel2")
        self.frequencyChannel2.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel3 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel3")
        self.frequencyChannel3.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel4 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel4")
        self.frequencyChannel4.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel5 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel5")
        self.frequencyChannel5.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel6 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel6")
        self.frequencyChannel6.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel7 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel7")
        self.frequencyChannel7.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel8 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel8")
        self.frequencyChannel8.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel9 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel9")
        self.frequencyChannel9.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel10 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel10")
        self.frequencyChannel10.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel11 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel11")
        self.frequencyChannel11.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel12 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel12")
        self.frequencyChannel12.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel13 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel13")
        self.frequencyChannel13.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel14 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel14")
        self.frequencyChannel14.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel15 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel15")
        self.frequencyChannel15.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel16 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel16")
        self.frequencyChannel16.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel17 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel17")
        self.frequencyChannel17.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel18 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel18")
        self.frequencyChannel18.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel19 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel19")
        self.frequencyChannel19.pack(anchor="w", pady="10 0", side="top")
        self.frequencyChannel20 = frequencyChannel(
            self.scrolledChannelFrame.innerframe, name="frequencychannel20")
        self.frequencyChannel20.pack(anchor="w", pady="10 0", side="top")
        self.scrolledChannelFrame.pack(anchor="w", expand=True, fill="both")
        self.frameSizer.pack(expand=True, fill="both", side="left")
        self.frameSizer.pack_propagate(0)
        frame2.pack(expand=True, fill="both", side="top")
        frame3 = ttk.Frame(frame1)
        frame3.configure(height=200, style="Normal.TFrame", width=200)
        self.channelEdit_Frame = ttk.Frame(frame3, name="channeledit_frame")
        self.channelEdit_Frame.configure(style="Normal.TFrame", width=200)
        self.ChannelToVFO_Button = ttk.Button(
            self.channelEdit_Frame, name="channeltovfo_button")
        self.ChannelToVFO_Button.configure(
            compound="none",
            state="normal",
            style="Button2b.TButton",
            text='Channel->VFO',
            width=14)
        self.ChannelToVFO_Button.grid(column=0, padx="0 15", row=0)
        self.ChannelToVFO_Button.configure(command=self.ChannelToVFO_CB)
        self.VFOToChannel_Button = ttk.Button(
            self.channelEdit_Frame, name="vfotochannel_button")
        self.VFOToChannel_Button.configure(
            state="normal",
            style="Button2b.TButton",
            text='VFO->Channel',
            width=14)
        self.VFOToChannel_Button.grid(column=1, padx="0 15", row=0)
        self.VFOToChannel_Button.configure(command=self.VFOToChannel_CB)
        self.scan_Button = ttk.Button(
            self.channelEdit_Frame, name="scan_button")
        self.scan_Channel_ButtonText_VAR = tk.StringVar(value='Run Scan')
        self.scan_Button.configure(
            style="Button2b.TButton",
            text='Run Scan',
            textvariable=self.scan_Channel_ButtonText_VAR,
            width=14)
        self.scan_Button.grid(column=2, columnspan=2, row=0)
        self.scan_Button.configure(command=self.scan_Channel_CB)
        self.channelEdit_Frame.pack(expand=False, pady="5 15", side="top")
        self.channelEdit_Frame.grid_anchor("center")
        self.closingFrame = ttk.Frame(frame3, name="closingframe")
        self.closingFrame.configure(style="Normal.TFrame")
        self.saveChannel_Button = ttk.Button(
            self.closingFrame, name="savechannel_button")
        self.saveChannel_Button.configure(
            state="normal",
            style="Button2b.TButton",
            text='Save Channel')
        self.saveChannel_Button.grid(column=0, padx="0 15", row=0)
        self.saveChannel_Button.configure(command=self.saveChannel_CB)
        self.saveAllChannels_Button = ttk.Button(
            self.closingFrame, name="saveallchannels_button")
        self.saveAllChannels_Button.configure(
            state="normal", style="Button2b.TButton", text='Save All')
        self.saveAllChannels_Button.grid(column=1, padx="0 15", row=0)
        self.saveAllChannels_Button.configure(command=self.saveAllChannels_CB)
        self.refresh_Button = ttk.Button(
            self.closingFrame, name="refresh_button")
        self.refresh_Button.configure(style="Button2b.TButton", text='Refresh')
        self.refresh_Button.grid(column=2, padx="0 15", row=0)
        self.refresh_Button.configure(command=self.refresh_Channel_CB)
        self.close_Button = ttk.Button(self.closingFrame, name="close_button")
        self.close_Button.configure(style="Button2b.TButton", text='Close')
        self.close_Button.grid(column=3, row=0)
        self.close_Button.configure(command=self.close_Channel_CB)
        self.closingFrame.pack(pady="30 15", side="left")
        self.closingFrame.grid_anchor("center")
        frame3.pack(padx="75 0", side="left")
        self.scanSettings_Frame = ttk.Frame(frame1, name="scansettings_frame")
        self.scanSettings_Frame.configure(
            height=200, style="NormalOutline.TFrame", width=200)
        self.scan_Select_Channel_Label = ttk.Label(
            self.scanSettings_Frame, name="scan_select_channel_label")
        self.scan_Select_Channel_Label.configure(
            style="Heading2b.TLabel", text='Select Scan Set')
        self.scan_Select_Channel_Label.grid(
            column=0, padx=5, pady=15, row=1, sticky="e")
        self.scan_Select_Channel_Menubutton = ttk.Menubutton(
            self.scanSettings_Frame, name="scan_select_channel_menubutton")
        self.scan_Select_Channel_VAR = tk.StringVar(value='Select')
        self.scan_Select_Channel_Menubutton.configure(
            style="Heading1b.TMenubutton",
            text='Select',
            textvariable=self.scan_Select_Channel_VAR)
        self.scan_Select_Channel_Menu = tk.Menu(
            self.scan_Select_Channel_Menubutton,
            name="scan_select_channel_menu")
        self.scan_Select_Channel_Menu.configure(tearoff=False)

        def None_Command_cmd(
            itemid="None_Command"): self.selectScanSet_CB(itemid)
        self.scan_Select_Channel_Menu.add(
            "command",
            command=None_Command_cmd,
            font="{Arial} 20 {bold}",
            label='None')

        def Scan1_Command_cmd(
            itemid="Scan1_Command"): self.selectScanSet_CB(itemid)
        self.scan_Select_Channel_Menu.add(
            "command",
            command=Scan1_Command_cmd,
            font="{Arial} 20 {}",
            label='Scan1')

        def Scan2_Command_cmd(
            itemid="Scan2_Command"): self.selectScanSet_CB(itemid)
        self.scan_Select_Channel_Menu.add(
            "command",
            command=Scan2_Command_cmd,
            font="{Arial} 20 {bold}",
            label='Scan2')

        def Scan3_Command_cmd(
            itemid="Scan3_Command"): self.selectScanSet_CB(itemid)
        self.scan_Select_Channel_Menu.add(
            "command",
            command=Scan3_Command_cmd,
            font="{Arial} 20 {bold}",
            label='Scan3')
        def Scan4_Command_cmd(
            itemid="Scan4_Command"): self.selectScanSet_CB(itemid)
        self.scan_Select_Channel_Menu.add(
            "command",
            command=Scan4_Command_cmd,
            font="{Arial} 20 {bold}",
            label='Scn4')
        self.scan_Select_Channel_Menubutton.configure(
            menu=self.scan_Select_Channel_Menu)
        self.scan_Select_Channel_Menubutton.grid(column=1, row=1)
        self.Time_On_Freq_Label = ttk.Label(
            self.scanSettings_Frame, name="time_on_freq_label")
        self.Time_On_Freq_Label.configure(
            style="Heading2b.TLabel",
            text='Time on Freq(sec)')
        self.Time_On_Freq_Label.grid(
            column=0, padx="5 0", pady="10 0", row=2, sticky="e")
        self.Time_On_Freq_Spinbox = ttk.Spinbox(
            self.scanSettings_Frame, name="time_on_freq_spinbox")
        self.Time_On_Freq_VAR = tk.StringVar()
        self.Time_On_Freq_Spinbox.configure(
            font="{Arial} 36 {}",
            from_=1,
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.Time_On_Freq_VAR,
            to=20,
            width=2)
        self.Time_On_Freq_Spinbox.grid(
            column=1, padx="15 5", pady="40 20", row=2, sticky="w")
        self.scanSettings_Frame.pack(padx=5, pady="5 10", side="right")
        frame1.pack(expand=True, fill="both", side="top")
        self.configure(
            height=600,
            style="Heading2.TLabelframe",
            text='Frequency Channels')
        # Layout for 'labelframe1' skipped in custom widget template.

    def ChannelToVFO_CB(self):
        pass

    def VFOToChannel_CB(self):
        pass

    def scan_Channel_CB(self):
        pass

    def saveChannel_CB(self):
        pass

    def saveAllChannels_CB(self):
        pass

    def refresh_Channel_CB(self):
        pass

    def close_Channel_CB(self):
        pass

    def selectScanSet_CB(self, itemid):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = channelsUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
