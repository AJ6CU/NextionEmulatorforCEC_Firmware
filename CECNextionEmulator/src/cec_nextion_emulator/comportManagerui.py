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
class comportManagerUI(ttk.Frame):
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

        self.comportMessage_Frame = ttk.Frame(
            self, name="comportmessage_frame")
        self.comportMessage_Frame.configure(
            height=150, style="Normal.TFrame", width=200)
        # First object created
        on_first_object_cb(self.comportMessage_Frame)

        label1 = ttk.Label(self.comportMessage_Frame)
        label1.configure(
            style="Heading1b.TLabel",
            text='Connect to Your uBITX')
        label1.pack(side="top")
        label3 = ttk.Label(self.comportMessage_Frame)
        label3.configure(
            anchor="w",
            justify="left",
            style="Heading2b.TLabel",
            text='The connection to your uBITX to is either unspecified or not working. \n\nYou must specify the correct \nconnection below before proceeding.',
            width=35,
            wraplength=380)
        label3.pack(pady=10, side="top")
        frame2 = ttk.Frame(self.comportMessage_Frame)
        frame2.configure(height=200, style="Normal.TFrame", width=200)
        self.connectionTypeLabel = ttk.Label(
            frame2, name="connectiontypelabel")
        self.connectionTypeLabel.configure(
            anchor="w",
            justify="left",
            style="Heading2b.TLabel",
            text='Select Connection Type:',
            wraplength=380)
        self.connectionTypeLabel.pack(
            expand=True, fill="x", padx=5, pady=5, side="left")
        frame6 = ttk.Frame(frame2)
        frame6.configure(height=200, style="Normal.TFrame", width=200)
        self.connectionType_Combobox = ttk.Combobox(
            frame6, name="connectiontype_combobox")
        self.radioConnectionType_VAR = tk.StringVar()
        self.connectionType_Combobox.configure(
            style="ComboBox1.TCombobox",
            textvariable=self.radioConnectionType_VAR,
            values='ComPort Socket',
            width=20)
        self.connectionType_Combobox.pack(pady=10, side="top")
        self.connectionType_Combobox.bind(
            "<<ComboboxSelected>>",
            self.connectionTypeSelected_CB,
            add="+")
        frame6.pack(padx=10, side="top")
        frame2.pack(side="top")
        self.comportMessage_Frame.pack(
            expand=False, fill="both", padx=10, pady=10, side="top")
        self.wifiPort_Frame = ttk.Frame(self, name="wifiport_frame")
        self.wifiPort_Frame.configure(
            height=200,
            relief="raised",
            style="NormalOutline.TFrame",
            width=200)
        self.selectComportTitle_Label = ttk.Label(
            self.wifiPort_Frame, name="selectcomporttitle_label")
        self.selectComportTitle_Label.configure(
            style="Heading2b.TLabel", text='Radio:')
        self.selectComportTitle_Label.pack(
            anchor="w", padx="10 0", pady=5, side="left")
        self.comportSelection_Frame = ttk.Frame(
            self.wifiPort_Frame, name="comportselection_frame")
        self.comportSelection_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.IPv4_Octet1_Entry = ttk.Entry(
            self.comportSelection_Frame,
            name="ipv4_octet1_entry")
        self.IPv4_Octet1_VAR = tk.StringVar()
        self.IPv4_Octet1_Entry.configure(
            style="Entry1b.TEntry",
            textvariable=self.IPv4_Octet1_VAR,
            width=3)
        self.IPv4_Octet1_Entry.pack(side="left")
        label5 = ttk.Label(self.comportSelection_Frame)
        label5.configure(style="Heading2b.TLabel", text='.')
        label5.pack(side="left")
        self.IPv4_Octet2_Entry = ttk.Entry(
            self.comportSelection_Frame,
            name="ipv4_octet2_entry")
        self.IPv4_Octet2_VAR = tk.StringVar()
        self.IPv4_Octet2_Entry.configure(
            style="Entry1b.TEntry",
            textvariable=self.IPv4_Octet2_VAR,
            width=3)
        self.IPv4_Octet2_Entry.pack(side="left")
        label6 = ttk.Label(self.comportSelection_Frame)
        label6.configure(style="Heading2b.TLabel", text='.')
        label6.pack(side="left")
        self.IPv4_Octet3_Entry = ttk.Entry(
            self.comportSelection_Frame,
            name="ipv4_octet3_entry")
        self.IPv4_Octet3_VAR = tk.StringVar()
        self.IPv4_Octet3_Entry.configure(
            style="Entry1b.TEntry",
            textvariable=self.IPv4_Octet3_VAR,
            width=3)
        self.IPv4_Octet3_Entry.pack(side="left")
        label7 = ttk.Label(self.comportSelection_Frame)
        label7.configure(style="Heading2b.TLabel", text='.')
        label7.pack(side="left")
        self.IPv4_Octet4_Entry = ttk.Entry(
            self.comportSelection_Frame,
            name="ipv4_octet4_entry")
        self.IPv4_Octet4_VAR = tk.StringVar()
        self.IPv4_Octet4_Entry.configure(
            style="Entry1b.TEntry",
            textvariable=self.IPv4_Octet4_VAR,
            width=3)
        self.IPv4_Octet4_Entry.pack(side="left")
        label2 = ttk.Label(self.comportSelection_Frame)
        label2.configure(style="Heading2b.TLabel", text=':')
        label2.pack(side="left")
        self.IPv4_Port_Entry = ttk.Entry(
            self.comportSelection_Frame,
            name="ipv4_port_entry")
        self.IPv4_Port_VAR = tk.StringVar()
        self.IPv4_Port_Entry.configure(
            style="Entry1b.TEntry",
            textvariable=self.IPv4_Port_VAR,
            width=5)
        self.IPv4_Port_Entry.pack(side="left")
        self.wifi_Port_Test_Button = ttk.Button(
            self.comportSelection_Frame, name="wifi_port_test_button")
        self.wifi_Port_Test_Button.configure(
            style="Button3.TButton", text='Test', width=5)
        self.wifi_Port_Test_Button.pack(side="top")
        self.wifi_Port_Test_Button.configure(
            command=self.test_Entered_IP_Address_CB)
        self.comportSelection_Frame.pack(
            expand=True, fill="x", padx=10, pady=5, side="top")
        self.wifiPort_Frame.pack(
            expand=True,
            fill="x",
            padx=10,
            pady=10,
            side="top")
        self.comPort_Frame = ttk.Frame(self, name="comport_frame")
        self.comPort_Frame.configure(
            height=200,
            relief="raised",
            style="NormalOutline.TFrame",
            width=200)
        self.label4 = ttk.Label(self.comPort_Frame, name="label4")
        self.label4.configure(style="Heading2b.TLabel", text='Radio:')
        self.label4.pack(anchor="w", padx="10 0", pady=5, side="left")
        self.frame5 = ttk.Frame(self.comPort_Frame, name="frame5")
        self.frame5.configure(height=200, style="Normal.TFrame", width=200)
        self.availableComPorts_VAR = tk.StringVar(value='Select Serial Port')
        __values = ['Select Serial Port']
        self.comPortsOptionMenu = ttk.OptionMenu(
            self.frame5,
            self.availableComPorts_VAR,
            "Select Serial Port",
            *__values,
            command=self.radioSerialPortSelected_CB)
        self.comPortsOptionMenu.pack(side="left")
        self.comPortListRefresh = tk.Button(
            self.frame5, name="comportlistrefresh")
        self.comPortListRefresh.configure(
            bitmap="error",
            borderwidth=0,
            cursor="arrow",
            font="TkDefaultFont")
        self.comPortListRefresh.pack(padx=10, side="left")
        self.comPortListRefresh.configure(command=self.updateComPorts)
        self.frame5.pack(expand=True, fill="x", padx=10, pady=5, side="top")
        self.comPort_Frame.pack(
            expand=True,
            fill="x",
            padx=10,
            pady=10,
            side="top")
        self.configure(height=300, style="Normal.TFrame", width=400)
        self.pack(anchor="w", expand=True, fill="both", side="top")

    def connectionTypeSelected_CB(self, event=None):
        pass

    def test_Entered_IP_Address_CB(self):
        pass

    def radioSerialPortSelected_CB(self, option):
        pass

    def updateComPorts(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = comportManagerUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
