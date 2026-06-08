#!/usr/bin/python3
"""
settingsLogbook

Manages the settings for the logbook function

UI source file: settingsLogbook.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.pathchooserinput import PathChooserButton


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
class settingsLogbookUI(ttk.Labelframe):
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

        self.general_Settings_Frame = ttk.Frame(
            self, name="general_settings_frame")
        self.general_Settings_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        # First object created
        on_first_object_cb(self.general_Settings_Frame)

        self.logbookSwitch_Label = ttk.Label(
            self.general_Settings_Frame,
            name="logbookswitch_label")
        self.logbookSwitch_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Logbook On')
        self.logbookSwitch_Label.grid(
            column=0, padx=10, pady="40 20", row=1, sticky="e")
        self.logbookSwitch_Menbutton = ttk.Menubutton(
            self.general_Settings_Frame, name="logbookswitch_menbutton")
        self.Virtual_Keyboard_VAR = tk.StringVar()
        self.logbookSwitch_Menbutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.Virtual_Keyboard_VAR,
            width=5)
        self.logbookSwitch_Menu = tk.Menu(
            self.logbookSwitch_Menbutton,
            name="logbookswitch_menu")
        self.logbookSwitch_Menu.configure(tearoff=False)
        self.logbookSwitch_Menu.add(
            "command",
            command=self.selectLogbookOn_CB,
            font="{Arial} 36 {}",
            label='True ',
            state="normal")
        self.logbookSwitch_Menu.add(
            "command",
            command=self.selectLogbookOff_CB,
            font="{Arial} 36 {}",
            label='False',
            state="normal")
        self.logbookSwitch_Menbutton.configure(menu=self.logbookSwitch_Menu)
        self.logbookSwitch_Menbutton.grid(
            column=1, padx="15 5", pady="40 20", row=1, sticky="w")
        self.logbookType_Label = ttk.Label(
            self.general_Settings_Frame,
            name="logbooktype_label")
        self.logbookType_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Logbook Type')
        self.logbookType_Label.grid(
            column=0, padx=10, pady="40 20", row=2, sticky="e")
        self.logbookType_Menubutton = ttk.Menubutton(
            self.general_Settings_Frame, name="logbooktype_menubutton")
        self.VFO_Touch_Optimized_VAR = tk.StringVar()
        self.logbookType_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.VFO_Touch_Optimized_VAR,
            width=5)
        self.logbookType_Menu = tk.Menu(
            self.logbookType_Menubutton,
            name="logbooktype_menu")
        self.logbookType_Menu.configure(tearoff=False)
        self.logbookType_Menu.add(
            "command",
            command=self.selectLogbookType_CSV_CB,
            font="{Arial} 36 {}",
            label='CSV (QRZ)',
            state="normal")
        self.logbookType_Menu.add(
            "command",
            command=self.selectLogbookType_ADI_CB,
            font="{Arial} 36 {}",
            label='ADI (ARRL)',
            state="normal")
        self.logbookType_Menubutton.configure(menu=self.logbookType_Menu)
        self.logbookType_Menubutton.grid(
            column=1, padx="15 5", pady="40 20", row=2, sticky="w")
        self.logbookFileSelectorButton = PathChooserButton(
            self.general_Settings_Frame, name="logbookfileselectorbutton")
        self.logbookFileSelectorButton.configure(
            mustexist=True,
            style="Button2Sunken.TButton",
            text='Select\nLogbook\nLocation',
            type="directory")
        self.logbookFileSelectorButton.grid(
            column=0, padx=10, pady="40 10", row=4, sticky="nse")
        self.logbookSelectedDirectory = tk.Entry(
            self.general_Settings_Frame,
            name="logbookselecteddirectory")
        self.logbookSelectedDirectory_VAR = tk.StringVar(
            value='>>>location<<<  ')
        self.logbookSelectedDirectory.configure(
            background="gray",
            borderwidth=0,
            font="{Arial} 14 {bold}",
            foreground="white",
            highlightbackground="gray",
            readonlybackground="gray",
            state="readonly",
            textvariable=self.logbookSelectedDirectory_VAR,
            width=50)
        _text_ = '>>>location<<<  '
        self.logbookSelectedDirectory["state"] = "normal"
        self.logbookSelectedDirectory.delete("0", "end")
        self.logbookSelectedDirectory.insert("0", _text_)
        self.logbookSelectedDirectory["state"] = "readonly"
        self.logbookSelectedDirectory.grid(
            column=1, padx=10, pady="40 10", row=4, rowspan=1, sticky="nsw")
        self.logbookName_Label1 = ttk.Label(
            self.general_Settings_Frame,
            name="logbookname_label1")
        self.logbookName_Label1.configure(
            style="Heading1b.TLabel", text='Logfile\nName')
        self.logbookName_Label1.grid(
            column=0, pady="20 0", row=5, sticky="nse")
        self.logbookFileName_Entry = tk.Entry(
            self.general_Settings_Frame,
            name="logbookfilename_entry")
        self.logbookFileName_VAR = tk.StringVar(value='>>>location<<<  ')
        self.logbookFileName_Entry.configure(
            background="gray",
            borderwidth=0,
            font="{Arial} 14 {bold}",
            foreground="white",
            highlightbackground="gray",
            readonlybackground="gray",
            state="readonly",
            textvariable=self.logbookFileName_VAR,
            width=50)
        _text_ = '>>>location<<<  '
        self.logbookFileName_Entry["state"] = "normal"
        self.logbookFileName_Entry.delete("0", "end")
        self.logbookFileName_Entry.insert("0", _text_)
        self.logbookFileName_Entry["state"] = "readonly"
        self.logbookFileName_Entry.grid(
            column=1, padx=10, pady="40 10", row=5, sticky="nsw")
        self.general_Settings_Frame.pack(padx=10, pady=10, side="top")
        self.closingFrame = ttk.Frame(self, name="closingframe")
        self.closingFrame.configure(
            height=50, style="Normal.TFrame", width=200)
        self.apply_Button = ttk.Button(self.closingFrame, name="apply_button")
        self.apply_Button.configure(style="Button2b.TButton", text='Apply')
        self.apply_Button.pack(anchor="center", padx=10, side="left")
        self.apply_Button.configure(command=self.apply_CB)
        self.cancel_Buttom = ttk.Button(
            self.closingFrame, name="cancel_buttom")
        self.cancel_Buttom.configure(style="Button2b.TButton", text='Cancel')
        self.cancel_Buttom.pack(anchor="center", padx=10, side="left")
        self.cancel_Buttom.configure(command=self.cancel_CB)
        self.closingFrame.pack(
            anchor="center",
            expand=False,
            pady=20,
            side="top")
        self.configure(style="Heading2.TLabelframe", text='Logbook Settings')
        # Layout for 'labelframe1' skipped in custom widget template.

    def selectLogbookOn_CB(self):
        pass

    def selectLogbookOff_CB(self):
        pass

    def selectLogbookType_CSV_CB(self):
        pass

    def selectLogbookType_ADI_CB(self):
        pass

    def apply_CB(self):
        pass

    def cancel_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsLogbookUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
