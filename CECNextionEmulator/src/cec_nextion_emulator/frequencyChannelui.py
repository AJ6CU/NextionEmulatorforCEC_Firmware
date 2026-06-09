#!/usr/bin/python3
"""
frequency channel line

an individual frame to contain channel information for read/write/scan

UI source file: frequencyChannel.ui
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
class frequencyChannelUI(ttk.Frame):
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

        self.channel_Number_Label = ttk.Label(
            self, name="channel_number_label")
        self.channel_Number_VAR = tk.StringVar()
        self.channel_Number_Label.configure(
            anchor="e",
            style="Heading1bi.TLabel",
            textvariable=self.channel_Number_VAR,
            width=3)
        # First object created
        on_first_object_cb(self.channel_Number_Label)

        self.channel_Number_Label.grid(column=0, padx="0 5", row=0, sticky="w")
        self.channel_Select_Button = ttk.Button(
            self, name="channel_select_button")
        self.channel_Select_VAR = tk.StringVar(value='Select')
        self.channel_Select_Button.configure(
            style="Button1bARaised.TButton",
            text='Select',
            textvariable=self.channel_Select_VAR,
            width=8)
        self.channel_Select_Button.grid(column=1, padx="5 0", row=0)
        self.channel_Select_Button.configure(command=self.channel_Select_CB)
        self.channel_Name_Entry = ttk.Entry(self, name="channel_name_entry")
        self.channel_Label_VAR = tk.StringVar()
        self.channel_Name_Entry.configure(
            font="{Arial} 20 {bold}",
            justify="left",
            textvariable=self.channel_Label_VAR,
            validate="focusout",
            width=6)
        self.channel_Name_Entry.grid(
            column=2, ipady=2, padx="5 0", row=0, sticky="w")
        _validatecmd = (self.channel_Name_Entry.register(
            self.channel_Lavel_Validation_CB), "%P", "%V")
        self.channel_Name_Entry.configure(validatecommand=_validatecmd)
        self.channel_Name_Entry.bind(
            "<Button>", self.channel_Label_Entered_CB, add="+")
        self.freq_Entry = ttk.Entry(self, name="freq_entry")
        self.channel_Freq_VAR = tk.StringVar()
        self.freq_Entry.configure(
            font="{Arial} 20 {bold}",
            justify="right",
            style="Entry1b.TEntry",
            textvariable=self.channel_Freq_VAR,
            validate="focusout",
            width=10)
        self.freq_Entry.grid(column=3, ipady=2, padx="5 0", row=0, sticky="w")
        _validatecmd = (
            self.freq_Entry.register(
                self.channel_Freq_Validation_CB),
            "%P",
            "%V")
        self.freq_Entry.configure(validatecommand=_validatecmd)
        self.freq_Entry.bind("<Button>", self.numeric_Keypad_CB, add="+")
        self.dirtyChannel_Label = ttk.Label(self, name="dirtychannel_label")
        self.dirtyChannel_Label.configure(style="GreenLED.TLabel", width=2)
        self.dirtyChannel_Label.grid(column=7, padx="10 5", row=0)
        self.mode_Menubutton = ttk.Menubutton(self, name="mode_menubutton")
        self.channel_Mode_VAR = tk.StringVar(value=' ')
        self.mode_Menubutton.configure(
            style="Heading1b.TMenubutton",
            text=' ',
            textvariable=self.channel_Mode_VAR,
            width=5)
        self.mode_Menu = tk.Menu(self.mode_Menubutton, name="mode_menu")
        self.mode_Menu.configure(tearoff=False)
        def DFT_cmd(itemid="DFT"): self.Channel_Mode_Changed_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=DFT_cmd,
            font="{Arial} 24 {}",
            label='DFT')

        def LSB_cmd(itemid="LSB"): self.Channel_Mode_Changed_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=LSB_cmd,
            font="{Arial} 24 {}",
            label='LSB')

        def USB_cmd(itemid="USB"): self.Channel_Mode_Changed_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=USB_cmd,
            font="{Arial} 24 {}",
            label='USB')

        def CWL_cmd(itemid="CWL"): self.Channel_Mode_Changed_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=CWL_cmd,
            font="{Arial} 24 {}",
            label='CWL')

        def CWU_cmd(itemid="CWU"): self.Channel_Mode_Changed_CB(itemid)
        self.mode_Menu.add(
            "command",
            command=CWU_cmd,
            font="{Arial} 24 {}",
            label='CWU')
        self.mode_Menubutton.configure(menu=self.mode_Menu)
        self.mode_Menubutton.grid(column=4, padx="5 0", row=0)
        self.show_Label_Menubutton = ttk.Menubutton(
            self, name="show_label_menubutton")
        self.channel_ShowLabel_VAR = tk.StringVar(value=' ')
        self.show_Label_Menubutton.configure(
            style="Heading1b.TMenubutton",
            text=' ',
            textvariable=self.channel_ShowLabel_VAR,
            width=5)
        self.show_Label_Menu = tk.Menu(
            self.show_Label_Menubutton,
            name="show_label_menu")
        self.show_Label_Menu.configure(tearoff=False)
        def Yes_cmd(itemid="Yes"): self.Channel_ShowLabel_Changed_CB(itemid)
        self.show_Label_Menu.add(
            "command",
            command=Yes_cmd,
            font="{Arial} 24 {}",
            label='Yes')

        def No_cmd(itemid="No"): self.Channel_ShowLabel_Changed_CB(itemid)
        self.show_Label_Menu.add(
            "command",
            command=No_cmd,
            font="{Arial} 24 {}",
            label='No')
        self.show_Label_Menubutton.configure(menu=self.show_Label_Menu)
        self.show_Label_Menubutton.grid(column=5, padx="5 0", row=0)
        self.scan_Set_Menubutton = ttk.Menubutton(
            self, name="scan_set_menubutton")
        self.channel_ScanSet_VAR = tk.StringVar(value=' ')
        self.scan_Set_Menubutton.configure(
            style="Heading1b.TMenubutton",
            text=' ',
            textvariable=self.channel_ScanSet_VAR,
            width=5)
        self.scan_Set_Menu = tk.Menu(
            self.scan_Set_Menubutton,
            name="scan_set_menu")
        self.scan_Set_Menu.configure(tearoff=False)

        def None_Command_cmd(
            itemid="None_Command"): self.Channel_ScanSet_Changed_CB(itemid)
        self.scan_Set_Menu.add(
            "command",
            command=None_Command_cmd,
            font="{Arial} 24 {}",
            label='None')

        def Scan1_Command_cmd(
            itemid="Scan1_Command"): self.Channel_ScanSet_Changed_CB(itemid)
        self.scan_Set_Menu.add(
            "command",
            command=Scan1_Command_cmd,
            font="{Arial} 24 {}",
            label='Scan1')

        def Scan2_Command_cmd(
            itemid="Scan2_Command"): self.Channel_ScanSet_Changed_CB(itemid)
        self.scan_Set_Menu.add(
            "command",
            command=Scan2_Command_cmd,
            font="{Arial} 24 {}",
            label='Scan2')

        def Scan3_Command_cmd(
            itemid="Scan3_Command"): self.Channel_ScanSet_Changed_CB(itemid)
        self.scan_Set_Menu.add(
            "command",
            command=Scan3_Command_cmd,
            font="{Arial} 24 {}",
            label='Scan3')
        def Scan4_Command_cmd(
            itemid="Scan4_Command"): self.Channel_ScanSet_Changed_CB(itemid)
        self.scan_Set_Menu.add(
            "command",
            command=Scan4_Command_cmd,
            font="{Arial} 24 {}",
            label='Scan4')
        self.scan_Set_Menubutton.configure(menu=self.scan_Set_Menu)
        self.scan_Set_Menubutton.grid(column=6, padx="5 0", row=0)
        self.configure(height=200, style="Normal.TFrame", width=600)
        # Layout for 'frequencyChannel' skipped in custom widget template.

    def channel_Select_CB(self):
        pass

    def channel_Lavel_Validation_CB(self, p_entry_value, v_condition):
        pass

    def channel_Label_Entered_CB(self, event=None):
        pass

    def channel_Freq_Validation_CB(self, p_entry_value, v_condition):
        pass

    def numeric_Keypad_CB(self, event=None):
        pass

    def Channel_Mode_Changed_CB(self, itemid):
        pass

    def Channel_ShowLabel_Changed_CB(self, itemid):
        pass

    def Channel_ScanSet_Changed_CB(self, itemid):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = frequencyChannelUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
