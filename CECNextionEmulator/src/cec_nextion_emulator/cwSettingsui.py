#!/usr/bin/python3
"""
CW Settings Window

Used to save cw settings

UI source file: cwSettings.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
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
class cwSettingsUI(ttk.Labelframe):
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

        self.General_CW_Settings_Frame = ttk.Frame(
            frame1, name="general_cw_settings_frame")
        self.General_CW_Settings_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.CW_KEY_TYPE_LABEL = ttk.Label(
            self.General_CW_Settings_Frame,
            name="cw_key_type_label")
        self.CW_KEY_TYPE_LABEL.configure(
            style="Heading1b.TLabel", text='Key Type')
        self.keytype_Tooltip = Tooltip(self.CW_KEY_TYPE_LABEL)
        self.keytype_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Select the type of key you are using.',
            wraplength=300)
        self.CW_KEY_TYPE_LABEL.grid(column=0, pady="40 0", row=0, sticky="e")
        self.CW_Key_Type_Menubutton = ttk.Menubutton(
            self.General_CW_Settings_Frame, name="cw_key_type_menubutton")
        self.key_type_value_VAR = tk.StringVar()
        self.CW_Key_Type_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.key_type_value_VAR,
            width=9)
        self.CW_Key_Type_Menu = tk.Menu(
            self.CW_Key_Type_Menubutton,
            name="cw_key_type_menu")
        self.CW_Key_Type_Menu.configure(tearoff=False)
        self.CW_Key_Type_Menu.add(
            "command",
            command=self.selectCWStraightKey_CB,
            font="{Arial} 24 {}",
            label='STRAIGHT',
            state="normal")
        self.CW_Key_Type_Menu.add(
            "command",
            command=self.selectCWIAMBICAKey_CB,
            font="{Arial} 24 {}",
            label='IAMBICA',
            state="normal")
        self.CW_Key_Type_Menu.add(
            "command",
            command=self.selectCWIAMBICBKey_CB,
            font="{Arial} 24 {}",
            label='IAMBICB ',
            state="normal")
        self.CW_Key_Type_Menubutton.configure(menu=self.CW_Key_Type_Menu)
        self.CW_Key_Type_Menubutton.grid(
            column=1, padx="20 0", pady="40 0", row=0, sticky="w")
        self.CW_START_MS_LABEL = ttk.Label(
            self.General_CW_Settings_Frame,
            name="cw_start_ms_label")
        self.CW_START_MS_LABEL.configure(
            style="Heading1b.TLabel",
            text='Delay Starting TX (ms)')
        self.startCW_Tooltip = Tooltip(self.CW_START_MS_LABEL)
        self.startCW_Tooltip.configure(
            padx=8,
            relief="raised",
            text='This allows you to select how long from start of TX after going into CW mode. Useful for amps or other systems that need some time to get ready for TX.',
            wraplength=300)
        self.CW_START_MS_LABEL.grid(column=3, pady="40 0", row=0, sticky="e")
        self.CW_Start_TX_Spinbox = ttk.Spinbox(
            self.General_CW_Settings_Frame,
            name="cw_start_tx_spinbox")
        self.delay_starting_tx_value_VAR = tk.StringVar()
        self.CW_Start_TX_Spinbox.configure(
            font="{Arial} 36 {}",
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.delay_starting_tx_value_VAR,
            width=5)
        self.CW_Start_TX_Spinbox.grid(
            column=4, padx="20 0", pady="40 0", row=0, sticky="w")
        self.CW_SIDETONE_LABEL = ttk.Label(
            self.General_CW_Settings_Frame,
            name="cw_sidetone_label")
        self.CW_SIDETONE_LABEL.configure(
            style="Heading1b.TLabel", text='Sidetone (HZ)')
        self.sidetone_Tooltip = Tooltip(self.CW_SIDETONE_LABEL)
        self.sidetone_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Select the frequency of the sidetone of the CW you prefer.',
            wraplength=300)
        self.CW_SIDETONE_LABEL.grid(column=0, pady="40 0", row=2, sticky="e")
        self.CW_Sidetone_Spinbox = ttk.Spinbox(
            self.General_CW_Settings_Frame,
            name="cw_sidetone_spinbox")
        self.tone_value_VAR = tk.StringVar()
        self.CW_Sidetone_Spinbox.configure(
            font="{Arial} 36 {}",
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.tone_value_VAR,
            width=3)
        self.CW_Sidetone_Spinbox.grid(
            column=1, padx="20 0", pady="40 0", row=2, sticky="w")
        self.CW_DELAY_MS_LABEL = ttk.Label(
            self.General_CW_Settings_Frame,
            name="cw_delay_ms_label")
        self.CW_DELAY_MS_LABEL.configure(
            style="Heading1b.TLabel",
            text='Delay Returning to RX (ms)')
        self.cwDelayAfterTX_Tooltip = Tooltip(self.CW_DELAY_MS_LABEL)
        self.cwDelayAfterTX_Tooltip.configure(
            padx=8,
            relief="raised",
            text='This allows you to select how long after the last item transmitted before leaving TX mode. This allows you think time between thoughts before the relays click off.',
            wraplength=300)
        self.CW_DELAY_MS_LABEL.grid(column=3, pady="40 0", row=2, sticky="e")
        self.CW_SPEED_WPM_LABEL = ttk.Label(
            self.General_CW_Settings_Frame,
            name="cw_speed_wpm_label")
        self.CW_SPEED_WPM_LABEL.configure(
            style="Heading1b.TLabel", text='Speed (WPM)')
        self.keyspeed_Tooltip = Tooltip(self.CW_SPEED_WPM_LABEL)
        self.keyspeed_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Select the key speed.',
            wraplength=300)
        self.CW_SPEED_WPM_LABEL.grid(column=0, pady="40 0", row=3, sticky="e")
        self.CW_Speed_WPM_Spinbox = ttk.Spinbox(
            self.General_CW_Settings_Frame,
            name="cw_speed_wpm_spinbox")
        self.key_speed_value_VAR = tk.StringVar()
        self.CW_Speed_WPM_Spinbox.configure(
            font="{Arial} 36 {}",
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.key_speed_value_VAR,
            width=3)
        self.CW_Speed_WPM_Spinbox.grid(
            column=1, padx="20 0", pady="40 0", row=3, sticky="w")
        self.label209 = ttk.Label(
            self.General_CW_Settings_Frame,
            name="label209")
        self.label209.configure(
            style="Heading1b.TLabel",
            text='VFO Freq Displays')
        self.label209.grid(column=3, pady="40 0", row=3, sticky="e")
        self.text4 = tk.Text(self.General_CW_Settings_Frame, name="text4")
        self.text4.configure(
            background="#eeeeee",
            borderwidth=2,
            font="TkMenuFont",
            foreground="black",
            height=6,
            padx=5,
            pady=5,
            relief="groove",
            state="disabled",
            takefocus=False,
            width=30,
            wrap="word")
        _text_ = 'Controls whether the VFO will display the TX or RX frequency while in CW.\n\nThis setting will be reset to that stored in the EEPROM on reboot.  Use the Settings Editor to make a permanent change.'
        self.text4.configure(state="normal")
        self.text4.insert("0.0", _text_)
        self.text4.configure(state="disabled")
        self.text4.grid(column=2, columnspan=5, padx="70 0", pady=20, row=4)
        self.CW_Delay_Returning_RX_Spinbox = ttk.Spinbox(
            self.General_CW_Settings_Frame, name="cw_delay_returning_rx_spinbox")
        self.delay_returning_to_rx_value_VAR = tk.StringVar()
        self.CW_Delay_Returning_RX_Spinbox.configure(
            font="{Arial} 36 {}",
            justify="right",
            style="Custom.TSpinbox",
            textvariable=self.delay_returning_to_rx_value_VAR,
            width=5)
        self.CW_Delay_Returning_RX_Spinbox.grid(
            column=4, padx="20 0", pady="40 0", row=2, sticky="w")
        self.CW_Freq_Display_Menubutton = ttk.Menubutton(
            self.General_CW_Settings_Frame, name="cw_freq_display_menubutton")
        self.CW_Display_TXFreq_VAR = tk.StringVar()
        self.CW_Freq_Display_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.CW_Display_TXFreq_VAR,
            width=3)
        self.CW_Freq_Display_Menu = tk.Menu(
            self.CW_Freq_Display_Menubutton,
            name="cw_freq_display_menu")
        self.CW_Freq_Display_Menu.configure(tearoff=False)
        self.CW_Freq_Display_Menu.add(
            "command",
            command=self.selectCWDisplayTX_CB,
            font="{Arial} 24 {}",
            label='TX',
            state="normal")
        self.CW_Freq_Display_Menu.add(
            "command",
            command=self.selectCWDisplayRX_CB,
            font="{Arial} 24 {}",
            label='RX',
            state="normal")
        self.CW_Freq_Display_Menubutton.configure(
            menu=self.CW_Freq_Display_Menu)
        self.CW_Freq_Display_Menubutton.grid(
            column=4, padx="20 0", pady="40 0", row=3, sticky="w")
        self.copyVFOonSplit_Label = ttk.Label(
            self.General_CW_Settings_Frame,
            name="copyvfoonsplit_label")
        self.copyVFOonSplit_Label.configure(
            style="Heading1b.TLabel",
            text='Copy VFO-A to\nVFO-B on Split')
        self.copyVFOonSplit_Tooltip = Tooltip(self.copyVFOonSplit_Label)
        self.copyVFOonSplit_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Should VFO-A be copied to VFO-B on split? Under Split, VFO-B is TX and VFO-B is RX.',
            wraplength=300)
        self.copyVFOonSplit_Label.grid(
            column=0, pady="40 0", row=4, sticky="e")
        self.CopyVFOonSplit_Menubutton = ttk.Menubutton(
            self.General_CW_Settings_Frame, name="copyvfoonsplit_menubutton")
        self.CopyVFOonSplit_VAR = tk.StringVar()
        self.CopyVFOonSplit_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.CopyVFOonSplit_VAR,
            width=5)
        self.CopyVFOonSplit_Menu = tk.Menu(
            self.CopyVFOonSplit_Menubutton,
            name="copyvfoonsplit_menu")
        self.CopyVFOonSplit_Menu.configure(tearoff=False)
        def Copy_cmd(itemid="Copy"): self.CopyVFOAtoVFOBonSplit_CB(itemid)
        self.CopyVFOonSplit_Menu.add(
            "command",
            command=Copy_cmd,
            font="{Arial} 24 {}",
            label='True ',
            state="normal")
        def DoNotCopy_cmd(
            itemid="DoNotCopy"): self.CopyVFOAtoVFOBonSplit_CB(itemid)
        self.CopyVFOonSplit_Menu.add(
            "command",
            command=DoNotCopy_cmd,
            font="{Arial} 24 {}",
            label='False',
            state="normal")
        self.CopyVFOonSplit_Menubutton.configure(menu=self.CopyVFOonSplit_Menu)
        self.CopyVFOonSplit_Menubutton.grid(
            column=1, padx="20 0", pady="40 0", row=4, sticky="w")
        self.General_CW_Settings_Frame.pack(padx="50 0", side="top")
        frame1.pack(side="top")
        self.closingFrame = ttk.Frame(self, name="closingframe")
        self.closingFrame.configure(
            height=50, style="Normal.TFrame", width=200)
        self.apply_Button = ttk.Button(self.closingFrame, name="apply_button")
        self.apply_Button.configure(style="Button2b.TButton", text='Apply')
        self.applyButton_Tooltip = Tooltip(self.apply_Button)
        self.applyButton_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Saves your changes and closes the window. Some changes may require a reboot to be effective.',
            wraplength=300)
        self.apply_Button.pack(anchor="center", padx=10, side="left")
        self.apply_Button.configure(command=self.apply_CB)
        self.cancel_Buttom = ttk.Button(
            self.closingFrame, name="cancel_buttom")
        self.cancel_Buttom.configure(style="Button2b.TButton", text='Cancel')
        self.cancelButton_Tooltip = Tooltip(self.cancel_Buttom)
        self.cancelButton_Tooltip.configure(
            padx=8,
            relief="raised",
            text='Discards your changes and closes the window.',
            wraplength=300)
        self.cancel_Buttom.pack(anchor="center", padx=10, side="left")
        self.cancel_Buttom.configure(command=self.cancel_CB)
        self.closingFrame.pack(
            anchor="center",
            expand=False,
            pady=10,
            side="top")
        self.configure(
            height=400,
            style="Heading2.TLabelframe",
            text='CW Settings',
            width=600)
        # Layout for 'labelframe1' skipped in custom widget template.

    def selectCWStraightKey_CB(self):
        pass

    def selectCWIAMBICAKey_CB(self):
        pass

    def selectCWIAMBICBKey_CB(self):
        pass

    def selectCWDisplayTX_CB(self):
        pass

    def selectCWDisplayRX_CB(self):
        pass

    def CopyVFOAtoVFOBonSplit_CB(self, itemid):
        pass

    def apply_CB(self):
        pass

    def cancel_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = cwSettingsUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
