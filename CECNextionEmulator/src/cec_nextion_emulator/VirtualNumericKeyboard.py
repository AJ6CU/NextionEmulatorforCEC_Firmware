#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import StringVar
import globalvars as gv



class VirtualNumericKeyboard(tk.Toplevel):
    def __init__(self, master=None, fieldStrVar=None, postProcessor=None, maxDigits=None,  **kw):
        self.master = master
        self.fieldStrVar = fieldStrVar
        self.postProcessor = postProcessor
        # self.dirty_CB = dirtyCallback
        self.maxDigits = maxDigits
        # # self.formatVFOFlag = formatVFOFlag
        # self.formatCallback = formatCallback
        self.originalValue = self.fieldStrVar.get().replace(",","").replace(".","")
        self.textField = StringVar()
        self.textField.set(self.originalValue)
        # self.textField.set(self.originalValue)

        #
        # if self.formatVFOFlag:
        # self.fieldStrVar.set(gv.unformatFrequency(self.originalValue))


        super().__init__(master, **kw)

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.messageTooLong = "Too Many Characters, Max = " + str(self.maxDigits)
        self.messageEmpty = ""

        self.message = StringVar()
        self.message.set(self.messageEmpty)

        self.currentPos = len(self.textField.get())


        self.textField.set(self.textField.get() + gv.CURSOR)
        
        self.wait_visibility()  # required on Linux
        self.grab_set()  # This line makes the cw settings window modal
        self.transient(self.master)  # Makes the cw settings appear above the mainwindow
        # toplevel_offsetx, toplevel_offsety = self.master.winfo_x() , self.master.winfo_y()
        # padx = 350  # the padding you need.
        # pady = 0
        # # self.geometry(f"+{toplevel_offsetx + padx}+{toplevel_offsety + pady}")
        self.geometry(gv.VNUMERICKEYBOARD_OFFSET)

        self.mainframe = ttk.Frame(self)
        self.leftArrow = "\u2190"
        if gv.config.get_NUMBER_DELIMITER() == ",":
            self.decimalPoint = "."
        else:
            self.decimalPoint = ","
        # self.decimalPoint = gv.NUMBER_DELIMITER

        # if formatVFOFlag:

        rows = [["7", "8", "9"],
                ["4", "5", "6"],
                ["1", "2", "3"],
                ["0", self.leftArrow, "Del"]]
        # else:
        #     rows = [["7", "8", "9"],
        #             ["4", "5", "6"],
        #             ["1", "2", "3"],
        #             ["0", self.decimalPoint, "Del"]]

        for r, row in enumerate(rows, 1):
            for c, t in enumerate(row):
                ttk.Button(self.mainframe, style='Button1Raised.TButton',text="\n"+t+"\n", width=6, command=lambda t=t: self.press(t)).grid(row=r, column=c,pady=1,padx="0 1")

        ttk.Button(self.mainframe, style='Button1Raised.TButton',text="\nClear\n", width=9, command=self.clear).grid(row=len(rows)+1,column=0, columnspan=2,sticky='w',pady=1,padx="0 1")
        ttk.Button(self.mainframe, style='Button1Raised.TButton', text="\nEnter\n", width=9, command=self.enter).grid(row=len(rows)+1, column=1,columnspan=2,sticky='e',pady=1,padx=1)
        ttk.Entry(self.mainframe, style='Entry1b.TEntry', font=('Arial', 18), textvariable=self.textField,
                  # state="readonly",
                  width=18, justify="center").grid(row=len(rows) + 2, column=0, columnspan=3, pady=2,
                                                                     padx="0 1", sticky='ew')
        ttk.Entry(self.mainframe, style='Entry1b.TEntry', font=('Arial', 18, 'italic'),textvariable=self.message, state="readonly", width=18,justify="center").grid(row=len(rows)+3,column=0,columnspan=3,pady=2,padx="0 1",sticky='ew')

        master.bind("<Return>", self.enter)

        self.mainframe.configure(style='Normal.TFrame', height=200, width=200)
        self.mainframe.pack(fill="both", expand=True, padx=5, pady=5)
        self.configure(background="gray", height=200, width=200)

    def clear(self,event=None):

        self.textField.set("")
        self.currentPos = 0
        self.message.set(self.messageEmpty)

    def cancel(self,event=None):
        # self.fieldStrVar.set(self.originalValue)
        self.destroy()

    def enter(self,event=None):

        self.textField.set(self.textField.get().replace(gv.CURSOR, ''))
        # if self.formatCallback != None:
        #     self.fieldStrVar.set(self.formatCallback(self.textField.get()))
        # else:
        #     self.fieldStrVar.set(self.textField.get())
        #
        # if self.originalValue !=self.fieldStrVar.get():
        self.postProcessor(self.originalValue,self.textField.get())
            # self.dirty_CB(self.originalValue)
        self.destroy()

    def press(self,t):
        if t == "Del":
            self.currentPos -=  1
            if self.currentPos < self.maxDigits:
                self.message.set(self.messageEmpty)
            first_half = (self.textField.get()[:self.currentPos].replace(gv.CURSOR,''))
            second_half = self.textField.get()[self.currentPos+1:].replace(gv.CURSOR,'')
            self.textField.set(first_half  + gv.CURSOR + second_half)
        elif t == self.leftArrow:
            self.currentPos -= 1
            if self.currentPos < 0:
                self.currentPos = len(self.textField.get())-1
                self.textField.set(self.textField.get().replace(gv.CURSOR,'')+gv.CURSOR)
            else:
                first_half = self.textField.get()[:self.currentPos].replace(gv.CURSOR,'')
                second_half = self.textField.get()[self.currentPos:].replace(gv.CURSOR,'')
                self.textField.set(first_half + gv.CURSOR + second_half)
        else:
            if t == self.decimalPoint:
                if self.decimalPoint in self.textField.get():   # ignore attempts to enter multiple periods
                    return

            if self.currentPos < self.maxDigits:
                first_half = self.textField.get()[:self.currentPos].replace(gv.CURSOR,'')
                second_half = self.textField.get()[self.currentPos:].replace(gv.CURSOR,'')
                self.textField.set(first_half + t + gv.CURSOR + second_half)
                self.currentPos += 1
            else:
                self.message.set(self.messageTooLong)
