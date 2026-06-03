#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk


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
class theVFOUI(ttk.Frame):
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

        self.vfoA_Frame = ttk.Frame(self, name="vfoa_frame")
        self.vfoA_Frame.configure(borderwidth=3, style="NormalOutline.TFrame")
        # First object created
        on_first_object_cb(self.vfoA_Frame)

        self.rxTX_Status_Frame = ttk.Frame(
            self.vfoA_Frame, name="rxtx_status_frame")
        self.rxTX_Status_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.rx_Status_Light_Label = ttk.Label(
            self.rxTX_Status_Frame, name="rx_status_light_label")
        self.rx_Status_Light_Label.configure(
            borderwidth=4,
            state="normal",
            style="GreenLED.TLabel",
            text='  RX',
            width=5)
        self.rx_Status_Light_Label.grid(column=0, pady=10, row=0)
        self.tx_Status_Light_Label = ttk.Label(
            self.rxTX_Status_Frame, name="tx_status_light_label")
        self.tx_Status_Light_Label.configure(
            borderwidth=4,
            state="disabled",
            style="RedLED.TLabel",
            text='  TX',
            width=5)
        self.tx_Status_Light_Label.grid(column=0, pady=15, row=1)
        self.stop_Button = ttk.Button(
            self.rxTX_Status_Frame, name="stop_button")
        self.stop_Button.configure(
            state="normal",
            style="RedButton2.TButton",
            text='\nSTOP!\n',
            width=6)
        self.stop_Button.grid(column=1, padx="20 10", row=0, rowspan=2)
        self.stop_Button.configure(command=self.stop_CB)
        separator2 = ttk.Separator(self.rxTX_Status_Frame)
        separator2.configure(orient="vertical")
        separator2.grid(column=2, row=0, rowspan=3, sticky="ns")
        self.rxTX_Status_Frame.grid(column=0, padx=15, row=0, sticky="e")
        self.vfo_display_Frame = ttk.Frame(
            self.vfoA_Frame, name="vfo_display_frame")
        self.vfo_display_Frame.configure(style="Normal.TFrame", width=200)
        self.VFO_Frame = ttk.Frame(self.vfo_display_Frame, name="vfo_frame")
        self.VFO_Frame.configure(height=200, style="Normal.TFrame", width=200)
        self.digit7_primary_VFO_Label = ttk.Label(
            self.VFO_Frame, name="digit7_primary_vfo_label")
        self.digit7_primary_VFO_VAR = tk.StringVar(value='7')
        self.digit7_primary_VFO_Label.configure(
            anchor="e",
            style="VFO.TLabel",
            text='7',
            textvariable=self.digit7_primary_VFO_VAR,
            width=1)
        self.digit7_primary_VFO_Label.grid(column=0, row=0, sticky="e")
        self.digit7_primary_VFO_Label.bind(
            "<Button>", self.primary_vfo_10mhz_CB, add="")
        self.digit7_Highlight_Label = ttk.Label(
            self.VFO_Frame, name="digit7_highlight_label")
        self.digit7_Highlight_Label.configure(style="OffLED.TLabel", width=7)
        self.digit7_Highlight_Label.grid(column=0, row=1)
        self.digit6_primary_VFO_Label = ttk.Label(
            self.VFO_Frame, name="digit6_primary_vfo_label")
        self.digit6_primary_VFO_VAR = tk.StringVar(value='6')
        self.digit6_primary_VFO_Label.configure(
            anchor="e",
            style="VFO.TLabel",
            text='6',
            textvariable=self.digit6_primary_VFO_VAR,
            width=1)
        self.digit6_primary_VFO_Label.grid(column=1, row=0, sticky="e")
        self.digit6_primary_VFO_Label.bind(
            "<Button>", self.primary_vfo_1mhz_CB, add="")
        self.digit6_Highlight_Label = ttk.Label(
            self.VFO_Frame, name="digit6_highlight_label")
        self.digit6_Highlight_Label.configure(style="OffLED.TLabel", width=7)
        self.digit6_Highlight_Label.grid(column=1, row=1)
        self.digit_delimiter_primary_VFO_1M_Label = ttk.Label(
            self.VFO_Frame, name="digit_delimiter_primary_vfo_1m_label")
        self.digit_delimiter_primary_VFO_VAR = tk.StringVar(value='.')
        self.digit_delimiter_primary_VFO_1M_Label.configure(
            style="VFO.TLabel",
            text='.',
            textvariable=self.digit_delimiter_primary_VFO_VAR,
            width=0)
        self.digit_delimiter_primary_VFO_1M_Label.grid(
            column=2, row=0, sticky="e")
        self.digital_highlight_1M_Period = ttk.Label(
            self.VFO_Frame, name="digital_highlight_1m_period")
        self.digital_highlight_1M_Period.configure(
            style="OffLED.TLabel", width=1)
        self.digital_highlight_1M_Period.grid(column=2, row=1)
        self.digit5_primary_VFO_Label = ttk.Label(
            self.VFO_Frame, name="digit5_primary_vfo_label")
        self.digit5_primary_VFO_VAR = tk.StringVar(value='5')
        self.digit5_primary_VFO_Label.configure(
            anchor="e",
            style="VFO.TLabel",
            text='5',
            textvariable=self.digit5_primary_VFO_VAR,
            width=1)
        self.digit5_primary_VFO_Label.grid(column=3, row=0, sticky="e")
        self.digit5_primary_VFO_Label.bind(
            "<Button>", self.primary_vfo_100khz_CB, add="")
        self.digit5_Highlight_Label = ttk.Label(
            self.VFO_Frame, name="digit5_highlight_label")
        self.digit5_Highlight_Label.configure(style="OffLED.TLabel", width=7)
        self.digit5_Highlight_Label.grid(column=3, row=1)
        self.digit4_primary_VFO_Label = ttk.Label(
            self.VFO_Frame, name="digit4_primary_vfo_label")
        self.digit4_primary_VFO_VAR = tk.StringVar(value='4')
        self.digit4_primary_VFO_Label.configure(
            anchor="e",
            style="VFO.TLabel",
            text='4',
            textvariable=self.digit4_primary_VFO_VAR,
            width=1)
        self.digit4_primary_VFO_Label.grid(column=4, row=0, sticky="e")
        self.digit4_primary_VFO_Label.bind(
            "<Button>", self.primary_vfo_10khz_CB, add="")
        self.digit4_Highlight_Label = ttk.Label(
            self.VFO_Frame, name="digit4_highlight_label")
        self.digit4_Highlight_Label.configure(style="OffLED.TLabel", width=7)
        self.digit4_Highlight_Label.grid(column=4, row=1)
        self.digit3_primary_VFO_Label = ttk.Label(
            self.VFO_Frame, name="digit3_primary_vfo_label")
        self.digit3_primary_VFO_VAR = tk.StringVar(value='3')
        self.digit3_primary_VFO_Label.configure(
            style="VFO.TLabel",
            text='3',
            textvariable=self.digit3_primary_VFO_VAR,
            width=1)
        self.digit3_primary_VFO_Label.grid(column=5, row=0, sticky="e")
        self.digit3_primary_VFO_Label.bind(
            "<Button>", self.primary_vfo_1khz_CB, add="")
        self.digit3_Highlight_Label = ttk.Label(
            self.VFO_Frame, name="digit3_highlight_label")
        self.digit3_Highlight_Label.configure(style="OffLED.TLabel", width=7)
        self.digit3_Highlight_Label.grid(column=5, row=1)
        self.digit_delimiter_primary_VFO_1k_Label = ttk.Label(
            self.VFO_Frame, name="digit_delimiter_primary_vfo_1k_label")
        self.digit_delimiter_primary_VFO_1k_Label.configure(
            style="VFO.TLabel",
            text='.',
            textvariable=self.digit_delimiter_primary_VFO_VAR,
            width=0)
        self.digit_delimiter_primary_VFO_1k_Label.grid(
            column=6, row=0, sticky="e")
        self.digital_highlight1K_Period = ttk.Label(
            self.VFO_Frame, name="digital_highlight1k_period")
        self.digital_highlight1K_Period.configure(
            anchor="e", style="OffLED.TLabel", width=1)
        self.digital_highlight1K_Period.grid(column=6, row=1)
        self.digit2_primary_VFO_Label = ttk.Label(
            self.VFO_Frame, name="digit2_primary_vfo_label")
        self.digit2_primary_VFO_VAR = tk.StringVar(value='2')
        self.digit2_primary_VFO_Label.configure(
            anchor="e",
            style="VFO.TLabel",
            text='2',
            textvariable=self.digit2_primary_VFO_VAR,
            width=1)
        self.digit2_primary_VFO_Label.grid(column=7, row=0, sticky="e")
        self.digit2_primary_VFO_Label.bind(
            "<Button>", self.primary_vfo_100hz_CB, add="")
        self.digit2_Highlight_Label = ttk.Label(
            self.VFO_Frame, name="digit2_highlight_label")
        self.digit2_Highlight_Label.configure(style="OffLED.TLabel", width=7)
        self.digit2_Highlight_Label.grid(column=7, row=1)
        self.digit1_primary_VFO_Label = ttk.Label(
            self.VFO_Frame, name="digit1_primary_vfo_label")
        self.digit1_primary_VFO_VAR = tk.StringVar(value='1')
        self.digit1_primary_VFO_Label.configure(
            anchor="e",
            style="VFO.TLabel",
            text='1',
            textvariable=self.digit1_primary_VFO_VAR,
            width=1)
        self.digit1_primary_VFO_Label.grid(column=8, row=0, sticky="e")
        self.digit1_primary_VFO_Label.bind(
            "<Button>", self.primary_vfo_10hz_CB, add="")
        self.digit1_Highlight_Label = ttk.Label(
            self.VFO_Frame, name="digit1_highlight_label")
        self.digit1_Highlight_Label.configure(style="OffLED.TLabel", width=7)
        self.digit1_Highlight_Label.grid(column=8, row=1)
        self.digit0_primary_VFO_Label = ttk.Label(
            self.VFO_Frame, name="digit0_primary_vfo_label")
        self.digit0_primary_VFO_VAR = tk.StringVar(value='0')
        self.digit0_primary_VFO_Label.configure(
            anchor="e",
            style="VFO.TLabel",
            text='0',
            textvariable=self.digit0_primary_VFO_VAR,
            width=1)
        self.digit0_primary_VFO_Label.grid(column=9, row=0, sticky="e")
        self.digit0_Highlight_Label = ttk.Label(
            self.VFO_Frame, name="digit0_highlight_label")
        self.digit0_Highlight_Label.configure(style="OffLED.TLabel", width=7)
        self.digit0_Highlight_Label.grid(column=9, row=1)
        self.VFO_Frame.grid(column=1, row=4)
        self.VFO_TX_Offset_Frame = ttk.Frame(
            self.vfo_display_Frame, name="vfo_tx_offset_frame")
        self.VFO_TX_Offset_Frame.configure(height=200, width=200)
        self.Tx_Freq_Alert_Label = ttk.Label(
            self.VFO_TX_Offset_Frame, name="tx_freq_alert_label")
        self.Tx_Freq_Alert_VAR = tk.StringVar(value='       ')
        self.Tx_Freq_Alert_Label.configure(
            style="Heading2bi.TLabel",
            text='       ',
            textvariable=self.Tx_Freq_Alert_VAR,
            width=7)
        self.Tx_Freq_Alert_Label.pack(
            anchor="w", expand=True, fill="x", side="left")
        self.VFO_TX_Offset_Frame.grid(column=0, padx="0 10", row=4, sticky="w")
        self.vfo_display_Frame.grid(column=1, padx="0 0", row=0, sticky="ew")
        self.vfoA_Frame.grid(column=0, row=0, sticky="ew")
        self.vfoA_Frame.grid_anchor("w")
        self.rx_vof_frame = ttk.Frame(self, name="rx_vof_frame")
        self.rx_vof_frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.RX_VFO_Frame = ttk.Frame(self.rx_vof_frame, name="rx_vfo_frame")
        self.RX_VFO_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.RX_Freq_Label = ttk.Label(self.RX_VFO_Frame, name="rx_freq_label")
        self.RX_Freq_Label.configure(
            style="Heading2bi.TLabel", text='RX Freq:')
        self.RX_Freq_Label.pack(side="left")
        self.RX_Freq_VFO_Label = ttk.Label(
            self.RX_VFO_Frame, name="rx_freq_vfo_label")
        self.RX_VFO_VAR = tk.StringVar(value='99.999.999')
        self.RX_Freq_VFO_Label.configure(
            style="Heading2bi.TLabel",
            text='99.999.999',
            textvariable=self.RX_VFO_VAR,
            width=11)
        self.RX_Freq_VFO_Label.pack(padx="10 0", side="left")
        self.RX_VFO_Frame.pack(side="left")
        self.RX_Freq_Place_Holder = ttk.Label(
            self.rx_vof_frame, name="rx_freq_place_holder")
        self.RX_Freq_Place_Holder.configure(
            style="Heading2bi.TLabel", text='  ')
        self.RX_Freq_Place_Holder.pack(side="right")
        self.rx_vof_frame.grid(column=0, row=1, sticky="e")
        self.vfoB_Frame = ttk.Frame(self, name="vfob_frame")
        self.vfoB_Frame.configure(borderwidth=3, style="NormalOutline.TFrame")
        self.vfo_Frame = ttk.Frame(self.vfoB_Frame, name="vfo_frame")
        self.vfo_Frame.configure(style="Normal.TFrame")
        self.secondary_VFO_Label = ttk.Label(
            self.vfo_Frame, name="secondary_vfo_label")
        self.secondary_VFO_Formatted_VAR = tk.StringVar(value='99.999.999')
        self.secondary_VFO_Label.configure(
            style="Heading1Fixed.TLabel",
            text='99.999.999',
            textvariable=self.secondary_VFO_Formatted_VAR,
            width=10)
        self.secondary_VFO_Label.pack(anchor="nw", padx="10 0", side="left")
        self.secondary_Mode_Label = ttk.Label(
            self.vfo_Frame, name="secondary_mode_label")
        self.secondary_Mode_VAR = tk.StringVar(value='CWL')
        self.secondary_Mode_Label.configure(
            style="Heading1.TLabel",
            text='CWL',
            textvariable=self.secondary_Mode_VAR)
        self.secondary_Mode_Label.pack(anchor="ne", padx="5 0", side="right")
        self.vfo_Frame.pack(side="left")
        self.callsign_Frame = ttk.Frame(self.vfoB_Frame, name="callsign_frame")
        self.callsign_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        label5 = ttk.Label(self.callsign_Frame)
        self.callSign_VAR = tk.StringVar(value='AJ6CUxyz')
        label5.configure(
            style="Heading2b.TLabel",
            text='AJ6CUxyz',
            textvariable=self.callSign_VAR,
            width=10)
        label5.pack(anchor="center", padx="0 10", side="left")
        label6 = ttk.Label(self.callsign_Frame)
        self.firmwareVersion_VAR = tk.StringVar(value='V2.0 RCLxyz')
        label6.configure(
            style="Heading2b.TLabel",
            text='V2.0 RCLxyz',
            textvariable=self.firmwareVersion_VAR)
        label6.pack(anchor="center", side="left")
        self.callsign_Frame.pack(padx="20 0", side="left")
        self.tuning_Step_Frame = ttk.Frame(
            self.vfoB_Frame, name="tuning_step_frame")
        self.tuning_Step_Frame.configure(style="Normal.TFrame", width=200)
        self.tuning_Preset_Menubutton = ttk.Menubutton(
            self.tuning_Step_Frame, name="tuning_preset_menubutton")
        self.tuning_Preset_Label_VAR = tk.StringVar(value='0')
        self.tuning_Preset_Menubutton.configure(
            style="Heading2b.TMenubutton",
            text='0',
            textvariable=self.tuning_Preset_Label_VAR,
            width=6)
        self.tuning_Preset_Menu = tk.Menu(
            self.tuning_Preset_Menubutton,
            name="tuning_preset_menu")
        self.tuning_Preset_Menu.configure(tearoff=False)
        self.tuning_Preset_Menu.add(
            "command",
            command=self.tuning_Preset_5_CB,
            label='50000')
        self.tuning_Preset_Menu.add(
            "command",
            command=self.tuning_Preset_4_CB,
            label='10000')
        self.tuning_Preset_Menu.add(
            "command",
            command=self.tuning_Preset_3_CB,
            label='5000')
        self.tuning_Preset_Menu.add(
            "command",
            command=self.tuning_Preset_2_CB,
            label='1000')
        self.tuning_Preset_Menu.add(
            "command",
            command=self.tuning_Preset_1_CB,
            label='100')
        self.tuning_Preset_Menubutton.configure(menu=self.tuning_Preset_Menu)
        self.tuning_Preset_Menubutton.pack(side="left")
        self.tuning_Preset_Units_Label = ttk.Label(
            self.tuning_Step_Frame, name="tuning_preset_units_label")
        self.tuning_Preset_Units_Label.configure(
            style="Heading1.TLabel", text='Hz')
        self.tuning_Preset_Units_Label.pack(padx=15, side="left")
        self.tuning_Multiplier_Button = ttk.Button(
            self.tuning_Step_Frame, name="tuning_multiplier_button")
        self.tuning_Multiplier_VAR = tk.StringVar(
            value='Dial Tuning\nx 100mhz')
        self.tuning_Multiplier_Button.configure(
            style="Button2b.TButton",
            text='Dial Tuning\nx 100mhz',
            textvariable=self.tuning_Multiplier_VAR)
        self.tuning_Multiplier_Button.pack(
            anchor="e", expand=True, fill="x", padx="20 0", side="left")
        self.tuning_Multiplier_Button.configure(
            command=self.tuning_Multiplier_Button_CB)
        self.tuning_Step_Frame.pack(padx="30 0", side="left")
        self.vfoB_Frame.grid(column=0, row=2, sticky="new")
        self.configure(height=200, style="Normal.TFrame", width=1250)
        # Layout for 'MainVFO_Frame' skipped in custom widget template.

    def stop_CB(self):
        pass

    def primary_vfo_10mhz_CB(self, event=None):
        pass

    def primary_vfo_1mhz_CB(self, event=None):
        pass

    def primary_vfo_100khz_CB(self, event=None):
        pass

    def primary_vfo_10khz_CB(self, event=None):
        pass

    def primary_vfo_1khz_CB(self, event=None):
        pass

    def primary_vfo_100hz_CB(self, event=None):
        pass

    def primary_vfo_10hz_CB(self, event=None):
        pass

    def tuning_Preset_5_CB(self):
        pass

    def tuning_Preset_4_CB(self):
        pass

    def tuning_Preset_3_CB(self):
        pass

    def tuning_Preset_2_CB(self):
        pass

    def tuning_Preset_1_CB(self):
        pass

    def tuning_Multiplier_Button_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = theVFOUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
