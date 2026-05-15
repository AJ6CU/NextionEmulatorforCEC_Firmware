#!/usr/bin/python3
"""
settingsMachine

Used to save of machines

UI source file: settingsMachine.ui
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
class settingsMachineUI(ttk.Labelframe):
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
        frame1.configure(height=200, style="Normal.TFrame", width=200)
        # First object created
        on_first_object_cb(frame1)

        self.DSP_Enable_Label = ttk.Label(frame1, name="dsp_enable_label")
        self.DSP_Enable_Label.configure(
            state="disabled",
            style="Heading1b.TLabel",
            text='Use DSP Processor')
        self.DSP_Enable_Label.grid(
            column=0, padx=10, pady=10, row=0, sticky="e")
        self.DSP_Enable_Menubutton = ttk.Menubutton(
            frame1, name="dsp_enable_menubutton")
        self.DSP_Enable_VAR = tk.StringVar()
        self.DSP_Enable_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.DSP_Enable_VAR,
            width=5)
        self.DSP_Enable_Menu = tk.Menu(
            self.DSP_Enable_Menubutton,
            name="dsp_enable_menu")
        self.DSP_Enable_Menu.configure(tearoff=False)
        self.DSP_Enable_Menu.add(
            "command",
            command=self.selectDSP_On_CB,
            font="{Arial} 36 {}",
            label='True',
            state="normal")
        self.DSP_Enable_Menu.add(
            "command",
            command=self.selectDSP_Off_CB,
            font="{Arial} 36 {}",
            label='False',
            state="normal")
        self.DSP_Enable_Menubutton.configure(menu=self.DSP_Enable_Menu)
        self.DSP_Enable_Menubutton.grid(
            column=1, padx="15 5", pady=10, row=0, sticky="w")
        self.DSPMessage_Label = ttk.Label(frame1, name="dspmessage_label")
        self.DSPMessage_VAR = tk.StringVar(
            value='No DSP Found on startup. Option automatically disabled')
        self.DSPMessage_Label.configure(
            style="Heading2bi.TLabel",
            text='No DSP Found on startup. Option automatically disabled',
            textvariable=self.DSPMessage_VAR)
        self.DSPMessage_Label.grid(
            column=0,
            columnspan=2,
            pady="0 20",
            row=1,
            sticky="ew")
        self.MCU_Command_Headroom_Label = ttk.Label(
            frame1, name="mcu_command_headroom_label")
        self.MCU_Command_Headroom_Label.configure(
            style="Heading1b.TLabel",
            text='Minimum time between\ncommands sent to\nRadio (ms):')
        self.MCU_Command_Headroom_Label.grid(
            column=0, padx=10, pady=10, row=2, sticky="w")
        self.MCU_Update_Period_Label = ttk.Label(
            frame1, name="mcu_update_period_label")
        self.MCU_Update_Period_Label.configure(
            style="Heading1b.TLabel",
            text='Frequency to check for\nUX changes (ms):')
        self.MCU_Update_Period_Label.grid(
            column=0, padx=10, pady=10, row=3, sticky="w")
        self.MCU_Read_Wait_Period_Label = ttk.Label(
            frame1, name="mcu_read_wait_period_label")
        self.MCU_Read_Wait_Period_Label.configure(
            style="Heading1b.TLabel",
            text='Wait time for completion \nof data transfer from\nMCU/DPS (ms):')
        self.MCU_Read_Wait_Period_Label.grid(
            column=0, padx=10, pady="20 50", row=4, sticky="e")
        self.MCU_Command_Headroom_Spinbox = ttk.Spinbox(
            frame1, name="mcu_command_headroom_spinbox")
        self.MCU_Command_Headroom_VAR = tk.StringVar()
        self.MCU_Command_Headroom_Spinbox.configure(
            font="{Arial} 36 {}",
            from_=1,
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.MCU_Command_Headroom_VAR,
            to=20,
            width=3)
        self.MCU_Command_Headroom_Spinbox.grid(
            column=1, padx=20, pady=10, row=2, sticky="w")
        self.MCU_Update_Period_Spinbox = ttk.Spinbox(
            frame1, name="mcu_update_period_spinbox")
        self.MCU_Update_Period_VAR = tk.StringVar()
        self.MCU_Update_Period_Spinbox.configure(
            font="{Arial} 36 {}",
            from_=1,
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.MCU_Update_Period_VAR,
            to=20,
            width=3)
        self.MCU_Update_Period_Spinbox.grid(
            column=1, padx=20, pady=10, row=3, sticky="w")
        self.MCU_Read_Wait_Period_Spinbox = ttk.Spinbox(
            frame1, name="mcu_read_wait_period_spinbox")
        self.MCU_Read_Wait_Period_VAR = tk.StringVar()
        self.MCU_Read_Wait_Period_Spinbox.configure(
            font="{Arial} 36 {}",
            from_=1,
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.MCU_Read_Wait_Period_VAR,
            to=20,
            width=3)
        self.MCU_Read_Wait_Period_Spinbox.grid(
            column=1, padx=20, pady=10, row=4, sticky="w")
        frame1.pack(
            anchor="center",
            expand=True,
            fill="both",
            padx=20,
            pady=10,
            side="top")
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
            cursor="arrow",
            height=500,
            style="Heading2.TLabelframe",
            text='Machine Settings ( Caution Advised)',
            width=450)
        # Layout for 'labelframe1' skipped in custom widget template.

    def selectDSP_On_CB(self):
        pass

    def selectDSP_Off_CB(self):
        pass

    def apply_CB(self):
        pass

    def cancel_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsMachineUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
