# from imghdr import test_xbm
import tkinter.ttk as ttk
import tkinter as tk

import mainScreenui as baseui
from settings import settings
from cwSettings import cwSettings, cwSettings

from channels import channels
from cwDecoder import cwDecoder
from frequencySpectrum import frequencySpectrum
from bandScanner import bandScanner
from logQSO import logQSO

from barPlotter import barPlotterBdata
from cwLogger import cwLogger
from QSOLogger import QSOLogger
from Classic_uBITX_Control import Classic_uBITX_Control

import mystyles  # Styles definition module
from time import sleep
import globalvars as gv
from tkinter import messagebox
import sys
import EEPROM as EEPROM
import os


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
        self.startingspectrum = False

        self.theRadio = None            # Object pointer for the Radio
        self.theVFO_Object.attachMainWindow(self)
        self.cwSettingsWindow = None    # Object pointer for the CW Settinge Window
        self.settingsWindow = None      # Object pointer for the General Settings Window
        self.channelsWindow = None      # object pointer for the Memory-> VFO Window
        self.logQSOWindow = None
        self.spectrumWindow = None       #object point for the SpectrumScan Window
        self.consumerSpectrumdata = None #Object pointer to the current consumer of spectrum data

        self.bandScannerWindow = None   # object pointer to the band scanner window
        self.consumerDSPdata = self     # object pointer to the object receiving DSP data
                                        # This could be:
                                        # "self" in the case where the DSP graph is displayed in the main window
                                        # or could point to Spectrum, CW Decode or Band scan if those windows
                                        # are active
        self.mainScreenPlotter = None   # Plot object for main window
        self.mainScreenCW_logger = None # CW display for the main window
        self.QSOLogger_Object = None    # points to the object for the QSO logger

        self.frequencyDecodeScale = None
        self.frequencySigValue = None
        self.frequencyPlotcwToneScale = 10          # default implies 10*50 + 300
        self.frequencyPlotcwToneValue = 800

        self.frequencySpectrumMode = "FreqScan"     # start with the frequency scan unless DSP EEPROM says otherwise when
                                                    # the eeprome data for the dsp is fetched. See call in initUX

        self.DSPFound = False           # No DSP until proven by returning info at startup

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



        self.lastPWRSWR_Reading = None              # tracks what was the last PWR/SWR reading received

        #
        #   Get the images for the 4 states of the VFO tuning buttons
        #
        self.arrow_down_normal = gv.get_image(gv.DOWNARROWBUTTONNORMAL)
        self.arrow_down_pressed = gv.get_image(gv.DOWNARROWBUTTONPRESSED)
        self.arrow_down_disabled = gv.get_image(gv.DOWNARROWBUTTONDISABLED)

        self.arrow_up_normal = gv.get_image(gv.UPARROWBUTTONNORMAL)
        self.arrow_up_pressed = gv.get_image(gv.UPARROWBUTTONPRESSED)
        self.arrow_up_disabled = gv.get_image(gv.UPARROWBUTTONDISABLED)




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

    def savePortHandle(self, portHandle):
        self.portHandle = portHandle

    def initUX(self):
        self.theVFO_Object.initVFO(self.theRadio)

        self.place(x=0, y=0)  # place the mainWindow on the screen

        self.update()       # since we just created the window, need to run update to get width and height calculated

        self.master.geometry(str(self.winfo_width()) + "x" + str(self.winfo_height()) + gv.MAIN_WINDOW_OFFSET)
        self.master.title("CECNextionEmulator - A Nextion Emulator for CEC Firmware running on the uBITX")

        self.master.protocol("WM_DELETE_WINDOW", lambda: self.close_MainWindow())
        self.SWR_PWR_Frame.grid_remove()
        self.mainScreenPlotter = barPlotterBdata(self, self.spectrumCanvas, 63, 70)
        self.mainScreenCW_logger = cwLogger(self, self.decodedCWText, 100)
        self.consumerDSPdata.request_DSP_EEPROM_Data()          # Request data. If we get some, then DSP will be marked as exists

        #
        #   Set up default VFO up/down buttons
        #

        self.downButton = self.downButton_Canvas.create_image(5,5, image=self.arrow_down_normal, anchor="nw")
        # self.downButton_Canvas.image_reference = self.arrow_down_normal

        self.upButton = self.upButton_Canvas.create_image(5,5, image=self.arrow_up_normal, anchor="nw")
        # self.upButton_Canvas.image_reference = self.arrow_up_normal

        if gv.config.get_Logbook_Switch() == "False":               # Disable the Log QSO button on startup if log is disabled
            self.logQSO_Button.configure(state="disabled")


    def close_MainWindow (self):
        self.portHandle.close()         # Close connection to Radio
        self.master.destroy()           # Close Window

    ######################################################################################
    #   This looks up the command processing routing to be called via a dictionary
    #   based on the command type (characters 3,4 in the buffer after prelogue stripped
    ######################################################################################

    def validateKey(self, command, buffer):
        validateFlag = False
        if len(command) != 2:
            print("invalid command", command)
        elif len(buffer) == 0:
            print("empty buffer", buffer)
        elif command.isalnum() == False:
            print("invalid command", command)
        elif buffer[0] != 'p' or buffer[1] != 'm':
            print("invalid command - doesnt start pm", command)
        elif buffer[2] != '.' or buffer[5] != '.':
            print("invalid command - periods in wrong place ")
        elif ((buffer[6] != 'v') or (buffer[7] != 'a') or (buffer[8] != 'l')) and ((buffer[6] != 't') or (buffer[7] != 'x') or  (buffer[8] != 't')):
            print("invalid command - not txt or val")
        elif buffer[9] != '=':
            print("invalid command format, no =")
        elif len(self.extractValue(buffer, 10, len(buffer) - 3)) < 1:
            print("invalid value format, empty")
        elif 'val' in self.extractValue(buffer, 10, len(buffer) - 3):
            print("invalid value format, looks like val")
        else:
            validateFlag = True
        #
        #   Need to figure out how to recover from this type of bad data
        #
        # if validateFlag == False:
        #     self.theRadio.rebootRadio()

        return validateFlag



    def delegate_command_processing(self,command, buffer):
        # print(command, buffer)

        if self.validateKey(command, buffer) == False:
            print(buffer)
            return
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
            case "vm": self.vm_UX_PW_SWR_Level(buffer)
            case "ci": self.ci_UX_IFS_State_Set(buffer)
            case "cx": self.cx_UX_TX_Stop_Toggle(buffer)
            case "cp": self.cp_UX_S_Meter_Value(buffer)  # Related to S meter. search CMD_SMETER
            case "ct": self.ct_UX_RX_TX_Mode(buffer)
            case "al": self.al_UX_S_Meter_Value(buffer)
            case "vv": self.vv_UX_Command_Data(buffer)
            case "vg": self.vg_UX_DSP_Flag(buffer)
            case "sb": self.sb_UX_CW_Decoded_Characters(buffer)
            case "sp": self.sp_UX_DSP_Spectrum_Values(buffer)
            case "xt": self.sp_UX_DSP_Spectrum_Values(buffer)
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


#MJH

    def downButtonPressed_CB(self, event=None):
        if self.downButton_Canvas.cget("state") == "normal":
            self.downButton_Canvas.itemconfig(self.downButton, image=self.arrow_down_pressed)
            self.downButton_Canvas.move(self.downButton, 10, 10)

    def downButtonReleased_CB(self, event=None):
        if self.downButton_Canvas.cget("state") == "normal":
            self.downButton_Canvas.itemconfig(self.downButton, image=self.arrow_down_normal)
            self.downButton_Canvas.move(self.downButton,-10,-10)
            newFreq = self.theVFO_Object.getIntPrimaryVFO()-self.theVFO_Object.getCurrentVFO_Tuning_Rate()
            # print("newFreq=", newFreq)
            self.theRadio.Set_New_Frequency(newFreq)

    def upButtonPressed_CB(self, event=None):
        if self.upButton_Canvas.cget("state") == "normal":
            self.upButton_Canvas.itemconfig(self.upButton, image=self.arrow_up_pressed)
            self.upButton_Canvas.move(self.upButton, 10, 10)

    def upButtonReleased_CB(self, event=None):
        if self.upButton_Canvas.cget("state") == "normal":
            self.upButton_Canvas.itemconfig(self.upButton, image=self.arrow_up_normal)
            self.upButton_Canvas.move(self.upButton, -10, -10)
            newFreq = self.theVFO_Object.getIntPrimaryVFO()+self.theVFO_Object.getCurrentVFO_Tuning_Rate()
            # print("newFreq=", newFreq)
            self.theRadio.Set_New_Frequency(newFreq)


#
#   This function sends to the Radio a notice that a screen lock has been requested
#   The actual locking of the screen waits until the Radio sends back a common
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

    def cwDecode_Button_CB(self, event=None):
        #
        #   Intercept any attempt to start CW Decoding ig DSP is not enabled
        #
        if gv.config.get_DSP_Switch() != "True":
            messagebox.showerror(message="Error: DSP not enabled", detail="Please enable in Machine Settings and try again.\n\n",
                                 parent=self)
        else:
            self.consumerDSPdata = cwDecoder(self.master, self)

    def spectrumScan_Button_CB(self, event=None):
        #
        #   Start CW Scanner Window
        #
        self.theRadio.Set_Spectrum_Mode(94)
        self.consumerSpectrumdata = frequencySpectrum(self.master, self, self.theVFO_Object.getIntPrimaryVFO())

    def bandScan_Button_CB(self, event=None):
        #
        #   Start BandScanner Window
        #
        self.theRadio.Set_Spectrum_Mode(94)
        self.consumerSpectrumdata = bandScanner(self.master, self)

    def logQSO_CB(self):
        # print("logQSO_CB")
        self.logQSOWindow = logQSO(self.master, self)




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
            print("correcting for mal formed s-meter commend", buffer, "setting s-meter to", value)
            self.s_meter_Progressbar_VAR.set(int(value))
        else:
            print("another weird malformed command, buffer =", buffer)
    #
    #   This command provides Nextion with the Power and SWR levels
    #   PWR is sent first, followed by the SWR second
    #
    def vm_UX_PW_SWR_Level(self, buffer):
        if gv.config.get_PWR_SWR_Switch() == "True":
            value = self.extractValue(buffer, 10, len(buffer) - 3)
            adjustedValue = int(value)/100

            if self.lastPWRSWR_Reading == None or self.lastPWRSWR_Reading == "SWR":
                self.lastPWRSWR_Reading = "PWR"
                factorPWR = round(adjustedValue/float(gv.config.get_PWR_Factor()),1)              # 3.91
                self.PWR_Value_VAR.set(str(factorPWR).replace(".", gv.config.get_NUMBER_DELIMITER()))
            else:
                self.lastPWRSWR_Reading = "SWR"
                factorSWR=round(adjustedValue / float(gv.config.get_SWR_Factor()), 1)   # 2,95
                if factorSWR < 1.0 or factorSWR > 2.9:
                    self.SWR_Label.configure(style="Heading3bRed.TLabel")
                    self.SWR_Value.configure(style="Heading4bRed.TLabel")
                else:
                    self.SWR_Label.configure(style="Heading3b.TLabel")
                    self.SWR_Value.configure(style="Heading4b.TLabel")

                self.SWR_Value_VAR.set(str(factorSWR).replace(".",gv.config.get_NUMBER_DELIMITER()))


    def vv_UX_Command_Data(self, buffer):

        #
        # saving this data because dont know what to do with it until next command
        # could be retrieving EEPROM DSP settings to screen dimming or ?
        #

        self.vv_Command_Buffer = self.extractValue(buffer, 10, len(buffer) - 3)
        # print("Received VV data", self.vv_Command_Buffer, "len=", len(self.vv_Command_Buffer))


    def vg_UX_DSP_Flag(self, buffer):
        commandType = self.extractValue(buffer, 10, len(buffer) - 3)
        # print("vg_UX_DSP_Flag Received:", commandType)
        #
        #   Dsp data is weird. You get a "vv" command with the data followed by a "vg" with
        #   the command to send the "vv" buffer that you received previously.
        #
        self.process_DSP_EEPROM_Data(self.vv_Command_Buffer)


    def sb_UX_CW_Decoded_Characters(self, buffer):
        print("Decoded CW Characters", buffer)
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        self.consumerDSPdata.process_CWDecoded_Data(value)


    def sp_UX_DSP_Spectrum_Values(self, buffer):
        if buffer[3] == "x" and buffer[4] == "t":         #error catch for malformed spectrum responses
            value = self.extractValue(buffer, 6, len(buffer) - 3)
            # print("fixing malformed p., value =", value)
        else:
            value = self.extractValue(buffer, 10, len(buffer) - 3)
        # print("buffer=", buffer)
        # print("value=", value)
        # if self.consumerDSPdata
        self.consumerDSPdata.process_Spectrum_Data(value)

    def highlightCWorSpectrumBoxes(self, flag):
        self.mainScreenCW_logger.clearLog()
        self.mainScreenPlotter.clearCanvas()

        if flag:
            if self.frequencySpectrumMode == "FreqScan":
                self.spectrumCanvas.configure(
                    highlightbackground="white",
                    highlightcolor="white")
                self.decodedCWText.configure(
                    highlightbackground="gray",
                    highlightcolor="gray")
                # self.mainScreenCW_logger.clearLog()
                return
            elif self.frequencySpectrumMode == "CWDecode":
                self.spectrumCanvas.configure(
                    highlightbackground="gray",
                    highlightcolor="gray")
                self.decodedCWText.configure(
                    highlightbackground="white",
                    highlightcolor="white")
                # self.mainScreenPlotter.clearCanvas()
                return

        self.decodedCWText.configure(
            highlightbackground="gray",
            highlightcolor="gray")
        self.spectrumCanvas.configure(
            highlightbackground="gray",
            highlightcolor="gray")
        # self.mainScreenCW_logger.clearLog()
        # self.mainScreenPlotter.clearCanvas()

    def process_Spectrum_Data(self, buffer):
        #
        #   If the DSP had been previously enabled, it can be generating data before
        #   the "consumer" in the mainscreen has been started. This just throws this data
        #   away until it is ready
        #
        # print("mainscreen Processing Spectrum Data", buffer)
        if self.mainScreenPlotter != None:
            self.mainScreenPlotter.process_Data(buffer)


    def process_CWDecoded_Data(self, buffer):
        print("Processing CW Data for main window", buffer)
        #
        #   If the DSP had been previously enabled, it can be generating data before
        #   the "consumer" in the mainscreen has been started. This just throws this data
        #   away until it is ready
        #

        if self.mainScreenCW_logger!= None:
            self.mainScreenCW_logger.process_CWDecoded_Data(buffer)

    def process_DSP_EEPROM_Data(self, buffer):
        # print("Processing DSP Data for main window", buffer)
        byteList = int(buffer).to_bytes(4, 'little')
        # print("process_DSP_Data", byteList)

        if int(buffer) < 0xffffff:  # only a 3 hex byte number
            self.DSPFound = True


            # print("main window eeprom values returned")
            # print(hex(int(buffer)))
            # print("main window decodescale*10=", byteList[0])
            # print("main window useDSPFlag=", byteList[1])

            self.frequencyDecodeScale = int(byteList[0] / 10)

            if byteList[1] == 1 and gv.config.get_DSP_Switch() == "False":          # configuration file/option says no, DSP says yes...
                messagebox.showwarning(message="Configuration Mismatch!", detail="Configuration file disables DSP while DSP believes it is active.\n\n" +
                    "Updating configuration file to Enable DSP. You can change this in Machine Settings.", parent=self)
                gv.config.set_DSP_Switch("True")
            elif byteList[1] == 0 and gv.config.get_DSP_Switch() == "True":         # configuration file says yes, DSP says no
                messagebox.showwarning(message="Configuration Mismatch!", detail="Configuration file enables DSP while DSP is inactive.\n\n" +
                    "Updating configuration file to Disable DSP. You can change this in Machine Settings.", parent=self)
                gv.config.set_DSP_Switch("False")
            else:
                pass # configuration file and DSP agree, do nothing

            if byteList[2] == 95:
                self.frequencySpectrumMode = "FreqScan"
            elif byteList[2] >= 100 and byteList[2] < 146:          # in CW mode
                self.frequencyPlotcwToneScale = int(byteList[2] - 100)
                self.frequencyPlotcwToneValue = ((byteList[2]-100)*50)+300
                self.frequencySpectrumMode = "CWDecode"

            #
            #   Now that we know which mode we are in, set white boundaries around the cw or spectrum areas
            #   appropriately and clear the areas to start fresh
            #
            self.highlightCWorSpectrumBoxes(True)

            # print("eeprom fetch:", hex(int(buffer)))

    def request_DSP_EEPROM_Data(self):
        #
        # Request DSP data stored in EEPROM
        self.theRadio.Req_DSP_EEPROM_Settings()
    #
    #   Indicates a switching of RX/TX mode. 1=TX, 0=RX
    #
    def ct_UX_RX_TX_Mode(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)
        if value == "1":  #going into transmit mode
            self.theVFO_Object.setTXButtonState()
            if gv.config.get_PWR_SWR_Switch() == "True":            # If PWR/SWR Switch is off display nothing
                self.SWR_PWR_Frame.grid()

        else:
            self.theVFO_Object.setRXButtonState()
            #
            #   the self.master.state('normal') is a little magic that is needed on macos to make sure the
            #   frame really disappears. Only need to schedule this if PWR/SWR switch is on.
            #
            if gv.config.get_PWR_SWR_Switch() == "True":
                self.master.after(2000, lambda: [self.SWR_PWR_Frame.grid_remove(), self.master.state('normal')])



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
            # print("sh_UX_Get_Memory", self.theRadio.lenMemoryQueue())
            if self.theRadio.lenMemoryQueue() == 0:    # make sure something in queue, otherwise fatal error
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

                case "Spectrum_Scan":
                    # print("Spectrum_Scan", self.theRadio.lenMemoryQueue(), buffer)
                    self.consumerSpectrumdata.process_Spectrum_Data(value)

                case _:
                    # print("case=",memoryCategory)
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
        self.downButton_Canvas.configure(state="disabled")
        self.downButton_Canvas.itemconfig(self.downButton,image=self.arrow_down_disabled)

        self.upButton_Canvas.configure(state="disabled")
        self.upButton_Canvas.itemconfig(self.upButton, image=self.arrow_up_disabled)

        self.theVFO_Object.setVFOUXState("disabled")
        self.cwDecode_Button.configure(state="disabled")
        self.spectrumScan_Button.configure(state="disabled")
        self.bandScan_Button.configure(state="disabled")

        self.logQSO_Button.configure(state="disabled")



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

        self.downButton_Canvas.configure(state="normal")
        self.downButton_Canvas.itemconfig(self.downButton, image=self.arrow_down_normal)
        self.upButton_Canvas.configure(state="normal")
        self.upButton_Canvas.itemconfig(self.upButton, image=self.arrow_up_normal)
        self.theVFO_Object.setVFOUXState("normal")
        self.cwDecode_Button.configure(state="normal")
        self.spectrumScan_Button.configure(state="normal")
        self.bandScan_Button.configure(state="normal")

        if gv.config.get_Logbook_Switch() == "True":
            self.logQSO_Button.configure(state="normal")



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
            self.theVFO_Object.setSplitmode("OFF")
        else:
            self.split_Button_On = True
            self.split_Button.configure(style='GreenButton2b.TButton', state="pressed")
            self.theVFO_Object.setSplitmode("ON")
    #
    #   This appears to be a no-op command. If the last rit TX frequency does not equal
    #   the current frequency, this is called to set the VFO to the RIT TX frequency which happens to be
    #   the current vfo setting anyway.
    #
    def vr_UX_Update_RIT_Freq(self, buffer):
        # if self.CurrentDebug:
        print("vr called")  # command is rit related
        print(buffer)
        pass


    def cr_UX_RIT_Toggle(self, buffer):
        if (self.rit_Button_On):
            self.rit_Button_On = False
            self.rit_Button.configure(style='Button2b.TButton', state="normal")
            self.theVFO_Object.setRITmode("OFF")
        else:
            self.rit_Button_On = True
            self.rit_Button.configure(style='GreenButton2b.TButton', state="pressed")
            self.theVFO_Object.setRITmode("ON")

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
        print(value)
        self.theVFO_Object.setPrimaryVFO(value)


        if self.channelsWindow != None:      #  Only update frequency if the channel window has been created once
            self.channelsWindow.update_Current_Frequency(self.theVFO_Object.getFormattedPrimaryVFO())
            # self.channelsWindow.update_Current_Frequency(gv.formatFrequency(self.primary_VFO_VAR.get()))

    #
    #   The "cc" command indicates a change to a new mode for primary (e.g. USB, LSB, etc.)
    #
    def cc_UX_Set_Primary_Mode(self, buffer):
        value = self.extractValue(buffer, 10, len(buffer) - 3)


        if value == '':
            print("cc_UX_Set_Primary_Mode key error, buffer=", buffer)
        self.primary_Mode_VAR.set(EEPROM.modeNum_To_TextDict[value])
        if self.cwTX_OffsetFlag and (EEPROM.modeNum_To_TextDict[value] == "CWL" or EEPROM.modeNum_To_TextDict[value] == "CWU"):
            #
            #   We are showing the TX frequency on the VFO so need to offset it
            #
            self.theVFO_Object.set_CW_OffsetforTX("ON")
        else:
            self.theVFO_Object.set_CW_OffsetforTX("OFF")


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

        if value == '4pm.vb.val=100980':
            print("ca_UX_Set_VFO_A_Mode error 4pm.vb.val=100980, buffer:", buffer)


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
        if value == '':
            print("ck_UX_Set_CW_Key_Type error, buffer:", buffer)
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


