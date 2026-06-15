import re
from VirtualNumericKeyboard import VirtualNumericKeyboard
from VirtualKeyboard import VirtualKeyboard
import tkinter as tk
import tkinter.ttk as ttk
import globalvars as gv

class entryFieldHandler:
    def __init__(self, parent, widget_name, fieldWidth, vkeyboard, nextWidget=None, **kw):
        self.parent = parent
        self.widget_name = widget_name
        self.fieldWidth = fieldWidth
        self.vkeyboard = vkeyboard
        self.nextWidget = nextWidget

        #
        #   Inferred/required methods
        #
        self.widget = getattr(self.parent, self.widget_name + "_Entry")
        self.widget_VAR = getattr(self.parent, self.widget_name + "_VAR")
        self.validationCallback = getattr(self.parent, self.widget_name + "_validation")
        self.errorHandlerCallback = getattr(self.parent, self.widget_name + "_errorHandler")
        self.preProcessorCallback = getattr(self.parent, self.widget_name + "_preProcessor")
        self.postProcessorCallback = getattr(self.parent, self.widget_name + "_postProcessor")

        self.widget.bind("<FocusIn>", self.focusInHandler)
        self.widget.bind("<FocusOut>",self.focusOutHandler)

        self.saveVAR = None

    def focusInHandler(self, event):

        self.saveVAR= self.widget_VAR.get()
        self.widget_VAR.set(self.preProcessorCallback())

        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.widget.unbind("<FocusOut>")    # necessary to avoid generating focusout with virtual keyboard
            self.vKeyboard = self.vkeyboard(self.parent, self.widget_VAR, self.keyboardClosed, self.fieldWidth)



    def focusOutHandler(self, event):

        if (self.validationCallback()):
            self.postProcessorCallback()        #   Perform any post processing of values
            #
            #   Set focus to next logical widget
            #
            self._manageFocus(self.nextWidget)   # this is the problem call

        else:
            self.widget.unbind("<FocusIn>")            #   Need to unbind to avoid focus in on return
            self.widget.unbind("<FocusOut>")           #   from error handling


            self.errorHandlerCallback()         # Generate error message and clean up things
            self._restoreSaveValue()
            #
            #   Reset focus to end of entry field
            #

            self.widget.bind("<FocusIn>", self.focusInHandler)
            self.widget.bind("<FocusOut>", self.focusOutHandler)

            self._manageFocus(self.widget)


    def keyboardClosed(self, origValue, newValue):
        self.widget_VAR.set(newValue)

        self.widget.bind("<FocusOut>", self.focusOutHandler)
        self.widget.event_generate("<FocusOut>")


    def _manageFocus(self,target):

        target.focus_set()
        # target.event_generate("<FocusIn>")



    def _restoreSaveValue(self):
        self.widget_VAR.set(self.saveVAR)


