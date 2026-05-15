#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import cwSettingsui as baseui
from tkinter import messagebox
import globalvars as gv
from time import sleep


#
# Manual user code
#


class cwSettings(baseui.cwSettingsUI):
    def __init__(self, master=None, mainWindow=None, **kw):

        self.mainWindow = mainWindow
        self.master = master

        #
        #   Create a toplevel window to contain the settings popup
        #
        self.popup = tk.Toplevel(self.master)

        super().__init__(self.popup,  **kw)

        #
        #   Magic code to get a handle on the current font of the default item and propagate it to the list...
        #







        self.CW_Sidetone_Spinbox.configure(values=gv.CW_Sidetone_Values)
        self.CW_Speed_WPM_Spinbox.configure(values=gv.CW_WPM_Values)
        self.CW_Start_TX_Spinbox.configure(values=gv.Start_TX_Values)
        self.CW_Delay_Returning_RX_Spinbox.configure(values=gv.Delay_Return_RX_Values)



        self.orig_tone = None
        self.orig_key_type = None
        self.orig_keySpeed = None
        self.delay_starting_tx = None
        self.delay_returning_to_rx = None
        self.offset_Freq_Flag = None

        #
        #   Can now kickoff the UX
        #

        self.initUX()

    def initUX(self):

        self.loadCurrentCWSettings(self.mainWindow.tone_value_VAR.get(),
                                                       self.mainWindow.key_type_value_VAR.get(),
                                                       self.mainWindow.key_speed_value_VAR.get(),
                                                       self.mainWindow.delay_starting_tx_value_VAR.get(),
                                                       self.mainWindow.delay_returning_to_rx_value_VAR.get(),
                                                       self.mainWindow.cwTX_OffsetFlag
                                                       )

        self.popup.title("CW Settings")

        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)
        gv.trimAndLocateWindow(self.popup, 0, 0)






    def loadCurrentCWSettings(self,tone,keyType,keySpeed,delayToTX,delayToRX, offset_Freq_Flag):
        #
        #   Save originals for dirty testing later
        #
        self.orig_tone = tone
        self.orig_key_type = keyType
        self.orig_keySpeed = keySpeed
        self.delay_starting_tx = delayToTX
        self.delay_returning_to_rx = delayToRX
        self.offset_Freq_Flag = offset_Freq_Flag
        #
        #   Stuff values into stringvars of the UX
        #
        self.CW_Sidetone_Spinbox.configure(values=gv.CW_Sidetone_Values)
        self.CW_Speed_WPM_Spinbox.configure(values=gv.CW_WPM_Values)
        self.CW_Start_TX_Spinbox.configure(values=gv.Start_TX_Values)
        self.CW_Delay_Returning_RX_Spinbox.configure(values=gv.Delay_Return_RX_Values)

        #
        #   The following code deals with the situation where an existing value is in EEPROM that
        #   is not a "normal" value provided by the Combobox. We deal with this situation by just
        #   temporarily adding the value to the comboobox and then selecting it
        #

        if tone not in gv.CW_Sidetone_Values:
            self.CW_Sidetone_Spinbox.configure(values=gv.CW_Sidetone_Values + [tone])
        self.tone_value_VAR.set(tone)

        self.key_type_value_VAR.set(keyType)

        if keySpeed not in gv.CW_WPM_Values:
            self.CW_Speed_WPM_Spinbox.configure(values=gv.CW_WPM_Values + [keySpeed])
        self.key_speed_value_VAR.set(keySpeed)

        if delayToTX not in gv.Start_TX_Values:
            self.CW_Start_TX_Spinbox.configure(values=gv.Start_TX_Values + [delayToTX])
        self.delay_starting_tx_value_VAR.set(delayToTX)

        if delayToRX not in gv.Delay_Return_RX_Values:
            self.CW_Delay_Returning_RX_Spinbox.configure(values=gv.Delay_Return_RX_Values + [delayToRX])
        self.delay_returning_to_rx_value_VAR.set(delayToRX)


        if self.offset_Freq_Flag:
            self.CW_Display_TXFreq_VAR.set("TX")
        else:
            self.CW_Display_TXFreq_VAR.set("RX")


    def dirty_DisplayCWSettings (self):
        reboot_required = False
        if( self.tone_value_VAR.get() != self.orig_tone):
            self.mainWindow.theRadio.Set_CW_Tone(self.tone_value_VAR.get())
            reboot_required = True

        if (self.key_type_value_VAR.get() != self.orig_key_type):
            self.mainWindow.theRadio.Set_CW_Keytype(self.key_type_value_VAR.get())

        if (self.key_speed_value_VAR.get() != self.orig_keySpeed):
            self.mainWindow.theRadio.Set_CW_Speed(self.key_speed_value_VAR.get())

        if (self.delay_starting_tx_value_VAR.get() != self.delay_starting_tx):
            self.mainWindow.theRadio.Set_CW_Delay_Starting_TX(self.delay_starting_tx_value_VAR.get())
            reboot_required = True

        if (self.delay_returning_to_rx_value_VAR.get() != self.delay_returning_to_rx):
            self.mainWindow.theRadio.Set_CW_Delay_Returning_To_RX(self.delay_returning_to_rx_value_VAR.get())
            reboot_required = True
        #
        #   Note: self.offset_Freq_Flag should generally be the sames as self.mainWindow.cwTX_OffsetFlag
        #   However, there could be a case where a delayed setting by the MCU comes after the CW settings
        #   is displayed causing a race condition. THis is the logic for using the saved value
        #
        if (self.CW_Display_TXFreq_VAR.get()) == 'RX' and self.offset_Freq_Flag:
            self.mainWindow.cwTX_OffsetFlag = False
            self.mainWindow.theVFO_Object.offsetVFOforTX(False)
        elif (self.CW_Display_TXFreq_VAR.get()) == 'TX' and not self.offset_Freq_Flag:
            self.mainWindow.cwTX_OffsetFlag = True
            self.mainWindow.theVFO_Object.offsetVFOforTX(True)



        if(reboot_required):
            response = messagebox.askyesno("Reboot Required", "One or more changes require a reboot to take effect.\n\n"+
                                           "Do you want to reboot now?",
                                            parent=self, icon="warning")
            if response:
                sleep (1.5)              # sleep a little so that the change to settings are processed before reboot
                self.mainWindow.theRadio.rebootRadio()
            else:
                print('told us to wait')

    def selectCWStraightKey_CB(self):
        self.key_type_value_VAR.set("STRAIGHT")

    def selectCWIAMBICAKey_CB(self):
        self.key_type_value_VAR.set("IAMBICA")

    def selectCWIAMBICBKey_CB(self):
        self.key_type_value_VAR.set("IAMBICB")

    def selectCWDisplayTX_CB(self):
        self.CW_Display_TXFreq_VAR.set('TX')

    def selectCWDisplayRX_CB(self):
        self.CW_Display_TXFreq_VAR.set('RX')

    def apply_CB(self):
        self.dirty_DisplayCWSettings()
        self.master.destroy()

    def cancel_CB(self):
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = cwSettings(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
