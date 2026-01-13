#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import channelsui as baseui
from tkinter import messagebox
from configuration import configuration
import globalvars as gv

import traceback
#
# Manual user code
#



class channels(baseui.channelsUI):
    channelList = []
    currentChannel = 0

    def __init__(self, master=None, mainWindow=None, refreshCallback=None, **kw):

        self.master = master                # save parameters for re-use later
        self.mainWindow = mainWindow
        self.refreshCallback = refreshCallback

        channels.channelList = []           #initialize class variables
        channels.currentChannel = 0

        self.channelSlotCount = 0           #initialize instance variables to process channels
        self.channelSlotSelection = None


        self.popup = tk.Toplevel(self.master)           # Create a top level window to contain the channel window

        super().__init__(self.popup, **kw)
        #
        #   Catch closes that happen thru Window Manager
        #
        self.popup.protocol("WM_DELETE_WINDOW", self.close_Channel_CB)
        #
        #   Channels could have been created using any frequency. Need to use
        #   the smallest preset to avoid frequency being truncated. So capture it,
        #   reset it and late we will reset it.
        #
        self.mainWindow.theVFO_Object.savePresetState()
        self.mainWindow.Radio_Set_Tuning_Preset(1)

        #
        #   Since we display the frequency using the selected Delimiter, need
        #   to register interest in its value in case it changes while channel window
        #   is open.
        gv.config.register_observer("NUMBER DELIMITER", self.reformatChannelFreq)

        #
        #   Initialize scanning functions.
        #
        self.scanRunning = False
        self.scanTimer = None
        self.scanSetSelected = None
        self.scanIndex = None
        self.scanList = []

        #
        #   Each channel is actually created from another object (frequencyChannel). So
        #   We create a list of those channels so we can access them later either.
        #   Also need to capture the callback of the particular frequencyChannel so when
        #   the user selects, we can know which one to use. The callaback stores pointer
        #   in channels.currentChannel
        #

        for child in self.scrolledChannelFrame.innerframe.winfo_children():
            channels.channelList.append(child)
            child.assignChannelSelect_CB(self.channelSlot_CB)
            child.assignChannelNum(self.channelSlotCount)
            #
            # Set defaults
            #
            child.channel_Number_Default()
            child.Label_Default()
            child.Freq_Default()
            child.Mode_Default()
            child.Showlabel_Default()
            child.ScanSet_Default(gv.config.get_ScanSet_Settings(self.channelSlotCount))

            self.channelSlotCount += 1

        self.scan_Select_Channel_Default()
        self.scan_Station_Time_Default()

    #
    #   This routine is called after the object has been created and initialized. Some tweaking
    #   happens to the user interface as well as an attempt to place the popup in a reasonable
    #   place on the screen. Unfortunately, many window managers defeat this good intention and
    #   will place it in the center of the screen
    #

    def initChannelsUX(self):
        self.update_Current_Frequency(self.mainWindow.theVFO_Object.getFormattedPrimaryVFO())
        self.update_Current_Mode(self.mainWindow.primary_Mode_VAR.get())
        self.mainWindow.Radio_Req_Channel_Freqs()
        self.mainWindow.Radio_Req_Channel_Labels()
        self.mainWindow.Radio_Req_Channel_Show_Labels()



        self.popup.title("Frequency Channels")
        self.popup.geometry("800x700")
        self.popup.wait_visibility()  # required on Linux
        # self.popup.grab_set()         # dont want as we can allow other things to click while using channels
        self.popup.transient(self.mainWindow)

        gv.formatCombobox(self.scan_Select_Combobox, "Arial", "14", "bold")
        gv.formatCombobox(self.Time_On_Freq_Combobox, "Arial", "14", "bold")

        self.pack(expand=tk.YES, fill=tk.BOTH)
        gv.trimAndLocateWindow(self.popup, 0, 0)

    #
    #   Handles reformating the frequencies in the case someone changes the number delimiter
    #   while the Channels window is open.
    #
    def reformatChannelFreq(self, new_delimiter):
        if new_delimiter  == ",":
            prior_delimiter = "."
        else:
            prior_delimiter = ","

        for child in channels.channelList:
            child.channel_Freq_VAR.set(child.channel_Freq_VAR.get().replace(prior_delimiter,new_delimiter))

        self.current_VFO_VAR.set(self.current_VFO_VAR.get().replace(prior_delimiter,new_delimiter))

    #
    #   Channels could have been created using any frequency. Need to use
    #   the smallest preset to avoid frequency being truncated. SO this method capture it,
    #   reset it and late we will reset it.
    #
    # def SaveAndSetPreset(self):
    #     # if (self.mainWindow.theVFO_Object.saved_tuning_Preset_Selection == None):  # None value indicates we *were* in "preset tune" mode
    #     #     self.mainWindow.theVFO_Object.savePresetState()
    #     #     self.mainWindow.Radio_Set_Tuning_Preset(1)
    #     self.mainWindow.theVFO_Object.set_Tuning_Mode("direct tune")
    #
    #   The following are just external visible methods to set/change various values
    #

    def update_Current_Frequency(self, freq):
        self.current_VFO_VAR.set(freq)

    def update_Current_Mode(self, mode):
        self.current_Mode_VAR.set(mode)


    def scan_Select_Channel_Default(self):
        self.scan_Select_Channel_VAR.set("None")

    #
    #   Time hanging around each channel during a scan is controllable via a configuration
    #   parameter that can also be set in settings
    #
    def scan_Station_Time_Default(self):
        self.scan_Time_On_Station = gv.config.get_Scan_On_Station_Time()
        self.Time_On_Freq_VAR.set(str(int(int(gv.config.get_Scan_On_Station_Time())/1000)))

    def update_Time_On_Station_CB(self, event=None):
        self.scan_Time_On_Station = int(self.Time_On_Freq_VAR.get()) * 1000
        gv.config.set_Scan_On_Station_Time(self.scan_Time_On_Station)



    #
    #   These routines are called from the routines in piCECNextion that process memory
    #   contents sent by the MCU. The format of the information in the EEPROM was originally
    #   designed to be concise so it needs to be reformated for humans
    #

    def EEPROM_SetChanneFreqMode(self, channelNum,freq, mode):

        channels.channelList[channelNum].Set_Freq(str(freq))

        channels.channelList[channelNum].Set_Mode(self.mainWindow.modeNum_To_TextDict[str(mode)])

    def EEPROM_SetChannelLabel(self, channelNum, label):
        channels.channelList[channelNum].Set_Label(label)

    def EEPROM_SetChannelShowLabel(self, channelNum, showFlag):
        channels.channelList[channelNum].Set_ShowLabel(showFlag)

    #
    # method called to implement Channel->VFO request
    #
    def ChannelToVFO_CB(self):

        if self.channelSlotSelection == None:
            messagebox.showinfo("Information", "Must SELECT a channel first.",
                                parent=self)
            return

        self.mainWindow.Radio_Set_Mode(
            self.mainWindow.Text_To_ModeNum[channels.channelList[self.channelSlotSelection].Get_Mode()])
        self.mainWindow.Radio_Set_New_Frequency(channels.channelList[self.channelSlotSelection].Get_Freq())
        # self.mainWindow.Radio_Set_Mode(self.mainWindow.Text_To_ModeNum[channels.channelList[self.channelSlotSelection].Get_Mode()])
        self.current_Channel_VAR.set(channels.channelList[self.channelSlotSelection].Get_Label())

    #
    # method called to write current VFO to channel
    #

    def VFOToChannel_CB(self):
        if self.channelSlotSelection == None:
            messagebox.showinfo("Information", "Must SELECT a channel first.",
                                parent=self)
            return
        channels.channelList[self.channelSlotSelection].Set_Freq(self.current_VFO_VAR.get())
        channels.channelList[self.channelSlotSelection].Set_Mode(self.current_Mode_VAR.get())
        channels.channelList[self.channelSlotSelection].channel_Dirty()

    #
    #   Controls the scanning process. Builds the list of channels to scan and sends it to
    #   "performScan" to actually process the list.
    #

    def startScan(self):
        self.scanRunning = True
        self.scan_Channel_ButtonText_VAR.set("Stop Scan")
        self.scanIndex = 0
        self.scanList = []

        if self.scan_Select_Channel_VAR.get() == "None":
            messagebox.showinfo("Information", "Must SELECT a set of Channels to Scan before clicking the Scan Button",
                                parent=self)
            self.stopScan()
            return

        for i in range(len(channels.channelList)):
            if self.scanSetSelected == channels.channelList[i].Get_ScanSet():
                self.scanList.append(i)

        if len(self.scanList) == 0:
            messagebox.showinfo("Information", "No Channels attached to this Scan Set.",
                                parent=self)
            self.stopScan()
            return
        self.performScan()
    #
    #   Actually performs the scan. Note that it calls itself after "scan_Time_On_Station" happens
    #

    def performScan(self):
        self.channelSlot_CB(self.scanList[self.scanIndex])
        self.ChannelToVFO_CB()
        self.scanIndex += 1

        if self.scanIndex == len(self.scanList):
            self.scanIndex = 0
        self.scanTimer = self.master.after(self.scan_Time_On_Station, self.performScan)

    #
    #   Just handles completion of the scan after the stop button is pressed.
    #
    def stopScan(self):
        self.scanRunning = False
        self.scan_Channel_ButtonText_VAR.set("Run Scan")
        if self.scanTimer != None:
            self.master.after_cancel(self.scanTimer)
            self.scanTimer = None
        self.scanIndex = 0

    def scan_Channel_CB(self):              # method called to start channel scanning
        if self.scanRunning:
            self.stopScan()
        else:
            self.startScan()

    def runScan_Selection_CB(self, event=None):
        self.scanSetSelected = self.scan_Select_Channel_VAR.get()

    #
    #   Callback for the Refresh button. Checks for dirty info, and then does the referesh
    #

    def refresh_Channel_CB(self):           # method called when user wants to refresh channels from EEPROM
        self.confirmExitorWriteDirty()
        self.refreshCallback()

    #
    #   Handles the request to close window. Also called if the channels window is closed
    #   via the window manager
    #
    def close_Channel_CB(self):             # method called when window closed
        self.confirmExitorWriteDirty()
        self.mainWindow.theVFO_Object.restorePresetState()
        self.stopScan()                 # Stop any scan that might be running
        self.master.withdraw()

    #
    #   Called on close or refresh to check whether any information is "dirty". If so, a dialog
    #   is popped up asking the user whether they want to save the values before exiting.
    #
    def confirmExitorWriteDirty(self):
        for channelNum in range(len(self.channelList)):
            if (channels.channelList[channelNum].dirty):
                response = messagebox.askyesno("Confirmation",
                                               "Not all channels have been saved to EEPROM\nDo you want to save these channels?",
                                               parent=self)

                # Process the user's response
                if response:  # True if "Yes" is clicked
                    self.saveAllChannels_CB()
                break
    #
    #   This method is called when the user selects a particular channel. It is a little
    #   complicated because need to figure out which of 20 possible channels has been selected.
    #   This is where the list of channels (channels.channelList) comes in!
    #
    def channelSlot_CB(self, slotNumber):
        if self.channelSlotSelection != None:
            channels.channelList[self.channelSlotSelection].channel_Select_Button.configure(
                style="Button2b.TButton")
            channels.channelList[self.channelSlotSelection].channel_Select_VAR.set("Select")  # unselect the prior one

        if self.channelSlotSelection == slotNumber:         #Unselect if already selected
            self.channelSlotSelection = None
        else:
            self.channelSlotSelection = slotNumber
            channels.channelList[self.channelSlotSelection].channel_Select_Button.configure(
                    style="Button2bipressed.TButton")
            channels.channelList[self.channelSlotSelection].channel_Select_VAR.set("Selected") # select the new one
    #
    #   Does the actual saving of a particular channel when a save is requested. A "save all"
    #   just calls this method repeatedly
    #

    def saveChannel(self,channelNum):
        if channelNum == None:
            messagebox.showinfo("Information", "No Channel Selected to Save",
                                parent=self)
            return
        if  (channels.channelList[channelNum].dirty):
            channels.channelList[channelNum].channel_Not_Dirty()

            self.mainWindow.Radio_Write_EEPROM_Channel_FreqMode(
                channelNum,
                channels.channelList[channelNum].Get_Freq(),
                channels.channelList[channelNum].Get_Mode())

            self.mainWindow.Radio_Write_EEPROM_Channel_Label(
                channelNum,
                channels.channelList[channelNum].Get_Label())

            self.mainWindow.Radio_Write_EEPROM_Channel_ShowLabel(
                channelNum,
                channels.channelList[channelNum].Get_ShowLabel())

            gv.config.set_ScanSet_Settings(channelNum,
                                               channels.channelList[channelNum].Get_ScanSet())
    #
    #   The two save all and save one channel button callbacks
    #

    def saveChannel_CB(self):
        self.saveChannel(self.channelSlotSelection)

    def saveAllChannels_CB(self):
        for aChannel in range(len(self.channelList)):
            self.saveChannel(aChannel)



if __name__ == "__main__":
    root = tk.Tk()
    widget = channels(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
