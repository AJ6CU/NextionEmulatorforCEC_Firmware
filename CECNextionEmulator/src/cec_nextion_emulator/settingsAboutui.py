#!/usr/bin/python3
"""
settingsAbout

Used to save general settings

UI source file: settingsAbout.ui
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
class settingsAboutUI(ttk.Labelframe):
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

        self.version_Label = ttk.Label(
            self.general_Settings_Frame,
            name="version_label")
        self.version_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Version:')
        self.version_Label.grid(column=0, padx=10, pady=10, row=0, sticky="e")
        self.versionID_Label = ttk.Label(
            self.general_Settings_Frame,
            name="versionid_label")
        self.versionID_VAR = tk.StringVar(value='2.0')
        self.versionID_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='2.0',
            textvariable=self.versionID_VAR)
        self.versionID_Label.grid(
            column=1, padx=10, pady=10, row=0, sticky="w")
        self.date_Label = ttk.Label(
            self.general_Settings_Frame,
            name="date_label")
        self.date_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Date:')
        self.date_Label.grid(column=0, padx=10, pady="0 10", row=1, sticky="e")
        self.releaseDate_Label = ttk.Label(
            self.general_Settings_Frame,
            name="releasedate_label")
        self.releaseDate_VAR = tk.StringVar(value='January 1, 1957')
        self.releaseDate_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='January 1, 1957',
            textvariable=self.releaseDate_VAR)
        self.releaseDate_Label.grid(
            column=1, padx=10, pady="0 10", row=1, sticky="w")
        self.author_Label = ttk.Label(
            self.general_Settings_Frame,
            name="author_label")
        self.author_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Author:')
        self.author_Label.grid(
            column=0,
            padx=10,
            pady="0 10",
            row=2,
            sticky="e")
        self.authorName_Label = ttk.Label(
            self.general_Settings_Frame,
            name="authorname_label")
        self.authorName_Label.configure(
            justify="left",
            style="Heading1b.TLabel",
            text='Mark Hatch (AJ6CU)')
        self.authorName_Label.grid(
            column=1, padx=10, pady="0 10", row=2, sticky="w")
        self.email_Label = ttk.Label(
            self.general_Settings_Frame,
            name="email_label")
        self.email_Label.configure(
            justify="left",
            style="Heading1b.TLabel",
            text='email:')
        self.email_Label.grid(
            column=0,
            padx=10,
            pady="0 10",
            row=3,
            sticky="e")
        self.emailAddress_Label = ttk.Label(
            self.general_Settings_Frame,
            name="emailaddress_label")
        self.emailAddress_Label.configure(
            justify="left",
            style="Heading1b.TLabel",
            text='markjhatch@gmail.com')
        self.emailAddress_Label.grid(
            column=1, padx=10, pady="0 10", row=3, sticky="w")
        self.configurationFile_Label = ttk.Label(
            self.general_Settings_Frame, name="configurationfile_label")
        self.configurationFile_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Configuration FIle:')
        self.configurationFile_Label.grid(
            column=0, padx=10, pady="0 10", row=4, sticky="e")
        self.configurationFileLocation_Entry = tk.Entry(
            self.general_Settings_Frame, name="configurationfilelocation_entry")
        self.configurationFileLocation_VAR = tk.StringVar(
            value='>>>location<<<')
        self.configurationFileLocation_Entry.configure(
            background="gray",
            borderwidth=0,
            font="{Arial} 14 {bold}",
            foreground="white",
            highlightbackground="gray",
            readonlybackground="gray",
            state="readonly",
            textvariable=self.configurationFileLocation_VAR,
            width=50)
        _text_ = '>>>location<<<'
        self.configurationFileLocation_Entry["state"] = "normal"
        self.configurationFileLocation_Entry.delete("0", "end")
        self.configurationFileLocation_Entry.insert("0", _text_)
        self.configurationFileLocation_Entry["state"] = "readonly"
        self.configurationFileLocation_Entry.grid(
            column=1, padx=10, pady="0 10", row=4, sticky="w")
        self.logFile_Label = ttk.Label(
            self.general_Settings_Frame,
            name="logfile_label")
        self.logFile_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Log FIle:')
        self.logFile_Label.grid(
            column=0,
            padx=10,
            pady="0 10",
            row=5,
            sticky="e")
        self.logFileLocation_Entry = tk.Entry(
            self.general_Settings_Frame,
            name="logfilelocation_entry")
        self.logFileLocation_VAR = tk.StringVar(value='>>>location<<<')
        self.logFileLocation_Entry.configure(
            background="gray",
            borderwidth=0,
            font="{Arial} 14 {bold}",
            foreground="white",
            highlightbackground="gray",
            readonlybackground="gray",
            state="readonly",
            textvariable=self.logFileLocation_VAR,
            width=50)
        _text_ = '>>>location<<<'
        self.logFileLocation_Entry["state"] = "normal"
        self.logFileLocation_Entry.delete("0", "end")
        self.logFileLocation_Entry.insert("0", _text_)
        self.logFileLocation_Entry["state"] = "readonly"
        self.logFileLocation_Entry.grid(
            column=1, padx=10, pady="0 10", row=5, sticky="w")
        self.license_Label = ttk.Label(
            self.general_Settings_Frame,
            name="license_label")
        self.license_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='License:')
        self.license_Label.grid(
            column=0,
            padx=10,
            pady="0 10",
            row=8,
            sticky="e")
        self.gplV3_Label = ttk.Label(
            self.general_Settings_Frame,
            name="gplv3_label")
        self.gplV3_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='GPL V3')
        self.gplV3_Label.grid(
            column=1,
            padx=10,
            pady="0 10",
            row=8,
            sticky="w")
        self.license_ID = ttk.Label(
            self.general_Settings_Frame,
            name="license_id")
        self.license_ID.configure(
            justify="left",
            style="Heading2b.TLabel",
            text='https://www.gnu.org/licenses/gpl-3.0.en.html')
        self.license_ID.grid(column=1, padx=10, pady="0 10", row=9, sticky="w")
        self.general_Settings_Frame.pack(padx=10, pady=10, side="top")
        self.closingFrame = ttk.Frame(self, name="closingframe")
        self.closingFrame.configure(
            height=50, style="Normal.TFrame", width=200)
        self.close_Button = ttk.Button(self.closingFrame, name="close_button")
        self.close_Button.configure(style="Button2b.TButton", text='Close')
        self.close_Button.pack(anchor="center", padx=10, side="left")
        self.close_Button.configure(command=self.close_CB)
        self.closingFrame.pack(
            anchor="center",
            expand=False,
            pady=20,
            side="top")
        self.configure(
            style="Heading2.TLabelframe",
            text='About CECNextionEmulator')
        # Layout for 'labelframe1' skipped in custom widget template.

    def close_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsAboutUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
