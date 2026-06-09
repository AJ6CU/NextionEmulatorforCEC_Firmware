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
        self.logbookSwitch_VAR = tk.StringVar()
        self.logbookSwitch_Menbutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.logbookSwitch_VAR,
            width=5)
        self.logbookSwitch_Menu = tk.Menu(
            self.logbookSwitch_Menbutton,
            name="logbookswitch_menu")
        self.logbookSwitch_Menu.configure(tearoff=False)
        self.logbookSwitch_Menu.add(
            "command",
            command=self.selectLogbookOn_CB,
            font="{Arial} 24 {}",
            label='True ',
            state="normal")
        self.logbookSwitch_Menu.add(
            "command",
            command=self.selectLogbookOff_CB,
            font="{Arial} 24 {}",
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
        self.logbookType_VAR = tk.StringVar()
        self.logbookType_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.logbookType_VAR,
            width=5)
        self.logbookType_Menu = tk.Menu(
            self.logbookType_Menubutton,
            name="logbooktype_menu")
        self.logbookType_Menu.configure(tearoff=False)
        self.logbookType_Menu.add(
            "command",
            command=self.selectLogbookType_CSV_CB,
            font="{Arial} 24 {}",
            label='csv',
            state="normal")
        self.logbookType_Menu.add(
            "command",
            command=self.selectLogbookType_ADI_CB,
            font="{Arial} 24 {}",
            label='adi',
            state="normal")
        self.logbookType_Menubutton.configure(menu=self.logbookType_Menu)
        self.logbookType_Menubutton.grid(
            column=1, padx="15 5", pady="40 20", row=2, sticky="w")
        self.logbookFileSelectorButton = PathChooserButton(
            self.general_Settings_Frame, name="logbookfileselectorbutton")
        self.logbookDirectoryLocation_VAR = tk.StringVar(
            value='Select\nLogbook\nLocation')
        self.logbookFileSelectorButton.configure(
            initialdir="~",
            mustexist=True,
            style="Button2Sunken.TButton",
            text='Select\nLogbook\nLocation',
            textvariable=self.logbookDirectoryLocation_VAR,
            type="directory")
        self.logbookFileSelectorButton.grid(
            column=0, padx=10, pady="40 10", row=4, sticky="nse")
        self.logbookFileSelectorButton.bind(
            "<<PathChooserPathChanged>>",
            self.newLogbookLocation_CB,
            add="+")
        self.logbookLocation_Text = tk.Text(
            self.general_Settings_Frame,
            name="logbooklocation_text")
        self.logbookLocation_Text.configure(
            background="gray",
            borderwidth=0,
            font="{Arial} 14 {bold}",
            foreground="white",
            height=3,
            highlightbackground="gray",
            highlightcolor="gray",
            highlightthickness=0,
            inactiveselectbackground="gray",
            insertbackground="gray",
            insertborderwidth=0,
            selectbackground="blue",
            selectborderwidth=0,
            selectforeground="gray",
            width=50,
            wrap="char")
        self.logbookLocation_Text.grid(column=1, padx=10, row=4)
        self.logbookName_Label1 = ttk.Label(
            self.general_Settings_Frame,
            name="logbookname_label1")
        self.logbookName_Label1.configure(
            style="Heading1b.TLabel", text='Logfile\nName')
        self.logbookName_Label1.grid(
            column=0, pady="20 0", row=5, sticky="nse")
        self.logbookName_Entry = tk.Entry(
            self.general_Settings_Frame,
            name="logbookname_entry")
        self.logbookName_VAR = tk.StringVar()
        self.logbookName_Entry.configure(
            background="gray",
            borderwidth=0,
            font="{Arial} 14 {bold}",
            foreground="white",
            highlightbackground="gray",
            justify="left",
            readonlybackground="gray",
            state="readonly",
            textvariable=self.logbookName_VAR,
            width=40)
        self.logbookName_Entry.grid(
            column=1,
            padx=10,
            pady="40 10",
            row=5,
            rowspan=1,
            sticky="nsw")
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

    def newLogbookLocation_CB(self, event=None):
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
