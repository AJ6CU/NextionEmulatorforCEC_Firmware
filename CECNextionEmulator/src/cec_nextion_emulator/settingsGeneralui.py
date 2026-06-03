#!/usr/bin/python3
"""
settingsGeneral

Used to save general settings

UI source file: settingsGeneral.ui
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

        self.Number_Delimiter_Label = ttk.Label(
            self.general_Settings_Frame,
            name="number_delimiter_label")
        self.Number_Delimiter_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Number Delimiter')
        self.Number_Delimiter_Label.grid(
            column=0, padx=10, pady=10, row=0, sticky="e")
        self.Number_Delimiter_Menubutton = ttk.Menubutton(
            self.general_Settings_Frame, name="number_delimiter_menubutton")
        self.NUMBER_DELIMITER_VAR = tk.StringVar()
        self.Number_Delimiter_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.NUMBER_DELIMITER_VAR,
            width=2)
        self.Number_Delimiter_Menu = tk.Menu(
            self.Number_Delimiter_Menubutton,
            name="number_delimiter_menu")
        self.Number_Delimiter_Menu.configure(tearoff=False)
        self.Number_Delimiter_Menu.add(
            "command",
            command=self.selectCommaDelimiter_CB,
            font="{Arial} 36 {}",
            label='  ,  ',
            state="normal")
        self.Number_Delimiter_Menu.add(
            "command",
            command=self.selectPeriodDelimiter_CB,
            font="{Arial} 36 {}",
            label='  .  ',
            state="normal")
        self.Number_Delimiter_Menubutton.configure(
            menu=self.Number_Delimiter_Menu)
        self.Number_Delimiter_Menubutton.grid(
            column=1, padx="15 5", pady=10, row=0, sticky="w")
        self.Virtual_Keyboard_Menubutton = ttk.Menubutton(
            self.general_Settings_Frame, name="virtual_keyboard_menubutton")
        self.Virtual_Keyboard_VAR = tk.StringVar()
        self.Virtual_Keyboard_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.Virtual_Keyboard_VAR,
            width=5)
        self.Virtual_Keyboard_Menu = tk.Menu(
            self.Virtual_Keyboard_Menubutton,
            name="virtual_keyboard_menu")
        self.Virtual_Keyboard_Menu.configure(tearoff=False)
        self.Virtual_Keyboard_Menu.add(
            "command",
            command=self.selectVirtualKeyboardOn_CB,
            font="{Arial} 36 {}",
            label='True ',
            state="normal")
        self.Virtual_Keyboard_Menu.add(
            "command",
            command=self.selectVirtualKeyboardOff_CB,
            font="{Arial} 36 {}",
            label='False',
            state="normal")
        self.Virtual_Keyboard_Menubutton.configure(
            menu=self.Virtual_Keyboard_Menu)
        self.Virtual_Keyboard_Menubutton.grid(
            column=1, padx="15 5", pady="40 20", row=1, sticky="e")
        self.Virtual_Keyboard_Label = ttk.Label(
            self.general_Settings_Frame,
            name="virtual_keyboard_label")
        self.Virtual_Keyboard_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Virtual Keyboard On')
        self.Virtual_Keyboard_Label.grid(
            column=0, padx=10, pady="40 20", row=1, sticky="e")
        self.VFO_Touch_Optimized_Label = ttk.Label(
            self.general_Settings_Frame, name="vfo_touch_optimized_label")
        self.VFO_Touch_Optimized_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='VFO Touch Optimized')
        self.VFO_Touch_Optimized_Label.grid(
            column=0, padx=10, pady="40 20", row=2, sticky="e")
        self.VFO_Touch_Optimized_Menubutton = ttk.Menubutton(
            self.general_Settings_Frame, name="vfo_touch_optimized_menubutton")
        self.VFO_Touch_Optimized_VAR = tk.StringVar()
        self.VFO_Touch_Optimized_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.VFO_Touch_Optimized_VAR,
            width=5)
        self.VFO_Touch_Optimized_Menu = tk.Menu(
            self.VFO_Touch_Optimized_Menubutton,
            name="vfo_touch_optimized_menu")
        self.VFO_Touch_Optimized_Menu.configure(tearoff=False)
        self.VFO_Touch_Optimized_Menu.add(
            "command",
            command=self.selectVFO_TouchOn_CB,
            font="{Arial} 36 {}",
            label='True ',
            state="normal")
        self.VFO_Touch_Optimized_Menu.add(
            "command",
            command=self.selectVFO_TouchOff_CB,
            font="{Arial} 36 {}",
            label='False',
            state="normal")
        self.VFO_Touch_Optimized_Menubutton.configure(
            menu=self.VFO_Touch_Optimized_Menu)
        self.VFO_Touch_Optimized_Menubutton.grid(
            column=1, padx="15 5", pady="40 20", row=2, sticky="w")
        self.Time_On_Freq_Label = ttk.Label(
            self.general_Settings_Frame,
            name="time_on_freq_label")
        self.Time_On_Freq_Label.configure(
            justify="right",
            style="Heading1b.TLabel",
            text='Seconds on Frequency\nduring Scan')
        self.Time_On_Freq_Label.grid(
            column=0, padx=10, pady="40 20", row=3, sticky="e")
        spinbox1 = ttk.Spinbox(self.general_Settings_Frame)
        self.Time_On_Freq_VAR = tk.StringVar()
        spinbox1.configure(
            font="{Arial} 36 {}",
            from_=1,
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.Time_On_Freq_VAR,
            to=20,
            width=2)
        spinbox1.grid(column=1, padx="15 5", pady="40 20", row=3, sticky="w")
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
        self.configure(style="Heading2.TLabelframe", text='General Settings')
        # Layout for 'labelframe1' skipped in custom widget template.

    def selectCommaDelimiter_CB(self):
        pass

    def selectPeriodDelimiter_CB(self):
        pass

    def selectVirtualKeyboardOn_CB(self):
        pass

    def selectVirtualKeyboardOff_CB(self):
        pass

    def selectVFO_TouchOn_CB(self):
        pass

    def selectVFO_TouchOff_CB(self):
        pass

    def apply_CB(self):
        pass

    def cancel_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsGeneralUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
