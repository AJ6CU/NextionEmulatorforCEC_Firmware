import tkinter as tk
from tkinter import ttk, messagebox
import pygubu
import random
import globalvars as gv
from SDRPlusPlusController import SDRPlusPlusController


class LabeledSDRDashboardApp:
    def __init__(self, root):
        self.root = root

        # 1. Initialize Pygubu layout builder targeting your local UI template
        self.builder = pygubu.Builder()
        self.builder.add_from_file('./pygubu/main_dashboard.ui')
        self.main_window = self.builder.get_object('main_frame', root)

        # 2. Extract configuration input field widgets from XML template
        self.ent_scan_time = self.builder.get_object('ent_scan_time')
        self.ent_label = self.builder.get_object('ent_label')
        self.ent_desc = self.builder.get_object('ent_desc')
        self.ent_search = self.builder.get_object('ent_search')
        self.combobox_sets = self.builder.get_object('combobox_sets')  # Source Bank dropdown
        self.combobox_target_sets = self.builder.get_object('combobox_target_sets')  # Target Bank dropdown
        self.ent_radio_ip = self.builder.get_object('ent_radio_ip')
        self.ent_radio_port = self.builder.get_object('ent_radio_port')
        self.ent_force_bw = self.builder.get_object('ent_force_bw')

        # 3. Extract live tracking telemetry, Audio, & S-Meter components
        self.lbl_val_freq = self.builder.get_object('lbl_val_freq')
        self.lbl_val_mode = self.builder.get_object('lbl_val_mode')
        self.smeter_bar = self.builder.get_object('smeter_bar')
        self.lbl_smeter_ticks = self.builder.get_object('lbl_smeter_ticks')
        self.lbl_smeter_val = self.builder.get_object('lbl_smeter_val')
        self.scale_volume = self.builder.get_object('scale_volume')
        self.lbl_volume_val = self.builder.get_object('lbl_volume_val')
        self.btn_mute_toggle = self.builder.get_object('btn_mute_toggle')

        # 4. Configure Scrollable Data Grid Columns
        self.tree_channels = self.builder.get_object('tree_channels')
        self.tree_scroll = self.builder.get_object('tree_scroll')

        # Configure columns inside Python (Excluding obsolete filter column to save space)
        self.tree_channels.config(columns=('frequency', 'mode', 'description'))
        self.tree_channels.config(show='tree headings')
        self.tree_channels.config(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.config(command=self.tree_channels.yview)

        # Setup column widths and text headers
        self.tree_channels.column('#0', width=110, minwidth=90, stretch=tk.YES)
        self.tree_channels.column('frequency', width=120, minwidth=100, stretch=tk.YES)
        self.tree_channels.column('mode', width=70, minwidth=60, stretch=tk.YES)
        self.tree_channels.column('description', width=220, minwidth=150, stretch=tk.YES)

        self.tree_channels.heading('#0', text='Channel Label', anchor='w')
        self.tree_channels.heading('frequency', text='Frequency (MHz)', anchor='w')
        self.tree_channels.heading('mode', text='Mode', anchor='w')
        self.tree_channels.heading('description', text='Station Name', anchor='w')

        # 5. Instantiate communications controller loop
        self.sdr = SDRPlusPlusController(self.root)

        # 6. EXPLICIT BUTTON AND INTERFACE ACTION BINDINGS
        self.builder.get_object('btn_connect').config(command=self.action_connect)
        self.builder.get_object('btn_delete').config(command=self.action_del_ch)
        self.builder.get_object('btn_start_scan').config(command=self.action_start_scan)
        self.builder.get_object('btn_stop_scan').config(command=self.sdr.stop_scan)
        self.builder.get_object('btn_filter_widen').config(command=self.action_filter_widen)
        self.builder.get_object('btn_filter_narrow').config(command=self.action_filter_narrow)
        self.builder.get_object('btn_filter_reset').config(command=self.action_filter_reset)
        self.builder.get_object('btn_force_bw').config(command=self.action_master_force_bw)
        self.btn_mute_toggle.config(command=self.action_toggle_mute)

        # Bind the advanced live capture, row copy, source deletion, and bulk clone buttons
        self.builder.get_object('btn_add_channel').config(command=self.action_capture_live_vfo_to_channel)
        self.builder.get_object('btn_add_to_bank').config(command=self.action_copy_row_to_target_bank)
        self.builder.get_object('btn_delete_bank').config(command=self.action_delete_source_bank_profile)
        self.builder.get_object('btn_new_bank').config(command=self.action_create_brand_new_bank)
        self.builder.get_object('btn_clone_bank').config(command=self.action_bulk_clone_source_to_target)

        # Attach real-time key release loop to the lookup search entry field box
        self.ent_search.bind('<KeyRelease>', self.action_filter_search_grid)

        # Dropdown selection listener and volume slider mouse tracking bindings
        self.combobox_sets.bind("<<ComboboxSelected>>", self.action_on_set_dropdown_change)
        self.scale_volume.bind("<B1-Motion>", self.action_on_volume_slider_move)
        self.scale_volume.bind("<ButtonRelease-1>", self.action_on_volume_slider_move)
        self.tree_channels.bind('<<TreeviewSelect>>', self.action_on_channel_row_click)

        # Ham Bands Matrix quick configuration lookups
        self.builder.get_object('btn_band_80m').config(command=lambda: self.action_quick_band(3500000, "LSB"))
        self.builder.get_object('btn_band_40m').config(command=lambda: self.action_quick_band(7000000, "LSB"))
        self.builder.get_object('btn_band_20m').config(command=lambda: self.action_quick_band(14000000, "USB"))
        self.builder.get_object('btn_band_2m').config(command=lambda: self.action_quick_band(144200000, "USB"))

        # Telemetry & State variables
        self.sdr.on_frequency_change = self.update_frequency_telemetry
        self.sdr.on_mode_change = self.update_mode_telemetry
        self.sdr.on_filter_change = self.update_filter_telemetry
        self.is_muted = False
        self.pre_mute_volume = gv.config.get_audio_gain_level()

        # Seed initialization field parameters
        self.ent_scan_time.insert(0, str(gv.config.get_scan_station_time_ms()))
        self.ent_radio_ip.insert(0, str(gv.config.get_sdr_server_ip()))
        self.ent_radio_port.insert(0, str(gv.config.get_sdr_tcp_port()))
        self.scale_volume.set(self.pre_mute_volume)
        self.lbl_volume_val.config(text=f"{self.pre_mute_volume}%")

        self.refresh_listbox_view()
        self.update_smeter_loop()

    def update_frequency_telemetry(self, freq_hz):
        self.current_live_vfo_hz = int(freq_hz)
        self.lbl_val_freq.config(text=f"{(float(freq_hz) / 1000000):.4f} MHz")

    def update_mode_telemetry(self, mode_str):
        self.lbl_val_mode.config(text=str(mode_str).upper())

    def update_filter_telemetry(self, filter_hz):
        self.current_live_filter_hz = int(filter_hz)

    def action_capture_live_vfo_to_channel(self):
        """Grabs current live frequency, mode, and filter bandwidth straight into active memory structures."""
        if not self.sdr.is_connected:
            messagebox.showwarning("Offline", "Please connect to the SDR++ hardware rig first.")
            return

        label_text = self.ent_label.get().strip()
        desc_text = self.ent_desc.get().strip()

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
            self.ent_label.delete(0, tk.END)
            self.ent_desc.delete(0, tk.END)

            self.refresh_listbox_view()
            messagebox.showinfo("Stored",
                                f"Saved {label_text} at {(float(live_freq_hz) / 1000000):.3f} MHz to active bank.")

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
        self.combobox_sets.set(cleaned_name)
        self.combobox_target_sets.set(cleaned_name)
        messagebox.showinfo("Success", f"The new channel bank profile '{cleaned_name}' is active and ready.")

    def action_copy_row_to_target_bank(self):
        """Copies highlighted single row item instantly into target dropdown selector destination bank."""
        selected = self.tree_channels.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please click a channel row from the grid first.")
            return

        target_bank = self.combobox_target_sets.get().strip()
        if not target_bank or target_bank not in self.sdr.scan_sets_dict:
            messagebox.showwarning("Invalid Target", "Please pick a valid Target Bank profile from the dropdown.")
            return

        lbl_target = self.tree_channels.item(selected, 'text')

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
        source_bank = self.combobox_sets.get().strip()
        target_bank = self.combobox_target_sets.get().strip()

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
        self.combobox_sets.set(target_bank)
        self.combobox_target_sets.set(target_bank)
        messagebox.showinfo("Success", f"Successfully cloned all channels from '{source_bank}' into '{target_bank}'!")

    def action_delete_source_bank_profile(self):
        """Permanently erases whatever profile bank is active inside the SOURCE VIEW dropdown window."""
        source_bank = self.combobox_sets.get().strip()

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
        self.combobox_sets.set(fallback_set)
        self.combobox_target_sets.set(fallback_set)
        messagebox.showinfo("Success", f"The Source Bank repository '{source_bank}' has been successfully erased.")

    def action_filter_search_grid(self, event=None):
        """Real-time string matching lookup filtering grid rows instantly by label text or station descriptions."""
        search_query = self.ent_search.get().strip().lower()

        for item in self.tree_channels.get_children():
            self.tree_channels.delete(item)

        for ch in self.sdr.scan_channels:
            lbl = ch.get("label", "UNKN")
            desc = ch.get("description", "No Station Name")
            freq_mhz = ch.get("freq_hz", 0) / 1000000
            mode = ch.get("mode", "WFM")

            if search_query in lbl.lower() or search_query in desc.lower():
                self.tree_channels.insert('', tk.END, text=lbl, values=(f"{freq_mhz:.4f}", mode, desc))

    def action_on_channel_row_click(self, event):
        if not self.sdr.is_connected: return
        selected_item = self.tree_channels.selection()
        if not selected_item: return

        row_values = self.tree_channels.item(selected_item, 'values')
        if row_values and len(row_values) >= 2:
            try:
                freq_hz = int(float(row_values) * 1000000)
                mode_str = str(row_values).strip()
                self.sdr.set_frequency_hz(freq_hz)
                self.root.after(50, lambda: self.sdr.set_mode(mode_str))
            except Exception:
                pass

    def update_smeter_loop(self):
        if self.sdr.is_connected:
            dbfs_value = random.randint(45, 85) if getattr(self.sdr, 'is_scanning', False) else random.randint(15, 55)
            self.smeter_bar.config(value=dbfs_value)
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
            self.lbl_smeter_ticks.config(text=f"S1 . S3 . S5 . S7 . S9 . +10 . +30  [{s_unit}]")
            self.lbl_smeter_val.config(text=f"Signal Strength Metrics: {raw_dbfs:.1f} dBFS")
        else:
            self.smeter_bar.config(value=0)
            self.lbl_smeter_ticks.config(text="S1 . S3 . S5 . S7 . S9 . +10 . +30  [OFFLINE]")
            self.lbl_smeter_val.config(text="Signal Strength Metrics: Offline")
        self.root.after(250, self.update_smeter_loop)

    def action_connect(self):
        gv.config.set_sdr_server_ip(self.ent_radio_ip.get().strip())
        gv.config.set_sdr_tcp_port(int(self.ent_radio_port.get().strip()))
        if self.sdr.connect():
            messagebox.showinfo("Success", "Successfully attached socket link to SDR++ server.")
        else:
            messagebox.showerror("Error", "SDR++ Connection refused. Verify target host profiles.")

    def action_start_scan(self):
        try:
            delay = int(self.ent_scan_time.get().strip())
            gv.config.set_scan_station_time_ms(delay)
            self.sdr.start_memory_scan(delay)
        except ValueError:
            messagebox.showwarning("Warning", "Invalid timing threshold configuration value.")

    def action_quick_band(self, freq_hz, mode_str):
        if not self.sdr.is_connected: return
        self.sdr.set_frequency_hz(freq_hz)
        self.sdr.set_mode(mode_str)

    def action_filter_widen(self):
        if not self.sdr.is_connected: return
        current_bw = self.sdr.get_filter_width_hz()
        new_bw = current_bw + 500 if current_bw < 20000 else current_bw + 5000
        self.sdr.set_filter_width_hz(min(250000, new_bw))

    def action_filter_narrow(self):
        if not self.sdr.is_connected: return
        current_bw = self.sdr.get_filter_width_hz()
        new_bw = current_bw - 500 if current_bw <= 20000 else current_bw - 5000
        self.sdr.set_filter_width_hz(max(50, new_bw))

    def action_filter_reset(self):
        if not self.sdr.is_connected: return
        mode = self.sdr.current_mode
        fallbacks = self.sdr.get_all_mode_fallbacks()
        self.sdr.set_filter_width_hz(fallbacks.get(mode, 120000))

    def action_master_force_bw(self):
        if not self.sdr.is_connected: return
        try:
            target_bw = int(self.ent_force_bw.get().strip())
            self.sdr.set_filter_width_hz(target_bw)
        except ValueError:
            messagebox.showwarning("Warning", "Forced bandwidth window must be an integer.")

    def action_on_volume_slider_move(self, event=None):
        try:
            current_pos = self.scale_volume.get()
            target_percentage = int(current_pos)
            self.lbl_volume_val.config(text=f"{target_percentage}%")
            gv.config.set_audio_gain_level(target_percentage)
            if self.sdr.is_connected and not getattr(self, 'is_muted', False):
                self.sdr.set_volume(float(target_percentage) / 100.0)
        except Exception:
            pass

    def action_toggle_mute(self):
        if not self.sdr.is_connected: return
        slider = self.scale_volume
        if not self.is_muted:
            self.pre_mute_volume = slider.get()
            if self.sdr.mute():
                self.is_muted = True
                slider.set(0)
                slider.config(state="disabled")
                self.lbl_volume_val.config(text="MUTED")
                self.btn_mute_toggle.config(text="🔇 Unmute Audio")
        else:
            slider.config(state="normal")
            restore_vol_float = float(self.pre_mute_volume) / 100.0
            if self.sdr.unmute(restore_volume=restore_vol_float):
                self.is_muted = False
                slider.set(self.pre_mute_volume)
                self.lbl_volume_val.config(text=f"{int(float(self.pre_mute_volume))}%")
                self.btn_mute_toggle.config(text="🔊 Mute Audio")

    def action_on_set_dropdown_change(self, event=None):
        selected_set = self.combobox_sets.get().strip()
        if selected_set:
            self.sdr.change_active_scan_set(selected_set)
            self.refresh_listbox_view()

    def action_del_ch(self):
        selected = self.tree_channels.selection()
        if not selected: return
        lbl_target = self.tree_channels.item(selected, 'text')
        if self.sdr.delete_channel(lbl_target):
            self.ent_label.delete(0, tk.END)
            self.ent_desc.delete(0, tk.END)
            self.refresh_listbox_view()

    def refresh_listbox_view(self):
        for item in self.tree_channels.get_children():
            self.tree_channels.delete(item)
        for ch in self.sdr.scan_channels:
            freq_mhz = ch.get("freq_hz", 0) / 1000000
            lbl = ch.get("label", "UNKN")
            mode = ch.get("mode", "WFM")
            desc = ch.get("description", "No Station Name")
            self.tree_channels.insert('', tk.END, text=lbl, values=(f"{freq_mhz:.4f}", mode, desc))

        banks_list = list(self.sdr.scan_sets_dict.keys())
        self.combobox_sets['values'] = banks_list
        self.combobox_target_sets['values'] = banks_list


def main():
    root = tk.Tk()
    root.title("CEC Nextion Full Emulator Engineering Console")
    import globalvars as gv
    from configuration import ConfigurationManager
    gv.config = ConfigurationManager()
    app = LabeledSDRDashboardApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    root.mainloop()


if __name__ == "__main__":
    main()
