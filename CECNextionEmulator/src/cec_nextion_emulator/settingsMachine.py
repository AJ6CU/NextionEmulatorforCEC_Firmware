#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import settingsMachineui as baseui
from configuration import configuration
import globalvars as gv
from VirtualNumericKeyboard import VirtualNumericKeyboard
from tkinter import messagebox


#
# Manual user code
#

class settingsMachine(baseui.settingsMachineUI):
    def __init__(self, master=None, mainWindow=None, **kw):
        self.master = master
        self.mainWindow = mainWindow
        #
        #   Create a toplevel window to contain the settings popup
        #
        self.popup = tk.Toplevel(self.master)

        super().__init__(self.popup, **kw)

        self.MCU_Command_Headroom_Spinbox.configure(values=gv.MCU_Headroom_Values)
        self.MCU_Update_Period_Spinbox.configure(values=gv.Frequency_To_Run_UX_loop)
        self.MCU_Read_Wait_Period_Spinbox.configure(values=gv.MCU_Read_Completion_Wait_Period)


        self.saveDSP_Enable = gv.config.get_DSP_Switch()

        self.savePWR_SWR_Switch = gv.config.get_PWR_SWR_Switch()
        self.savePWR_Factor = gv.config.get_PWR_Factor()
        self.saveSWR_Factor = gv.config.get_SWR_Factor()

        self.saveMCU_Command_Headroom = int(gv.config.get_MCU_Command_Headroom()*1000)
        self.saveMCU_Update_Period = gv.config.get_MCU_Update_Period()
        self.saveMCU_Read_Wait_Period = gv.config.get_MCU_Read_Wait_Period()

        self.PWR_SWR_Enable_VAR.set(self.savePWR_SWR_Switch)
        formatted_factor = self.savePWR_Factor.replace(".",gv.config.get_NUMBER_DELIMITER())
        self.PWR_Factor_VAR.set(formatted_factor)

        formatted_factor = self.saveSWR_Factor.replace(".", gv.config.get_NUMBER_DELIMITER())
        self.SWR_Factor_VAR.set(formatted_factor)

        if self.PWR_SWR_Enable_VAR.get() == 'False':
            self.disablePWR_SWR_CB()
        else:
            self.enablePWR_SWR_CB()


        self.DSP_Enable_VAR.set(self.saveDSP_Enable)
        self.MCU_Command_Headroom_VAR.set(str(self.saveMCU_Command_Headroom))
        self.MCU_Update_Period_VAR.set(str(self.saveMCU_Update_Period))
        self.MCU_Read_Wait_Period_VAR.set(str(int(self.saveMCU_Read_Wait_Period*1000)))

        if self.mainWindow.DSPFound:
            self.DSP_Enable_Label.configure(state="normal")
            self.DSP_Enable_Menubutton.configure(state="normal")
            self.DSPMessage_VAR.set("")
        else:
            self.DSP_Enable_Label.configure(state="disabled")
            self.DSP_Enable_Menubutton.configure(state="disabled")
            self.DSPMessage_VAR.set("No DSP Found on startup. Option automatically disabled")

        #
        #   Can now kickoff the UX
        #

        self.initUX()

    def initUX(self):
        self.popup.title("Machine Settings - Advanced Usage Only")
        self.popup.geometry(gv.POPUP_WINDOW_OFFSET)

        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)

    def selectDSP_On_CB(self):
        self.DSP_Enable_VAR.set('True')

    def selectDSP_Off_CB(self):
        self.DSP_Enable_VAR.set('False')

    def enablePWR_SWR_CB(self):
        self.PWR_SWR_Enable_VAR.set("True")
        self.PWR_Factor_Label.configure(state="normal")
        self.SWR_Factor_Label.configure(state="normal")
        self.PWR_Factor_Entry.configure(state="normal")
        self.SWR_Factor_Entry.configure(state="normal")

    def disablePWR_SWR_CB(self):
        self.PWR_SWR_Enable_VAR.set("False")
        self.PWR_Factor_Label.configure(state="disabled")
        self.SWR_Factor_Label.configure(state="disabled")
        self.PWR_Factor_Entry.configure(state="disabled")
        self.SWR_Factor_Entry.configure(state="disabled")

    def PWR_Factor_Validation_CB(self, p_entry_value, v_condition):
        if (v_condition == "focusout") and (gv.config.get_Virtual_Keyboard_Switch() == "False"):
            std_float_str = p_entry_value.replace(",",".")
            if std_float_str.replace(".","").isdecimal():
                if  std_float_str.count(".") <=1:
                    if 10.0 >= float(std_float_str) >= 0.1:
                        return True
                    else:
                        # Bad factor entered, generate warning message and reset
                        messagebox.showinfo("Error Factor Out of bounds",
                                            "PWR Factor must be a number in the range of 0.1 to 10.0 \n\n Reset to Prior value.", parent=self)
                else:
                    messagebox.showinfo("Error Bad Number",
                                        "Number included more than one decimal points \n\n Reset to Prior value.", parent=self)
            else:
                messagebox.showinfo("Error Bad Number", "No a valid decimal number \n\n Reset to Prior value.", parent=self)

            self.PWR_Factor_VAR.set(self.PWR_Entered_Saved)
            return False
        else:
            return True

    def PWR_Factor_Entered_CB(self, event=None):
        self.PWR_Entered_Saved = self.PWR_Factor_VAR.get()          # Save the pre-edited version
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vNumericPad = VirtualNumericKeyboard(self, self.PWR_Factor_VAR, self.PWR_Changed_CB, 4, False)

    def PWR_Changed_CB(self, event=None):
        if float(self.PWR_Factor_VAR.get().replace(",",".")) > 10.0 or float(self.PWR_Factor_VAR.get().replace(",",".")) < 0.1:
            messagebox.showinfo("Error Factor Out of bounds", "PWR Factor must be in range 0.1 to 10.0 \n\n Reset to Prior value.", parent=self)
            self.PWR_Factor_VAR.set(self.PWR_Entered_Saved)

    def SWR_Changed_CB(self, event=None):
        if float(self.SWR_Factor_VAR.get().replace(",",".")) > 10.0 or float(self.SWR_Factor_VAR.get().replace(",",".")) < 0.1:
            messagebox.showinfo("Error Factor Out of bounds",
                                "SWR Factor must be in range 0.1 to 10.0 \n\n Reset to Prior value.", parent=self)
            self.SWR_Factor_VAR.set(self.SWR_Entered_Saved)

    def SWR_Factor_Validation_CB(self, p_entry_value, v_condition):

        if (v_condition == "focusout") and (gv.config.get_Virtual_Keyboard_Switch() == "False"):
            std_float_str = p_entry_value.replace(",", ".")
            if std_float_str.replace(".", "").isdecimal():
                if std_float_str.count(".") <= 1:
                    if 10.0 >= float(std_float_str) >= 0.1:
                        return True
                    else:
                        # Bad factor entered, generate warning message and reset
                        messagebox.showinfo("Error Factor Out of bounds",
                                            "SWR Factor must be a number in the range of 0.1 to 10.0 \n\n Reset to Prior value.",
                                            parent=self)
                else:
                    messagebox.showinfo("Error Bad Number",
                                        "Number included more than one decimal points \n\n Reset to Prior value.",
                                        parent=self)
            else:
                messagebox.showinfo("Error Bad Number", "No a valid decimal number \n\n Reset to Prior value.",
                                    parent=self)

            self.SWR_Factor_VAR.set(self.SWR_Entered_Saved)
            return False
        else:
            return True

    def SWR_Factor_Entered_CB(self, event=None):
        self.SWR_Entered_Saved = self.SWR_Factor_VAR.get()  # Save the pre-edited version
        if gv.config.get_Virtual_Keyboard_Switch() == "True":
            self.vNumericPad = VirtualNumericKeyboard(self, self.SWR_Factor_VAR, self.SWR_Changed_CB, 4, False)

    def apply_CB(self):
        if self.DSP_Enable_VAR.get() != self.saveDSP_Enable:
            gv.config.set_DSP_Switch(self.DSP_Enable_VAR.get())
            print('changing DSP_Switch, new setting is', gv.config.get_DSP_Switch(), self.DSP_Enable_VAR.get())
            self.mainWindow.theRadio.Set_DSP_State(self.DSP_Enable_VAR.get())

            if self.DSP_Enable_VAR.get() == "True":
                self.mainWindow.highlightCWorSpectrumBoxes(True)
            else:
                self.mainWindow.highlightCWorSpectrumBoxes(False)


        if self.PWR_SWR_Enable_VAR.get() != self.savePWR_SWR_Switch:
            gv.config.set_PWR_SWR_Switch(self.PWR_SWR_Enable_VAR.get())

        if self.PWR_Factor_Entry.get() != self.savePWR_Factor:
            formatted_factor = self.PWR_Factor_Entry.get().replace(",", ".")
            gv.config.set_PWR_Factor(formatted_factor)

        if self.SWR_Factor_Entry.get() != self.saveSWR_Factor:
            formatted_factor = self.SWR_Factor_Entry.get().replace(",", ".")
            gv.config.set_SWR_Factor(formatted_factor)


        if int(self.MCU_Command_Headroom_VAR.get()) != self.saveMCU_Command_Headroom:
            gv.config.set_MCU_Command_Headroom(int(self.MCU_Command_Headroom_VAR.get())/1000)


        if int(self.MCU_Update_Period_VAR.get()) != self.saveMCU_Update_Period:
            gv.config.set_MCU_Update_Period(int(self.MCU_Update_Period_VAR.get()))

        if int(self.MCU_Read_Wait_Period_VAR.get()) != self.saveMCU_Read_Wait_Period:
            gv.config.set_MCU_Read_Wait_Period(int(self.MCU_Read_Wait_Period_VAR.get())/1000)

        self.master.destroy()

    def cancel_CB(self):
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsMachine(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
