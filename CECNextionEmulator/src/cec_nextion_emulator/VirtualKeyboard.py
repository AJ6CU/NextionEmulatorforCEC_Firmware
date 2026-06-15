#!/usr/bin/python3
#
#   Based on code available at: https://github.com/AbhiK002/virtual-keyboard
#   The license for this original code is MIT, which allows modification and redistribution under more restrictive license
#   In this case GPL V3.0
#
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import StringVar
from tkinter import messagebox
import globalvars as gv


class VirtualKeyboard(tk.Toplevel):
    def __init__(self, master=None, fieldStrVar=None, postProcessor=None, maxChars=None,  **kw):
        self.master = master
        self.fieldStrVar = fieldStrVar
        self.localStrVar = StringVar()      # we work with this local value and then write it back into the original on "enter" key
        self.postProcessor = postProcessor
        self.maxChars = maxChars

        self.localStrVar.set(self.fieldStrVar.get().replace(" ",""))        # Labels are blank padded to 5 chars
        self.currentPos = len(self.localStrVar.get())


        self.shift_status = False                   # tracks the shift key. When true, use upper case. click on/off to toggle

        self.uppercase ={                           # Used to map to upper case if shift key is on
                        "`":"~",
                        "1":"!",
                        "2":"@",
                        "3":"#",
                        "4":"$",
                        "5":"%",
                        "6":"^",
                        "7":"&",
                        "8":"*",
                        "9":"(",
                        "0":")",
                        "-":"_",
                        "=":"+",
                        "[":"{",
                        "]":"}",
                        ";":":",
                        "'":'"',
                        "\\":"|",
                        ",":"<",
                        ".":">",
                        "/":"?"
                        }



        super().__init__(self.master, **kw)
        #
        #       Two possible error messages.
        #

        self.messageTooLong = "Too Many Chars, Max = " + str(self.maxChars)
        self.messageNoBackslash = "Backslash (\\) not allowed in name"
        self.wait_visibility()      # required on Linux
        self.grab_set()                 # This line makes the window modal
        self.transient(self.master)     # Puts the keyboard on top of the underlying window that called up the keyboard
        # self.geometry(gv.VALPHAKEYBOARD_OFFSET)



        #
        #   Rows of the keyboard
        #


        self.row1keys = ["`", "1", "2", "3", "4", "5", "6", "7","8", "9", "0", "-", "=", "backspace"]
        self.row2keys = ["q", "w", "e", "r", "t", "y", 'u', 'i', 'o', 'p', '[', ']', 'enter']
        self.row3keys = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", '\\', 'home', 'end']
        self.row4keys = ["left shift", 'z', 'x', 'c', 'v', 'b', 'n', 'm',',', '.', '/', 'right shift']
        self.row5keys = ['spacebar','left', 'right']

        # buttons for each row
        self.row1buttons = []
        self.row2buttons = []
        self.row3buttons = []
        self.row4buttons = []
        self.row5buttons = []

        appendrow1 = self.row1buttons.append
        appendrow2 = self.row2buttons.append
        appendrow3 = self.row3buttons.append
        appendrow4 = self.row4buttons.append
        appendrow5 = self.row5buttons.append

        # prevents frames having inconsistent relative dimensions
        self.master.columnconfigure(0, weight=1)
        for i in range(5):
            self.master.rowconfigure(i, weight=1)

        #
        #   Row 1 Button Creation
        #

        # create a frame for row1buttons
        keyframe1 = ttk.Frame(self, height=1)
        keyframe1.rowconfigure(0, weight=1)

        # create row1buttons. special case some keys that need wider keys (like backspace)
        for key in self.row1keys:
            ind = self.row1keys.index(key)
            if key == "backspace":
                keyframe1.columnconfigure(ind, weight=2)
            else:
                keyframe1.columnconfigure(ind, weight=1)
            appendrow1(ttk.Button(keyframe1,style='Button1Raised.TButton', width=3))
            if key == "backspace":
                self.row1buttons[ind].config(text=key.title(), width=8)

            self.row1buttons[ind].grid(row=0, column=ind, sticky="NSEW", ipadx=8, ipady=8)
        #
        #   For symbol and numeric keys, add in the second level selected on shift
        #
        self.row1buttons[0].config(text="~\n`")
        self.row1buttons[1].config(text="!\n1")
        self.row1buttons[2].config(text="@\n2")
        self.row1buttons[3].config(text="#\n3")
        self.row1buttons[4].config(text="$\n4")
        self.row1buttons[5].config(text="%\n5")
        self.row1buttons[6].config(text="^\n6")
        self.row1buttons[7].config(text="&\n7")
        self.row1buttons[8].config(text="*\n8")
        self.row1buttons[9].config(text="(\n9")
        self.row1buttons[10].config(text=")\n0")
        self.row1buttons[11].config(text="_\n-")
        self.row1buttons[12].config(text="+\n=")

        #
        # Row 2 Creation
        #

        # create a frame for row2buttons
        keyframe2 = ttk.Frame(self, width=1)
        keyframe2.rowconfigure(0, weight=1)

        # create row2buttons. Special case some keys that need more space (like enter key)
        for key in self.row2keys:
            ind = self.row2keys.index(key)

            if key == "enter":              # Only Enter key needs additional weight because it is larger
                keyframe2.columnconfigure(ind, weight=2)
            else:
                keyframe2.columnconfigure(ind, weight=1)

            appendrow2(ttk.Button(keyframe2,style='Button1Raised.TButton', width=3))

            if key ==  "[":
                self.row2buttons[ind].config(text="{\n[")
            elif key == "]":
                self.row2buttons[ind].config(text="}\n]")
            elif key == "enter":
                self.row2buttons[ind].config(text="Enter", width=7)
            else:
                self.row2buttons[ind].config(text=key.title())

            self.row2buttons[ind].grid(row=0, column=ind, sticky="NSEW", ipadx=8, ipady=8)

        #
        #   Row 3 creation
        #

        # create a frame for row3buttons
        keyframe3 = ttk.Frame(self, height=1)
        keyframe3.rowconfigure(0, weight=1)

        # create row4buttons
        for key in self.row3keys:
            ind = self.row3keys.index(key)

            if key == "home" or key == "end":                   # Special case home and end that need greater size
                keyframe3.columnconfigure(ind, weight=2)
                appendrow3(ttk.Button(keyframe3,style='Button1Raised.TButton', width=4))
            else:
                keyframe3.columnconfigure(ind, weight=1)
                appendrow3(ttk.Button(keyframe3, style='Button1Raised.TButton', width=3))

            if key == ";":
                self.row3buttons[ind].config(text=":\n;")
            elif key == "'":
                self.row3buttons[ind].config(text='"\n\'')
            elif key == "\\":
                self.row3buttons[ind].config(text="|\n\\")
            else:
                self.row3buttons[ind].config(text=key.title())

            self.row3buttons[ind].grid(row=0, column=ind, sticky="NSEW", ipadx=8, ipady=8)

        #
        # Row 4 Creation
        #

        # create a frame for row4buttons
        keyframe4 = ttk.Frame(self, height=1)
        keyframe4.rowconfigure(0, weight=1)

        # create row4buttons
        for key in self.row4keys:
            ind = self.row4keys.index(key)

            if key == "left shift" or key == "right shift":     # Special case left and right movement because larger
                keyframe4.columnconfigure(ind, weight=3)
            else:
                keyframe4.columnconfigure(ind, weight=1)

            appendrow4(ttk.Button(keyframe4,style='Button1Raised.TButton', width=3))

            if key == ",":
                self.row4buttons[ind].config(text="<\n,")
            elif key == ".":
                self.row4buttons[ind].config(text=">\n.")
            elif key == "/":
                self.row4buttons[ind].config(text="?\n/")
            elif key == "up":
                self.row4buttons[ind].config(text="↑")
            elif key == "left shift":
                self.row4buttons[ind].config(text="Shift", width=6)
            elif key == "right shift":
                self.row4buttons[ind].config(text="Shift", width=6)
            else:
                self.row4buttons[ind].config(text=key.title())

            self.row4buttons[ind].grid(row=0, column=ind, sticky="NSEW", ipadx=8, ipady=8)
        #
        #   ROW 5  Creation
        #

        # create a frame for row5buttons
        keyframe5 = ttk.Frame(self, height=1)
        keyframe5.rowconfigure(0, weight=1)

        #   This row has a special entry field that displays what the user is typing. This is necessary because the
        #   keyboard is so large that on smaller screens it will overlap the window where the information will end up
        #
        self.entryField = ttk.Entry(keyframe5, style='Entry1b.TEntry',font=('Arial',18, 'italic' ), textvariable=self.localStrVar, width=40)
        keyframe5.columnconfigure(0, weight=0)


        for key in self.row5keys:
            ind = self.row5keys.index(key)

            appendrow5(ttk.Button(keyframe5, style='Button1Raised.TButton', width=3))

            if key == "spacebar":
                keyframe5.columnconfigure(ind+1, weight=12)
                self.row5buttons[ind].config(text="Space", width=15)
            elif key == "left":
                self.row5buttons[ind].config(text="\u2190", width=3)
                keyframe5.columnconfigure(ind + 1, weight=1)
            elif key == "right":
                self.row5buttons[ind].config(text="\u2192", width=3)
                keyframe5.columnconfigure(ind + 1, weight=1)
            else:
                self.row5buttons[ind].config(text=key.title(), width=3)


        self.entryField.grid(row=0, column=0, sticky="NSEW", ipadx=8, ipady=8)
        for key in self.row5keys:
            ind = self.row5keys.index(key)
            self.row5buttons[ind].grid(row=0, column=ind+1, sticky="NSEW", ipadx=8, ipady=8)



        # add the frames to the main window
        self.update()
        self.geometry(gv.VALPHAKEYBOARD_OFFSET)
        keyframe1.grid(row=1, sticky="NSEW", padx=9, pady=6)
        keyframe2.grid(row=2, sticky="NSEW", padx=9)
        keyframe3.grid(row=3, sticky="NSEW", padx=9)
        keyframe4.grid(row=4, sticky="NSEW", padx=9)
        keyframe5.grid(row=5, sticky="NSEW", padx=9)

        #
        #   Now add the callbacks for each key. Most of the time it will be just "vpresskey". But other
        #   keys like enter, left and right arrow, backspace etc. need special handling
        #

        for key in self.row1keys:
            ind = self.row1keys.index(key)
            if key == "backspace":
                self.row1buttons[ind].config(command=self.backspace)
            else:
                self.row1buttons[ind].config(command=lambda x=key: self.vpresskey(x))

        for key in self.row2keys:
            ind = self.row2keys.index(key)
            if key == "enter":
                self.row2buttons[ind].config(command=self.enter)
            else:
                self.row2buttons[ind].config(command=lambda x=key: self.vpresskey(x))


        for key in self.row3keys:
            ind = self.row3keys.index(key)
            if key == "home":
                self.row3buttons[ind].config(command=self.home)
            elif key == "end":
                self.row3buttons[ind].config(command=self.end)
            else:
                self.row3buttons[ind].config(command=lambda x=key: self.vpresskey(x))

        for key in self.row4keys:
            ind = self.row4keys.index(key)
            if key == "left shift" or key == "right shift":
                self.row4buttons[ind].config(command=self.shift)
            else:
                self.row4buttons[ind].config(command=lambda x=key: self.vpresskey(x))

        for key in self.row5keys:
            ind = self.row5keys.index(key)
            if key == "spacebar":
                self.row5buttons[ind].config(command=lambda x=key: self.vpresskey(" "))
            elif key == "left":
                self.row5buttons[ind].config(command=self.moveLeft)
            elif key == "right":
                self.row5buttons[ind].config(command=self.moveRight)
            else:
                self.row5buttons[ind].config(command=lambda x=key: self.vpresskey(x))

    #
    #   Tracks whether the keyboard is in shift mode. When clicked, it is on until unclicked
    #
    def shift (self,event=None):
        indLeft = self.row4keys.index("left shift")
        indRight = self.row4keys.index("right shift")

        if self.shift_status == True:
            self.row4buttons[indLeft].config(style='Button1Raised.TButton')
            self.row4buttons[indRight].config(style='Button1Raised.TButton')

            self.shift_status = False
        else:
            self.row4buttons[indLeft].config(style='Button1Sunken.TButton')
            self.row4buttons[indRight].config(style='Button1Sunken.TButton')

            self.shift_status = True
    #
    #   Backspace moves the cursor back one position by erasing the character to its immediate left
    #
    def backspace(self):
        if self.currentPos != 0:
            first_half = self.localStrVar.get()[:self.currentPos-1].replace(gv.CURSOR, '')
            second_half = self.localStrVar.get()[self.currentPos + 1:].replace(gv.CURSOR, '')
            self.localStrVar.set(first_half + gv.CURSOR + second_half)
            self.currentPos -= 1
    #
    #   Enter key writes the result back to the appropriate field in the parent widget
    #   Calls a function in the parent to indicate if the value is now "dirty"
    #
    def enter(self,event=None):
        # label = self.localStrVar.get().replace(gv.CURSOR, '')
        self.localStrVar.set(self.localStrVar.get().replace(gv.CURSOR, ''))
        # if self.localStrVar.get() !=self.fieldStrVar.get():
        #     self.fieldStrVar.set(self.localStrVar.get())
        #     if self.dirty_CB != None:
        #         self.dirty_CB()

        self.postProcessor(self.fieldStrVar.get(), self.localStrVar.get())
        self.destroy()
    #
    #   Moves the cursor to beginning of field
    #
    def home(self):
        label = self.localStrVar.get().replace(gv.CURSOR, "")
        self.localStrVar.set(gv.CURSOR + label)
        self.currentPos = 0
    #
    #   Moves the cursor to the end of the field
    #
    def end(self):
        label = self.localStrVar.get().replace(gv.CURSOR, "")
        self.localStrVar.set(label+gv.CURSOR)
        self.currentPos = len(self.localStrVar.get())-1
    #
    #   Moves the cursor left one character without deleting anything
    #
    def moveLeft(self):
        if self.currentPos == 0:
            return
        self.currentPos -= 1
        first_half = self.localStrVar.get()[:self.currentPos].replace(gv.CURSOR, '')
        second_half = self.localStrVar.get()[self.currentPos:].replace(gv.CURSOR, '')
        self.localStrVar.set(first_half + gv.CURSOR + second_half)
    #
    #   Moves the cursor to the right one character without adding or deleting characts
    #
    def moveRight(self):
        if self.currentPos == self.maxChars:
            return
        self.currentPos += 1
        label = self.localStrVar.get().replace(gv.CURSOR, "")
        self.localStrVar.set(label)
        first_half = self.localStrVar.get()[:self.currentPos].replace(gv.CURSOR, '')

        second_half = self.localStrVar.get()[self.currentPos:].replace(gv.CURSOR, '')

        self.localStrVar.set(first_half + gv.CURSOR + second_half)

    #
    #   Handles the pressing of a typical key. Maps lower to upper case based on setting of shift flag
    #   Forbids the entry of backslash

    def vpresskey(self,t):
        if len(self.localStrVar.get().replace(gv.CURSOR,"")) < self.maxChars:
            if t == "\\":
                warning = messagebox.showinfo("Warning", self.messageNoBackslash, parent=self)
                return

            if self.shift_status:
                if t.isalpha():
                    t=t.upper()
                else:
                    t = self.uppercase[t]

            first_half = self.localStrVar.get()[:self.currentPos].replace(gv.CURSOR,'')
            second_half = self.localStrVar.get()[self.currentPos+1:].replace(gv.CURSOR,'')
            self.localStrVar.set(first_half + t + gv.CURSOR + second_half)
            self.currentPos += 1
        else:
            warning = messagebox.showinfo("Warning", self.messageTooLong, parent=self)
