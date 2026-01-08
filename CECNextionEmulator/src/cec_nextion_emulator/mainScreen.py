# from imghdr import test_xbm
import tkinter.ttk as ttk
import tkinter as tk

# from Cython.Compiler.Naming import self_cname

import mainScreenui as baseui
from settings import settings
from cwSettings import cwSettings, cwSettings

from channels import channels
from Classic_uBITX_Control import Classic_uBITX_Control

import mystyles  # Styles definition module
from time import sleep
import globalvars as gv
from tkinter import messagebox
import sys

class mainScreen(baseui.mainScreenUI):

    def __init__(self, master=None, **kw):
        self.theVFO_Object = None  # pointer to the VFO Object
        super().__init__(
            master,
            translator=None,
            on_first_object_cb=mystyles.setup_ttk_styles,
        )

        self.master = master

        self.pack_forget()

        self.theRadio = None            # Object pointer for the Radio
        self.theVFO_Object.attachMainWindow(self)
        self.cwSettingsWindow = None    # Object pointer for the CW Settinge Window
        self.settingsWindow = None      # Object pointer for the General Settings Window
        self.channelsWindow = None      # object pointer for the Memory-> VFO Window
        # self.vfoToMemWindow = None      # object pointer for the VFO->Memory Window

        self.classic_uBITX_ControlWindow = None
        self.classic_uBITX_ControlWindowObj = None
        self.DeepDebug = False
        self.CurrentDebug = True

        self.memoryQueue =[]            # when a memory slot is requested, it later comes in without any indication of which
                                        # memory slot it belong to. Fortunately, all in order. So everytime a memory slot is
                                        # requested, the type of memory requested is added to the queue so when we take it
                                        # off the queue, we know where it goes.

        # self.rate_selection = {
        #     0: self.tuning_Preset_Button,
        #     1: self.digit1_Highlight_Label,
        #     2: self.digit2_Highlight_Label,
        #     3: self.digit3_Highlight_Label,
        #     4: self.digit4_Highlight_Label,
        #     5: self.digit5_Highlight_Label,
        #     6: self.digit6_Highlight_Label,
        #     7: self.digit7_Highlight_Label
        # }
        #
        # self.DigitPos_to_Powers_of_Ten = {
        #     0: 0,
        #     1: 10,
        #     2: 100,
        #     3: 1000,
        #     4: 10000,
        #     5: 100000,
        #     6: 1000000,
        #     7: 10000000
        # }

        # self.currentDigitPos = 0
        # self.currentVFO_Tuning_Rate = 0


        self.VFO_A = "VFO-A"                        # String used for label of VFO-A
        self.VFO_B = "VFO-B"                        # String used for label of VFO-B
        self.vfo_VAR.set(self.VFO_A)                #Specifies which VFO is active. Also
                                                    #Label on VFO toggle button

        self.lock_Button_On = False                 #controls lock of console
        self.speaker_Button_On = False              #On means in Mute/SDR
        # self.stop_Button_On = False                 #Emergency stop all tx
        self.split_Button_On = False                #Controls entry into split mode
        self.rit_Button_On = False                  #Controls RIT. On means in RIT mode
        self.ATT_Button_On = False                  #On allows onscreen control of signal attn
        self.IFS_Button_On = False                  #On allows onscreen mod of the ifs
        self.IFS_On_Boot_Flag = True              # a default IFS value can be set in eeprom. If so, MCU sends a flag.
                                                    # The handling routine will set this flag to true so that when the default value
                                                    # is sent to the UX, the IFS setting and Jogwheel will be enabled.

        # self.primary_VFO_VAR = tk.StringVar()
        # self.secondary_VFO_VAR = tk.StringVar()
        # self.freqOffset = 0                         # used to save the offset on the main dial. Only non-zero for CWL/CWU
        #
        # gv.config.register_observer("NUMBER DELIMITER", self.reformatVFO)
        # self.digit_delimiter_primary_VFO_VAR.set(gv.config.get_NUMBER_DELIMITER())



        self.cwTX_OffsetFlag = False                # Controls whether the display shows the transmit freq when in CW
        self.cwTX_OffsetFlagOverride = None
        self.cwTX_Offset = 0
        self.cwTX_Tweak = 0                         # Apparently an additional value that can be set in the original editor but not SE



        # self.tuning_Preset_Selection_Frame.grid_remove()
        self.tuning_Jogwheel.configure(scroll=True, touchOptimized=gv.config.get_VFO_Touch_Optimized())
        self.theVFO_Object.attachDial(self.tuning_Jogwheel)
        self.tuning_Jogwheel.grid_remove()
        gv.config.register_observer("VFO Touch Optimized", self.switchVFO_Tuning_Optimization)
        self.baselineJogValue = 0

        # self.saved_tuning_Preset_VAR = None
        # self.update_Tuning_Preset_Button_Label = True



        # self.channelSelection = None                    # assigned to channel number when selected in channels

#   Constants
        #######################################################################################
        #   Dictionaries that follow are used to lookup textual values based on internal
        #   Representations. Sometimes it is a string integer. Other times it is a string of
        #   a couple characters. These translations are collected here to avoid them being
        #   "codified" directly in the functions that use them.
        #######################################################################################


        self.toRadioCommandDict = {
            "TS_CMD_MODE":1,
            "TS_CMD_FREQ":2,
            "TS_CMD_BAND":3,
            "TS_CMD_VFO":4,
            "TS_CMD_SPLIT":5,
            "TS_CMD_RIT":6,
            "TS_CMD_TXSTOP":7,
            "TS_CMD_SDR":8,
            "TS_CMD_LOCK":9,            # Dial Lock
            "TS_CMD_ATT":10,            # ATT
            "TS_CMD_IFS":11,            # IFS Enabled
            "TS_CMD_IFSVALUE":12,       # IFS VALUE
            "TS_CMD_STARTADC":13,
            "TS_CMD_STOPADC":14,
            "TS_CMD_SPECTRUMOPT":15,    # Option for Spectrum
            "TS_CMD_SPECTRUM":16,       # Get Spectrum Value
            "TS_CMD_TUNESTEP":17,       # Get Spectrum Value
            "TS_CMD_WPM":18,            # Set WPM
            "TS_CMD_KEYTYPE":19,        # Set KeyType
            "TS_CMD_SWTRIG":21,         # SW Action Trigger for WSPR and more
            "TS_CMD_READMEM":31,        # Read EEProm
            "TS_CMD_WRITEMEM":32,       # Write EEProm
            "TS_CMD_LOOPBACK0":74,      # Loopback1 (Response to Loopback Channgel)
            "TS_CMD_LOOPBACK1":75,      # Loopback2 (Response to Loopback Channgel)
            "TS_CMD_LOOPBACK2":76,      # Loopback3 (Response to Loopback Channgel)
            "TS_CMD_LOOPBACK3":77,      # Loopback4 (Response to Loopback Channgel)
            "TS_CMD_LOOPBACK4":78,      # Loopback5 (Response to Loopback Channgel)
            "TS_CMD_LOOPBACK5":79,      # Loopback6 (Response to Loopback Channgel)
            "TS_CMD_FACTORYRESET":85,   # Factory Reset
            "TS_CMD_UBITX_REBOOT":95    # Reboot
        }
        self.modeNum_To_TextDict = {
            "0":"DFT",
            "2":"LSB",
            "3":"USB",
            "4":"CWL",
            "5":"CWU"
        }

        self.Text_To_ModeNum = {
            "DFT":0,
            "LSB":2,
            "USB":3,
            "CWL":4,
            "CWU":5
        }

        self.Text_To_BandChange = {
            "UP": 2,
            "DOWN":1
        }
        self.Text_To_VFO= {
            "0": "VFO-A",
            "1": "VFO-B"
        }

        # self.CW_KeyType = {         # 0: straight, 1 : iambica, 2: iambicb
        #     "0":"STRAIGHT",
        #     "1":"IAMBICA",
        #     "2":"IAMBICB"
        # }
        #
        # self.CW_KeyValue = {
        #     "STRAIGHT": 0x0,
        #     "IAMBICA": 0x01,
        #     "IAMBICB": 0x02
        # }
        self.lsb = 0                    # index of least significant eeprom mem address in list below
        self.msb = 1                    # index of most significant eeprom emem address in list below
        self.memLength = 2
        self.charFlag = 3
        self.memOffset = 4
        self.totalSlots = 5
        self.EEPROM_Mem_Address = {
            "cw_key_type": [ 0x66, 0x01, 0x01, 0x0, 0x0, 0x1],
            "cw_wpm": [ 0x1c, 0x0, 0x04, 0x0, 0x0, 0x1],
            "cw_sidetone": [ 0x18, 0x0, 0x04, 0x0, 0x0, 0x1],
            "cw_Delay_Returning_to_RX": [0x02, 0x1, 0x01, 0x0, 0x0, 0x1],  # eeprom value divided by 10
            "cw_Delay_Starting_TX": [0x03, 0x1, 0x1, 0x0, 0x0,  0x1],  # eeprom saved valued divided by 2
            "channel_freq_Mode": [0x76, 0x2, 0x4, 0x48, 0x4, 0x14], # 0x48 indicates a integer number
            "channel_Label": [0xc7, 0x2, 0x5, 0x57, 0x6, 0x9],  # should be 0xa for total, but bug with v2 cec
                                                                # 0x57 indicates it is a character
            "channel_ShowLabel": [0xc6, 0x2, 0x1, 0x57, 0x6,  0x9], # should be 0xa for total, but bug with v2 cec
                                                                # 0x57 indicates it is a character
            "master_cal": [0x0, 0x0, 0x4, 0x48 ],
            "ssb_bfo": [ 0x08, 0x0, 0x04, 0x48],
            "cw_bfo":[ 0xfc, 0x0, 0x04, 0x48],

            "factory_master_cal": [0x41, 0x0, 0x4, 0x48],
            "factory_ssb_bfo": [0x49, 0x0, 0x04, 0x48],
            "factory_cw_wpm":[0x5d, 0x0, 0x01, 0x0, 0x0, 0x1],
            "factory_cw_sidetone":[0x59, 0x0, 0x04, 0x0, 0x0, 0x1]

        }

        self.memReadingState = "Freq"

        #
        #   These three variables are used to track which memory location (or "slot")
        #   that the retreived memory is from. This is needed because the MCU does not
        #   send any info on which memory location is associated with the value sent back
        #   to the Nextion. It assumes (hopefully corrcctly) that they appear in order.
        #
        self.EEPROM_Current_Slot_Freq = 0
        self.EEPROM_Current_Slot_Label = 0
        self.EEPROM_Current_Slot_ShowLabel = 0


        self.ATT_Status_Off = 0         #indicates that ATT has been turned off

    #####################################################################################
    #       End of dictionaries of constants
    #####################################################################################

    def attachRadio(self, radio):
        self.theRadio = radio

    def initUX(self):
        self.theVFO_Object.initVFO(self.theRadio)
        # if self.Tx_Freq_Alert_VAR.get() == "TX Freq":   #This indicates that we were in TX offset mode
        #                                                 #Need to correct display because originally set with incorrect
        #                                                 #Value for Tone. So need to redo it
        #     self.offsetVFOforTX(True)
        # self.updateRateMultiplier()
        # self.updateLabelTuning_Multiplier()
        # self.toggle_Digit_Highlight(self.rate_selection[self.currentDigitPos], True)

        self.place(x=0, y=0)  # place the mainWindow on the screen
        self.master.geometry(gv.trimAndLocateWindow(self, 5, 30))



    ######################################################################################
    #   This looks up the command processing routing to be called via a dictionary
    #   based on the command type (characters 3,4 in the buffer after prelogue stripped
    ######################################################################################

    def delegate_command_processing(self,command, buffer):
        match command:
            case "v1": self.v1_UX_Set_Tuning_Preset_1(buffer)
            case "v2": self.v2_UX_Set_Tuning_Preset_2(buffer)
            case "v3": self.v3_UX_Set_Tuning_Preset_3(buffer)
            case "v4": self.v4_UX_Set_Tuning_Preset_4(buffer)
            case "v5": self.v5_UX_Set_Tuning_Preset_5(buffer)
            case "cn": self.cn_UX_Set_Active_Tuning_Preset(buffer)
            case "ch": self.ch_UX_Set_CW_TX_OFFSET(buffer)
            case "vh": self.vh_UX_Set_CW_Tweak(buffer)
            case "vo": self.voGet(buffer)
            case "vp": self.vpGet(buffer)
            case "vq": self.vqGet(buffer)
            case "sv": self.sv_UX_Set_SW_Version(buffer)
            case "sc": self.sc_UX_Set_User_Callsign(buffer)
            case "cm": self.cm_UX_Display_Callsign_Version_Flag(buffer)
            case "c0": self.c0_UX_Toggle_Classic_uBITX_Control(buffer)
            case "vc": self.vc_UX_Set_Primary_VFO_Frequency(buffer)
            case "cc": self.cc_UX_Set_Primary_Mode(buffer)
            case "va": self.va_UX_Set_VFO_A_Frequency(buffer)
            case "ca": self.ca_UX_Set_VFO_A_Mode(buffer)
            case "vb": self.vb_UX_Set_VFO_B_Frequency(buffer)
            case "cb": self.cb_UX_Set_VFO_B_Mode(buffer)
            case "vt": self.vt_UX_SET_CW_Tone(buffer)
            case "ck": self.ck_UX_Set_CW_Key_Type(buffer)
            case "vs": self.vs_UX_Set_CW_Speed(buffer)
            case "vy": self.vy_UX_Set_CW_Delay_Returning_to_RX(buffer)
            case "ve": self.ve_UX_Set_CW_Delay_Starting_TX(buffer)
            case "cv": self.cv_UX_VFO_Toggle(buffer)  # sets active VFO, A=0, B=1
            case "s0": self.s0_UX_Greenbox_Line1(buffer)
            case "s1": self.s1_UX_Greenbox_Line2(buffer)
            case "sh": self.sh_UX_Get_Memory(buffer)
            case "vn": self.vn_UX_ACK_Memory_Write(buffer)
            case "cl": self.cl_UX_Lock_Screen(buffer)
            case "cj": self.cj_UX_Speaker_Toggle(buffer)
            case "cs": self.cs_UX_SPLIT_Toggle(buffer)
            case "vr": self.vr_UX_Update_RIT_Freq(buffer)
            case "cr": self.cr_UX_RIT_Toggle(buffer)
            case "vf": self.vf_UX_ATT_Level(buffer)
            case "vi": self.vi_UX_IFS_Level(buffer)
            case "ci": self.ci_UX_IFS_State_Set(buffer)
            case "cx": self.cx_UX_TX_Stop_Toggle(buffer)
            case "cp": self.cp_UX_S_Meter_Value(buffer)  # Related to S meter. search CMD_SMETER
            case "ct": self.ct_UX_RX_TX_Mode(buffer)
            case "al": self.al_UX_S_Meter_Value(buffer)
            case _:
                print("Command not recognized=", buffer,"*")
                print("command:", command,"*",sep="*")

        # try:
        #     self.MCU_Command_To_CB_Dict[command](buffer)
        # except:
        #     print("Command not recognized=", buffer,"*")
        #     print("command:", command,"*",sep="*")

    ################################################################################
    #   Format of command sent by radio:
    #   1. Prelog
    #   2. command type: characters 0-2, format "xx." Where "xx" is mostly "pm"
    #   3. subcommand type: characters 3,4  The translation between these characters
    #   and the code that implements them is in the dictionary above "MCU_Command_To_CB_Dict"
    #   4. value: This is the 4 bytes between 10-13. Mostly these are characters. But
    #   in some cases the might represent hex bytes that need to be recoded into an int
    ################################################################################

    def extractValue(self, buffer, start, end):
        returnBuffer =""
        i = start
        while i < end:
            returnBuffer = returnBuffer + buffer[i]
            i +=1
        return returnBuffer.replace('"','')

    # def offsetVFOforTX (self, flag):
    #     if flag:            # indicates we need to offset VFO by the Tone and Tweak
    #         self.Tx_Freq_Alert_VAR.set("TX Freq")
    #         self.RX_VFO_Visability(True)        # make the RX frequency frame visible
    #         if self.primary_Mode_VAR.get() == 'CWL':
    #             self.freqOffset  = int(self.tone_value_VAR.get()) + self.cwTX_Tweak
    #
    #         elif self.primary_Mode_VAR.get() == 'CWU':
    #             self.freqOffset = - int(self.tone_value_VAR.get()) + self.cwTX_Tweak
    #     else:
    #         self.Tx_Freq_Alert_VAR.set("       ")
    #         self.freqOffset = 0
    #         self.RX_VFO_Visability(False)       # Turn off the RX frequency window
    #
    #     self.update_VFO_Display(self.primary_VFO_VAR.get(), self.freqOffset)
    #
    #     self.updateJogTracking()                # Since changed flag, may need to reset jogwheel position
    #
    # def update_VFO_Display (self, unformatted_VFO_String, offset=0 ):
    #     self.displayedVFO = int(unformatted_VFO_String) + offset
    #
    #     paddedVFO = str(self.displayedVFO).rjust(8)
    #
    #     self.digit0_primary_VFO_VAR.set(paddedVFO[7])
    #     self.digit1_primary_VFO_VAR.set(paddedVFO[6])
    #     self.digit2_primary_VFO_VAR.set(paddedVFO[5])
    #     self.digit3_primary_VFO_VAR.set(paddedVFO[4])
    #     self.digit4_primary_VFO_VAR.set(paddedVFO[3])
    #     self.digit5_primary_VFO_VAR.set(paddedVFO[2])
    #     self.digit6_primary_VFO_VAR.set(paddedVFO[1])
    #     self.digit7_primary_VFO_VAR.set(paddedVFO[0])
    #
    #     self.RX_VFO_VAR.set(gv.formatFrequency(unformatted_VFO_String))     # Update RX freq reminder displayed if TX Freq displayed
    #
    #




    #   Callbacks
    #####################################################################################
    ### Start Callbacks
    #   These are the callbacks as defined in the GUI Builder pygubu-designer
    #####################################################################################


    def settings_CB(self):
        self.settingsWindow  = settings(self.master, self)


    def displayCWSettingsWindow(self):
        self.settingsCWWindow = cwSettings(self.master, self)


    #
    #   This routine makes requests from the MCU for all the Channel Frequencies, Mode, and Labels
    #   The actual setting of the corresponding values awaits the response of the eeprom
    #   packages sent by the MCU via the "sh_UX_Get_Memory" function
    #
    def displayChannelWindow(self):
        if self.channelsWindow == None:
            self.channelsWindow = channels(self.master, self, self.refresh_ChannelWindow_CB)

            self.channelsWindow.initChannelsUX()

        else:
            self.channelsWindow.SaveAndSetPreset()
            self.channelsWindow.popup.deiconify()
            self.channelsWindow.current_Channel_VAR.set("Not Saved")

    def displayClassic_uBITXControlWindow(self):
        self.classic_uBITX_ControlWindow  = tk.Toplevel(self.master)
        self.classic_uBITX_ControlWindow.title("Classic uBITX Control")
        self.classic_uBITX_ControlWindowObj=Classic_uBITX_Control(self.classic_uBITX_ControlWindow)
        self.classic_uBITX_ControlWindowObj.pack()

        toplevel_offsetx, toplevel_offsety = self.master.winfo_x(), self.master.winfo_y()
        padx = 350  # the padding you need.
        pady = 250
        self.classic_uBITX_ControlWindow.geometry(f"+{toplevel_offsetx + padx}+{toplevel_offsety + pady}")

        self.classic_uBITX_ControlWindow.grab_set()
        self.classic_uBITX_ControlWindow.transient(self.master)  # Makes the Classic box appear above the mainwindow

    def displayLine1Classic_uBITX_Control(self, value):
        if self.classic_uBITX_ControlWindowObj != None:  # Need to protect against a s0/s1 sent when turning on lock mode
            self.classic_uBITX_ControlWindowObj.greenBoxSelection_VAR.set(value)

    def displayLine2Classic_uBITX_Control(self, value):
        if self.classic_uBITX_ControlWindowObj != None:
            self.classic_uBITX_ControlWindowObj.greenBoxInstructions_VAR.set(value)
    #
    def refresh_ChannelWindow_CB(self):
        self.channelsWindow.popup.destroy()
        self.channelsWindow = None
        self.displayChannelWindow()

    def Radio_Req_Channel_Freqs(self):

        base = self.EEPROM_Mem_Address["channel_freq_Mode"][self.lsb]

        for i in range(self.EEPROM_Mem_Address["channel_freq_Mode"][self.totalSlots]):
            command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                       base,
                       self.EEPROM_Mem_Address["channel_freq_Mode"][self.msb],
                       self.EEPROM_Mem_Address["channel_freq_Mode"][self.memLength],
                       self.EEPROM_Mem_Address["channel_freq_Mode"][self.charFlag]
                       ]
            self.memoryQueue.append("Freq")         # Add  it to queue to be processed when MCU responds
            self.theRadio.sendCommandToMCU(bytes(command))
            base += self.EEPROM_Mem_Address["channel_freq_Mode"][self.memOffset]


        base = self.EEPROM_Mem_Address["channel_freq_Mode"][self.lsb]

    def Radio_Req_Channel_Labels(self):
        base = self.EEPROM_Mem_Address["channel_Label"][self.lsb]
        for i in range(self.EEPROM_Mem_Address["channel_Label"][self.totalSlots]):
            command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                       base,
                       self.EEPROM_Mem_Address["channel_Label"][self.msb],
                       self.EEPROM_Mem_Address["channel_Label"][self.memLength],
                       self.EEPROM_Mem_Address["channel_Label"][self.charFlag]
                       ]
            self.memoryQueue.append("Label")
            self.theRadio.sendCommandToMCU(bytes(command))
            base += self.EEPROM_Mem_Address["channel_Label"][self.memOffset]

        base = self.EEPROM_Mem_Address["channel_Label"][self.lsb]

    def Radio_Req_Channel_Show_Labels(self):
        base = self.EEPROM_Mem_Address["channel_ShowLabel"][self.lsb]
        for i in range(self.EEPROM_Mem_Address["channel_ShowLabel"][self.totalSlots]):
            command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                       base,
                       self.EEPROM_Mem_Address["channel_ShowLabel"][self.msb],
                       self.EEPROM_Mem_Address["channel_ShowLabel"][self.memLength],
                       self.EEPROM_Mem_Address["channel_ShowLabel"][self.charFlag]
                       ]
            self.memoryQueue.append("ShowLabel")
            self.theRadio.sendCommandToMCU(bytes(command))
            base += self.EEPROM_Mem_Address["channel_ShowLabel"][self.memOffset]

        base = self.EEPROM_Mem_Address["channel_ShowLabel"][self.lsb]


    def Radio_Req_Master_Cal(self, setter_CB):

        self.Master_Cal_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   self.EEPROM_Mem_Address["master_cal"][self.lsb],
                   self.EEPROM_Mem_Address["master_cal"][self.msb],
                   self.EEPROM_Mem_Address["master_cal"][self.memLength],
                   self.EEPROM_Mem_Address["master_cal"][self.charFlag]
                   ]


        self.memoryQueue.append("MasterCal")         # tell the command that receives the data what is it for

        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Req_SSB_BFO(self, setter_CB):

        self.SSB_BFO_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   self.EEPROM_Mem_Address["ssb_bfo"][self.lsb],
                   self.EEPROM_Mem_Address["ssb_bfo"][self.msb],
                   self.EEPROM_Mem_Address["ssb_bfo"][self.memLength],
                   self.EEPROM_Mem_Address["ssb_bfo"][self.charFlag]
                   ]
        self.memoryQueue.append("SSB_BFO")
        self.theRadio.sendCommandToMCU(bytes(command))


    def Radio_Req_CW_BFO(self,setter_CB):

        self.CW_BFO_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   self.EEPROM_Mem_Address["cw_bfo"][self.lsb],
                   self.EEPROM_Mem_Address["cw_bfo"][self.msb],
                   self.EEPROM_Mem_Address["cw_bfo"][self.memLength],
                   self.EEPROM_Mem_Address["cw_bfo"][self.charFlag]
                   ]

        self.memoryQueue.append("CW_BFO")
        self.theRadio.sendCommandToMCU(bytes(command))


    def Radio_Req_Factory_Master_Cal(self, setter_CB):

        self.Factory_Master_Cal_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   self.EEPROM_Mem_Address["factory_master_cal"][self.lsb],
                   self.EEPROM_Mem_Address["factory_master_cal"][self.msb],
                   self.EEPROM_Mem_Address["factory_master_cal"][self.memLength],
                   self.EEPROM_Mem_Address["factory_master_cal"][self.charFlag]
                   ]


        self.memoryQueue.append("Factory_MasterCal")         # tell the command that receives the data what is it for

        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Req_Factory_SSB_BFO(self, setter_CB):

        self.Factory_SSB_BFO_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   self.EEPROM_Mem_Address["factory_ssb_bfo"][self.lsb],
                   self.EEPROM_Mem_Address["factory_ssb_bfo"][self.msb],
                   self.EEPROM_Mem_Address["factory_ssb_bfo"][self.memLength],
                   self.EEPROM_Mem_Address["factory_ssb_bfo"][self.charFlag]
                   ]

        self.memoryQueue.append("Factory_SSB_BFO")
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Req_Factory_CW_Speed(self, setter_CB):

        self.Factory_CW_Speed_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   self.EEPROM_Mem_Address["factory_cw_wpm"][self.lsb],
                   self.EEPROM_Mem_Address["factory_cw_wpm"][self.msb],
                   self.EEPROM_Mem_Address["factory_cw_wpm"][self.memLength],
                   self.EEPROM_Mem_Address["factory_cw_wpm"][self.charFlag]
                   ]

        self.memoryQueue.append("Factory_CW_Speed")
        self.theRadio.sendCommandToMCU(bytes(command))


    def Radio_Req_Factory_CW_Sidetone(self, setter_CB):

        self.Factory_CW_Sidetone_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   self.EEPROM_Mem_Address["factory_cw_sidetone"][self.lsb],
                   self.EEPROM_Mem_Address["factory_cw_sidetone"][self.msb],
                   self.EEPROM_Mem_Address["factory_cw_sidetone"][self.memLength],
                   self.EEPROM_Mem_Address["factory_cw_sidetone"][self.charFlag]
                   ]

        self.memoryQueue.append("Factory_CW_Sidetone")
        self.theRadio.sendCommandToMCU(bytes(command))

    def vfo_CB(self):
        self.Radio_Toggle_VFO()

    def mode_lsb_CB(self):
        self.Radio_Set_Mode(self.Text_To_ModeNum["LSB"])

    def mode_usb_CB(self):
        self.Radio_Set_Mode(self.Text_To_ModeNum["USB"])


    def mode_cwl_CB(self):
        self.Radio_Set_Mode(self.Text_To_ModeNum["CWL"])


    def mode_cwu_CB(self):
        self.Radio_Set_Mode(self.Text_To_ModeNum["CWU"])

    def band_up_CB(self):
         self.Radio_Change_Band(self.Text_To_BandChange["UP"])

    def band_down_CB(self):
         self.Radio_Change_Band(self.Text_To_BandChange["DOWN"])

    def cwSettings_CB(self, event=None):
       if (not self.lock_Button_On):
           self.displayCWSettingsWindow()

    # def tuning_Preset_5_CB(self):
    #     self.Radio_Set_Tuning_Preset(5)
    #     # self.tuning_Preset_Selection_Frame.grid_remove()
    #
    # def tuning_Preset_4_CB(self):
    #     self.Radio_Set_Tuning_Preset(4)
    #     # self.tuning_Preset_Selection_Frame.grid_remove()
    #
    # def tuning_Preset_3_CB(self):
    #     self.Radio_Set_Tuning_Preset(3)
    #     # self.tuning_Preset_Selection_Frame.grid_remove()
    #
    # def tuning_Preset_2_CB(self):
    #     self.Radio_Set_Tuning_Preset(2)
    #     # self.tuning_Preset_Selection_Frame.grid_remove()
    #
    # def tuning_Preset_1_CB(self):
    #     self.Radio_Set_Tuning_Preset(1)
    #     # self.tuning_Preset_Selection_Frame.grid_remove()


    # def tuning_Preset_Select_CB(self):
    #     #
    #     #   check if frame containing radiobuttons is displayed
    #     #   if not, display it. If currently displayed, remove it
    #     #
    #     if (self.tuning_Preset_Selection_Frame.winfo_ismapped()):
    #         self.tuning_Preset_Selection_Frame.grid_remove()
    #     else:
    #         self.tuning_Preset_Selection_Frame.grid()

    def tuning_Jogwheel_CB(self):
        newFreq =  (self.theVFO_Object.getIntPrimaryVFO()
                    - (self.theVFO_Object.getCurrentVFO_Tuning_Rate() * self.baselineJogValue))

        newFreq += self.theVFO_Object.getCurrentVFO_Tuning_Rate() * self.tuning_Jogwheel.get()

        self.Radio_Set_New_Frequency(newFreq)

    #
    # def find_msd_position(self, number_string):
    #     # Finds the index of the most significant digit from the right in a string representation of a number.
    #
    #     # Returns:
    #     #     int or None: The index of the most significant digit, or None if no non-zero digit is found.
    #
    #     reversed_number_string = number_string[::-1].strip()  # neat trick to reverse a string
    #
    #     for i, char in enumerate(reversed_number_string):
    #         if char.isdigit() and char != '0':
    #             return i
    #     return None
    #
    # #
    # #   this function returns a single digit integer that occupies the position
    # #   corresponding to the current selected rate.
    # #   Conveniently, presets are allocated to position 0,
    # #   which is always zero in CEC and not setable
    # #
    #
    # def getVFOdigit(self):
    #     #
    #     #   get the VFO currently displayed
    #     #
    #     currentVFO = str(self.displayedVFO) #self.primary_VFO_VAR.get()
    #
    #     #
    #     #   reverse it so that least significant is in position 0
    #     #
    #     reversedVFO = currentVFO[::-1].strip()      # neat trick to reverse a string
    #
    #     #
    #     #   pad it on right with zeros so we have 8 characters
    #     #
    #     reversedVFO = reversedVFO.ljust(8,"0")
    #
    #     if (self.currentDigitPos == 0):
    #         if (self.currentVFO_Tuning_Rate != 0):
    #             pos=self.find_msd_position(str(self.currentVFO_Tuning_Rate))
    #             return int(reversedVFO[pos])
    #         else:
    #             return int(reversedVFO[2])
    #     else:
    #         #
    #         #   now we can just return the character of the selected rate
    #         #
    #         return int(reversedVFO[self.currentDigitPos])
    # def RX_VFO_Visability (self, RX_Frame_Visible = False):
    #     if RX_Frame_Visible:
    #         self.RX_VFO_Frame.pack(side="left")
    #     else:
    #         self.RX_VFO_Frame.pack_forget()
    # #
    # #   This routine handles switching between Direct and "Preset" tuning mode
    # #   The complexity here comes from the original CEC software using the current
    # #   preset-1 (i.e. if Preset 3 was 100 and Preset 2 was 50, and we were on preset 3,
    # #   everything below Preset 3 would be zero'ed out. This means to allow direct
    # #   tune mode on the tens digit, we must first make the preset the lowest # (i.e. 1)
    # #   so that the tens digit is not masked out and turned to zero.
    # #   As a result, we need to save the state of the preset when we move to Direct Tune,
    # #   and then restore it as we exit Direct Tune and go into Preset mode.
    # #   Since the MCU can also force changes in preset, we must temporarily turn off
    # #   the updating of the label
    # #
    # def toggle_Tuning_Mode(self, mode):
    #     if (mode == "direct tune"):
    #         if (self.saved_tuning_Preset_Selection == None):        #None value indicates we *were* in "direct tune" mode
    #             #
    #             #   save state prior to going into Direct Mode
    #             #
    #             self.saved_tuning_Preset_Selection = self.tuning_Preset_Selection_VAR.get()
    #             self.saved_tuning_Preset_VAR = self.tuning_Preset_Label_VAR.get()
    #             #
    #             #   Sets label that displays current present with "Direct Tune" string
    #             #
    #             self.tuning_Preset_Label_VAR.set("Direct Tune")
    #             #   turn off any changes in the label due to a change in preset coming from the radio
    #             self.update_Tuning_Preset_Button_Label = False
    #             #   Disable the tuning rate button so selected preset cannot be changed while in direct tune
    #             self.tuning_Preset_Button.configure(state='disabled')
    #             #
    #             #   Select the lowest tuning rate of the presets. The need to do this is the result of the original
    #             #   CEC software using the rate preselects to truncate digits below the preset. For example.
    #             #   if a preset of 100 was selected, then it would be impossible to set the dial in increments of 20
    #             #   or 10 because it would be truncated to lower 100.
    #             #
    #             self.Radio_Set_Tuning_Preset(1)
    #
    #     else:       # Switching into pre-set tuning mode and have to restore the state
    #         if (self.saved_tuning_Preset_Selection != None):          # dont restore unless it was previously saved
    #             #   Allow updating of the Label for the selected preset
    #             self.update_Tuning_Preset_Button_Label = True
    #             #   Restore the saved states
    #             self.tuning_Preset_Label_VAR.set(self.saved_tuning_Preset_VAR)
    #             self.Radio_Set_Tuning_Preset(int(self.saved_tuning_Preset_Selection))
    #             #   Re-enable the button to select a preset
    #             self.tuning_Preset_Button.configure(state='enabled')
    #             #   indicate the saved states are now invalid
    #             self.saved_tuning_Preset_Selection = None
    #
    #
    # def toggle_Digit_Highlight(self, light, Status):
    #
    #     if (Status):
    #         if (isinstance(light, ttk.Button)):
    #             light.configure(style='GreenButton2b.TButton')
    #             self.toggle_Tuning_Mode("preset tune")      # go into preset tune mode
    #
    #         else:
    #             light.configure(style='OnLED.TLabel')
    #             self.toggle_Tuning_Mode("direct tune")      # go into direct tune mode
    #
    #     else:
    #         if (isinstance(light, ttk.Button)):
    #             light.configure(style='Button2b.TButton')
    #         else:
    #             light.configure(style='OffLED.TLabel')


    # #
    # #   When the tuning_Multiplier is clicked, it cycles through the digits in the VFO to allow them to be
    # #   manually tuned. The initial case the use of the preset tuning cycles is used, much in the same
    # #   way it would be if you are adjusting the physical tuning knob.
    # #
    # def tuning_Multiplier_Button_CB(self):
    #     #
    #     #   First turn off the old LED, turn on new LED indicator for tuning
    #     #
    #     self.updateLEDTuningHighlight()
    #     #
    #     #   Update rate multiplier for jogwheel
    #     #
    #     self.updateRateMultiplier()
    #     #
    #     #   set tracking variables for new rate change
    #     #
    #     self.updateJogTracking()
    #     #
    #     #   Update the label on the tuning button selector
    #     #
    #     self.updateLabelTuning_Multiplier()


    # def updateLEDTuningHighlight(self, tuning_Digit = None):
    #     #
    #     #   First turn off the old LED
    #     #
    #     self.toggle_Digit_Highlight(self.rate_selection[self.currentDigitPos], False)
    #     #
    #     #   IF increment mode (tuning_Digit == None)
    #     #   Increment to the next slot and turn its LED on, check for rollover, otherwise go directly to the indicated
    #     #   digit
    #     #
    #     if tuning_Digit == None:
    #         self.currentDigitPos += 1
    #         if self.currentDigitPos > len(self.rate_selection) - 1:
    #             self.currentDigitPos = 0
    #     else:
    #         self.currentDigitPos = tuning_Digit
    #
    #     self.toggle_Digit_Highlight(self.rate_selection[self.currentDigitPos], True)

    # def updateRateMultiplier(self):
    #     #
    #     #   Set the frequency multiplier
    #     #
    #     self.currentVFO_Tuning_Rate = self.DigitPos_to_Powers_of_Ten[self.currentDigitPos]
    #     #
    #     #   Special case 0, which is the current value of the preset
    #     #
    #     if (self.currentVFO_Tuning_Rate == 0):
    #        if self.tuning_Preset_Label_VAR.get() == "Direct Tune":
    #            self.Radio_Set_Tuning_Preset(1)
    #        else:
    #            self.currentVFO_Tuning_Rate = int(self.tuning_Preset_Label_VAR.get())
    #
    # def updateJogTracking(self,newBaseline=True):
    #     # if self.DeepDebug:
    #     #     print("updating jogwheel, digit=", self.getVFOdigit())
    #     #     print("current jogwheel position =", self.tuning_Jogwheel.get())
    #
    #     self.tuning_Jogwheel.set(self.getVFOdigit(), False)
    #     if(newBaseline):
    #         self.baselineJogValue = self.tuning_Jogwheel.get()

    # def updateLabelTuning_Multiplier(self):
    #     if (self.currentVFO_Tuning_Rate < 1000):
    #         multiplier_string = str(int(self.currentVFO_Tuning_Rate)) + "Hz"
    #     elif (self.currentVFO_Tuning_Rate < 1000000):
    #         multiplier_string = str(int(self.currentVFO_Tuning_Rate / 1000)) + "KHz"
    #     else:
    #         multiplier_string = str(int(self.currentVFO_Tuning_Rate / 1000000)) + "MHz"
    #
    #     #   Now set the text on the multiplier button to reflect the new rate
    #     #
    #     self.tuning_Multiplier_VAR.set("Tuning Factor\nx" + multiplier_string)
#
    # #
    # #   this callback allows a user to click on the 10hz digit and then use the tuning jogwheel
    # #
    # def primary_vfo_direct_digit_set(self, digit):
    #     #
    #     #   First turn off the old LED, turn on new LED indicator for tuning
    #     #
    #     self.updateLEDTuningHighlight(digit)
    #     #
    #     #   Update rate multiplier for jogwheel
    #     #
    #     self.updateRateMultiplier()
    #     #
    #     #   set tracking variables for new rate change
    #     #
    #     self.updateJogTracking()
    #     #
    #     #   Update the label on the tuning button selector
    #     #
    #     self.updateLabelTuning_Multiplier()
    #
    #
    #
    # def primary_vfo_10mhz_CB(self, event=None):
    #     self.primary_vfo_direct_digit_set(7)
    #
    # def primary_vfo_1mhz_CB(self, event=None):
    #     self.primary_vfo_direct_digit_set(6)
    #
    # def primary_vfo_100khz_CB(self, event=None):
    #     self.primary_vfo_direct_digit_set(5)
    #
    # def primary_vfo_10khz_CB(self, event=None):
    #     self.primary_vfo_direct_digit_set(4)
    #
    # def primary_vfo_1khz_CB(self, event=None):
    #     self.primary_vfo_direct_digit_set(3)
    #
    # def primary_vfo_100hz_CB(self, event=None):
    #     self.primary_vfo_direct_digit_set(2)
    #
    # def primary_vfo_10hz_CB(self, event=None):
    #     self.primary_vfo_direct_digit_set(1)
#
#   This function sends to the Radio a notice that a screen lock has been requested
#   The actual locking of the screen waits until the Radio sends back a commond
#   to lock the screen. This ensures that the screen is not locked by the UX
#   and the Radio never gets the request for some reason.
#   The actual locking of screen is set performed by cl_UX_Lock_Screen()
#

    def lock_CB(self):
        self.Radio_Toggle_Lock()    # Inform  Radio that a screen lock has been requested

    def speaker_CB(self):           # Inform Radio that a request was made to mute speaker
        self.Radio_Toggle_Speaker()

    def stop_CB(self):
        self.Radio_Toggle_Stop()

    def split_CB(self):
        self.Radio_Toggle_Split()

    def rit_CB(self):
        self.Radio_Toggle_RIT()



    def channels_CB(self):
        self.displayChannelWindow()
    #
    #   The following routines handles the ATT jogwheel.
    #   Basically any click with no movement will toggle
    #   the ATT on or off. When turned on it remembers the last value
    #   (or 70 if this is the first time)
    #   The two "ButtonPressed_CB" and "ButtonReleased" are used to
    #   capture the initial value when first clicked and then when
    #   the jogwheel is released, a check is made on whether there was
    #   a change in value.
    #   The routines in this area just send a command to the Radio via the
    #   self.Radio_Set_ATT (value) routine. Zero turns it off, any other value turns it on.
    #   Note that although the UX is updated as the jogwheel is moved, the real value is set
    #   self.vf_UX_ATT_Level routine which is kicked off when the Radio(MCU) sends a "vf"
    #   command to the screen
    #
    def ATT_Jogwheel_ButtonPressed_CB(self, event=None):
        if(self.lock_Button_On == False):                           # Have to check explictly for lock button because of
                                                                    # Release callbacks
            self.ATT_Jogwheel.lastValue = self.ATT_Jogwheel.get()

    def ATT_Jogwheel_ButtonReleased_CB(self, event=None):
        if(self.lock_Button_On == False):
            currentValue = self.ATT_Jogwheel.get()
            if (self.ATT_Jogwheel.lastValue == currentValue) :
                self.toggleATT_State()
            else:
                self.Radio_Set_ATT(currentValue)

    #
    #   toggle ATT state to on if it was off, off it it was on
    #
    def toggleATT_State(self):
        if self.ATT_Jogwheel.state == "disabled":
            self.Radio_Set_ATT(self.ATT_Jogwheel.lastValue)     # Signal radio ATT on and last value
        else:
            self.Radio_Set_ATT(self.ATT_Status_Off)             # Signal radio ATT turning off

    #
    #   Send Radio/MCU the updated value for the  ATT. Although the UX reflects the new
    #   value up front, it gets re-set when the radio/mcu sends the "real" value via the "vf"
    #   command.  This means that the wheel might do a little forward/back dance depending
    #   on the speed of the MCU
    #
    def updateATTValue_CB(self):

        self.Radio_Set_ATT(self.ATT_Jogwheel.get())


    #
    #   The following handles the IFS Jogwheel. This is basically the same pattern
    #   as the ATT jogwheel above, except IFS hastwo functions (on/off and
    #   value set) where the ATT command only has one value with a "Zero" indicating ON/OFF.
    #

    def IFS_Jogwheel_ButtonPressed_CB(self, event=None):
        if (self.lock_Button_On == False):
            self.IFS_Jogwheel.lastValue = self.IFS_Jogwheel.get()

    def IFS_Jogwheel_ButtonReleased_CB(self, event=None):
        if (self.lock_Button_On == False):
            currentValue = self.IFS_Jogwheel.get()
            if self.IFS_Jogwheel.lastValue == currentValue:
                self.toggleIFS_State()
            else:
                self.Radio_Set_IFS_Level(currentValue)


    def toggleIFS_State(self):
        self.Radio_Toggle_IFS()

    def updateIFSValue_CB(self):
        self.Radio_Set_IFS_Level(self.IFS_Jogwheel.get())




########################################################################################
#   End of Callbacks executed by the UX
########################################################################################

#   Radio Commands
########################################################################################
#   These routines are called to tell the MCU that an action has happened in the UX.
#   Typically these should be used by the UX Callbacks
########################################################################################
    def Radio_Freq_Encode(self, freq):
        encodedBytes = bytearray()
        intFreq = int(freq)
        encodedBytes.append(intFreq & 0xff)

        intFreq = (intFreq >> 8)
        encodedBytes.append(intFreq & 0xff)

        intFreq = (intFreq >> 8)
        encodedBytes.append(intFreq & 0xff)

        intFreq = (intFreq >> 8)
        encodedBytes.append(intFreq & 0xff)

        return encodedBytes

    def Radio_Set_Master_Cal(self, cal):

        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #   This requires reboot to take effect
        #

        checksum = (self.EEPROM_Mem_Address["master_cal"][self.lsb] + self.EEPROM_Mem_Address["master_cal"][self.msb]
                    + self.EEPROM_Mem_Address["master_cal"][self.memLength]) % 256

        fourBytes = self.Radio_Freq_Encode(str(cal))

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   self.EEPROM_Mem_Address["master_cal"][self.lsb],
                   self.EEPROM_Mem_Address["master_cal"][self.msb],
                   self.EEPROM_Mem_Address["master_cal"][self.memLength],
                   checksum,
                   fourBytes[0],
                   fourBytes[1],
                   fourBytes[2],
                   fourBytes[3]
                   ]
        self.theRadio.sendCommandToMCU(bytes(command))


    def Radio_Set_SSB_BFO(self, cal):

        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #   This requires reboot to take effect
        #

        checksum = (self.EEPROM_Mem_Address["ssb_bfo"][self.lsb] + self.EEPROM_Mem_Address["ssb_bfo"][self.msb]
                    + self.EEPROM_Mem_Address["ssb_bfo"][self.memLength]) % 256

        fourBytes = self.Radio_Freq_Encode(str(cal))

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   self.EEPROM_Mem_Address["ssb_bfo"][self.lsb],
                   self.EEPROM_Mem_Address["ssb_bfo"][self.msb],
                   self.EEPROM_Mem_Address["ssb_bfo"][self.memLength],
                   checksum,
                   fourBytes[0],
                   fourBytes[1],
                   fourBytes[2],
                   fourBytes[3]
                   ]
        self.theRadio.sendCommandToMCU(bytes(command))



    def Radio_Set_CW_BFO(self, cal):

        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #   This requires reboot to take effect
        #

        checksum = (self.EEPROM_Mem_Address["cw_bfo"][self.lsb] + self.EEPROM_Mem_Address["cw_bfo"][self.msb]
                    + self.EEPROM_Mem_Address["cw_bfo"][self.memLength]) % 256

        fourBytes = self.Radio_Freq_Encode(str(cal))

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   self.EEPROM_Mem_Address["cw_bfo"][self.lsb],
                   self.EEPROM_Mem_Address["cw_bfo"][self.msb],
                   self.EEPROM_Mem_Address["cw_bfo"][self.memLength],
                   checksum,
                   fourBytes[0],
                   fourBytes[1],
                   fourBytes[2],
                   fourBytes[3]
                   ]
        self.theRadio.sendCommandToMCU(bytes(command))


    def Radio_Set_Tuning_Preset(self, rate: bytes):
        command = [self.toRadioCommandDict["TS_CMD_TUNESTEP"], rate, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Set_New_Frequency(self, value):
        fourBytes = self.Radio_Freq_Encode(value)
        command = [self.toRadioCommandDict["TS_CMD_FREQ"],fourBytes[0],fourBytes[1],fourBytes[2],fourBytes[3]]
        self.theRadio.sendCommandToMCU(bytes(command))

    #
    #   This function tells the Radio that a new mode has been selected for
    #   the primary (displayed) VFO. After receiving the new mode, the
    #   Radio will separately send back the mode to the UX
    #
    def Radio_Set_Mode(self, newMode):
        command = [self.toRadioCommandDict["TS_CMD_MODE"], newMode, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    #
    #   This function tells the Radio that a button up or down has been pushed
    #   in the UX. After receiving this command the radio will send back a new frequency
    #   and mode for the displayed VOF
    #
    def Radio_Change_Band(self, direction):
        command = [self.toRadioCommandDict["TS_CMD_BAND"], direction, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Tuning_Rate(self,value: bytes):
        command = [self.toRadioCommandDict["TS_CMD_TUNESTEP"], value, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Toggle_VFO(self):
        command = [self.toRadioCommandDict["TS_CMD_VFO"], 0, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Toggle_Lock(self):
        command = [self.toRadioCommandDict["TS_CMD_LOCK"], 0, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Toggle_Speaker(self):
        command = [self.toRadioCommandDict["TS_CMD_SDR"], 0, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Toggle_Stop(self):
        command = [self.toRadioCommandDict["TS_CMD_TXSTOP"], 0, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Toggle_Split(self):
        command = [self.toRadioCommandDict["TS_CMD_SPLIT"], 0, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Toggle_RIT(self):
        command = [self.toRadioCommandDict["TS_CMD_RIT"], 0, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Set_ATT(self, value: bytes):
        command = [self.toRadioCommandDict["TS_CMD_ATT"], value, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Toggle_IFS(self):
        command = [self.toRadioCommandDict["TS_CMD_IFS"], 0, 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))



    def Radio_Set_IFS_Level(self, level):
        encodedBytes = self.Radio_Freq_Encode(str(level))

        command = [self.toRadioCommandDict["TS_CMD_IFSVALUE"], encodedBytes[0], encodedBytes[1], encodedBytes[2], 0]
        self.theRadio.sendCommandToMCU(bytes(command))


    def Radio_Set_CW_Tone(self, tone):

        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #   This requires reboot to take effect
        #

        checksum = (self.EEPROM_Mem_Address["cw_sidetone"][self.lsb] + self.EEPROM_Mem_Address["cw_sidetone"][self.msb]
                    + self.EEPROM_Mem_Address["cw_sidetone"][self.memLength]) % 256


        fourBytes = self.Radio_Freq_Encode(str(tone))

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   self.EEPROM_Mem_Address["cw_sidetone"][self.lsb],
                   self.EEPROM_Mem_Address["cw_sidetone"][self.msb],
                   self.EEPROM_Mem_Address["cw_sidetone"][self.memLength],
                   checksum,
                   fourBytes[0],
                   fourBytes[1],
                   fourBytes[2],
                   fourBytes[3]
                   ]
        self.theRadio.sendCommandToMCU(bytes(command))


    def Radio_Set_CW_Keytype(self, keyType):
        #
        #   first send command to officially change the keytype
        #
        command = [self.toRadioCommandDict["TS_CMD_KEYTYPE"], gv.CW_KeyValue[keyType], 0, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))
        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #

        checksum = (self.EEPROM_Mem_Address["cw_key_type"][self.lsb] + self.EEPROM_Mem_Address["cw_key_type"][self.msb]
                    + self.EEPROM_Mem_Address["cw_key_type"][self.memLength]) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   self.EEPROM_Mem_Address["cw_key_type"][self.lsb],
                   self.EEPROM_Mem_Address["cw_key_type"][self.msb],
                   self.EEPROM_Mem_Address["cw_key_type"][self.memLength],
                   checksum,
                   gv.CW_KeyValue[keyType]
                   ]
        self.theRadio.sendCommandToMCU(bytes(command))




    def Radio_Set_CW_Speed(self, keySpeed):

        #
        #
        #   first send command to officially change the key speed
        #   wpm directly saved. It is the dot length which is 1200/wpm
        #

        dotLength_ms = int(1200 / int(keySpeed))
        command = [self.toRadioCommandDict["TS_CMD_WPM"], dotLength_ms, 0, 0]
        self.theRadio.sendCommandToMCU(bytes(command))

        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #

        checksum = (self.EEPROM_Mem_Address["cw_wpm"][self.lsb] + self.EEPROM_Mem_Address["cw_wpm"][self.msb]
                    + self.EEPROM_Mem_Address["cw_wpm"][self.memLength]) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   self.EEPROM_Mem_Address["cw_wpm"][self.lsb],
                   self.EEPROM_Mem_Address["cw_wpm"][self.msb],
                   self.EEPROM_Mem_Address["cw_wpm"][self.memLength],
                   checksum,
                   dotLength_ms,                # Eeprom allows up to two bytes for adjusted key,
                                                    # but keychage without reboot only 1 byte
                   0,0,0
                   ]

        self.theRadio.sendCommandToMCU(bytes(command))


    def Radio_Set_CW_Delay_Starting_TX(self, startTXDelay):
        #
        #   Requires reboot to take effect
        #
        #
        # adjust the wpm speed to format of EEPROM
        #
        adjustedStartTXDelay = int(int(startTXDelay)/2)

        #
        #   write it to EEPROM as will be picked up on next reboot
        #

        checksum = (self.EEPROM_Mem_Address["cw_Delay_Starting_TX"][self.lsb] + self.EEPROM_Mem_Address["cw_Delay_Starting_TX"][self.msb]
                    + self.EEPROM_Mem_Address["cw_Delay_Starting_TX"][self.memLength]) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   self.EEPROM_Mem_Address["cw_Delay_Starting_TX"][self.lsb],
                   self.EEPROM_Mem_Address["cw_Delay_Starting_TX"][self.msb],
                   self.EEPROM_Mem_Address["cw_Delay_Starting_TX"][self.memLength],
                   checksum,
                   adjustedStartTXDelay
                   ]

        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Set_CW_Delay_Returning_To_RX(self, returnRXDelay):
        # value stored to eeprom needs to divided by 10
        #
        #   Requires reboot to take effect
        #
        #
        # adjust the wpm speed to format of EEPROM
        #
        adjustedReturnToRXDelay = int(int(returnRXDelay) / 10)

        #
        #   write it to EEPROM as will be picked up on next reboot
        #

        checksum = (self.EEPROM_Mem_Address["cw_Delay_Returning_to_RX"][self.lsb] +
                    self.EEPROM_Mem_Address["cw_Delay_Returning_to_RX"][self.msb]
                    + self.EEPROM_Mem_Address["cw_Delay_Returning_to_RX"][self.memLength]) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   self.EEPROM_Mem_Address["cw_Delay_Returning_to_RX"][self.lsb],
                   self.EEPROM_Mem_Address["cw_Delay_Returning_to_RX"][self.msb],
                   self.EEPROM_Mem_Address["cw_Delay_Returning_to_RX"][self.memLength],
                   checksum,
                   adjustedReturnToRXDelay
                   ]

        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Write_EEPROM_Channel_FreqMode (self, channelNum, freq, mode ):

        encoded_data = (int(freq) & 0x1FFFFFFF) + ((int(self.Text_To_ModeNum[mode])& 0x7)<<29)

        encodedBytes = self.Radio_Freq_Encode(str(encoded_data))

        lsb = (channelNum*self.EEPROM_Mem_Address["channel_freq_Mode"][self.memOffset]) + self.EEPROM_Mem_Address["channel_freq_Mode"][self.lsb]
        msb = self.EEPROM_Mem_Address["channel_freq_Mode"][self.msb]
        totalBytes = self.EEPROM_Mem_Address["channel_freq_Mode"][self.memLength]


        checksum = (lsb + msb + totalBytes) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   lsb,
                   msb,
                   totalBytes,
                   checksum,
                   encodedBytes[0], encodedBytes[1], encodedBytes[2], encodedBytes[3]
                   ]

        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Write_EEPROM_Channel_Label (self, channelNum, label ):

        if channelNum > self.EEPROM_Mem_Address["channel_ShowLabel"][self.totalSlots]:
            return

        lsb = ((channelNum * self.EEPROM_Mem_Address["channel_Label"][self.memOffset]) +
               self.EEPROM_Mem_Address["channel_Label"][self.lsb])
        msb = self.EEPROM_Mem_Address["channel_Label"][self.msb]
        totalBytes = self.EEPROM_Mem_Address["channel_Label"][self.memLength]

        # strip blanks
        noBlankLabel = label.strip()
        labelBytes = bytes(noBlankLabel.ljust(totalBytes), 'utf-8')


        checksum = (lsb + msb + totalBytes) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   lsb,
                   msb,
                   totalBytes,
                   checksum,
                   labelBytes[0], labelBytes[1], labelBytes[2], labelBytes[3], labelBytes[4]
                   ]

        self.theRadio.sendCommandToMCU(bytes(command))

    def Radio_Write_EEPROM_Channel_ShowLabel (self, channelNum, showLabel ):

        #
        #   Don't write to EEPROMs showLabels 10+
        #
        if channelNum > self.EEPROM_Mem_Address["channel_ShowLabel"][self.totalSlots]:
            return

        lsb = (channelNum * self.EEPROM_Mem_Address["channel_ShowLabel"][self.memOffset]) + \
              self.EEPROM_Mem_Address["channel_ShowLabel"][self.lsb]
        msb = self.EEPROM_Mem_Address["channel_ShowLabel"][self.msb]
        totalBytes = self.EEPROM_Mem_Address["channel_ShowLabel"][self.memLength]

        checksum = (lsb + msb + totalBytes) % 256

        if showLabel == 'Yes':
            value = 0x3
        else:
            value = 0x0

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   lsb,
                   msb,
                   totalBytes,
                   checksum,
                   value
                   ]

        self.theRadio.sendCommandToMCU(bytes(command))


#   MCU Commands
#########################################################################################
####    Start of command processing sent by Radio(MCU) to Screen
#########################################################################################

    #
    #   The "v1" command is used for smallest tuning rate
    #

    def v1_UX_Set_Tuning_Preset_1(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.theVFO_Object.set_Tuning_Preset_1(value)


    #
    #   The "v2" command is used for smallest tuning rate
    #
    def v2_UX_Set_Tuning_Preset_2(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.theVFO_Object.set_Tuning_Preset_2(value)

    #
    #   The "v3" command 1s used for the third (middle) tuning rate
    #
    def v3_UX_Set_Tuning_Preset_3(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.theVFO_Object.set_Tuning_Preset_3(value)

    #
    #   The "v4" command 1s used for the next largest tuning rate
    #
    def v4_UX_Set_Tuning_Preset_4(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.theVFO_Object.set_Tuning_Preset_4(value)


    #
    #   The "v5" command 1s used for the largest tuning rate
    #
    def v5_UX_Set_Tuning_Preset_5(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.theVFO_Object.set_Tuning_Preset_5(value)

    #
    #   The "cn" command indicates which tuning step is active (1(smallest) - 5(largest)
    #
    def cn_UX_Set_Active_Tuning_Preset(self, buffer):

        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.theVFO_Object.set_Active_Tuning_Preset(value)
        # self.tuning_Preset_Selection_VAR.set(value)
        #
        # match value:
        #     case "5":
        #         if (self.update_Tuning_Preset_Button_Label):
        #             self.tuning_Preset_Label_VAR.set(self.tuning_Preset_5_VAR.get())
        #         self.tuning_Preset_Selection_VAR.set(5)
        #         self.currentVFO_Tuning_Rate = int(self.tuning_Preset_5_VAR.get())
        #
        #     case "4":
        #         if (self.update_Tuning_Preset_Button_Label):
        #             self.tuning_Preset_Label_VAR.set(self.tuning_Preset_4_VAR.get())
        #         self.tuning_Preset_Selection_VAR.set(4)
        #         self.currentVFO_Tuning_Rate = int(self.tuning_Preset_4_VAR.get())
        #     case "3":
        #         if (self.update_Tuning_Preset_Button_Label):
        #             self.tuning_Preset_Label_VAR.set(self.tuning_Preset_3_VAR.get())
        #         self.tuning_Preset_Selection_VAR.set(3)
        #         self.currentVFO_Tuning_Rate = int(self.tuning_Preset_3_VAR.get())
        #     case "2":
        #         if (self.update_Tuning_Preset_Button_Label):
        #             self.tuning_Preset_Label_VAR.set(self.tuning_Preset_2_VAR.get())
        #         self.tuning_Preset_Selection_VAR.set(2)
        #         self.currentVFO_Tuning_Rate = int(self.tuning_Preset_2_VAR.get())
        #     case "1":
        #         if (self.update_Tuning_Preset_Button_Label):
        #             self.tuning_Preset_Label_VAR.set(self.tuning_Preset_1_VAR.get())
        #         self.tuning_Preset_Selection_VAR.set(1)
        #         self.currentVFO_Tuning_Rate = int(self.tuning_Preset_1_VAR.get())
        #
        # self.updateRateMultiplier()
        # self.updateJogTracking()
        # self.updateLabelTuning_Multiplier()


    #
    #   The "ch" command originates from the EEPROM and is added to the frequency to shift it
    #
    def ch_UX_Set_CW_TX_OFFSET(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        #
        #   The following provides the ability to override the EEPROM value as a setting config
        #
        if self.cwTX_OffsetFlagOverride != None:
            self.cwTX_OffsetFlag = self.cwTX_OffsetFlagOverride
            return

        if value == 0:              #turn off CW TX offset mode
            self.cwTX_OffsetFlag = False
        else:                       #turn on CW TX offset - only effects CWL and CWU modes
            self.cwTX_OffsetFlag = True


    #
    #   The "vh" command originates from the EEPROM and is added to the frequency to shift it
    #
    def vh_UX_Set_CW_Tweak(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.cwTX_Tweak = int(value)

    #
    #   The "vo" if 1, then turn on IFS and use initial value
    #
    def voGet(self, buffer):
        pass
        # print("voGet, buffer=",buffer)


    def cp_UX_S_Meter_Value(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.s_meter_Progressbar_VAR.set(int(value))

    #
    #   This is a hack fix for a bug in CEC (at least v2.0, perhaps in 1.x too)
    #   Command for S-meter is ill formed and we  get "p.val=x" instead of "pm.cp.val=x'
    #   Just got tired of seeing this error flagged...
    #
    def al_UX_S_Meter_Value(self, buffer):
        value = self.extractValue(buffer, 6, len(buffer) - 3)
        if value.isnumeric():
            # print("correcting for mal formed s-meter commend", buffer, "setting s-meter to", value)
            self.s_meter_Progressbar_VAR.set(int(value))
        else:
            print("another weird malformed command, buffer =", buffer)

    def ct_UX_RX_TX_Mode(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        print("ct get called:", "buffer =", buffer)
        if value == "1":  #going into transmit mode
            self.theVFO_Object.setTXButtonState()
        else:
            self.theVFO_Object.setRXButtonState()


    #
    #   The "vp" command originates from the EEPROM and is added to the frequency to shift it
    #
    def vpGet(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        # print("vp get called:", "buffer =", buffer)

    #
    #   The "vq" command is referred to as display option 2 in EEPROM
    #
    def vqGet(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        # print("vq get called: buffer=", buffer)



    #
    #   The "sv" command is stores the text of the firmware version
    #
    def sv_UX_Set_SW_Version(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.theVFO_Object.setFirmwareVersion(value)



    #
    #   The "sc" command is stores the text of the operators callsign
    #
    def sc_UX_Set_User_Callsign(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.theVFO_Object.setCallsign(value)


    #
    #   The "cm" command determines whether call sign and firmware versions are displayed
    #
    def cm_UX_Display_Callsign_Version_Flag(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        if value == "0":
            self.firmwareVersion_VAR.set("")
            self.callSign_VAR.set("")




    #
    #   The "c0" command determines whether we are in text (yellow box) or graphics mode
    #
    def c0_UX_Toggle_Classic_uBITX_Control(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        if value == "0":
            if self.classic_uBITX_ControlWindowObj != None:
                self.classic_uBITX_ControlWindowObj.pack_forget()
                self.classic_uBITX_ControlWindowObj = None
            if self.classic_uBITX_ControlWindow != None:
                self.classic_uBITX_ControlWindow.destroy()
                self.classic_uBITX_ControlWindow = None

        else:
            self.displayClassic_uBITXControlWindow()


    #
    # The purpose of this command is a little puzzling
    # code talks about this being used to eliminate duplicate data
    # Only sent on the first attempt to lock the screen
    # Also contains the text for the speaker button
    #
    def s0_UX_Greenbox_Line1(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.displayLine1Classic_uBITX_Control(value)


    def s1_UX_Greenbox_Line2(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.displayLine2Classic_uBITX_Control(value)


    def sh_UX_Get_Memory(self, buffer):
        try:
            value = self.extractValue(buffer, 10, len(buffer) - 3)
            if not self.memoryQueue:    # make sure something in queue, otherwise fatal error
                messagebox.showerror("Application Error", "Memory Queue is empty, yet memory value delivered by MCU")
                sys.exit("A fatal internal error occurred")

            memoryCategory = self.memoryQueue.pop(0)
            match memoryCategory:

                case "Freq":                # Got a channel frequency request
                    freq = int(value,16) & 0x1FFFFFFF
                    mode = (int(value,16) >> 29) & 0x7
                    self.channelsWindow.EEPROM_SetChanneFreqMode(
                        self.EEPROM_Current_Slot_Freq,
                        freq,
                        mode)
                    self.EEPROM_Current_Slot_Freq += 1
                    if (self.EEPROM_Current_Slot_Freq ==
                            self.EEPROM_Mem_Address["channel_freq_Mode"][self.totalSlots]):
                        self.EEPROM_Current_Slot_Freq = 0

                case "Label":               # have a label for a memory channel
                    self.channelsWindow.EEPROM_SetChannelLabel(
                        self.EEPROM_Current_Slot_Label,
                        value)
                    # if self.EEPROM_Current_Slot_Label == 9:
                    #         print("label slot=", self.EEPROM_Current_Slot_Label, "value=", value, sep='*', end='*')
                    self.EEPROM_Current_Slot_Label += 1
                    if (self.EEPROM_Current_Slot_Label ==
                            self.EEPROM_Mem_Address["channel_Label"][self.totalSlots]):
                        self.EEPROM_Current_Slot_Label = 0

                case "ShowLabel":           # Reading switch on whether to show or not show the label
                    if (ord(value) == 0):
                        self.channelsWindow.EEPROM_SetChannelShowLabel(
                            self.EEPROM_Current_Slot_ShowLabel,
                            "No")

                    else:
                        self.channelsWindow.EEPROM_SetChannelShowLabel(
                            self.EEPROM_Current_Slot_ShowLabel,
                            "Yes")

                    self.EEPROM_Current_Slot_ShowLabel += 1
                    if (self.EEPROM_Current_Slot_ShowLabel ==
                            self.EEPROM_Mem_Address["channel_ShowLabel"][self.totalSlots]):
                        self.EEPROM_Current_Slot_ShowLabel = 0

                case "MasterCal":          # Got a master cal value
                    self.Master_Cal_Setter(str(int(value, 16)))


                case "SSB_BFO":            # Got a SSB BFO value
                    self.SSB_BFO_Setter(str(int(value, 16)))

                case "CW_BFO":             # Got a CW BFO Value
                    self.CW_BFO_Setter(str(int(value, 16)))

                case "Factory_MasterCal":   #Got a Factory_MasterCal memory value
                    self.Factory_Master_Cal_Setter(str(int(value, 16)))

                case "Factory_SSB_BFO":     # Got a Factory SSB BFO memory value
                    self.Factory_SSB_BFO_Setter(str(int(value, 16)))

                case "Factory_CW_Speed":    # Got a CW Speed memory value
                    if int(value,16) != 0:
                        cw_speed = str(round(1200/int(value,16)))
                    else:
                        cw_speed = "0"

                    self.Factory_CW_Speed_Setter(cw_speed)

                case "Factory_CW_Sidetone":
                    self.Factory_CW_Sidetone_Setter(str(int(value, 16)))

                case _:
                    messagebox.showerror("Application Error", "Unknown Memory Request")
                    sys.exit("A fatal internal error occurred")
        except TypeError:
            print("type error")
            print("memory category =", memoryCategory)
            print(" freq slot =", self.EEPROM_Current_Slot_Freq)
            print(" label slot =", self.EEPROM_Current_Slot_Label)
            print(" show slot =", self.EEPROM_Current_Slot_ShowLabel)

            print("buffer =", buffer)
            message = messagebox.showerror("Application Error", "Unknown Memory Request\nRestart application")
            sys.exit("A fatal internal error occurred")



    def vn_UX_ACK_Memory_Write(self, buffer):
        # if (pm.vn.val == 358) // key Type Write Complete
        # {
        #     nSendProcess.val = 11
        # } else if (pm.vn.val == 28) // key Type Write Complete
        # {
        #     nSendProcess.val = 12
        # } else if (pm.vn.val == 24) // key Type Write Complete
        # {
        #     nSendProcess.val = 13
        # } else if (pm.vn.val == 258) // key Type Write Complete
        # {
        #     nSendProcess.val = 14
        # } else if (pm.vn.val == 259) // key Type Write Complete
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        if self.CurrentDebug:
            print("vn get called:", "buffer =", buffer)
            print("buffer=", buffer)
            if (int(value) == 358):
                print("write complete for keychange, mem=", int(value))
            elif (int(value) == 28):
                print("write complete for new WPM, mem=", int(value))
            elif (int(value) == 259):
                print("write complete for new RX->TX, mem=", int(value))
            elif (int(value) == 258):
                print("write complete for new TX->RX, mem=", int(value))
            else:
                print("memory location write complete, mem=", int(value))





    def cl_UX_Lock_Screen(self, buffer):

        if (self.lock_Button_On):
            self.lock_Button_On = False
            self.lock_Button.configure(style='Button2b.TButton', state="normal")
            self.lock_VAR.set("\nLOCK\n")
            self.unlockUX()
        else:
            self.lock_Button_On = True
            self.lock_Button.configure(style='RedButton2b.TButton', state='pressed')
            self.lock_VAR.set("\nLOCKED\n")
            self.lockUX()

    #
    #   Disable all of the control widgets when a LOCK action is requested
    #
    def lockUX(self):
        self.settings_Button.configure(state = "disabled")
        self.vfo_Button.configure(state="disabled")
        self.mode_select_Menubutton.configure(state="disabled")
        self.band_up_Button.configure(state="disabled")
        self.band_down_Button.configure(state="disabled")
        self.speaker_Button.configure(state="disabled")
        self.split_Button.configure(state="disabled")
        self.rit_Button.configure(state="disabled")
        self.channels_Button.configure(state="disabled")
        # self.tuning_Multiplier_Button.configure(state="disabled")
        # self.tuning_Preset_Button.configure(state="disabled")
        self.ATT_Jogwheel.setStateDisabled()
        self.IFS_Jogwheel.setStateDisabled()
        self.tuning_Jogwheel.setStateDisabled()
        self.theVFO_Object.setVFOUXState("disabled")


    #
    #   Reset all widgets to their "normal" state after the  unlock happens
    #
    def unlockUX(self):
        self.settings_Button.configure(state = "normal")
        self.vfo_Button.configure(state="normal")
        self.mode_select_Menubutton.configure(state="normal")
        self.band_up_Button.configure(state="normal")
        self.band_down_Button.configure(state="normal")
        self.speaker_Button.configure(state="normal")
        self.split_Button.configure(state="normal")
        self.rit_Button.configure(state="normal")
        self.channels_Button.configure(state="normal")
        # self.tuning_Multiplier_Button.configure(state="normal")
        # self.tuning_Preset_Button.configure(state="normal")
        if (self.ATT_Button_On == True):
            self.ATT_Jogwheel.setStateNormal()
        if (self.IFS_Button_On == True):
            self.IFS_Jogwheel.setStateNormal()
        self.tuning_Jogwheel.setStateNormal()
        self.theVFO_Object.setVFOUXState("normal")


    def cj_UX_Speaker_Toggle(self, buffer):

        if (self.speaker_Button_On):
            self.speaker_Button_On = False
            self.speaker_Button.configure(style='Button2b.TButton', state="normal")
            self.speaker_VAR.set("\nSPEAKER\n")
        else:
            self.speaker_Button_On = True
            self.speaker_Button.configure(style='RedButton2b.TButton', state="pressed")
            self.speaker_VAR.set("\nSPK MUTED\n")


    def cs_UX_SPLIT_Toggle(self, buffer):
        if (self.split_Button_On):
            self.split_Button_On = False
            self.split_Button.configure(style='Button2b.TButton', state="normal")
        else:
            self.split_Button_On = True
            self.split_Button.configure(style='GreenButton2b.TButton', state="pressed")
    #
    #   This appears to be a no-op command. If the last rit TX frequency does not equal
    #   the current frequency, this is called to set the VFO to the RIT TX frequency which happens to be
    #   the current vfo setting anyway.
    #
    def vr_UX_Update_RIT_Freq(self, buffer):
        if self.CurrentDebug:
            print("vr called")  # command is rit related
            print(buffer)


    def cr_UX_RIT_Toggle(self, buffer):
        if (self.rit_Button_On):
            self.rit_Button_On = False
            self.rit_Button.configure(style='Button2b.TButton', state="normal")
        else:
            self.rit_Button_On = True
            self.rit_Button.configure(style='GreenButton2b.TButton', state="pressed")

    def vf_UX_ATT_Level(self, buffer):

        value = int(self.extractValue(buffer, 10, len(buffer) - 3))

        #
        #   Zero Value indicated Radio turning off the ATT
        #
        if (value == 0):
            self.ATT_Jogwheel.setStateDisabled()
            self.ATT_Status_VAR.set("ATT (OFF)")
            self.ATT_Button_On = False
        else:
            if self.ATT_Jogwheel.state == 'disabled':
                self.ATT_Jogwheel.setStateNormal()
                self.ATT_Status_VAR.set("ATT (ON)")
                self.ATT_Button_On = True
            #
            # mjh normally ux should be set to the value ack-ed by mcu. Problem with this
            # with jog wheels is that they jerk around too much because of all the callbacks
            # This can also cause oscillation where are reported and stored in jogwheel
            # much after and so when correcting generate more old traffic.
            # On balance the chance of a lost packet is pretty low, so best option is to not
            # repond to the ack-ed value from the MCU
            #
            # BUT...
            # In Classic mode, still need to update the jogwheel...
            #
            if self.classic_uBITX_ControlWindow != None:
                self.ATT_Jogwheel.set(value)            # Set UX to value acked by MCU


    def ci_UX_IFS_State_Set(self, buffer):
        value = int(self.extractValue(buffer, 10, len(buffer) - 3))
        if (value == 0):                            # Zero value indicates IFS being turned off
            self.IFS_Jogwheel.setStateDisabled()
            self.IFS_Status_VAR.set("IFS (OFF)")
            self.IFS_Button_On = False
        else:
            self.IFS_Jogwheel.setStateNormal()
            self.IFS_Status_VAR.set("IFS (ON)")
            self.IFS_Button_On = True


    def vi_UX_IFS_Level(self, buffer):      #verification by MCU of new value
        value = int(self.extractValue(buffer, 10, len(buffer) - 3))
        # Note that if a "personalized" IF level is set in the EEPROM, then the radio comes
        # Up with IFS enabled. If value here is 0, just disable the jogwheel
        if (value == 0):
            self.IFS_Jogwheel.setStateDisabled()

        # mjh normally ux should be set to the value ack-ed by mcu. Problem with this
        # with jog wheels is that they jerk around too much because of all the callbacks
        # This can also cause oscillation where are reported and stored in jogwheel
        # much after and so when correcting generate more old traffic.
        # On balance the chance of a lost packet is pretty low, so best option is to not
        # repond to the ack-ed value from the MCU
        #
        #BUT.....
        # Need to respond when in Classic UX Mode. Can use a check for null to figure out whether we update or not
        #

        if self.classic_uBITX_ControlWindow != None:
            self.IFS_Jogwheel.set(value)

        if self.IFS_On_Boot_Flag:           # A little hack. Generally will not respond to MCU IFS requests for efficiency
                                            # On boot, the default setting is passed to the UX.
            self.IFS_Jogwheel.set(value)
            self.IFS_On_Boot_Flag = False




    def cx_UX_TX_Stop_Toggle(self, buffer):
        self.theVFO_Object.toggleStopButtonState()


    #
    #   The "vc" command indicates a new frequency for the Primary
    #
    def vc_UX_Set_Primary_VFO_Frequency(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)

        self.theVFO_Object.setPrimaryVFO(value)

        # self.primary_VFO_VAR.set(value)
        # self.update_VFO_Display(self.primary_VFO_VAR.get(),self.freqOffset)
        # self.updateJogTracking()

        if self.channelsWindow != None:      #  Only update frequency if the channel window has been created once
            self.channelsWindow.update_Current_Frequency(self.theVFO_Object.getFormattedPrimaryVFO)
            # self.channelsWindow.update_Current_Frequency(gv.formatFrequency(self.primary_VFO_VAR.get()))




    # def reformatVFO(self, value):
    #     self.digit_delimiter_primary_VFO_VAR.set(gv.config.get_NUMBER_DELIMITER())
    #     self.update_VFO_Display(str(self.displayedVFO))
    #     # self.update_VFO_Display(self.primary_VFO_VAR.get(), self.freqOffset)
    #     self.secondary_VFO_Formatted_VAR.set(gv.formatFrequency(self.secondary_VFO_VAR.get(), self.freqOffset))
    #     self.RX_VFO_VAR.set(gv.formatFrequency(self.RX_VFO_VAR.get().replace(gv.config.get_NUMBER_DELIMITER(),"")))

    def switchVFO_Tuning_Optimization(self, value):
        self.tuning_Jogwheel.configure(scroll=True, touchOptimized=value)

    #
    #   The "cc" command indicates a change to a new mode for primary (e.g. USB, LSB, etc.)
    #
    def cc_UX_Set_Primary_Mode(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.primary_Mode_VAR.set(self.modeNum_To_TextDict[value])
        if self.cwTX_OffsetFlag and (self.modeNum_To_TextDict[value] == "CWL" or self.modeNum_To_TextDict[value] == "CWU"):
            #
            #   We are showing the TX frequency on the VFO so need to offset it
            #
            self.theVFO_Object.offsetVFOforTX(True)
        else:
            self.theVFO_Object.offsetVFOforTX(False)

        self.theVFO_Object.updateJogTracking()            # Since changed mode, may need to reset jogwheel to tx frequency

        if self.channelsWindow != None:
            # Only update frequency if the channel window has been created once
            self.channelsWindow.update_Current_Mode(self.primary_Mode_VAR.get())


    #
    #   The "va" command indicates assignment of vfoA to new frequency
    #
    def va_UX_Set_VFO_A_Frequency(self, buffer):
        if (self.channelsWindow != None) and (self.channelsWindow.scanRunning):
            # print("***Ignoring va command as we're scanning***")
            return  # ignore the VFO A command during scanning as it can be out of order

        value = self.extractValue(buffer, 10, len(buffer) - 3)

        if (self.vfo_VAR.get()== self.VFO_A):       #update displayed frequency
            self.theVFO_Object.setPrimaryVFO(value)         #MJH dont we need to update vfoa and vfob directly

        else:
            self.theVFO_Object.setSecondaryVFO(value)




    #
    #   The "ca" command indicates assignment of a new mode to vfoA
    #
    def ca_UX_Set_VFO_A_Mode(self, buffer):
        if (self.channelsWindow != None) and (self.channelsWindow.scanRunning):
            # print("***Ignoring ca command as we're scanning***")
            return  # ignore the VFO A command during scanning  as it can be out of order

        value = self.extractValue(buffer, 10, len(buffer) - 3)

        if (self.vfo_VAR.get()== self.VFO_A):       #update displayed frequency
            self.primary_Mode_VAR.set(self.modeNum_To_TextDict[value])
        else:
            self.theVFO_Object.setSecondaryMode(self.modeNum_To_TextDict[value])


        # print("***ca get called:***", "buffer =", buffer)
        # print("ca assign mode for vfoA frequency")
        # print("value=", value, sep='*', end='*')
        # print("\n")

    #
    #   The "vb" command indicates assignment of vfoB to new frequency
    #
    def vb_UX_Set_VFO_B_Frequency(self, buffer):

        if (self.channelsWindow != None) and (self.channelsWindow.scanRunning):
            return  # ignore the VFO B command during scanning as it can be out of order

        value = self.extractValue(buffer, 10, len(buffer) - 3)


        if (self.vfo_VAR.get()== self.VFO_B):       #update displayed frequency
            self.theVFO_Object.setPrimaryVFO(value)
        else:
            self.theVFO_Object.setSecondaryVFO(value)       #need formatted here too

        # print("***vb get called:***", "buffer =", buffer)
        # print("vb assign vfo b frequency")
        # print("value=", value, sep='*', end='*')
        # print("\n")
    #
    #   This sets VFO B to a new mode
    #
    def cb_UX_Set_VFO_B_Mode(self, buffer):

        if (self.channelsWindow != None) and (self.channelsWindow.scanRunning):
            return  # ignore the VFO B command during scanning as it can be out of order

        value = self.extractValue(buffer, 10, len(buffer) - 3)

        if (self.vfo_VAR.get()== self.VFO_B):       #update displayed frequency
            self.primary_Mode_VAR.set(self.modeNum_To_TextDict[value])
        else:
            self.theVFO_Object.secondary_Mode_VAR.set(self.modeNum_To_TextDict[value])

        # print("***cb get called:***", "buffer =", buffer)
        # print("cb assign mode for vfoB frequency")
        # print("value=", value, sep='*', end='*')
        # print("\n")

    #
    #   The "vt" command stores the CW tone
    #
    def vt_UX_SET_CW_Tone(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.tone_value_VAR.set(value)
        # self.theVFO_Object.setCWTone(value)


    #
    #   The "ck" command stores which cw key is being used
    #
    def ck_UX_Set_CW_Key_Type(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.key_type_value_VAR.set(gv.CW_KeyType[value])

    #
    #   The "vs" command stores words/minute
    #
    def vs_UX_Set_CW_Speed(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.key_speed_value_VAR.set(str(int(1200/int(value))))


    #
    #   The "vy" command stores delay returning after last cw character
    #
    def vy_UX_Set_CW_Delay_Returning_to_RX(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.delay_returning_to_rx_value_VAR.set(str(int(value)*10))



    #
    #   The "ve" command stores delay prior to TX 1st cw character
    #
    def ve_UX_Set_CW_Delay_Starting_TX(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.delay_starting_tx_value_VAR.set(str(int(value)*2))

    #
    #   Returns active VFO, VFO-A=0, VFO-B=1
    #
    def cv_UX_VFO_Toggle(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.theVFO_Object.toggleVFO()
        self.vfo_VAR.set(self.Text_To_VFO[value])           # Update Label on button
        #
        #
        #
        # saveSecondary_VFO = self.secondary_VFO_VAR.get()
        # saveSecondary_Mode = self.secondary_Mode_VAR.get()
        #
        # # self.secondary_VFO_VAR.set(gv.unformatFrequency(self.primary_VFO_Formatted_VAR))
        # self.theVFO_Object.setSecondayVFO(self.theVFO_Object.getFormattedPrimaryVFO())
        # # self.secondary_VFO_Formatted_VAR.set(gv.formatFrequency(self.primary_VFO_VAR.get()))
        # # self.secondary_VFO_Formatted_VAR.set(self.primary_VFO_Formatted_VAR.get())
        # # self.secondary_VFO_Formatted_VAR.set(gv.formatFrequency(gv.unformatFrequency(self.primary_VFO_Formatted_VAR.get()), self.freqOffset))
        # self.secondary_Mode_VAR.set(self.primary_Mode_VAR.get())
        #
        # self.theVFO_Object.setPrimaryVFO(saveSecondary_VFO)
        #
        # # self.primary_VFO_Formatted_VAR.set(gv.formatFrequency(saveSecondary_VFO, self.freqOffset))
        # # self.update_VFO_Display(self.primary_VFO_VAR.get(), self.freqOffset)
        #
        # self.primary_Mode_VAR.set(saveSecondary_Mode)

########################################################################################
#   End processing of commands sent by MCU to Screen
########################################################################################


