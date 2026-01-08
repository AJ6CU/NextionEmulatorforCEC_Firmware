#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import theVFOui as baseui
import globalvars as gv


#
# Manual user code
#

class theVFO(baseui.theVFOUI):
    def __init__(self, master=None, **kw):
        
        super().__init__(master, **kw)

        self.rate_selection = {
            0: self.tuning_Preset_Menubutton,
            1: self.digit1_Highlight_Label,
            2: self.digit2_Highlight_Label,
            3: self.digit3_Highlight_Label,
            4: self.digit4_Highlight_Label,
            5: self.digit5_Highlight_Label,
            6: self.digit6_Highlight_Label,
            7: self.digit7_Highlight_Label
        }

        self.DigitPos_to_Powers_of_Ten = {
            0: 0,
            1: 10,
            2: 100,
            3: 1000,
            4: 10000,
            5: 100000,
            6: 1000000,
            7: 10000000
        }

        self.theRadio = None
        self.virtualDial = None                     # pointer to the jogwheel (vfo dial)
        self.mainWindow = None

        self.currentDigitPos = 0                    # Position of digit in VFO being edited
        self.currentVFO_Tuning_Rate = 0
        self.stop_Button_On = False                 # Emergency stop all tx
        
        #
        #   Primary VFO Variables
        #

        self.PrimaryVFO = 0                         # This is the integer version of the actual VFO with no offset
                                                    # for CW TX mode. It also does not contain any delimiters (it is an
                                                    # Integer!)
        
        self.intDisplayedPrimaryVFO = 0             # This is an integer version of the current VFO that includes
                                                    # any offsets for CW TX mode. It is an integer so does not
                                                    # contain any delimiters
        self.strDisplayedPrimaryVFO = None          # This is a VFO that currently appears on the screen.
                                                    # It includes any TX offsets as well as the current delimiter

        #
        #   Secondary VFO Variables
        #
        self.secondary_VFO = 0                      # This is the integer version of the secondart VFO with no offset
                                                    # for CW TX mode. It also does not contain any delimiters (it is an
                                                    # Integer!)

        # self.strDisplayedSecondaryVFO = None        # This is the secondary VFO that currently appears on the screen.
        #                                             # It includes any TX offsets as well as the current delimiter
        
        self.tone = 0                               # Current CW Tone value in HZ
        self.TXfreqOffset = 0                       # used to save the offset on the main dial. Only non-zero for CWL/CWU
        self.cwTX_Tweak = 0                         # A user can add an additional tweak on the offset as stored in eeprom
                                                    # This is not really supported here, but coded in for possible
                                                    # future use.


        self.saved_tuning_Preset_Selection = None       # This is a tristate variable.
                                                        # If None, this means we are in
                                                        # Preset mode.
                                                        # When NOT None, this saves the
                                                        # Preset selection value from the
                                                        # set of radiobuttons for the presets

        self.update_Tuning_Preset_Menubutton_Label = True


        #
    #   This routine is called to finish some inits that have to be done after other values (e.g. current machine state, eeprom)
    #   have been read in
    #
    def initVFO(self, radio):

        self.theRadio = radio


        #
        #   The CW Tone is read in after the initial frequency is initialized by the radio. So if we are operating
        #   in TX offset mode, then need to re-set the frequency to use the correct CW Tone value
        #
        if self.TXfreqOffset != 0:
            self.offsetVFOforTX(True)

        self.setVirtualDialRateMultiplier()         # set the multiplier for each change in virtual dial
        self.setTuningMultiplierLabel()             # set the Label text for the Tuning Select Button
        self.manage_Tuning_Mode(self.currentDigitPos, True)    # turn on the virtual "LED" below the vfo digit


        self.digit_delimiter_primary_VFO_VAR.set(gv.config.get_NUMBER_DELIMITER())

        gv.config.register_observer("NUMBER DELIMITER", self.reformatVFO)
        # gv.config.register_observer("CW Tone", self.setCWTone)


    #
    #   This function defines how many Hz the primary frequency changes for every change of one unit in the virtual
    #   dial (jogwheel)
    #
    def setVirtualDialRateMultiplier(self):
        #
        #   Set the frequency multiplier
        #
        self.currentVFO_Tuning_Rate = self.DigitPos_to_Powers_of_Ten[self.currentDigitPos]
        #
        #   Special case 0, which is the current value of the preset
        #
        if (self.currentVFO_Tuning_Rate == 0):
            if self.tuning_Preset_Label_VAR.get() == "Direct Tune":
                self.mainWindow.Radio_Set_Tuning_Preset(1)
            else:
                self.currentVFO_Tuning_Rate = int(self.tuning_Preset_Label_VAR.get())
    #
    #   The Label on the Tuning Select Button (just above the virtual Dial), should reflect
    #   the current multiplier for every notch change in the virtual Dial. This
    #   routine makes sure that the Label of this button is correct.
    #
    def setTuningMultiplierLabel(self):
        if (self.currentVFO_Tuning_Rate < 1000):
            multiplier_string = str(int(self.currentVFO_Tuning_Rate)) + "Hz"
        elif (self.currentVFO_Tuning_Rate < 1000000):
            multiplier_string = str(int(self.currentVFO_Tuning_Rate / 1000)) + "KHz"
        else:
            multiplier_string = str(int(self.currentVFO_Tuning_Rate / 1000000)) + "MHz"

        #   Now set the text on the multiplier button to reflect the new rate
        #
        self.tuning_Multiplier_VAR.set("Tuning Factor\nx" + multiplier_string)

    #
    #*********Routines that manage the virtual LED's below the digits of the VFO
    #
    #   There are two routines here. The lower level one is "manage_Tuning_mode" which is called
    #   on an individual light to turn on or off. It also handles the situation where we have moved
    #   back to digit "0" which is reserved for the classic preset tuning.
    #
    #   The second routine "updateLEDTuningHighlight" manages the transistion from one LED to the next
    #   and uses "manage_Tuning_Mode" to do the hard work.
    #

    #
    #   Ensures that all the proper labels are set based on the mode of the Tuning Select Button.
    #   There is some trickery going on here as "light" can be between 0 and 7. The "0" means that
    #   we are using the standard dial preset mode. A "1" means the 10Hz digit, "2" means, 100Hz, etc.
    #   KD8CEC does not allow tuning in 1Hz's increments which means the "0" digit can be repurposed
    #   for implying the use of the "classic" presets.
    #
    #   The "turnOn" parameter is used to turn on or off the respective LED indicator (or Button)

    def manage_Tuning_Mode(self, lightNum, turnOn):

        #*****Convenience Routine*******
        #
        #   This convenience routine handles switching between Direct and "Preset" tuning mode
        #   The complexity here comes from the original CEC software using the current
        #   preset-1 (i.e. if Preset 3 was 100 and Preset 2 was 50, and we were on preset 3,
        #   everything below Preset 3 would be zero'ed out. This means to allow direct
        #   tune mode on the tens digit, we must first make the preset the lowest # (i.e. 1)
        #   so that the tens digit is not masked out and turned to zero.
        #   As a result, we need to save the state of the preset when we move to Direct Tune,
        #   and then restore it as we exit Direct Tune and go into Preset mode.
        #   Since the MCU can also force changes in preset, we must temporarily turn off
        #   the updating of the label
        #
        def set_Tuning_Mode(mode):
            if (mode == "direct tune"):
                if (self.saved_tuning_Preset_Selection == None):  # None value indicates we *were* in "direct tune" mode
                    #
                    #   save state prior to going into Direct Mode
                    #
                    ####MJH need to change this to menubutton
                    self.saved_tuning_Preset_Selection = self.tuning_Preset_Label_VAR.get()
                    self.saved_tuning_Preset_VAR = self.tuning_Preset_Label_VAR.get()
                    #
                    #   Sets label that displays current present with "Direct Tune" string
                    #
                    self.tuning_Preset_Label_VAR.set("Direct Tune")
                    #   turn off any changes in the label due to a change in preset coming from the radio
                    self.update_Tuning_Preset_Menubutton_Label = False
                    #   Disable the tuning rate button so selected preset cannot be changed while in direct tune
                    self.tuning_Preset_Menubutton.configure(state='disabled')
                    #
                    #   Select the lowest tuning rate of the presets. The need to do this is the result of the original
                    #   CEC software using the rate preselects to truncate digits below the preset. For example.
                    #   if a preset of 100 was selected, then it would be impossible to set the dial in increments of 20
                    #   or 10 because it would be truncated to lower 100.
                    #
                    self.mainWindow.Radio_Set_Tuning_Preset(1)

            else:  # Switching into pre-set tuning mode and have to restore the state
                if (self.saved_tuning_Preset_Selection != None):  # dont restore unless it was previously saved
                    #   Allow updating of the Label for the selected preset
                    self.update_Tuning_Preset_Menubutton_Label = True
                    #   Restore the saved states
                    self.tuning_Preset_Label_VAR.set(self.saved_tuning_Preset_VAR)
                    self.mainWindow.Radio_Set_Tuning_Preset(int(self.saved_tuning_Preset_Selection))
                    #   Re-enable the button to select a preset
                    self.tuning_Preset_Menubutton.configure(state='enabled')
                    #   indicate the saved states are now invalid
                    self.saved_tuning_Preset_Selection = None

    #*****End Convenience Routine. - Start primary code of function "manage_Tuning_Mode"

        if lightNum == 0:         # This means we are in "classic" preset mode
            if turnOn:
                self.rate_selection[0].configure(style='GreenButton2b.TButton')
                set_Tuning_Mode("preset tune")  # go into preset tune mode
            else:
                self.rate_selection[0].configure(style='Button2b.TButton')
        else:                       # We are toggling one of the digit LED lights
            if turnOn:
                self.rate_selection[lightNum].configure(style='OnLED.TLabel')
                set_Tuning_Mode("direct tune")  # go into direct tune mode
            else:
                self.rate_selection[lightNum].configure(style='OffLED.TLabel')

    #
    #   This routine handles the cycling thru of LED highlights for VFO Digits.
    #   LED 0 indicates the classic tuning preset mode. Otherwise, digits 1-7 indicats
    #   a digit from right (least significant (x10Hz) to left (x10mhz).
    #   It is a loop so when we reach the most signicatint digit, it loops back to 0 and
    #   we are in preset mode.
    #
    def updateLEDTuningHighlight(self, tuning_Digit = None):
        #
        #   First turn off the old LED
        #
        self.manage_Tuning_Mode(self.currentDigitPos, False)
        #
        #   IF increment mode (tuning_Digit == None)
        #   Increment to the next slot and turn its LED on, check for rollover, otherwise go directly to the indicated
        #   digit
        #
        if tuning_Digit == None:
            self.currentDigitPos += 1
            if self.currentDigitPos > len(self.rate_selection) - 1:
                self.currentDigitPos = 0
        else:
            self.currentDigitPos = tuning_Digit

        self.manage_Tuning_Mode(self.currentDigitPos, True)

    #
    #******End of routines that manage the virtual LED's below each of the digits of the VFO
    #

    def attachMainWindow(self,mainWindow):
        self.mainWindow = mainWindow

    def attachDial(self,dial):
        self.virtualDial = dial


    def setDelimiter(self, delimiter):
        pass

    def setFirmwareVersion(self, firmwareVersion):
        self.firmwareVersion_VAR.set(firmwareVersion)

    def setCallsign(self, callsign):
        self.callSign_VAR.set(callsign)


    # def setCWTone(self, tone):
    #     self.tone = int(tone)

    def setTuningPreset(self, tuningPreset, value):
        pass

    #
    #   External routines to set states of Buttons
    #
    def settoggleStopButtonState(self):
        if (self.stop_Button_On):
            self.stop_Button_On = False
            self.stop_Button.configure(style='Button2b.TButton', state="normal")
        else:
            self.stop_Button_On = True
            self.stop_Button.configure(style='RedButton2b.TButton', state="pressed")

    def setRXButtonState(self):
        self.tx_Status_Light_Label.configure(state="disabled")
        self.rx_Status_Light_Label.configure(state="normal")
    def setTXButtonState(self):
        self.tx_Status_Light_Label.configure(state="normal")
        self.rx_Status_Light_Label.configure(state="disabled")
    #
    #   External routine to enable/disable UX control
    #
    def setVFOUXState(self, newState):
        self.tuning_Multiplier_Button.configure(state=newState)
        self.tuning_Preset_Menubutton.configure(state=newState)

    #
    #   Get/Set routines
    #
    def getPrimaryVFO(self):
        pass
    def getIntPrimaryVFO(self):
        return self.intDisplayedPrimaryVFO

    def getFormattedPrimaryVFO(self):
        return self.strDisplayedPrimaryVFO

    def setPrimaryVFO(self, value):
        self.PrimaryVFO = int(value)
        self.update_VFO_Display(self.PrimaryVFO, self.TXfreqOffset)
        self.updateJogTracking()

    def getSecondaryVFO(self):
        pass
    def getFormattedSecondaryVFO(self):
        pass
    def setSecondaryVFO(self, value):
        self.SecondaryVFO = int(value)
        self.secondary_VFO_Formatted_VAR.set(gv.formatFrequency(self.SecondaryVFO, self.TXfreqOffset))

    def setSecondaryMode(self, mode):
        self.secondary_Mode_VAR.set(mode)

    def getCurrentVFO_Tuning_Rate(self):
        return self.currentVFO_Tuning_Rate


    def setVFOA(self):
        pass
    def setVFOB(self):
        pass

    def toggleVFO(self):

        saveSecondary_VFO = self.secondary_VFO
        saveSecondary_Mode = self.secondary_Mode_VAR.get()

        # self.secondary_VFO_VAR.set(gv.unformatFrequency(self.primary_VFO_Formatted_VAR))
        self.secondary_VFO_Formatted_VAR.set(gv.formatFrequency(self.PrimaryVFO))
        # self.secondary_VFO_Formatted_VAR.set(self.strDisplayedPrimaryVFO)
        # self.secondary_VFO_Formatted_VAR.set(gv.formatFrequency(self.primary_VFO_VAR.get()))
        # self.secondary_VFO_Formatted_VAR.set(self.primary_VFO_Formatted_VAR.get())
        # self.secondary_VFO_Formatted_VAR.set(gv.formatFrequency(gv.unformatFrequency(self.primary_VFO_Formatted_VAR.get()), self.freqOffset))
        self.secondary_Mode_VAR.set(self.mainWindow.primary_Mode_VAR.get())

        self.setPrimaryVFO(saveSecondary_VFO)

        # self.primary_VFO_Formatted_VAR.set(gv.formatFrequency(saveSecondary_VFO, self.freqOffset))
        # self.update_VFO_Display(self.primary_VFO_VAR.get(), self.freqOffset)

        self.mainWindow.primary_Mode_VAR.set(saveSecondary_Mode)

    def setTXOffset(self,offset):
        self.TXfreqOffset = offset

    def getTXOffset(self):
        return self.TXfreqOffset

    def set_Tuning_Preset_5(self,value):
        self.tuning_Preset_Menu.entryconfigure(0,label=value)

    def set_Tuning_Preset_4(self, value):
        self.tuning_Preset_Menu.entryconfigure(1, label=value)
        
    def set_Tuning_Preset_3(self, value):
        self.tuning_Preset_Menu.entryconfigure(2, label=value)
        
    def set_Tuning_Preset_2(self, value):
        self.tuning_Preset_Menu.entryconfigure(3, label=value)
        
    def set_Tuning_Preset_1(self, value):
        self.tuning_Preset_Menu.entryconfigure(4, label=value)
        
    def set_Active_Tuning_Preset(self,value):


        match value:
            case "5":
                if (self.update_Tuning_Preset_Menubutton_Label):
                    self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(0, "label"))
                self.currentVFO_Tuning_Rate = int(self.tuning_Preset_Menu.entrycget(0, "label"))

            case "4":
                if (self.update_Tuning_Preset_Menubutton_Label):
                    self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(1, "label"))
                self.currentVFO_Tuning_Rate = int(self.tuning_Preset_Menu.entrycget(1, "label"))

            case "3":
                if (self.update_Tuning_Preset_Menubutton_Label):
                    self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(2, "label"))
                self.currentVFO_Tuning_Rate = int(self.tuning_Preset_Menu.entrycget(2, "label"))

            case "2":
                if (self.update_Tuning_Preset_Menubutton_Label):
                    self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(3, "label"))
                self.currentVFO_Tuning_Rate = int(self.tuning_Preset_Menu.entrycget(3, "label"))

            case "1":
                if (self.update_Tuning_Preset_Menubutton_Label):
                    self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(4, "label"))
                self.currentVFO_Tuning_Rate = int(self.tuning_Preset_Menu.entrycget(4, "label"))




        self.setVirtualDialRateMultiplier()  # set the multiplier for each change in virtual dial
        self.setTuningMultiplierLabel()  # set the Label text for the Tuning Select Button
        self.manage_Tuning_Mode(self.currentDigitPos, True)  # turn on the virtual "LED" below the vfo digit


    def reformatVFO(self, value):

            self.digit_delimiter_primary_VFO_VAR.set(value)
            if value == ",":
                old_value = "."
            else:
                old_value = ","

            self.RX_VFO_VAR.set(self.RX_VFO_VAR.get().replace(old_value,value))
            self.secondary_VFO_Formatted_VAR.set(self.secondary_VFO_Formatted_VAR.get().replace(old_value,value))

            self.digit_delimiter_primary_VFO_VAR.set(value)
            self.update_VFO_Display(int(self.PrimaryVFO), self.TXfreqOffset)
            # # self.update_VFO_Display(self.primary_VFO_VAR.get(), self.TXfreqOffset)
            # self.secondary_VFO_Formatted_VAR.set(gv.formatFrequency(self.secondary_VFO_Formatted_VAR.get().replace(self.digit_delimiter_primary_VFO_VAR.get(),"")))
            # self.RX_VFO_VAR.set(gv.formatFrequency(self.RX_VFO_VAR.get().replace(gv.config.get_NUMBER_DELIMITER(),"")))



    #   ****Start Callbacks****


    #
    #   When the tuning_Multiplier is clicked, it cycles through the digits in the VFO to allow them to be
    #   manually tuned. The initial case the use of the preset tuning cycles is used, much in the same
    #   way it would be if you are adjusting the physical tuning knob.
    #
    def tuning_Multiplier_Button_CB(self):
        #
        #   First turn off the old LED, turn on new LED indicator for tuning
        #
        self.updateLEDTuningHighlight()
        #
        #   Update rate multiplier for jogwheel
        #
        self.setVirtualDialRateMultiplier()
        #
        #   set tracking variables for new rate change
        #
        self.updateJogTracking()
        #
        #   Update the label on the tuning button selector
        #
        self.setTuningMultiplierLabel()

    #
    #   This routine is a convenience routine to update the tuning mode. It
    #   is involved by the individual callbacks of each digit which follow it
    #

    def primary_vfo_direct_digit_set(self, digit):
        #
        #   First turn off the old LED, turn on new LED indicator for tuning
        #
        self.updateLEDTuningHighlight(digit)
        #
        #   Update rate multiplier for jogwheel
        #
        self.setVirtualDialRateMultiplier()
        #
        #   set tracking variables for new rate change
        #
        self.updateJogTracking()
        #
        #   Update the label on the tuning button selector
        #
        self.setTuningMultiplierLabel()

    def primary_vfo_10mhz_CB(self, event=None):
        self.primary_vfo_direct_digit_set(7)

    def primary_vfo_1mhz_CB(self, event=None):
        self.primary_vfo_direct_digit_set(6)

    def primary_vfo_100khz_CB(self, event=None):
        self.primary_vfo_direct_digit_set(5)

    def primary_vfo_10khz_CB(self, event=None):
        self.primary_vfo_direct_digit_set(4)

    def primary_vfo_1khz_CB(self, event=None):
        self.primary_vfo_direct_digit_set(3)

    def primary_vfo_100hz_CB(self, event=None):
        self.primary_vfo_direct_digit_set(2)

    def primary_vfo_10hz_CB(self, event=None):
        self.primary_vfo_direct_digit_set(1)

    def tuning_Preset_5_CB(self):
        self.mainWindow.Radio_Set_Tuning_Preset(5)
        self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(0,"label"))

    def tuning_Preset_4_CB(self):
        self.mainWindow.Radio_Set_Tuning_Preset(4)
        self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(1,"label"))

    def tuning_Preset_3_CB(self):
        self.mainWindow.Radio_Set_Tuning_Preset(3)
        self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(2,"label"))

    def tuning_Preset_2_CB(self):
        self.mainWindow.Radio_Set_Tuning_Preset(2)
        self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(3,"label"))

    def tuning_Preset_1_CB(self):
        self.mainWindow.Radio_Set_Tuning_Preset(1)
        self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(4,"label"))


    #
    #   Controls visability of the RX freq display. It is only visable in the case where we are in CW and the
    #   user has selected to show the TX frequency on the primary display. This is just a "reminder" for the user
    #   of which frequency is being listen on.

    def RX_VFO_Visability (self, RX_Frame_Visible = False):
        if RX_Frame_Visible:
            self.RX_VFO_Frame.pack(side="left")
        else:
            self.RX_VFO_Frame.pack_forget()

    #
    #   Manages whether the primary VFO is showing the TX frequency (in the case of being in CW mode) or the RX
    #   frequency.
    #   In the case of a CWL or CWU, it calculates the offset being either + (CWL) or - (CWU).
    #

    def offsetVFOforTX (self, flag):

        tone = int(self.mainWindow.tone_value_VAR.get())
        if flag:            # indicates we need to offset VFO by the Tone and Tweak
            self.Tx_Freq_Alert_VAR.set("TX Freq")
            self.RX_VFO_Visability(True)        # make the RX frequency frame visible
            if self.mainWindow.primary_Mode_VAR.get() == 'CWL':
                self.TXfreqOffset  = tone + self.cwTX_Tweak

            elif self.mainWindow.primary_Mode_VAR.get() == 'CWU':
                self.TXfreqOffset =  -(tone + self.cwTX_Tweak)
        else:
            self.Tx_Freq_Alert_VAR.set("       ")
            self.TXfreqOffset = 0
            self.RX_VFO_Visability(False)       # Turn off the RX frequency window

        self.update_VFO_Display(self.PrimaryVFO, self.TXfreqOffset)

        self.updateJogTracking()                # Since changed flag, may need to reset jogwheel position



    def update_VFO_Display (self, vfo, offset=0 ):
        self.intDisplayedPrimaryVFO = vfo + offset


        paddedVFO = str(self.intDisplayedPrimaryVFO).rjust(8)
        self.strDisplayedPrimaryVFO = gv.formatFrequency(paddedVFO)

        self.digit0_primary_VFO_VAR.set(paddedVFO[7])
        self.digit1_primary_VFO_VAR.set(paddedVFO[6])
        self.digit2_primary_VFO_VAR.set(paddedVFO[5])
        self.digit3_primary_VFO_VAR.set(paddedVFO[4])
        self.digit4_primary_VFO_VAR.set(paddedVFO[3])
        self.digit5_primary_VFO_VAR.set(paddedVFO[2])
        self.digit6_primary_VFO_VAR.set(paddedVFO[1])
        self.digit7_primary_VFO_VAR.set(paddedVFO[0])

        self.RX_VFO_VAR.set(gv.formatFrequency(vfo))     # Update RX freq reminder displayed if TX Freq displayed





    def updateJogTracking(self,newBaseline=True):
        # if self.DeepDebug:
        #     print("updating jogwheel, digit=", self.getVFOdigit())
        #     print("current jogwheel position =", self.tuning_Jogwheel.get())

        self.virtualDial.set(self.getVFOdigit(), False)
        if(newBaseline):
            self.baselineJogValue = self.virtualDial.get()

    #
    #   this function returns a single digit integer that occupies the position
    #   corresponding to the current selected rate.
    #   Conveniently, presets are allocated to position 0,
    #   which is always zero in CEC and not setable
    #

    def getVFOdigit(self):
        #
        #   find_msd_position is a helper function that finds the index of the most significant digit from the right
        #   in a string representation of a number.
        #
        #   Returns:
        #     int or None: The index of the most significant digit, or None if no non-zero digit is found.

        def find_msd_position(number_string):

            reversed_number_string = number_string[::-1].strip()  # neat trick to reverse a string

            for i, char in enumerate(reversed_number_string):
                if char.isdigit() and char != '0':
                    return i
            return None

        #
        #   Actual function code begins here
        #

        currentVFO = str(
            self.intDisplayedPrimaryVFO)  # Get a string of the VFO currently displayed (including offsets)

        #
        #   reverse it so that least significant is in position 0
        #
        reversedVFO = currentVFO[::-1].strip()  # neat trick to reverse a string

        #
        #   pad it on right with zeros so we have 8 characters
        #
        reversedVFO = reversedVFO.ljust(8, "0")

        if (self.currentDigitPos == 0):
            if (self.currentVFO_Tuning_Rate != 0):
                pos = find_msd_position(str(self.currentVFO_Tuning_Rate))
                return int(reversedVFO[pos])
            else:
                return int(reversedVFO[2])
        else:
            #
            #   now we can just return the character of the selected rate
            #
            return int(reversedVFO[self.currentDigitPos])


if __name__ == "__main__":
    root = tk.Tk()
    widget = theVFO(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
