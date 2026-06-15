#!/usr/bin/python3
"""
settingsLogbook

Manages the settings for the logbook function

UI source file: settingsLogbook.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.pathchooserinput import PathChooserButton
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

        self.LogbookSwitch_Label = ttk.Label(
            self.general_Settings_Frame,
            name="logbookswitch_label")
        self.LogbookSwitch_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Logbook On')
        self.LogbookSwitch_Tooltip = Tooltip(self.LogbookSwitch_Label)
        self.LogbookSwitch_Tooltip.configure(
            padx=8,
            relief="raised",
            text="Turns off QSO logging. Any existing QSO's will be written to file.",
            wraplength=300)
        self.LogbookSwitch_Label.grid(
            column=0, padx=10, pady="40 20", row=1, sticky="e")
        self.LogbookSwitch_Menubutton = ttk.Menubutton(
            self.general_Settings_Frame, name="logbookswitch_menubutton")
        self.LogbookSwitch_VAR = tk.StringVar()
        self.LogbookSwitch_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.LogbookSwitch_VAR,
            width=5)
        self.LogbookSwitch_Menu = tk.Menu(
            self.LogbookSwitch_Menubutton,
            name="logbookswitch_menu")
        self.LogbookSwitch_Menu.configure(tearoff=False)
        self.LogbookSwitch_Menu.add(
            "command",
            command=self.selectLogbookOn_CB,
            font="{Arial} 24 {}",
            label='True ',
            state="normal")
        self.LogbookSwitch_Menu.add(
            "command",
            command=self.selectLogbookOff_CB,
            font="{Arial} 24 {}",
            label='False',
            state="normal")
        self.LogbookSwitch_Menubutton.configure(menu=self.LogbookSwitch_Menu)
        self.LogbookSwitch_Menubutton.grid(
            column=1, padx="15 5", pady="40 20", row=1, sticky="w")
        self.LogbookType_Label = ttk.Label(
            self.general_Settings_Frame,
            name="logbooktype_label")
        self.LogbookType_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Logbook Type')
        self.LogbookType_Tooltip = Tooltip(self.LogbookType_Label)
        self.LogbookType_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Select format for Logbook file. ".csv" for comma separated, or ".adi" for standard format used by ARRL and QRZ')
        self.LogbookType_Label.grid(
            column=0, padx=10, pady="40 20", row=2, sticky="e")
        self.LogbookType_Menubutton = ttk.Menubutton(
            self.general_Settings_Frame, name="logbooktype_menubutton")
        self.LogbookType_VAR = tk.StringVar()
        self.LogbookType_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.LogbookType_VAR,
            width=5)
        self.LogbookType_Menu = tk.Menu(
            self.LogbookType_Menubutton,
            name="logbooktype_menu")
        self.LogbookType_Menu.configure(tearoff=False)
        self.LogbookType_Menu.add(
            "command",
            command=self.selectLogbookType_CSV_CB,
            font="{Arial} 24 {}",
            label='csv',
            state="normal")
        self.LogbookType_Menu.add(
            "command",
            command=self.selectLogbookType_ADI_CB,
            font="{Arial} 24 {}",
            label='adi',
            state="normal")
        self.LogbookType_Menubutton.configure(menu=self.LogbookType_Menu)
        self.LogbookType_Menubutton.grid(
            column=1, padx="15 5", pady="40 20", row=2, sticky="w")
        self.backupInterval_Label = ttk.Label(
            self.general_Settings_Frame,
            name="backupinterval_label")
        self.backupInterval_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Backup Interval')
        self.backupInterval_Tooltip = Tooltip(self.backupInterval_Label)
        self.backupInterval_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Determines how often the log file is backed up. A "0" means at every write. Non-zero number indicates the minimum minutes between backups.',
            wraplength=300)
        self.backupInterval_Label.grid(
            column=0, padx=10, pady="40 20", row=3, sticky="e")
        self.backupInterval_Spinbox = ttk.Spinbox(
            self.general_Settings_Frame, name="backupinterval_spinbox")
        self.Backup_Interval_VAR = tk.StringVar()
        self.backupInterval_Spinbox.configure(
            font="{Arial} 36 {}",
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.Backup_Interval_VAR,
            values="0 5 10 15 30 60 120",
            width=3)
        self.backupInterval_Spinbox.grid(
            column=1, padx="20 0", pady="40 0", row=3, sticky="w")
        self.LogbookFileSelectorButton = PathChooserButton(
            self.general_Settings_Frame, name="logbookfileselectorbutton")
        self.LogbookDirectoryLocation_VAR = tk.StringVar(
            value='Select\nLogbook\nLocation')
        self.LogbookFileSelectorButton.configure(
            initialdir="~",
            mustexist=True,
            style="Button2Sunken.TButton",
            text='Select\nLogbook\nLocation',
            textvariable=self.LogbookDirectoryLocation_VAR,
            type="directory")
        self.LogbookFileSelector_Tooltip = Tooltip(
            self.LogbookFileSelectorButton)
        self.LogbookFileSelector_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Press this button and then navigate to the directory where you want your logbooks stored.',
            wraplength=300)
        self.LogbookFileSelectorButton.grid(
            column=0, padx=10, pady="40 10", row=4, sticky="nse")
        self.LogbookFileSelectorButton.bind(
            "<<PathChooserPathChanged>>",
            self.newLogbookLocation_CB,
            add="+")
        self.LogbookLocation_Text = tk.Text(
            self.general_Settings_Frame,
            name="logbooklocation_text")
        self.LogbookLocation_Text.configure(
            background="white",
            borderwidth=0,
            font="{Arial} 14 {bold}",
            foreground="black",
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
        self.LogbookLocation_Text.grid(column=1, padx=10, pady="40 10", row=4)
        self.LogbookName_Label = ttk.Label(
            self.general_Settings_Frame,
            name="logbookname_label")
        self.LogbookName_Label.configure(
            style="Heading1b.TLabel", text='Logfile Name')
        self.LogbookName_Tooltip = Tooltip(self.LogbookName_Label)
        self.LogbookName_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Enter a file name for your logfile. Files will be stored in the location specified above with either a "csv" or "adi" extension as appropriate.',
            wraplength=300)
        self.LogbookName_Label.grid(column=0, pady="20 0", row=5, sticky="e")
        self.LogbookName_Entry = tk.Entry(
            self.general_Settings_Frame,
            name="logbookname_entry")
        self.LogbookName_VAR = tk.StringVar()
        self.LogbookName_Entry.configure(
            background="white",
            borderwidth=0,
            cursor="arrow",
            font="{Arial} 14 {bold}",
            foreground="black",
            highlightbackground="gray",
            insertbackground="black",
            insertwidth=2,
            justify="left",
            readonlybackground="gray",
            state="normal",
            textvariable=self.LogbookName_VAR,
            validate="focusout",
            width=40)
        self.LogbookName_Entry.grid(
            column=1,
            padx=10,
            pady="20 0",
            row=5,
            rowspan=1,
            sticky="w")
        _validatecmd = (self.LogbookName_Entry.register(
            self.Logbook_Name_Validation_CB), "%P", "%V")
        self.LogbookName_Entry.configure(validatecommand=_validatecmd)
        _validatecmd = (
            self.LogbookName_Entry.register(
                self.Logbook_Name_Invalid_CB), "%P")
        self.LogbookName_Entry.configure(invalidcommand=_validatecmd)
        self.LogbookName_Entry.bind(
            "<Button>", self.Logbook_Name_Entered_CB, add="+")
        self.general_Settings_Frame.pack(padx=10, pady=10, side="top")
        self.closingFrame = ttk.Frame(self, name="closingframe")
        self.closingFrame.configure(
            height=50, style="Normal.TFrame", width=200)
        self.apply_Button = ttk.Button(self.closingFrame, name="apply_button")
        self.apply_Button.configure(style="Button2b.TButton", text='Apply')
        self.apply_Button_Tooltip = Tooltip(self.apply_Button)
        self.apply_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Accepts changes you made and closes the window',
            wraplength=300)
        self.apply_Button.pack(anchor="center", padx=10, side="left")
        self.apply_Button.configure(command=self.apply_CB)
        self.cancel_Buttom = ttk.Button(
            self.closingFrame, name="cancel_buttom")
        self.cancel_Buttom.configure(style="Button2b.TButton", text='Cancel')
        self.cancel_Button_Tooltip = Tooltip(self.cancel_Buttom)
        self.cancel_Button_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Closes the window without making any changes. ',
            wraplength=300)
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

    def Logbook_Name_Validation_CB(self, p_entry_value, v_condition):
        pass

    def Logbook_Name_Invalid_CB(self, p_entry_value):
        pass

    def Logbook_Name_Entered_CB(self, event=None):
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
