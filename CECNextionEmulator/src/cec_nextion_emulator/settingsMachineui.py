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

        self.DSP_Frame = ttk.Frame(frame1, name="dsp_frame")
        self.DSP_Frame.configure(
            height=200,
            style="NormalOutline.TFrame",
            width=200)
        self.DSP_Enable_Label = ttk.Label(
            self.DSP_Frame, name="dsp_enable_label")
        self.DSP_Enable_Label.configure(
            state="disabled",
            style="Heading1b.TLabel",
            text='Enable DSP Processor')
        self.DSP_Enable_Label.grid(
            column=0, padx=5, pady="5 0", row=0, sticky="w")
        self.DSP_Enable_Menubutton = ttk.Menubutton(
            self.DSP_Frame, name="dsp_enable_menubutton")
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
            font="{Arial} 24 {}",
            label='True',
            state="normal")
        self.DSP_Enable_Menu.add(
            "command",
            command=self.selectDSP_Off_CB,
            font="{Arial} 24 {}",
            label='False',
            state="normal")
        self.DSP_Enable_Menubutton.configure(menu=self.DSP_Enable_Menu)
        self.DSP_Enable_Menubutton.grid(
            column=1, padx="43 10", pady="5 0", row=0)
        self.DSPMessage_Label = ttk.Label(
            self.DSP_Frame, name="dspmessage_label")
        self.DSPMessage_VAR = tk.StringVar(
            value='No DSP Found on startup. Option automatically disabled')
        self.DSPMessage_Label.configure(
            style="Heading2bi.TLabel",
            text='No DSP Found on startup. Option automatically disabled',
            textvariable=self.DSPMessage_VAR)
        self.DSPMessage_Label.grid(
            column=0,
            columnspan=2,
            padx=5,
            pady="0 10",
            row=2,
            sticky="ew")
        self.DSP_Frame.grid(column=0, columnspan=2, row=0, sticky="ew")
        self.PWR_SWR_Frame = ttk.Frame(frame1, name="pwr_swr_frame")
        self.PWR_SWR_Frame.configure(
            height=200, style="NormalOutline.TFrame", width=200)
        self.PWR_SWR_Enable_Label = ttk.Label(
            self.PWR_SWR_Frame, name="pwr_swr_enable_label")
        self.PWR_SWR_Enable_Label.configure(
            state="disabled",
            style="Heading1b.TLabel",
            text='Enable PWR/SWR Meter')
        self.PWR_SWR_Enable_Label.grid(
            column=0, padx=5, pady="10 0", row=0, sticky="w")
        self.PWR_SWR_Menubutton = ttk.Menubutton(
            self.PWR_SWR_Frame, name="pwr_swr_menubutton")
        self.PWR_SWR_Enable_VAR = tk.StringVar()
        self.PWR_SWR_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.PWR_SWR_Enable_VAR,
            width=5)
        self.PWR_SWR_Menu = tk.Menu(
            self.PWR_SWR_Menubutton,
            name="pwr_swr_menu")
        self.PWR_SWR_Menu.configure(tearoff=False)
        self.PWR_SWR_Menu.add(
            "command",
            command=self.enablePWR_SWR_CB,
            font="{Arial} 24 {}",
            label='True',
            state="normal")
        self.PWR_SWR_Menu.add(
            "command",
            command=self.disablePWR_SWR_CB,
            font="{Arial} 24 {}",
            label='False',
            state="normal")
        self.PWR_SWR_Menubutton.configure(menu=self.PWR_SWR_Menu)
        self.PWR_SWR_Menubutton.grid(
            column=1, padx=10, pady="10 0", row=0, sticky="e")
        self.PWR_Factor_Label = ttk.Label(
            self.PWR_SWR_Frame, name="pwr_factor_label")
        self.PWR_Factor_Label.configure(
            state="disabled",
            style="Heading1b.TLabel",
            text='PWR Adjustment Factor\n(0.0-nn.nn)')
        self.PWR_Factor_Label.grid(
            column=0,
            padx="20 5",
            pady="10 0",
            row=1,
            sticky="w")
        self.PWR_Factor_Entry = ttk.Entry(
            self.PWR_SWR_Frame, name="pwr_factor_entry")
        self.PWR_Factor_VAR = tk.StringVar(value='0.0')
        self.PWR_Factor_Entry.configure(
            font="{Arial} 24 {}",
            justify="right",
            textvariable=self.PWR_Factor_VAR,
            validate="focusout",
            width=5)
        _text_ = '0.0'
        self.PWR_Factor_Entry.delete("0", "end")
        self.PWR_Factor_Entry.insert("0", _text_)
        self.PWR_Factor_Entry.grid(
            column=1, padx=10, pady="10 0", row=1, sticky="e")
        _validatecmd = (self.PWR_Factor_Entry.register(
            self.PWR_Factor_Validation_CB), "%P", "%V")
        self.PWR_Factor_Entry.configure(validatecommand=_validatecmd)
        self.PWR_Factor_Entry.bind(
            "<Button>", self.PWR_Factor_Entered_CB, add="+")
        self.SWR_Factor_Label = ttk.Label(
            self.PWR_SWR_Frame, name="swr_factor_label")
        self.SWR_Factor_Label.configure(
            state="disabled",
            style="Heading1b.TLabel",
            text='SWR Adjustment Factor\n(0.0-nn.nn)')
        self.SWR_Factor_Label.grid(
            column=0, padx="20 5", pady=10, row=2, sticky="w")
        self.SWR_Factor_Entry = ttk.Entry(
            self.PWR_SWR_Frame, name="swr_factor_entry")
        self.SWR_Factor_VAR = tk.StringVar(value='0.0')
        self.SWR_Factor_Entry.configure(
            font="{Arial} 24 {}",
            justify="right",
            textvariable=self.SWR_Factor_VAR,
            validate="focusout",
            width=5)
        _text_ = '0.0'
        self.SWR_Factor_Entry.delete("0", "end")
        self.SWR_Factor_Entry.insert("0", _text_)
        self.SWR_Factor_Entry.grid(
            column=1, padx=10, pady=10, row=2, sticky="e")
        _validatecmd = (self.SWR_Factor_Entry.register(
            self.SWR_Factor_Validation_CB), "%P", "%V")
        self.SWR_Factor_Entry.configure(validatecommand=_validatecmd)
        self.SWR_Factor_Entry.bind(
            "<Button>", self.SWR_Factor_Entered_CB, add="+")
        self.PWR_SWR_Frame.grid(
            column=0,
            columnspan=2,
            pady="10 0",
            row=2,
            sticky="ew")
        self.Timing_Frame = ttk.Frame(frame1, name="timing_frame")
        self.Timing_Frame.configure(
            height=200, style="NormalOutline.TFrame", width=200)
        self.MCU_Command_Headroom_Label = ttk.Label(
            self.Timing_Frame, name="mcu_command_headroom_label")
        self.MCU_Command_Headroom_Label.configure(
            style="Heading1b.TLabel",
            text='Minimum time between\ncommands sent to\nRadio (ms):')
        self.MCU_Command_Headroom_Label.grid(
            column=0, padx=5, pady="10 0", row=0, sticky="w")
        self.MCU_Command_Headroom_Spinbox = ttk.Spinbox(
            self.Timing_Frame, name="mcu_command_headroom_spinbox")
        self.MCU_Command_Headroom_VAR = tk.StringVar()
        self.MCU_Command_Headroom_Spinbox.configure(
            font="{Arial} 36 {}",
            from_=1,
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.MCU_Command_Headroom_VAR,
            to=20,
            width=4)
        self.MCU_Command_Headroom_Spinbox.grid(
            column=1, padx="15 10", pady="10 0", row=0, sticky="e")
        self.MCU_Update_Period_Label = ttk.Label(
            self.Timing_Frame, name="mcu_update_period_label")
        self.MCU_Update_Period_Label.configure(
            style="Heading1b.TLabel",
            text='Frequency to check for\nUX changes (ms):')
        self.MCU_Update_Period_Label.grid(
            column=0, padx=5, pady="15 0", row=2, sticky="w")
        self.MCU_Update_Period_Spinbox = ttk.Spinbox(
            self.Timing_Frame, name="mcu_update_period_spinbox")
        self.MCU_Update_Period_VAR = tk.StringVar()
        self.MCU_Update_Period_Spinbox.configure(
            font="{Arial} 36 {}",
            from_=1,
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.MCU_Update_Period_VAR,
            to=20,
            width=4)
        self.MCU_Update_Period_Spinbox.grid(
            column=1, padx="15 10", pady="15 0", row=2, sticky="e")
        self.MCU_Read_Wait_Period_Label = ttk.Label(
            self.Timing_Frame, name="mcu_read_wait_period_label")
        self.MCU_Read_Wait_Period_Label.configure(
            style="Heading1b.TLabel",
            text='Wait time for completion \nof data transfer from\nMCU/DPS (ms):')
        self.MCU_Read_Wait_Period_Label.grid(
            column=0, padx=5, pady="15 10", row=3, sticky="w")
        self.MCU_Read_Wait_Period_Spinbox = ttk.Spinbox(
            self.Timing_Frame, name="mcu_read_wait_period_spinbox")
        self.MCU_Read_Wait_Period_VAR = tk.StringVar()
        self.MCU_Read_Wait_Period_Spinbox.configure(
            font="{Arial} 36 {}",
            from_=1,
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.MCU_Read_Wait_Period_VAR,
            to=20,
            width=4)
        self.MCU_Read_Wait_Period_Spinbox.grid(
            column=1, padx="15 10", pady="15 10", row=3, sticky="e")
        self.Timing_Frame.grid(
            column=0,
            columnspan=2,
            pady=10,
            row=4,
            sticky="ew")
        frame1.pack(
            anchor="center",
            expand=True,
            fill="both",
            padx=10,
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
            style="Heading2.TLabelframe",
            text='Machine Settings ( Caution Advised)')
        # Layout for 'labelframe1' skipped in custom widget template.

    def selectDSP_On_CB(self):
        pass

    def selectDSP_Off_CB(self):
        pass

    def enablePWR_SWR_CB(self):
        pass

    def disablePWR_SWR_CB(self):
        pass

    def PWR_Factor_Validation_CB(self, p_entry_value, v_condition):
        pass

    def PWR_Factor_Entered_CB(self, event=None):
        pass

    def SWR_Factor_Validation_CB(self, p_entry_value, v_condition):
        pass

    def SWR_Factor_Entered_CB(self, event=None):
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
