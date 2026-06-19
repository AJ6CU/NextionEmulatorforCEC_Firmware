#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk

from PIL.JpegPresets import presets

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
        # self.virtualDial = None                     # pointer to the jogwheel (vfo dial)
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
        self.secondary_VFO = 0                      # This is the integer version of the secondary VFO with no offset
                                                    # for CW TX mode. It also does not contain any delimiters (it is an
                                                    # Integer!)

        
        self.tone = 0                               # Current CW Tone value in HZ
        self.TXfreqOffset = 0                       # used to save the offset on the main dial. Only non-zero for CWL/CWU
        self.TXfreqOffsetSaved = None               # when moving in and out of RIT and Split, need to save this to be later
                                                    # restored
        self.CW_OffsetWasOn = False                 # Needed to track when we need to restore the CW offset because it was turned off
        self.cwTX_Tweak = 0                         # A user can add an additional tweak on the offset as stored in eeprom
                                                    # This is not really supported here, but coded in for possible
                                                    # future use.
        # self.saveLastOffsetFlag = "CW_Off"          # Saves the last offset flag
        self.CW_VFOA_Offset_On = True
        self.CW_VFOAUX_Offset_On = True

        self.saved_tuning_Preset_Selection = None       # This is a tristate variable.
                                                        # If None, this means we are in
                                                        # Preset mode.
                                                        # When NOT None, this saves the
                                                        # Preset selection value from the
                                                        # set of radiobuttons for the presets
        self.saved_tuning_Preset_Label = None

        self.update_Tuning_Preset_Menubutton_Label = True

        self.RITmode = False                        # Saves whether RIT is on or off
        self.SPLITmode = False                      # Saves whether SPLIT mode is on or off



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
            self.set_CW_OffsetforTX("ON")

        self.setRateMultiplier()         # set the multiplier for each change in virtual dial
        self.setTuningMultiplierLabel()             # set the Label text for the Tuning Select Button
        self.setLEDTuningHighlight(self.currentDigitPos, True)    # turn on the virtual "LED" below the vfo digit


        self.digit_delimiter_primary_VFO_VAR.set(gv.config.get_NUMBER_DELIMITER())

        gv.config.register_observer("NUMBER DELIMITER", self.reformatVFO)
        # gv.config.register_observer("CW Tone", self.setCWTone)


    #
    #   This function defines how many Hz the primary frequency changes for every change of one unit click
    #   of the up/down arrows
    #
    def setRateMultiplier(self):
        #
        #   Set the frequency multiplier
        #
        self.currentVFO_Tuning_Rate = self.DigitPos_to_Powers_of_Ten[self.currentDigitPos]
        #
        #   Special case 0, which is the current value of the preset
        #
        if (self.currentVFO_Tuning_Rate == 0):
            if self.tuning_Preset_Label_VAR.get() == "Direct Tune":
                self.theRadio.Set_Tuning_Preset(1)
            else:
                self.currentVFO_Tuning_Rate = int(self.tuning_Preset_Label_VAR.get())

      # The Label on the Tuning Select Button (just to right of tuning preselects), should reflect
      # the current multiplier for every notch change in the virtual Dial. This
      # routine makes sure that the Label of this button is correct.

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
    #   There are three routines here. The lower level one is "set_Tuning_mode". It sets the mode between "direct tune"
    #   and "preset tune". When switching to direct tune, it needs to save the preset state. When switching to
    #   preset tune, it needs to restore the last state
    #
    #   The second routine "setNextLEDTuningHighlight" manages the transistion from one LED to the next. It also detects
    #   changes between direct and preset tuning and calls set_Tuning_mode.
    #
    #   The routine setLEDTuningHighlight deals with actually changing an LED light on or off. This is required
    #   because led(0) is actually the preset value and changing its state requires different styles.
    #
    #   The final two routines are convenince routines used both internally and externally to save/restore the state
    #   of the preset. This is necessary because the original software automatically truncates the digits below it.
    #   For example, if the dial was set for 100hz, then 10hz and 1hz would automatically get truncated to zero.
    #   So when the Virtual Dial is being used on an individual digit, we need to set the preset to the lowest available
    #   preset so that the frequency set by the Virtual dial is not truncated.
    #
    #   These routines are used both for individual dialing for the digits of the vfo as well as when in channel modes and
    #   Frequencies are being manually entered.
    #
    #


    def set_Tuning_Mode(self, mode):
        #
        #   Switching into direct tune mode and must save preset
        #
        if (mode == "direct tune"):
            if (self.saved_tuning_Preset_Selection == None):    # None value indicates we *are* in "preset tune" mode
                                                                # and must save preset state before switching into direct
                #
                #   save state prior to going into Direct Mode
                #
                self.savePresetState()
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
                self.theRadio.Set_Tuning_Preset(1)
        #
        #   Switching into preset tune mode and if a backup exists, restore it
        #
        else:  # Switching into pre-set tuning mode and have to restore the state

            if (self.saved_tuning_Preset_Selection != None):  # dont restore unless it was previously saved

                #   Allow updating of the Label for the selected preset
                self.update_Tuning_Preset_Menubutton_Label = True

                #   Restore the saved states
                self.restorePresetState()
                #   Re-enable the button to select a preset

                self.tuning_Preset_Menubutton.configure(state='enabled')

                #   indicate the saved states are now invalid
                self.saved_tuning_Preset_Selection = None

    #
    #   This routine handles the cycling thru of LED highlights for VFO Digits.
    #   LED 0 indicates the classic tuning preset mode. Otherwise, digits 1-7 indicats
    #   a digit from right (least significant (x10Hz) to left (x10mhz).
    #   It is a loop so when we reach the most signicatint digit, it loops back to 0 and
    #   we are in preset mode.
    #
    def setNextLEDTuningHighlight(self, lightnum=None):


        #
        #   Save current light number. This is needed to see if we transistioned into a different mode (direct vs preset)
        #
        savedLightNum = self.currentDigitPos

        self.setLEDTuningHighlight(self.currentDigitPos, False)
        #
        #   IF increment mode (tuning_Digit == None)
        #   Increment to the next slot and turn its LED on, check for rollover, otherwise go directly to the indicated
        #   digit
        #
        if lightnum == None:
            self.currentDigitPos += 1
            if self.currentDigitPos > len(self.rate_selection) - 1:
                self.currentDigitPos = 0
        else:
            self.currentDigitPos = lightnum

        self.setLEDTuningHighlight(self.currentDigitPos, True)

        if self.currentDigitPos == 0:
            # switched into preset mode
            self.set_Tuning_Mode("preset mode")
        elif savedLightNum == 0 and self.currentDigitPos != 0:
            # switched into direct mode
            self.set_Tuning_Mode("direct tune")
        else:
            # no mode change
            pass

    def setLEDTuningHighlight(self, lightNum, turnOn = True):
        #
        #   First turn off the old LED
        #
        if lightNum == 0:         # This means we are in "classic" preset mode

            if turnOn:
                self.rate_selection[0].configure(style='GreenButton2b.TButton')

            else:
                self.rate_selection[0].configure(style='Button2b.TButton')
        else:                       # We are toggling one of the digit LED lights

            if turnOn:
                self.rate_selection[lightNum].configure(style='OnLED.TLabel')
            else:
                self.rate_selection[lightNum].configure(style='OffLED.TLabel')

    def savePresetState(self):
        self.saved_tuning_Preset_Selection = self.get_Active_Tuning_Preset()
        self.saved_tuning_Preset_Label = self.tuning_Preset_Label_VAR.get()

    def restorePresetState(self):
        self.tuning_Preset_Label_VAR.set(self.saved_tuning_Preset_Label)
        self.theRadio.Set_Tuning_Preset(self.saved_tuning_Preset_Selection)
        self.set_Active_Tuning_Preset(self.saved_tuning_Preset_Selection)
        self.saved_tuning_Preset_Selection = None

    #
    #******End of routines that manage the virtual LED's below each of the digits of the VFO
    #

    def attachMainWindow(self,mainWindow):
        self.mainWindow = mainWindow

    def setFirmwareVersion(self, firmwareVersion):
        self.firmwareVersion_VAR.set(firmwareVersion)

    def setCallsign(self, callsign):
        self.callSign_VAR.set(callsign)


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
    def getIntPrimaryVFO(self):
        return self.intDisplayedPrimaryVFO

    def getFormattedPrimaryVFO(self):
        return self.strDisplayedPrimaryVFO

    def setPrimaryVFO(self, value):
        self.PrimaryVFO = int(value)
        self.update_VFO_Display(self.PrimaryVFO, self.TXfreqOffset)

    def setSecondaryVFO(self, value):
        self.SecondaryVFO = int(value)
        self.secondary_VFO_Formatted_VAR.set(gv.formatFrequency(self.SecondaryVFO, self.TXfreqOffset))

    def setSecondaryMode(self, mode):
        self.secondary_Mode_VAR.set(mode)

    def getCurrentVFO_Tuning_Rate(self):
        return self.currentVFO_Tuning_Rate

    def toggleVFO(self):

        saveSecondary_VFO = self.secondary_VFO
        saveSecondary_Mode = self.secondary_Mode_VAR.get()

        self.secondary_VFO_Formatted_VAR.set(gv.formatFrequency(self.PrimaryVFO))
        self.secondary_Mode_VAR.set(self.mainWindow.primary_Mode_VAR.get())

        self.setPrimaryVFO(saveSecondary_VFO)

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

    #
    #   Returns the preset number in terms of KD8CEC (5-highest to 1-lowest)
    #
    def get_Active_Tuning_Preset(self):
        for i in range(self.tuning_Preset_Menu.index(tk.END)+1):
            if(self.tuning_Preset_Menu.entrycget(i, "label") == self.tuning_Preset_Label_VAR.get()):
                return 5 - i
        return 1            # default to highest resolution if not found

        
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




        self.setRateMultiplier()  # set the multiplier for each change in virtual dial
        self.setTuningMultiplierLabel()  # set the Label text for the Tuning Select Button



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
        self.setNextLEDTuningHighlight()
        #
        #   Update rate multiplier
        #
        self.setRateMultiplier()

        #
        #   Update the label on the tuning button selector
        #
        self.setTuningMultiplierLabel()

    #
    #   This routine is a convenience routine to update the tuning mode. It
    #   is involved by the individual callbacks of each digit which follow it
    #

    def primary_vfo_direct_digit_set(self, digit):

        self.setNextLEDTuningHighlight(digit)
        #
        # #   Update rate multiplier for jogwheel
        #
        self.setRateMultiplier()

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
        self.theRadio.Set_Tuning_Preset(5)
        self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(0,"label"))

    def tuning_Preset_4_CB(self):
        self.theRadio.Set_Tuning_Preset(4)
        self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(1,"label"))

    def tuning_Preset_3_CB(self):
        self.theRadio.Set_Tuning_Preset(3)
        self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(2,"label"))

    def tuning_Preset_2_CB(self):
        self.theRadio.Set_Tuning_Preset(2)
        self.tuning_Preset_Label_VAR.set(self.tuning_Preset_Menu.entrycget(3,"label"))

    def tuning_Preset_1_CB(self):
        self.theRadio.Set_Tuning_Preset(1)
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
    def set_CW_OffsetforTX(self, switch):
        if switch == "ON":
            tone = int(self.mainWindow.tone_value_VAR.get())
            if self.mainWindow.primary_Mode_VAR.get() == 'CWL':
                self.TXfreqOffset = tone + self.cwTX_Tweak

            else:
                # must be true: self.mainWindow.primary_Mode_VAR.get() == 'CWU':
                self.TXfreqOffset = -(tone + self.cwTX_Tweak)
        else:
            self.TXfreqOffset = 0       # Turning off, so just set offset to zero
        #
        #   With offsets now correct, we can update the VFO display
        #
        # if not self.RITmode:
        self.update_VFO_Display(self.PrimaryVFO, self.TXfreqOffset)

        # self.updateVFO_Info("CW", switch)
        self._CW(switch)


    def _CW(self, switch):
        if self.RITmode or self.SPLITmode:
            #
            #   Handle complex situation where CW offset change is happening when either
            #   RIT or SPLIT is on
            if self.RITmode:
                if switch == "ON":
                    # Need to adjust the secondary info TX to reflect new offset
                    print("RIT and then CW")

                    self.RX_VFO_VAR.set(gv.formatFrequency(self.PrimaryVFO+self.TXfreqOffset))

                    # self._saveFreqOffset(True)

                    self.update_VFO_Display(self.PrimaryVFO, self.TXfreqOffset)
                else:
                    print("switch off")
                    #
                    #   Need to update Secondary VFO field since offset has changed
                    #
                    self.RX_VFO_VAR.set(gv.formatFrequency(self.intDisplayedPrimaryVFO))

            if self.SPLITmode:
                # Need to adjust vfo B by TX offset
                pass
        else:
            print("CW Labels", switch)
            #
            # Just a change in Mode. can handle it directly
            #
            self._CW_ManageLabels(switch)


    def _CW_ManageLabels(self,switch):
        if switch == "ON":
            self.Tx_Freq_Alert_VAR.set("TX Freq:")
            self.RX_Freq_VAR.set("RX Freq:")
            self.RX_VFO_Visability(True)  # make the RX frequency frame visible
            #   Note:
            #   Dont need to set the secondary vfo info field because
            #   update_VFO_Display does that automatically except when RIT
            #   is on
        else:
            self.Tx_Freq_Alert_VAR.set("       ")
            self.RX_VFO_Visability(False)  # Turn off the RX frequency window


    def _RIT(self, switch):
        if self.TXfreqOffset != 0 or self.SPLITmode:
            if self.SPLITmode:  # In SPLIT turning on/off RIT
                if switch == "ON":
                    self.RITmode = True  # RIT is being turned on
                    self._RIT_ManageLabels(switch)

                    self.RX_VFO_VAR.set(gv.formatFrequency(self.intDisplayedPrimaryVFO))

                else:
                    self.RITmode = False
                    self._RIT_ManageLabels(switch)


            else:  # CW offset must be on
                if switch == "ON":
                    self.RITmode = True  # RIT is being turned on
                    self.CW_VFOA_Offset_On = False
                    self.CW_VFOAUX_Offset_On = False
                    #
                    #   The current VFO is the TX frequency (VFO+CW offset). Should put the TX (offset TX) in lower
                    #   right INFO area.
                    #
                    self.RX_VFO_VAR.set(gv.formatFrequency(self.PrimaryVFO + self.TXfreqOffset))

                    #
                    #   Need to turn CW offset off since we dont want RIT RX on main VFO offset
                    #

                    self._RIT_ManageLabels(switch)


                else:
                    self.RITmode = False
                    self.CW_VFOA_Offset_On = True
                    self.CW_VFOAUX_Offset_On = True
                    self._RIT_ManageLabels(switch)
                    self._CW_ManageLabels("ON")


        else:
            if switch == "ON":
                self.RITmode = True  # RIT is being turned on
                self.CW_VFOA_Offset_On = False
                self.CW_VFOAUX_Offset_On = False
                #
                #   The current VFO is either the TX frequency (if only RIT), or the RX Frequency if
                #   already in SPLIT. In both cases, the frequency displayed in the lower right
                #   Is the same as the VFO. So just assign it now
                #
                self.RX_VFO_VAR.set(gv.formatFrequency(self.intDisplayedPrimaryVFO))
                self._RIT_ManageLabels(switch)


            else:
                self.RITmode = False
                self.CW_VFOA_Offset_On = True
                self.CW_VFOAUX_Offset_On = True
                self._RIT_ManageLabels(switch)
                if self.TXfreqOffset != 0:
                    self._CW_ManageLabels("ON")
        self.update_VFO_Display(self.PrimaryVFO, self.TXfreqOffset)



    def _RIT_ManageLabels(self, switch):
        if switch == "ON":
            self.Tx_Freq_Alert_VAR.set("RIT\nRX Freq:")  # Set label to left of main VFO
            if self.SPLITmode:
                self.RX_Freq_VAR.set("RIT Base RX Freq:")
            else:
                self.RX_Freq_VAR.set("RIT TX Freq:")
            self.RX_VFO_Visability(True)
        else:
            self.Tx_Freq_Alert_VAR.set("        ")
            self.RX_VFO_Visability(False)  # Turn off the RX frequency window




    def _SPLIT(self, switch):
        if self.TXfreqOffset != 0 or self.RITmode:
            if self.RITmode:  # In RIT turning on/off SPLIT
                if switch == "ON":
                    print("Error, Split being turned on and RIT still active")
                    self.SPLITmode = True  # RIT is being turned on
                # else:
                #     self.SPLITmode = False
            # else:  # CW offset must be on
            if switch == "ON":
                self.SPLITmode = True
                self.CW_VFOA_Offset_On = False
                self.CW_VFOAUX_Offset_On = False

                self._SPLIT_ManageLabels(switch)
            else:
                self.SPLITmode = False  # Saves whether SPLIT mode is on or off
                self._SPLIT_ManageLabels(switch)
                if self.TXfreqOffset != 0:
                    self.CW_VFOA_Offset_On = True
                    self.CW_VFOAUX_Offset_On = True
                    self._CW_ManageLabels("ON")
                else:
                    self._RIT_ManageLabels("ON")

        else:  # Simple SPlIT mode on and off
            if switch == "ON":
                self.SPLITmode = True
                self.CW_VFOA_Offset_On = False
                self.CW_VFOAUX_Offset_On = False
                self._SPLIT_ManageLabels(switch)


            else:  # Exiting Split mode, must unwind
                self.SPLITmode = False  # Saves whether SPLIT mode is on or off
                self._SPLIT_ManageLabels(switch)
                self.CW_VFOA_Offset_On = True
                self.CW_VFOAUX_Offset_On = True
                if self.TXfreqOffset != 0:
                    self._CW_ManageLabels("ON")

        self.update_VFO_Display(self.PrimaryVFO, self.TXfreqOffset)


    def _SPLIT_ManageLabels(self, switch):

        if switch == "ON":                  #Going into Split mode
            self.Tx_Freq_Alert_VAR.set("SPLT RX")
            self.split_TX_VAR.set("SPLT TX")
            self.RX_VFO_Visability(False)  # make the RX frequency frame visible

        #
        else:                               #Exiting Split mode, must unwind
            self.Tx_Freq_Alert_VAR.set("       ")
            self.split_TX_VAR.set("       ")
            self.RX_VFO_Visability(False)  # Turn off the RX frequency window



    def updateVFO_Info(self,settingChange, switch):
        match settingChange:
            case "CW":
                self._CW(switch)
            case "RIT":
                self._RIT(switch)
            case "SPLIT":
                self._SPLIT(switch)
            case _:
                print("unidentified info setting change:", settingChange)




    def update_VFO_Display (self, vfo, offset=0 ):
        if self.CW_VFOA_Offset_On:
            self.intDisplayedPrimaryVFO = vfo + offset
        else:
            self.intDisplayedPrimaryVFO = vfo


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

        if self.CW_VFOAUX_Offset_On:
            self.RX_VFO_VAR.set(gv.formatFrequency(vfo))     # Update RX freq reminder displayed if TX Freq displayed


    def setRITmode(self, RITswitch):
        self.updateVFO_Info("RIT",RITswitch)# self.RITmode = RITmode

    def setSplitmode(self, SPLITswitch):
        self.updateVFO_Info("SPLIT", SPLITswitch)  # self.RITmode = RITmode

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
