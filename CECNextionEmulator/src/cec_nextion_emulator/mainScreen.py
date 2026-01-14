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
import EEPROM as EEPROM

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

        # self.memoryQueue =[]            # when a memory slot is requested, it later comes in without any indication of which
        #                                 # memory slot it belong to. Fortunately, all in order. So everytime a memory slot is
        #                                 # requested, the type of memory requested is added to the queue so when we take it
        #                                 # off the queue, we know where it goes.


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


        self.cwTX_OffsetFlag = False                # Controls whether the display shows the transmit freq when in CW
        self.cwTX_OffsetFlagOverride = None
        self.cwTX_Offset = 0
        self.cwTX_Tweak = 0                         # Apparently an additional value that can be set in the original editor but not SE




        self.tuning_Jogwheel.configure(scroll=True, touchOptimized=gv.config.get_VFO_Touch_Optimized())
        self.theVFO_Object.attachDial(self.tuning_Jogwheel)
        self.tuning_Jogwheel.grid_remove()
        gv.config.register_observer("VFO Touch Optimized", self.switchVFO_Tuning_Optimization)
        self.baselineJogValue = 0


#   Constants
        #######################################################################################
        #   Dictionaries that follow are used to lookup textual values based on internal
        #   Representations. Sometimes it is a string integer. Other times it is a string of
        #   a couple characters. These translations are collected here to avoid them being
        #   "codified" directly in the functions that use them.
        #######################################################################################
        
        # EEPROM.modeNum_To_TextDict = {
        #     "0":"DFT",
        #     "2":"LSB",
        #     "3":"USB",
        #     "4":"CWL",
        #     "5":"CWU"
        # }
        # 
        # EEPROM.Text_To_ModeNum = {
        #     "DFT":0,
        #     "LSB":2,
        #     "USB":3,
        #     "CWL":4,
        #     "CWU":5
        # }

        self.Text_To_BandChange = {
            "UP": 2,
            "DOWN":1
        }
        self.Text_To_VFO= {
            "0": "VFO-A",
            "1": "VFO-B"
        }



        # self.memReadingState = "Freq"

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
            self.redisplayChannelWindow()

    #
    #   Initializes things when just deiconfying a prior channel window
    #
    def redisplayChannelWindow(self):
        self.theVFO_Object.savePresetState()
        self.theRadio.Set_Tuning_Preset(1)
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



    def vfo_CB(self):
        self.theRadio.Toggle_VFO()

    def mode_lsb_CB(self):
        self.theRadio.Set_Mode(EEPROM.Text_To_ModeNum["LSB"])

    def mode_usb_CB(self):
        self.theRadio.Set_Mode(EEPROM.Text_To_ModeNum["USB"])


    def mode_cwl_CB(self):
        self.theRadio.Set_Mode(EEPROM.Text_To_ModeNum["CWL"])


    def mode_cwu_CB(self):
        self.theRadio.Set_Mode(EEPROM.Text_To_ModeNum["CWU"])

    def band_up_CB(self):
         self.theRadio.Change_Band(self.Text_To_BandChange["UP"])

    def band_down_CB(self):
         self.theRadio.Change_Band(self.Text_To_BandChange["DOWN"])

    def cwSettings_CB(self, event=None):
       if (not self.lock_Button_On):
           self.displayCWSettingsWindow()


    def tuning_Jogwheel_CB(self):
        # print("\n\nin tuning_Jogwheel_CB")
        # print("intVFO =", self.theVFO_Object.getIntPrimaryVFO())
        # print("tuning rate=", self.theVFO_Object.getCurrentVFO_Tuning_Rate())
        # print("baselinejogvalue=",self.baselineJogValue )
        # print("jogwheel valye=", self.tuning_Jogwheel.get() )
        newFreq =  (self.theVFO_Object.getIntPrimaryVFO()
                    - (self.theVFO_Object.getCurrentVFO_Tuning_Rate() * self.baselineJogValue))

        newFreq += self.theVFO_Object.getCurrentVFO_Tuning_Rate() * self.tuning_Jogwheel.get()
        # print("newFreq=", newFreq)
        self.theRadio.Set_New_Frequency(newFreq)

#
#   This function sends to the Radio a notice that a screen lock has been requested
#   The actual locking of the screen waits until the Radio sends back a commond
#   to lock the screen. This ensures that the screen is not locked by the UX
#   and the Radio never gets the request for some reason.
#   The actual locking of screen is set performed by cl_UX_Lock_Screen()
#

    def lock_CB(self):
        self.theRadio.Toggle_Lock()    # Inform  Radio that a screen lock has been requested

    def speaker_CB(self):           # Inform Radio that a request was made to mute speaker
        self.theRadio.Toggle_Speaker()

    def stop_CB(self):
        self.theRadio.Toggle_Stop()

    def split_CB(self):
        self.theRadio.Toggle_Split()

    def rit_CB(self):
        self.theRadio.Toggle_RIT()



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
    #   self.theRadio.Set_ATT (value) routine. Zero turns it off, any other value turns it on.
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
                self.theRadio.Set_ATT(currentValue)

    #
    #   toggle ATT state to on if it was off, off it it was on
    #
    def toggleATT_State(self):
        if self.ATT_Jogwheel.state == "disabled":
            self.theRadio.Set_ATT(self.ATT_Jogwheel.lastValue)     # Signal radio ATT on and last value
        else:
            self.theRadio.Set_ATT(self.ATT_Status_Off)             # Signal radio ATT turning off

    #
    #   Send Radio/MCU the updated value for the  ATT. Although the UX reflects the new
    #   value up front, it gets re-set when the radio/mcu sends the "real" value via the "vf"
    #   command.  This means that the wheel might do a little forward/back dance depending
    #   on the speed of the MCU
    #
    def updateATTValue_CB(self):

        self.theRadio.Set_ATT(self.ATT_Jogwheel.get())


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
                self.theRadio.Set_IFS_Level(currentValue)


    def toggleIFS_State(self):
        self.theRadio.Toggle_IFS()

    def updateIFSValue_CB(self):
        self.theRadio.Set_IFS_Level(self.IFS_Jogwheel.get())




########################################################################################
#   End of Callbacks executed by the UX
########################################################################################

#   Radio Commands
########################################################################################
#   These routines are called to tell the MCU that an action has happened in the UX.
#   Typically these should be used by the UX Callbacks
########################################################################################


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
            if self.theRadio.lenMemoryQueue == 0:    # make sure something in queue, otherwise fatal error
                messagebox.showerror("Application Error", "Memory Queue is empty, yet memory value delivered by MCU")
                sys.exit("A fatal internal error occurred")

            memoryCategory = self.theRadio.popMemoryQueue()
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
                            EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.totalSlots]):
                        self.EEPROM_Current_Slot_Freq = 0

                case "Label":               # have a label for a memory channel
                    self.channelsWindow.EEPROM_SetChannelLabel(
                        self.EEPROM_Current_Slot_Label,
                        value)
                    # if self.EEPROM_Current_Slot_Label == 9:
                    #         print("label slot=", self.EEPROM_Current_Slot_Label, "value=", value, sep='*', end='*')
                    self.EEPROM_Current_Slot_Label += 1
                    if (self.EEPROM_Current_Slot_Label ==
                            EEPROM.Mem_Address["channel_Label"][EEPROM.totalSlots]):
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
                            EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.totalSlots]):
                        self.EEPROM_Current_Slot_ShowLabel = 0

                case "MasterCal":          # Got a master cal value
                    self.theRadio.Master_Cal_Setter(str(int(value, 16)))


                case "SSB_BFO":            # Got a SSB BFO value
                    self.theRadio.SSB_BFO_Setter(str(int(value, 16)))

                case "CW_BFO":             # Got a CW BFO Value
                    self.theRadio.CW_BFO_Setter(str(int(value, 16)))

                case "Factory_MasterCal":   #Got a Factory_MasterCal memory value
                    self.theRadio.Factory_Master_Cal_Setter(str(int(value, 16)))

                case "Factory_SSB_BFO":     # Got a Factory SSB BFO memory value
                    self.theRadio.Factory_SSB_BFO_Setter(str(int(value, 16)))

                case "Factory_CW_Speed":    # Got a CW Speed memory value
                    if int(value,16) != 0:
                        cw_speed = str(round(1200/int(value,16)))
                    else:
                        cw_speed = "0"

                    self.theRadio.Factory_CW_Speed_Setter(cw_speed)

                case "Factory_CW_Sidetone":
                    self.theRadio.Factory_CW_Sidetone_Setter(str(int(value, 16)))

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

        value = self.extractValue(buffer, 10, len(buffer) - 3)
        # if self.CurrentDebug:
        #     print("vn get called:", "buffer =", buffer)
        #     print("buffer=", buffer)
        #     if (int(value) == 358):
        #         print("write complete for keychange, mem=", int(value))
        #     elif (int(value) == 28):
        #         print("write complete for new WPM, mem=", int(value))
        #     elif (int(value) == 259):
        #         print("write complete for new RX->TX, mem=", int(value))
        #     elif (int(value) == 258):
        #         print("write complete for new TX->RX, mem=", int(value))
        #     else:
        #         print("memory location write complete, mem=", int(value))





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
        # if self.CurrentDebug:
        #     print("vr called")  # command is rit related
        #     print(buffer)
        pass


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


        if self.channelsWindow != None:      #  Only update frequency if the channel window has been created once
            self.channelsWindow.update_Current_Frequency(self.theVFO_Object.getFormattedPrimaryVFO())
            # self.channelsWindow.update_Current_Frequency(gv.formatFrequency(self.primary_VFO_VAR.get()))


    def switchVFO_Tuning_Optimization(self, value):
        self.tuning_Jogwheel.configure(scroll=True, touchOptimized=value)

    #
    #   The "cc" command indicates a change to a new mode for primary (e.g. USB, LSB, etc.)
    #
    def cc_UX_Set_Primary_Mode(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.primary_Mode_VAR.set(EEPROM.modeNum_To_TextDict[value])
        if self.cwTX_OffsetFlag and (EEPROM.modeNum_To_TextDict[value] == "CWL" or EEPROM.modeNum_To_TextDict[value] == "CWU"):
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
            self.primary_Mode_VAR.set(EEPROM.modeNum_To_TextDict[value])
        else:
            self.theVFO_Object.setSecondaryMode(EEPROM.modeNum_To_TextDict[value])


    #
    #   The "vb" command indicates assignment of vfoB to new frequency
    #
    def vb_UX_Set_VFO_B_Frequency(self, buffer):

        if (self.channelsWindow != None) and (self.channelsWindow.scanRunning):
            return  # ignore the VFO B command during scanning as it can be out of order

        value = self.extractValue(buffer, 10, len(buffer) - 3)


        if (self.vfo_VAR.get()== self.VFO_B):       #update displayed frequency
            print("vb_UX_Set_VFO_B_Frequency", value)
            self.theVFO_Object.setPrimaryVFO(value)
        else:
            self.theVFO_Object.setSecondaryVFO(value)       #need formatted here too

    #
    #   This sets VFO B to a new mode
    #
    def cb_UX_Set_VFO_B_Mode(self, buffer):

        if (self.channelsWindow != None) and (self.channelsWindow.scanRunning):
            return  # ignore the VFO B command during scanning as it can be out of order

        value = self.extractValue(buffer, 10, len(buffer) - 3)

        if (self.vfo_VAR.get()== self.VFO_B):       #update displayed frequency
            self.primary_Mode_VAR.set(EEPROM.modeNum_To_TextDict[value])
        else:
            self.theVFO_Object.secondary_Mode_VAR.set(EEPROM.modeNum_To_TextDict[value])


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


########################################################################################
#   End processing of commands sent by MCU to Screen
########################################################################################


