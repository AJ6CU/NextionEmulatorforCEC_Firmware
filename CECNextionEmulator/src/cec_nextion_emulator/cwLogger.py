# import tkinter as tk
# import tkinter.ttk as ttk
#
# import globalvars as gv

class cwLogger:
    def __init__(self, parent, textBoxObj, maxChars):
        self.parent = parent
        self.textBoxObj = textBoxObj
        self.maxChars = maxChars

    #
    #   Display CW in the target text box.
    #   logCW does the work of managing the text box and rolling characters off display (FIFO)
    #
    def process_CWDecoded_Data(self, buffer):
        # print("Processing CW Decoded in window", buffer)
        for char in buffer:
            self.logCW_Character(char)

    def logCW_Character (self,newchar):
        if len(self.textBoxObj.get('1.0', 'end')) > self.maxChars:
            self.textBoxObj.delete('1.0')
        self.textBoxObj.insert('2.end',newchar)

    def clearLog(self):
        # print("Clearing Log")
        self.textBoxObj.delete('1.0', 'end')