import serial
from time import sleep
from timeit import default_timer as timer
from configuration import configuration
import globalvars as gv
from tkinter import messagebox
import EEPROM as EEPROM

from comportManager import *


class piRadio:
    def __init__(self, serialPortName, serialPort, window, debugFlag=True):
        self.debugCommandDecoding = debugFlag
        self.tty = serialPortName
        # serial   # why wasnt this an error....
        self.mainWindow = window
        self.radioPort = serialPort

        self.MCU_Update_Period = gv.config.get_MCU_Update_Period()
        gv.config.register_observer("MCU Update Period", self.updateMCU_Update_Period)

        self.MCU_Command_Headroom = gv.config.get_MCU_Command_Headroom()
        gv.config.register_observer("MCU Command Headroom", self.updateMCU_Command_Headroom)

        self.toRadioCommandDict = {
            "TS_CMD_MODE": 1,
            "TS_CMD_FREQ": 2,
            "TS_CMD_BAND": 3,
            "TS_CMD_VFO": 4,
            "TS_CMD_SPLIT": 5,
            "TS_CMD_RIT": 6,
            "TS_CMD_TXSTOP": 7,
            "TS_CMD_SDR": 8,
            "TS_CMD_LOCK": 9,  # Dial Lock
            "TS_CMD_ATT": 10,  # ATT
            "TS_CMD_IFS": 11,  # IFS Enabled
            "TS_CMD_IFSVALUE": 12,  # IFS VALUE
            "TS_CMD_STARTADC": 13,
            "TS_CMD_STOPADC": 14,
            "TS_CMD_SPECTRUMOPT": 15,  # Option for Spectrum
            "TS_CMD_SPECTRUM": 16,  # Get Spectrum Value
            "TS_CMD_TUNESTEP": 17,  # Get Spectrum Value
            "TS_CMD_WPM": 18,  # Set WPM
            "TS_CMD_KEYTYPE": 19,  # Set KeyType
            "TS_CMD_SWTRIG": 21,  # SW Action Trigger for WSPR and more
            "TS_CMD_READMEM": 31,  # Read EEProm
            "TS_CMD_WRITEMEM": 32,  # Write EEProm
            "TS_CMD_LOOPBACK0": 74,  # Loopback1 (Response to Loopback Channgel)
            "TS_CMD_LOOPBACK1": 75,  # Loopback2 (Response to Loopback Channgel)
            "TS_CMD_LOOPBACK2": 76,  # Loopback3 (Response to Loopback Channgel)
            "TS_CMD_LOOPBACK3": 77,  # Loopback4 (Response to Loopback Channgel)
            "TS_CMD_LOOPBACK4": 78,  # Loopback5 (Response to Loopback Channgel)
            "TS_CMD_LOOPBACK5": 79,  # Loopback6 (Response to Loopback Channgel)
            "TS_CMD_FACTORYRESET": 85,  # Factory Reset
            "TS_CMD_UBITX_REBOOT": 95  # Reboot
        }

        self.memoryQueue =[]            # when a memory slot is requested, it later comes in without any indication of which
                                        # memory slot it belong to. Fortunately, all in order. So everytime a memory slot is
                                        # requested, the type of memory requested is added to the queue so when we take it
                                        # off the queue, we know where it goes.

        # print("update period is ", self.MCU_Update_Period)
        # print("command headroom = ", self.MCU_Command_Headroom)


#   note on external device to MCU protocol
        #   Proceeded by 3 bytes ("preamble), completed by 3 bytes ("postscript)
        #   In the middle there are 5 bytes tha are in one of two formats
        #   1. First byte is the command, 2nd byte is a subfunction and 3-5 bytes are not used and 0x0
        #   e.g. Mode change is command "1" and second byte selects the mode. 2= LSB, 3=USB, etc.
        #   The last 4 bytes could also be characters for 4 digits (e.g. v1-5 for tuning)
        #   2. First byte is the command and the remaining 4 bytes encode a number.
        #   e.g. Frequency is set with a "4" The remaining 4 bytes shift at 24 bit, 2nd 16, etc. and
        #   then add them together for the frequency

        self.tx_to_mcu_preamble = b'\x59\x58\x68'       # all commands to MCU must start with these three bytes
        self.tx_to_mcu_postscript = b'\xff\xff\x73'     # all commands to MCU must end with these three numbers

        self.mcu_command_buffer =[]                     # buffer used to send bytes to MCU
        self.time_of_last_sent = timer()                # used to avoid overloading MCU



#
#   Decoding command buffers sent from MCU to Nextion screens
#
#   Command format is "pm.xx.val=nn..n" terminated by 3 0xff
#   Command starts in position 3(0,1,2,3)
#   Value starts in position 10, and ends before the 3 0xff
#   All"values" are ascii characters  (i.e., frequency might be
#   pm.xx.val=7500000ffffff  for 7.5mhz and a 14m frequency might be
#   pm.xx.val=14032000ffffff
#

    #
    #   decode and update UX
    #   the command is used to access a dict with pointer to the "getter"
    #
    def processRadioCommand(self, buffer):
        command = buffer[3]  + buffer[4]
        self.mainWindow.delegate_command_processing (command, buffer)

    def rebootRadio(self):
        # self.openRadio()
        command=[0x5f,0x6c,0x48,0x45,0x59]
        self.sendCommandToMCU(bytes(command))

#
#   Read and process all the values sent at startup of radio
#
    def readALLValues(self):

        ffCount = 0
        buffer = []
        commandCount = 0

        while commandCount < 26:
            # Read a line from the serial port (until a newline character is received)
            # Decode the bytes to a string (e.g., 'utf-8') and remove leading/trailing whitespace

            in_byte= self.radioPort.read(1)

            if in_byte:
                #
                #   Looking for the first line with a "p" in the first character
                #   CEC sends a zero to start, just ignore it
                #
                if ((len(buffer) == 0) and (in_byte.decode(errors='ignore') != 'p')):
                    pass
                else:
                    buffer.append (in_byte)


                    if in_byte.hex() == 'ff':
                        ffCount += 1
                        if ffCount == 3:
                            #
                            #   decode the characters into ascii
                            #
                            decoded_buffer_char = [item.decode(errors='ignore') for item in buffer]

                            # if self.debugCommandDecoding:
                            #     for item in decoded_buffer_char:
                            #         print(f"{item:<{4}}", end="")
                            #     print("")

                            # decoded_buffer_hex = [item.hex() for item in buffer]
                                # for item in decoded_buffer_hex:
                                #     print(f"{item:<{4}}", end="")
                                # print("")

                            # decoded_buffer_ord = [ord(item) for item in buffer]
                                # for item in decoded_buffer_ord:
                                #     print(f"{item:<{4}}", end="")
                                # print("")
                            #
                            #   since we saw 3 0xff's in a row, we can call the getter to
                            #   set the value in the UX
                            #
                            self.processRadioCommand(decoded_buffer_char)
                            #
                            #   reset counters (and add one to total processed)
                            #
                            ffCount = 0
                            buffer = buffer[:0]
                            commandCount += 1

            # time.sleep(0.1)  # Small delay to prevent busy-waiting

    def updateData(self, repeatFlag=True):
        ffCount = 0
        buffer = []
        while self.radioPort.in_waiting > 0:
            #
            #   Get command
            #
            in_byte = self.radioPort.read(1)

            if in_byte:
                #
                #   Looking for the first line with a "p" in the first character
                #   CEC sends a zero to start, just ignore it
                #
                if ((len(buffer) == 0) and (in_byte.decode(errors='ignore') != 'p')):
                    pass
                else:

                    buffer.append(in_byte)

                    if in_byte.hex() == 'ff':
                        ffCount += 1
                        if ffCount == 3:
                            #
                            #   decode the characters into ascii
                            #
                            decoded_buffer_char = [item.decode(errors='ignore') for item in buffer]
                            #
                            #   since we saw 3 0xff's in a row, we can call the getter to
                            #   set the value in the UX
                            #
                            self.processRadioCommand(decoded_buffer_char)
                            #
                            #   reset counters (and add one to total processed)
                            #
                            ffCount = 0
                            buffer = buffer[:0]
        if repeatFlag:
            self.mainWindow.after(self.MCU_Update_Period,self.updateData)

#   Radio Commands
########################################################################################
#   These routines are called to tell the MCU that an action has happened in the UX.
#   Typically these should be used by the UX Callbacks
########################################################################################
    
    def Req_Channel_Freqs(self):

        base = EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.lsb]

        for i in range(EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.totalSlots]):
            command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                       base,
                       EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.msb],
                       EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.memLength],
                       EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.charFlag]
                       ]
            self.memoryQueue.append("Freq")         # Add  it to queue to be processed when MCU responds
            self.sendCommandToMCU(bytes(command))
            base += EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.memOffset]


        base = EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.lsb]

    def Req_Channel_Labels(self):
        base = EEPROM.Mem_Address["channel_Label"][EEPROM.lsb]
        for i in range(EEPROM.Mem_Address["channel_Label"][EEPROM.totalSlots]):
            command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                       base,
                       EEPROM.Mem_Address["channel_Label"][EEPROM.msb],
                       EEPROM.Mem_Address["channel_Label"][EEPROM.memLength],
                       EEPROM.Mem_Address["channel_Label"][EEPROM.charFlag]
                       ]
            self.memoryQueue.append("Label")
            self.sendCommandToMCU(bytes(command))
            base += EEPROM.Mem_Address["channel_Label"][EEPROM.memOffset]

        base = EEPROM.Mem_Address["channel_Label"][EEPROM.lsb]

    def Req_Channel_Show_Labels(self):
        base = EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.lsb]
        for i in range(EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.totalSlots]):
            command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                       base,
                       EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.msb],
                       EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.memLength],
                       EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.charFlag]
                       ]
            self.memoryQueue.append("ShowLabel")
            self.sendCommandToMCU(bytes(command))
            base += EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.memOffset]

        base = EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.lsb]


    def Req_Master_Cal(self, setter_CB):

        self.Master_Cal_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   EEPROM.Mem_Address["master_cal"][EEPROM.lsb],
                   EEPROM.Mem_Address["master_cal"][EEPROM.msb],
                   EEPROM.Mem_Address["master_cal"][EEPROM.memLength],
                   EEPROM.Mem_Address["master_cal"][EEPROM.charFlag]
                   ]


        self.memoryQueue.append("MasterCal")         # tell the command that receives the data what is it for

        self.sendCommandToMCU(bytes(command))

    def Req_SSB_BFO(self, setter_CB):

        self.SSB_BFO_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   EEPROM.Mem_Address["ssb_bfo"][EEPROM.lsb],
                   EEPROM.Mem_Address["ssb_bfo"][EEPROM.msb],
                   EEPROM.Mem_Address["ssb_bfo"][EEPROM.memLength],
                   EEPROM.Mem_Address["ssb_bfo"][EEPROM.charFlag]
                   ]
        self.memoryQueue.append("SSB_BFO")
        self.sendCommandToMCU(bytes(command))


    def Req_CW_BFO(self,setter_CB):

        self.CW_BFO_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   EEPROM.Mem_Address["cw_bfo"][EEPROM.lsb],
                   EEPROM.Mem_Address["cw_bfo"][EEPROM.msb],
                   EEPROM.Mem_Address["cw_bfo"][EEPROM.memLength],
                   EEPROM.Mem_Address["cw_bfo"][EEPROM.charFlag]
                   ]

        self.memoryQueue.append("CW_BFO")
        self.sendCommandToMCU(bytes(command))


    def Req_Factory_Master_Cal(self, setter_CB):

        self.Factory_Master_Cal_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   EEPROM.Mem_Address["factory_master_cal"][EEPROM.lsb],
                   EEPROM.Mem_Address["factory_master_cal"][EEPROM.msb],
                   EEPROM.Mem_Address["factory_master_cal"][EEPROM.memLength],
                   EEPROM.Mem_Address["factory_master_cal"][EEPROM.charFlag]
                   ]


        self.memoryQueue.append("Factory_MasterCal")         # tell the command that receives the data what is it for

        self.sendCommandToMCU(bytes(command))

    def Req_Factory_SSB_BFO(self, setter_CB):

        self.Factory_SSB_BFO_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   EEPROM.Mem_Address["factory_ssb_bfo"][EEPROM.lsb],
                   EEPROM.Mem_Address["factory_ssb_bfo"][EEPROM.msb],
                   EEPROM.Mem_Address["factory_ssb_bfo"][EEPROM.memLength],
                   EEPROM.Mem_Address["factory_ssb_bfo"][EEPROM.charFlag]
                   ]

        self.memoryQueue.append("Factory_SSB_BFO")
        self.sendCommandToMCU(bytes(command))

    def Req_Factory_CW_Speed(self, setter_CB):

        self.Factory_CW_Speed_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   EEPROM.Mem_Address["factory_cw_wpm"][EEPROM.lsb],
                   EEPROM.Mem_Address["factory_cw_wpm"][EEPROM.msb],
                   EEPROM.Mem_Address["factory_cw_wpm"][EEPROM.memLength],
                   EEPROM.Mem_Address["factory_cw_wpm"][EEPROM.charFlag]
                   ]

        self.memoryQueue.append("Factory_CW_Speed")
        self.sendCommandToMCU(bytes(command))


    def Req_Factory_CW_Sidetone(self, setter_CB):

        self.Factory_CW_Sidetone_Setter = setter_CB

        command = [self.toRadioCommandDict["TS_CMD_READMEM"],
                   EEPROM.Mem_Address["factory_cw_sidetone"][EEPROM.lsb],
                   EEPROM.Mem_Address["factory_cw_sidetone"][EEPROM.msb],
                   EEPROM.Mem_Address["factory_cw_sidetone"][EEPROM.memLength],
                   EEPROM.Mem_Address["factory_cw_sidetone"][EEPROM.charFlag]
                   ]

        self.memoryQueue.append("Factory_CW_Sidetone")
        self.sendCommandToMCU(bytes(command))
        
    def Freq_Encode(self, freq):
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

    def Set_Master_Cal(self, cal):

        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #   This requires reboot to take effect
        #

        checksum = (EEPROM.Mem_Address["master_cal"][EEPROM.lsb] + EEPROM.Mem_Address["master_cal"][EEPROM.msb]
                    + EEPROM.Mem_Address["master_cal"][EEPROM.memLength]) % 256

        fourBytes = self.Freq_Encode(str(cal))

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   EEPROM.Mem_Address["master_cal"][EEPROM.lsb],
                   EEPROM.Mem_Address["master_cal"][EEPROM.msb],
                   EEPROM.Mem_Address["master_cal"][EEPROM.memLength],
                   checksum,
                   fourBytes[0],
                   fourBytes[1],
                   fourBytes[2],
                   fourBytes[3]
                   ]
        self.sendCommandToMCU(bytes(command))


    def Set_SSB_BFO(self, cal):

        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #   This requires reboot to take effect
        #

        checksum = (EEPROM.Mem_Address["ssb_bfo"][EEPROM.lsb] + EEPROM.Mem_Address["ssb_bfo"][EEPROM.msb]
                    + EEPROM.Mem_Address["ssb_bfo"][EEPROM.memLength]) % 256

        fourBytes = self.Freq_Encode(str(cal))

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   EEPROM.Mem_Address["ssb_bfo"][EEPROM.lsb],
                   EEPROM.Mem_Address["ssb_bfo"][EEPROM.msb],
                   EEPROM.Mem_Address["ssb_bfo"][EEPROM.memLength],
                   checksum,
                   fourBytes[0],
                   fourBytes[1],
                   fourBytes[2],
                   fourBytes[3]
                   ]
        self.sendCommandToMCU(bytes(command))



    def Set_CW_BFO(self, cal):

        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #   This requires reboot to take effect
        #

        checksum = (EEPROM.Mem_Address["cw_bfo"][EEPROM.lsb] + EEPROM.Mem_Address["cw_bfo"][EEPROM.msb]
                    + EEPROM.Mem_Address["cw_bfo"][EEPROM.memLength]) % 256

        fourBytes = self.Freq_Encode(str(cal))

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   EEPROM.Mem_Address["cw_bfo"][EEPROM.lsb],
                   EEPROM.Mem_Address["cw_bfo"][EEPROM.msb],
                   EEPROM.Mem_Address["cw_bfo"][EEPROM.memLength],
                   checksum,
                   fourBytes[0],
                   fourBytes[1],
                   fourBytes[2],
                   fourBytes[3]
                   ]
        self.sendCommandToMCU(bytes(command))


    def Set_Tuning_Preset(self, rate: bytes):
        command = [self.toRadioCommandDict["TS_CMD_TUNESTEP"], rate, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    def Set_New_Frequency(self, value):
        fourBytes = self.Freq_Encode(value)
        command = [self.toRadioCommandDict["TS_CMD_FREQ"],fourBytes[0],fourBytes[1],fourBytes[2],fourBytes[3]]
        self.sendCommandToMCU(bytes(command))

    #
    #   This function tells the Radio that a new mode has been selected for
    #   the primary (displayed) VFO. After receiving the new mode, the
    #   Radio will separately send back the mode to the UX
    #
    def Set_Mode(self, newMode):
        command = [self.toRadioCommandDict["TS_CMD_MODE"], newMode, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    #
    #   This function tells the Radio that a button up or down has been pushed
    #   in the UX. After receiving this command the radio will send back a new frequency
    #   and mode for the displayed VOF
    #
    def Change_Band(self, direction):
        command = [self.toRadioCommandDict["TS_CMD_BAND"], direction, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    def Tuning_Rate(self,value: bytes):
        command = [self.toRadioCommandDict["TS_CMD_TUNESTEP"], value, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    def Toggle_VFO(self):
        command = [self.toRadioCommandDict["TS_CMD_VFO"], 0, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    def Toggle_Lock(self):
        command = [self.toRadioCommandDict["TS_CMD_LOCK"], 0, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    def Toggle_Speaker(self):
        command = [self.toRadioCommandDict["TS_CMD_SDR"], 0, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    def Toggle_Stop(self):
        command = [self.toRadioCommandDict["TS_CMD_TXSTOP"], 0, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    def Toggle_Split(self):
        command = [self.toRadioCommandDict["TS_CMD_SPLIT"], 0, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    def Toggle_RIT(self):
        command = [self.toRadioCommandDict["TS_CMD_RIT"], 0, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    def Set_ATT(self, value: bytes):
        command = [self.toRadioCommandDict["TS_CMD_ATT"], value, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))

    def Toggle_IFS(self):
        command = [self.toRadioCommandDict["TS_CMD_IFS"], 0, 0, 0, 0]
        self.sendCommandToMCU(bytes(command))



    def Set_IFS_Level(self, level):
        encodedBytes = self.Freq_Encode(str(level))

        command = [self.toRadioCommandDict["TS_CMD_IFSVALUE"], encodedBytes[0], encodedBytes[1], encodedBytes[2], 0]
        self.sendCommandToMCU(bytes(command))


    def Set_CW_Tone(self, tone):

        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #   This requires reboot to take effect
        #

        checksum = (EEPROM.Mem_Address["cw_sidetone"][EEPROM.lsb] + EEPROM.Mem_Address["cw_sidetone"][EEPROM.msb]
                    + EEPROM.Mem_Address["cw_sidetone"][EEPROM.memLength]) % 256


        fourBytes = self.Freq_Encode(str(tone))

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   EEPROM.Mem_Address["cw_sidetone"][EEPROM.lsb],
                   EEPROM.Mem_Address["cw_sidetone"][EEPROM.msb],
                   EEPROM.Mem_Address["cw_sidetone"][EEPROM.memLength],
                   checksum,
                   fourBytes[0],
                   fourBytes[1],
                   fourBytes[2],
                   fourBytes[3]
                   ]
        self.sendCommandToMCU(bytes(command))


    def Set_CW_Keytype(self, keyType):
        #
        #   first send command to officially change the keytype
        #
        command = [self.toRadioCommandDict["TS_CMD_KEYTYPE"], gv.CW_KeyValue[keyType], 0, 0, 0]
        self.sendCommandToMCU(bytes(command))
        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #

        checksum = (EEPROM.Mem_Address["cw_key_type"][EEPROM.lsb] + EEPROM.Mem_Address["cw_key_type"][EEPROM.msb]
                    + EEPROM.Mem_Address["cw_key_type"][EEPROM.memLength]) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   EEPROM.Mem_Address["cw_key_type"][EEPROM.lsb],
                   EEPROM.Mem_Address["cw_key_type"][EEPROM.msb],
                   EEPROM.Mem_Address["cw_key_type"][EEPROM.memLength],
                   checksum,
                   gv.CW_KeyValue[keyType]
                   ]
        self.sendCommandToMCU(bytes(command))




    def Set_CW_Speed(self, keySpeed):

        #
        #
        #   first send command to officially change the key speed
        #   wpm directly saved. It is the dot length which is 1200/wpm
        #

        dotLength_ms = int(1200 / int(keySpeed))
        command = [self.toRadioCommandDict["TS_CMD_WPM"], dotLength_ms, 0, 0]
        self.sendCommandToMCU(bytes(command))

        #
        #   Now have to write it to EEPROM as this is not one of the values that are automatically saved to EEPROM
        #

        checksum = (EEPROM.Mem_Address["cw_wpm"][EEPROM.lsb] + EEPROM.Mem_Address["cw_wpm"][EEPROM.msb]
                    + EEPROM.Mem_Address["cw_wpm"][EEPROM.memLength]) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   EEPROM.Mem_Address["cw_wpm"][EEPROM.lsb],
                   EEPROM.Mem_Address["cw_wpm"][EEPROM.msb],
                   EEPROM.Mem_Address["cw_wpm"][EEPROM.memLength],
                   checksum,
                   dotLength_ms,                # Eeprom allows up to two bytes for adjusted key,
                                                    # but keychage without reboot only 1 byte
                   0,0,0
                   ]

        self.sendCommandToMCU(bytes(command))


    def Set_CW_Delay_Starting_TX(self, startTXDelay):
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

        checksum = (EEPROM.Mem_Address["cw_Delay_Starting_TX"][EEPROM.lsb] + EEPROM.Mem_Address["cw_Delay_Starting_TX"][EEPROM.msb]
                    + EEPROM.Mem_Address["cw_Delay_Starting_TX"][EEPROM.memLength]) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   EEPROM.Mem_Address["cw_Delay_Starting_TX"][EEPROM.lsb],
                   EEPROM.Mem_Address["cw_Delay_Starting_TX"][EEPROM.msb],
                   EEPROM.Mem_Address["cw_Delay_Starting_TX"][EEPROM.memLength],
                   checksum,
                   adjustedStartTXDelay
                   ]

        self.sendCommandToMCU(bytes(command))

    def Set_CW_Delay_Returning_To_RX(self, returnRXDelay):
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

        checksum = (EEPROM.Mem_Address["cw_Delay_Returning_to_RX"][EEPROM.lsb] +
                    EEPROM.Mem_Address["cw_Delay_Returning_to_RX"][EEPROM.msb]
                    + EEPROM.Mem_Address["cw_Delay_Returning_to_RX"][EEPROM.memLength]) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   EEPROM.Mem_Address["cw_Delay_Returning_to_RX"][EEPROM.lsb],
                   EEPROM.Mem_Address["cw_Delay_Returning_to_RX"][EEPROM.msb],
                   EEPROM.Mem_Address["cw_Delay_Returning_to_RX"][EEPROM.memLength],
                   checksum,
                   adjustedReturnToRXDelay
                   ]

        self.sendCommandToMCU(bytes(command))

    def Write_EEPROM_Channel_FreqMode (self, channelNum, freq, mode ):

        encoded_data = (int(freq) & 0x1FFFFFFF) + ((int(EEPROM.Text_To_ModeNum[mode])& 0x7)<<29)

        encodedBytes = self.Freq_Encode(str(encoded_data))

        lsb = (channelNum*EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.memOffset]) + EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.lsb]
        msb = EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.msb]
        totalBytes = EEPROM.Mem_Address["channel_freq_Mode"][EEPROM.memLength]


        checksum = (lsb + msb + totalBytes) % 256

        command = [self.toRadioCommandDict["TS_CMD_WRITEMEM"],
                   lsb,
                   msb,
                   totalBytes,
                   checksum,
                   encodedBytes[0], encodedBytes[1], encodedBytes[2], encodedBytes[3]
                   ]

        self.sendCommandToMCU(bytes(command))

    def Write_EEPROM_Channel_Label (self, channelNum, label ):

        if channelNum > EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.totalSlots]:
            return

        lsb = ((channelNum * EEPROM.Mem_Address["channel_Label"][EEPROM.memOffset]) +
               EEPROM.Mem_Address["channel_Label"][EEPROM.lsb])
        msb = EEPROM.Mem_Address["channel_Label"][EEPROM.msb]
        totalBytes = EEPROM.Mem_Address["channel_Label"][EEPROM.memLength]

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

        self.sendCommandToMCU(bytes(command))

    def Write_EEPROM_Channel_ShowLabel (self, channelNum, showLabel ):

        #
        #   Don't write to EEPROMs showLabels 10+
        #
        if channelNum > EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.totalSlots]:
            return

        lsb = (channelNum * EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.memOffset]) + \
              EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.lsb]
        msb = EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.msb]
        totalBytes = EEPROM.Mem_Address["channel_ShowLabel"][EEPROM.memLength]

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

        self.sendCommandToMCU(bytes(command))

#
#   Send command to MCU
#
    def sendCommandToMCU(self, commandList):

        currentTime = timer()
        timeDiff = currentTime - self.time_of_last_sent

        if (timeDiff < self.MCU_Command_Headroom):
            sleep(self.MCU_Command_Headroom - timeDiff)
        self.time_of_last_sent = timer()

        self.tx_to_mcu_preamble = b'\x59\x58\x68'  # all commands to MCU must start with these three bytes
        self.tx_to_mcu_postscript = b'\xff\xff\x73'  # all commands to MCU must end with these three numbers

        try:
            self.radioPort.write(self.tx_to_mcu_preamble + commandList + self.tx_to_mcu_postscript)
        except:
            messagebox.showerror(title="ERROR Communicating with uBITX",
                                                     message="Communication failed with uBITX.", parent=self,
                                 DETAILS="Did you select the right com port?\n"+"You selected: "+ self.tty)
            sys.exit(-1)

    def popMemoryQueue(self):
        if len(self.memoryQueue) == 0:
            return None
        else:
            return self.memoryQueue.pop(0)


    def lenMemoryQueue(self):
        return len(self.memoryQueue)


    def updateMCU_Update_Period(self, value):
        self.MCU_Update_Period = value
        # print("update period is changing, now = ", self.MCU_Update_Period)

    def updateMCU_Command_Headroom(self, value):
        self.MCU_Command_Headroom = value
        # print("update MCU Command Headroom is changing, now = ", self.MCU_Command_Headroom)


