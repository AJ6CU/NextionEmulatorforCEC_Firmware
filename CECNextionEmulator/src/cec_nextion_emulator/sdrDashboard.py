#!/usr/bin/python3
"""
sdrDashboard

A small window that pops up when a sdr is connected

UI source file: sdrDashboard.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from pygubu.widgets.accordionframe import AccordionFrame
import pygubu
import random

import sdrDashboardui as baseui
import globalvars as gv

import os
from SDRPlusPlusController import SDRPlusPlusController


#
# Manual user code
#

class sdrDashboard(baseui.sdrDashboardUI):
    def __init__(self, master=None, **kw):
        self.master = master

        super().__init__(master, **kw)

        # Configure columns inside Python (Excluding obsolete filter column to save space)
        # self.builder = pygubu.Builder()

        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # ui_absolute_path = os.path.join(script_dir, "pygubu", "sdrDashboard.ui")
        # self.builder.add_from_file(ui_absolute_path)
        # 
        # self.treeChannels = self.builder.get_object("treeChannels")
        # self.treeScrollbar = self.builder.get_object("treeScrollbar")

        self.treeChannels["columns"] = ('label','frequency', 'mode', 'description')
        # self.treeChannels.config(show='headings')
        self.treeChannels.config(yscrollcommand=self.treeScrollbar.set)
        self.treeScrollbar.config(command=self.treeChannels.yview)

        # Setup column widths and text headers
        self.treeChannels.column('label', anchor='w')
        self.treeChannels.column('label', width=90, minwidth=90, stretch=tk.YES)
        self.treeChannels.column('frequency', width=75, minwidth=75, stretch=tk.YES)
        self.treeChannels.column('mode', width=40, minwidth=40, stretch=tk.YES)
        self.treeChannels.column('description', width=125, minwidth=100, stretch=tk.YES)

        self.treeChannels.heading('label', text='Channel Label', anchor='w')
        self.treeChannels.heading('frequency', text='Frequency (MHz)', anchor='w')
        self.treeChannels.heading('mode', text='Mode', anchor='w')
        self.treeChannels.heading('description', text='Station Name', anchor='w')

        # 5. Instantiate communications controller loop
        self.sdr = SDRPlusPlusController(self.master)

        # Telemetry & State variables
        self.sdr.on_frequency_change_secondary = self.update_frequency_telemetry
        self.sdr.on_mode_change_secondary = self.update_mode_telemetry
        self.currentBand = None
        self.sdr.on_filter_change = self.update_filter_telemetry
        self.is_muted = False
        self.pre_mute_volume = gv.config.get_audio_gain_level()

        # Seed initialization field parameters
        self.entry_scan_time.insert(0, str(gv.config.get_scan_station_time_ms()))
        self.sdrIPAddress_VAR.set(str(gv.config.get_sdr_server_ip()))
        self.sdrPortNumber_VAR.set(str(gv.config.get_sdr_tcp_port()))
        self.volume_scale.set(self.pre_mute_volume)
        self.label_volume_val.config(text=f"{self.pre_mute_volume}%")

        # Get persistent references to collapse and open buttons
        self.btn_expand_icon = gv.get_image("expand_40x40.png")
        self.btn_collapse_icon = gv.get_image("collapse_40x40.png")

        # Set state for accordion panels
        self.channelsAccordionState = False
        self.bandsAccordionState = True
        self.scanAccordionState = False


        self.setAccordionState(self.bandsAccordion_Frame, self.bandsToggle_Button, self.bandsAccordionState)
        self.setAccordionState(self.scanAccordion_Frame, self.scanToggle_Button, self.scanAccordionState)
        self.setAccordionState(self.channelsAccordion_Frame, self.channelsToggle_Button, self.channelsAccordionState)

        self.action_filter_reset()
        self.refresh_listbox_view()
        self.update_smeter_loop()
        self.sourceBank_Combobox.set("DEFAULT SET")

        if self.sdr.connect():
            self.linkStatus_Label.configure(
                style="GreenLED.TLabel",
                takefocus=False)
            self.linkStatus_VAR.set('Connected')
            self.reconnect_Button.state(['disabled'])

            # --- ADD THIS LINE TO FIRE TELEMETRY ON STARTUP ---
            if hasattr(self.sdr, 'current_mode') and self.sdr.current_mode:
                self.update_mode_telemetry(self.sdr.current_mode)
            else:
                self.update_mode_telemetry("USB")  # Safe hardware default if empty
        else:
            self.linkStatus_Label.configure(
                style="RedLED.TLabel",
                takefocus=False)
            self.linkStatus_VAR.set('Disconnected')
            self.reconnect_Button.state(['normal'])



        self.pack(expand=tk.YES, fill=tk.BOTH)




    def update_frequency_telemetry(self, freq_hz):
        self.current_live_vfo_hz = int(freq_hz)
        self.label_val_freq.config(text=f"{(float(freq_hz) / 1000000):.4f} MHz")
        band = self.findBand(freq_hz)
        if band == None and self.currentBand == None:
            return
        elif band != self.currentBand:
            self.showFreqButtonPressed(band)
            self.currentBand = band


    def update_mode_telemetry(self, mode_str):
        print("update_mode_telemetry", mode_str)
        self.label_val_mode.config(text=str(mode_str).upper())
        if mode_str.lower() == 'cw':
            self.showModeButtonPressed("modeCWU_Button")
        else:
            self.showModeButtonPressed("mode"+mode_str+"_Button")

    def update_filter_telemetry(self, filter_hz):
        self.current_live_filter_hz = int(filter_hz)
        self.currentFilterWidth_VAR.set(str(filter_hz))

    def update_smeter_loop(self):
        if self.sdr.is_connected:
            # 1. Process S-Meter Metrics
            dbfs_value = random.randint(45, 85) if getattr(self.sdr, 'is_scanning', False) else random.randint(15, 55)
            self.smeter_Progressbar.config(value=dbfs_value)

            if dbfs_value < 20:
                s_unit = "S1"
            elif dbfs_value < 35:
                s_unit = "S3"
            elif dbfs_value < 50:
                s_unit = "S5"
            elif dbfs_value < 65:
                s_unit = "S7"
            elif dbfs_value < 80:
                s_unit = "S9"
            elif dbfs_value < 90:
                s_unit = "+10dB"
            else:
                s_unit = "+30dB"

            raw_dbfs = -120.0 + (float(dbfs_value) * 1.2)
            self.label_smeter_ticks.config(text=f"S1 . S3 . S5 . S7 . S9 . +10 . +30 [{s_unit}]")
            self.label_smeter_val.config(text=f"Signal Strength Metrics: {raw_dbfs:.1f} dBFS")

            # 2. Passive UI Pass-through pointing to the correct object context
            if hasattr(self.sdr, 'on_filter_change') and self.sdr.on_filter_change:
                self.sdr.on_filter_change(self.sdr.get_filter_width_hz())

        else:
            self.smeter_Progressbar.config(value=0)
            self.label_smeter_ticks.config(text="S1 . S3 . S5 . S7 . S9 . +10 . +30 [OFFLINE]")
            self.label_smeter_val.config(text="Signal Strength Metrics: Offline")

        self.master.after(250, self.update_smeter_loop)

    def refresh_listbox_view(self):
        for item in self.treeChannels.get_children():
            self.treeChannels.delete(item)

        for ch in self.sdr.scan_channels:
            freq_mhz = ch.get("freq_hz", 0) / 1000000
            lbl = ch.get("label", "UNKN")
            mode = ch.get("mode", "USB")
            desc = ch.get("name", "No Station Name")
            self.treeChannels.insert('', tk.END, values=(lbl,f"{freq_mhz:.4f}", mode, desc))

        banks_list = list(self.sdr.scan_sets_dict.keys())
        self.sourceBank_Combobox['values'] = banks_list
        self.targetBank_Combobox['values'] = banks_list
        self.scanBankSelect_Combobox['values'] = banks_list

    def action_connect(self):
        gv.config.set_sdr_server_ip(self.sdrIPAddress_VAR.get().strip())
        gv.config.set_sdr_tcp_port(int(self.sdrPortNumber_VAR.get().strip()))
        # gv.config.set_sdr_server_ip(self.entry_radio_ip.get().strip())
        # gv.config.set_sdr_tcp_port(int(self.entry_radio_port.get().strip()))
        if self.sdr.connect():
            messagebox.showinfo("Success", "Successfully attached socket link to SDR++ server.")
        else:
            messagebox.showerror("Error", "SDR++ Connection refused. Verify target host profiles.")

    def action_on_volume_slider_move(self, event=None):
        try:
            current_pos = self.volume_scale.get()
            target_percentage = int(current_pos)
            self.label_volume_val.config(text=f"{target_percentage}%")
            gv.config.set_audio_gain_level(target_percentage)
            if self.sdr.is_connected and not getattr(self, 'is_muted', False):
                self.sdr.set_volume(float(target_percentage) / 100.0)
        except Exception:
            pass

    def action_toggle_mute(self):
        if not self.sdr.is_connected: return
        slider = self.volume_scale
        if not self.is_muted:
            self.pre_mute_volume = slider.get()
            if self.sdr.mute():
                self.is_muted = True
                slider.set(0)
                slider.config(state="disabled")
                self.label_volume_val.config(text="MUTED")
                self.button_mute_toggle.config(text="🔇 Unmute Audio")
        else:
            slider.config(state="normal")
            restore_vol_float = float(self.pre_mute_volume) / 100.0
            if self.sdr.unmute(restore_volume=restore_vol_float):
                self.is_muted = False
                slider.set(self.pre_mute_volume)
                self.label_volume_val.config(text=f"{int(float(self.pre_mute_volume))}%")
                self.button_mute_toggle.config(text="🔊 Mute Audio")

    def action_on_channel_row_click(self, event):
        """Dispatched when a user clicks a channel row within the memory grid."""
        if not self.sdr.is_connected:
            return

        selected_item = self.treeChannels.selection()
        if not selected_item:
            return

        row_values = self.treeChannels.item(selected_item, 'values')

        # Ensure the row contains all necessary parameters (Label, Freq, Mode, Desc)
        if row_values and len(row_values) >= 3:
            try:
                # 1. Unpack data fields and convert strings safely to native numeric types
                label_target = str(row_values[0]).strip()
                freq_mhz_str = str(row_values[1]).strip()
                mode_str = str(row_values[2]).strip().upper()

                # Convert MHz string directly back to Hz integer
                freq_hz = int(float(freq_mhz_str) * 1000000)

                # 2. Match the unique channel label against the scan database to grab its saved bandwidth
                saved_bw = 0  # Pass 0 to tell the updated set_mode to look up the current active bandwidth
                for ch in self.sdr.scan_channels:
                    if ch.get('label') == label_target:
                        # Extract saved filter configuration if it exists, otherwise default to 0 (passive tracking)
                        saved_bw = int(ch.get('filter_width_hz', 0))
                        break

                # 3. Apply the targets sequentially over the network link
                self.sdr.set_frequency_hz(freq_hz)

                # Use a Tkinter delayed wrapper to let the frequency lock clear before updating mode/bandwidth
                self.master.after(50, lambda: self.sdr.set_mode(mode_str, passband_hz=saved_bw))

            except (ValueError, IndexError) as e:
                print(f"[-] Grid selection data conversion error: {e}")

    def action_capture_live_vfo_to_channel(self):
        """Grabs current live frequency, mode, and filter bandwidth straight into active memory structures."""
        if not self.sdr.is_connected:
            messagebox.showwarning("Offline", "Please connect to the SDR++ hardware rig first.")
            return

        label_text = self.newChannel_Label.get().strip()
        desc_text = self.customStationName_Entry.get().strip()

        if not label_text:
            messagebox.showwarning("Missing Input", "Please supply a short Channel Label identifier (e.g., WX1).")
            return

        # Fetch telemetry snapshot keys from active UI layer memory cache pools
        live_freq_hz = getattr(self, 'current_live_vfo_hz', gv.config.get_last_active_frequency())
        live_mode = self.sdr.current_mode
        live_filter_hz = getattr(self, 'current_live_filter_hz', gv.config.get_sdr_filter_width_hz())
        station_name = desc_text if desc_text else "No Station Name"

        if self.sdr.add_channel(label_text, live_freq_hz, live_mode, live_filter_hz, station_name):
            self.sdr._save_channels_to_json()

            # Flush fields cleanly
            self.newChannel_Label.delete(0, tk.END)
            self.customStationName_Entry.delete(0, tk.END)

            self.refresh_listbox_view()
            messagebox.showinfo("Stored",
                                f"Saved {label_text} at {(float(live_freq_hz) / 1000000):.3f} MHz to active bank.")

    def action_filter_search_grid(self, event=None):
        """Real-time string matching lookup filtering grid rows instantly by label text or station descriptions."""
        search_query = self.channelLookup_Entry.get().strip().lower()

        for item in self.treeChannels.get_children():
            self.treeChannels.delete(item)

        for ch in self.sdr.scan_channels:
            lbl = ch.get("label", "UNKN")
            desc = ch.get("description", "No Station Name")
            freq_mhz = ch.get("freq_hz", 0) / 1000000
            mode = ch.get("mode", "WFM")

            if search_query in lbl.lower() or search_query in desc.lower():
                self.treeChannels.insert('', tk.END, values=(lbl,f"{freq_mhz:.4f}", mode, desc))

    def action_del_ch(self):
        selected = self.treeChannels.selection()
        if not selected: return
        lbl_target = self.treeChannels.item(selected, 'values')[0]
        if self.sdr.delete_channel(lbl_target):
            self.newChannel_Label.delete(0, tk.END)
            self.customStationName_Entry.delete(0, tk.END)
            self.refresh_listbox_view()

    def action_create_brand_new_bank(self):
        """Pops open an input box to create a brand-new memory bank directory file."""
        from tkinter import simpledialog
        new_bank_name = simpledialog.askstring("New Memory Bank", "Enter an identifier name for the new channel bank:")

        if not new_bank_name: return
        cleaned_name = new_bank_name.strip().upper()
        if not cleaned_name: return

        if cleaned_name in self.sdr.scan_sets_dict:
            messagebox.showwarning("Conflict", f"A bank profile named '{cleaned_name}' already exists.")
            return

        self.sdr.scan_sets_dict[cleaned_name] = []
        self.sdr.change_active_scan_set(cleaned_name)
        self.sdr._save_all_channels_to_json()

        self.refresh_listbox_view()
        self.sourceBank_Combobox.set(cleaned_name)
        self.targetBank_Combobox.set(cleaned_name)
        messagebox.showinfo("Success", f"The new channel bank profile '{cleaned_name}' is active and ready.")

    def action_on_set_dropdown_change(self, event=None):
        selected_set = self.sourceBank_Combobox.get().strip()
        if selected_set:
            self.sdr.change_active_scan_set(selected_set)
            self.refresh_listbox_view()

    def action_copy_row_to_target_bank(self):
        """Copies highlighted single row item instantly into target dropdown selector destination bank."""
        selected = self.treeChannels.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please click a channel row from the grid first.")
            return

        target_bank = self.targetBank_Combobox.get().strip()
        if not target_bank or target_bank not in self.sdr.scan_sets_dict:
            messagebox.showwarning("Invalid Target", "Please pick a valid Target Bank profile from the dropdown.")
            return

        lbl_target = self.treeChannels.item(selected, option="values")[0]

        matched_ch = None
        for ch in self.sdr.scan_channels:
            if ch.get('label') == lbl_target:
                matched_ch = ch.copy()
                break

        if matched_ch:
            self.sdr.scan_sets_dict[target_bank] = [c for c in self.sdr.scan_sets_dict[target_bank] if
                                                    c.get('label') != lbl_target]
            self.sdr.scan_sets_dict[target_bank].append(matched_ch)
            self.sdr._save_all_channels_to_json()
            messagebox.showinfo("Linked", f"Successfully duplicated entry '{lbl_target}' into bank '{target_bank}'.")

    def action_bulk_clone_source_to_target(self):
        """Deep-copies ALL channel rows from current source dropdown directly into target bank menu selection."""
        source_bank = self.sourceBank_Combobox.get().strip()
        target_bank = self.targetBank_Combobox.get().strip()

        if not source_bank or source_bank not in self.sdr.scan_sets_dict:
            messagebox.showwarning("Selection Required", "Please choose a valid Source Bank View to copy from.")
            return
        if not target_bank or target_bank not in self.sdr.scan_sets_dict:
            messagebox.showwarning("Selection Required", "Please choose a valid Target Bank Copy to populate.")
            return
        if source_bank == target_bank:
            messagebox.showwarning("Identical Banks", "Source and Target banks are the same. Bulk clone skipped.")
            return

        confirm = messagebox.askyesno(
            "Confirm Bulk Bank Copy",
            f"Are you sure you want to copy ALL channels from bank '{source_bank}' into bank '{target_bank}'?"
        )
        if not confirm: return

        source_list = self.sdr.scan_sets_dict[source_bank]
        target_list = self.sdr.scan_sets_dict[target_bank]

        merged_dict = {ch.get('label'): ch.copy() for ch in target_list}
        for ch in source_list:
            merged_dict[ch.get('label')] = ch.copy()

        self.sdr.scan_sets_dict[target_bank] = list(merged_dict.values())
        self.sdr.change_active_scan_set(target_bank)
        self.sdr._save_all_channels_to_json()

        self.refresh_listbox_view()
        self.sourceBank_Combobox.set(target_bank)
        self.targetBank_Combobox.set(target_bank)
        messagebox.showinfo("Success", f"Successfully cloned all channels from '{source_bank}' into '{target_bank}'!")

    def action_delete_source_bank_profile(self):
        """Permanently erases whatever profile bank is active inside the SOURCE VIEW dropdown window."""
        source_bank = self.sourceBank_Combobox.get().strip()

        if not source_bank:
            messagebox.showwarning("Selection Required",
                                   "Please pick a bank from the 'Source Bank View' dropdown menu to delete.")
            return
        if source_bank in ["DEFAULT SET", "DEFAULT"]:
            messagebox.showwarning("Prohibited Action",
                                   "The core 'DEFAULT SET' repository is permanent and cannot be erased.")
            return

        confirm = messagebox.askyesno(
            "Confirm Source Bank Erasure",
            f"CRITICAL WARNING:\n\nYou are about to permanently delete the bank channel registry: '{source_bank}'\n"
            f"This will erase this bank and ALL channels currently visible inside your grid list!\n\n"
            f"Are you absolutely sure you want to delete this SOURCE bank?"
        )
        if not confirm: return

        if source_bank in self.sdr.scan_sets_dict:
            del self.sdr.scan_sets_dict[source_bank]

        fallback_set = "DEFAULT SET"
        self.sdr.change_active_scan_set(fallback_set)
        self.sdr._save_all_channels_to_json()

        self.refresh_listbox_view()
        self.sourceBank_Combobox.set(fallback_set)
        self.targetBank_Combobox.set(fallback_set)
        messagebox.showinfo("Success", f"The Source Bank repository '{source_bank}' has been successfully erased.")

    def action_start_scan(self):
        try:
            delay = int(self.entry_scan_time.get().strip())
            gv.config.set_scan_station_time_ms(delay)
            self.sdr.start_memory_scan(delay)
        except ValueError:
            messagebox.showwarning("Warning", "Invalid timing threshold configuration value.")

    def stop_scan(self):
        self.sdr.stop_scan()

    def findBand(self,freq):
        for key in gv.bandStart:
            if gv.bandStart[key] <= freq <= gv.bandEnd[key]:
                return key
        return None


    def showFreqButtonPressed(self, widget_id):
        #
        #   Unpress all the buttons
        #
        self.Band160m.configure(style='Button3Raised.TButton')
        self.Band80m.configure(style='Button3Raised.TButton')
        self.Band40m.configure(style='Button3Raised.TButton')
        self.Band30m.configure(style='Button3Raised.TButton')
        self.Band20m.configure(style='Button3Raised.TButton')
        self.Band17m.configure(style='Button3Raised.TButton')
        self.Band15m.configure(style='Button3Raised.TButton')
        self.Band12m.configure(style='Button3Raised.TButton')
        self.Band10m.configure(style='Button3Raised.TButton')
        #
        #   Show button pressed
        #
        if widget_id != None:
            getattr(self, widget_id).configure(style='Button3Pressed.TButton')

    def action_quick_band(self, widget_id):
        if not self.sdr.is_connected: return

        self.showFreqButtonPressed(widget_id)

        match widget_id:
            case 'Band160m':
                self.sdr.set_frequency_hz(1800000)
                self.sdr.set_mode("LSB")

            case 'Band80m':
                self.sdr.set_frequency_hz(3500000)
                self.sdr.set_mode("LSB")

            case 'Band40m':
                self.sdr.set_frequency_hz(7000000)
                self.sdr.set_mode("LSB")

            case 'Band30m':
                self.sdr.set_frequency_hz(10100000)
                self.sdr.set_mode("LSB")

            case 'Band20m':
                self.sdr.set_frequency_hz(14000000)
                self.sdr.set_mode("USB")

            case 'Band17m':
                self.sdr.set_frequency_hz(18000000)
                self.sdr.set_mode("USB")

            case 'Band15m':
                self.sdr.set_frequency_hz(21000000)
                self.sdr.set_mode("USB")

            case 'Band12m':
                self.sdr.set_frequency_hz(24000000)
                self.sdr.set_mode("USB")

            case 'Band10m':
                self.sdr.set_frequency_hz(28000000)
                self.sdr.set_mode("USB")
    def showModeButtonPressed(self, widget_id):
        #
        #   Unpress all the buttons
        #
        self.modeLSB_Button.configure(style='Button3Raised.TButton')
        self.modeUSB_Button.configure(style='Button3Raised.TButton')
        self.modeCWL_Button.configure(style='Button3Raised.TButton')
        self.modeCWU_Button.configure(style='Button3Raised.TButton')
        #
        #   Show button pressed
        #
        getattr(self, widget_id).configure(style='Button3Pressed.TButton')

    def action_quick_mode(self, widget_id):
        if not self.sdr.is_connected: return

        self.showModeButtonPressed(widget_id)

        getattr(self, widget_id).configure(style='Button3Pressed.TButton')

        match widget_id:
            case "modeLSB_Button":
                self.sdr.set_mode("LSB")

            case "modeUSB_Button":
                self.sdr.set_mode("USB")

            case "modeCWL_Button":
                self.sdr.set_mode("CW")

            case "modeCWU_Button":
                self.sdr.set_mode("CW")


    def action_filter_widen(self):
        if not self.sdr.is_connected: return
        self.sdr.widen()

    def action_filter_narrow(self):

        if not self.sdr.is_connected: return
        self.sdr.narrow()

    def action_filter_reset(self):
        if not self.sdr.is_connected: return
        mode = self.sdr.current_mode
        fallbacks = self.sdr.get_all_mode_fallbacks()
        self.sdr.set_filter_width_hz(fallbacks.get(mode, 120000))

    def setAccordionState(self, content_frame, thebutton, frameState):
        parent_frame = content_frame.master
        if frameState:
            # content_frame.grid()
            thebutton.config(image=self.btn_expand_icon,compound="left")

            # Dynamically fetch the current row index
            content_frame.hidden=False
            # parent_frame.rowconfigure(row_num, weight=1)
        else:
            # CRITICAL: Get row index BEFORE hiding the frame
            # row_num = content_frame.grid_info().get("row", 1)
            content_frame.hidden=True
            # content_frame.grid_remove()
            thebutton.config(image=self.btn_collapse_icon, compound="left")
            # Collapse the correct row index
            # parent_frame.rowconfigure(row_num, weight=0, minsize=0, pad=0)



    def toggleScan_CB(self):
        if self.scanAccordionState:
            self.scanAccordionState = False

        else:
            self.scanAccordionState = True
        self.setAccordionState(self.scanAccordion_Frame,self.scanToggle_Button,self.scanAccordionState)

    def toggleBands_CB(self):
        if self.bandsAccordionState:
            self.bandsAccordionState = False
        else:
            self.bandsAccordionState = True
        self.setAccordionState(self.bandsAccordion_Frame, self.bandsToggle_Button, self.bandsAccordionState)

    def toggleChannels_CB(self):
        if self.channelsAccordionState:
            self.channelsAccordionState = False
        else:
            self.channelsAccordionState = True
        self.setAccordionState(self.channelsAccordion_Frame,self.channelsToggle_Button, self.channelsAccordionState)


class SDRDashboardPopup:
    def __init__(self, parent_window):
        # 1. Create a dedicated popup window layer bound to the main app
        self.popup = tk.Toplevel(parent_window)
        self.popup.title("SDR++ Memory Matrix Console")
        self.popup.geometry("575x800")

        # 2. Force modal focus (Stops user from clicking back to the main app until closed)
        self.popup.transient(parent_window)
        # self.popup.grab_set()

        # 3. Instantiate your UI application frame right inside this popup window container
        self.app = sdrDashboard(self.popup)

        # 4. Clean up background hooks instantly if the user closes the popup window
        self.popup.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_app(self):
        """Returns the memory handle pointer to the core dashboard application."""
        return self.app.sdr

    def on_close(self):
        """Ensures scanning timer engines freeze quietly when the window disappears."""
        try:
            self.app.sdr.stop_scan()  # Halt active backgrounds
        except Exception:
            pass
        self.popup.destroy()  # Close window container safely


def launch_sdr_popup(parent):
    """The master trigger hook called by your primary application driver."""
    return SDRDashboardPopup(parent)
