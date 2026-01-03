#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.combobox import Combobox


def i18n_translator_noop(value):
    """i18n - Setup translator in derived class file"""
    return value


def first_object_callback_noop(widget):
    """on first objec callback - Setup callback in derived class file."""
    pass


def image_loader_default(master, image_name: str):
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
class settingsGeneralUI(ttk.Labelframe):
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
            translator = i18n_translator_noop
        _ = translator  # i18n string marker.
        if image_loader is None:
            image_loader = image_loader_default
        if on_first_object_cb is None:
            on_first_object_cb = first_object_callback_noop

        super().__init__(master, **kw)

        self.general_Settings_Frame = ttk.Frame(
            self, name="general_settings_frame")
        self.general_Settings_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        # First object created
        on_first_object_cb(self.general_Settings_Frame)

        self.Number_Delimiter_Label = ttk.Label(
            self.general_Settings_Frame,
            name="number_delimiter_label")
        self.Number_Delimiter_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Number Delimiter')
        self.Number_Delimiter_Label.grid(
            column=0, padx=10, pady=10, row=0, sticky="e")
        self.Number_Delimiter_Combobox = Combobox(
            self.general_Settings_Frame,
            name="number_delimiter_combobox")
        self.NUMBER_DELIMITER_VAR = tk.StringVar()
        self.Number_Delimiter_Combobox.configure(
            justify="center",
            keyvariable=self.NUMBER_DELIMITER_VAR,
            style="ComboBox1.TCombobox",
            values=', .',
            width=5)
        self.Number_Delimiter_Combobox.grid(
            column=1, padx="20 0", row=0, sticky="w")
        self.Virtual_Keyboard_Label = ttk.Label(
            self.general_Settings_Frame,
            name="virtual_keyboard_label")
        self.Virtual_Keyboard_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Virtual Keyboard On')
        self.Virtual_Keyboard_Label.grid(
            column=0, padx=10, pady="40 20", row=1, sticky="e")
        self.Virtual_Keyboard_Combobox = Combobox(
            self.general_Settings_Frame,
            name="virtual_keyboard_combobox")
        self.Virtual_Keyboard_VAR = tk.StringVar()
        self.Virtual_Keyboard_Combobox.configure(
            keyvariable=self.Virtual_Keyboard_VAR,
            style="ComboBox1.TCombobox",
            values='True False',
            width=5)
        self.Virtual_Keyboard_Combobox.grid(
            column=1, padx="20 0", pady="40 20", row=1, sticky="w")
        self.VFO_Touch_Optimized_Label = ttk.Label(
            self.general_Settings_Frame, name="vfo_touch_optimized_label")
        self.VFO_Touch_Optimized_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='VFO Touch Optimized')
        self.VFO_Touch_Optimized_Label.grid(
            column=0, padx=10, pady="40 20", row=2, sticky="e")
        self.VFO_Touch_Optimized_Combobox = Combobox(
            self.general_Settings_Frame, name="vfo_touch_optimized_combobox")
        self.VFO_Touch_Optimized_VAR = tk.StringVar()
        self.VFO_Touch_Optimized_Combobox.configure(
            keyvariable=self.VFO_Touch_Optimized_VAR,
            style="ComboBox1.TCombobox",
            values='True False',
            width=5)
        self.VFO_Touch_Optimized_Combobox.grid(
            column=1, padx="20 0", pady="40 20", row=2, sticky="w")
        self.Time_On_Freq_Label = ttk.Label(
            self.general_Settings_Frame,
            name="time_on_freq_label")
        self.Time_On_Freq_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Time on Frequency\nduring Scan')
        self.Time_On_Freq_Label.grid(
            column=0, padx=10, pady="40 20", row=3, sticky="e")
        self.Time_On_Freq_Combobox = Combobox(
            self.general_Settings_Frame,
            name="time_on_freq_combobox")
        self.Time_On_Freq_VAR = tk.StringVar()
        self.Time_On_Freq_Combobox.configure(
            justify="right",
            keyvariable=self.Time_On_Freq_VAR,
            style="ComboBox1.TCombobox",
            values='1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20',
            width=5)
        self.Time_On_Freq_Combobox.grid(
            column=1, padx="20 0", pady="40 20", row=3, sticky="w")
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
        self.configure(
            height=400,
            style="Heading2.TLabelframe",
            text='General Settings',
            width=600)
        # Layout for 'labelframe1' skipped in custom widget template.

    def apply_CB(self):
        pass

    def cancel_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsGeneralUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
