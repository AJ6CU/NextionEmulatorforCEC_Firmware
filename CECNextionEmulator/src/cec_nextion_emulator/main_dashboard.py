import tkinter as tk
from tkinter import ttk, messagebox
import pygubu
import random
import globalvars as gv
from SDRPlusPlusController import SDRPlusPlusController


class LabeledSDRDashboardApp:
    def __init__(self, root):
        self.root = root

        # 1. Initialize Pygubu layout builder
        self.builder = pygubu.Builder()
        self.builder.add_from_file('./pygubu/main_dashboard.ui')
        self.main_window = self.builder.get_object('main_frame', root)

        # 2. Extract configuration input field widgets from XML template
        self.ent_scan_time = self.builder.get_object('ent_scan_time')
        self.ent_label = self.builder.get_object('ent_label')
        self.ent_freq = self.builder.get_object('ent_freq')
        self.ent_filter = self.builder.get_object('ent_filter')
        self.ent_desc = self.builder.get_object('ent_desc')
        self.combobox_sets = self.builder.get_object('combobox_sets')
        self.ent_radio_ip = self.builder.get_object('ent_radio_ip')
        self.ent_radio_port = self.builder.get_object('ent_radio_port')
        self.ent_force_bw = self.builder.get_object('ent_force_bw')

        # 3. Extract live tracking telemetry & S-Meter components
        self.lbl_val_freq = self.builder.get_object('lbl_val_freq')
        self.lbl_val_mode = self.builder.get_object('lbl_val_mode')
        self.smeter_bar = self.builder.get_object('smeter_bar')

        # Extract live tracker display & S-Meter elements
        self.lbl_val_freq = self.builder.get_object('lbl_val_freq')
        self.lbl_val_mode = self.builder.get_object('lbl_val_mode')
        self.smeter_bar = self.builder.get_object('smeter_bar')
        self.lbl_smeter_ticks = self.builder.get_object('lbl_smeter_ticks')

        # FIX: Extract the new S-Meter live numerical text readout widget
        self.lbl_smeter_val = self.builder.get_object('lbl_smeter_val')

        # 4. Configure Scrollable Data Grid Columns
        self.tree_channels = self.builder.get_object('tree_channels')
        self.tree_scroll = self.builder.get_object('tree_scroll')

        # --- FIX: Explicitly assign columns inside Python to prevent TclErrors ---
        self.tree_channels.config(columns=('frequency', 'mode', 'filter', 'description'))

        # Link the Scrollbar directly to the Data Grid
        self.tree_channels.config(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.config(command=self.tree_channels.yview)

        # Structure the 5 perfectly aligned grid text column headings safely
        self.tree_channels.heading('#0', text='Channel Label', anchor='w')
        self.tree_channels.heading('frequency', text='Frequency (MHz)', anchor='w')
        self.tree_channels.heading('mode', text='Mode', anchor='w')
        self.tree_channels.heading('filter', text='Filter (Hz)', anchor='w')
        self.tree_channels.heading('description', text='Station Name', anchor='w')

        # Structure the 5 perfectly aligned grid text column headings
        self.tree_channels.heading('#0', text='Channel Label', anchor='w')
        self.tree_channels.heading('frequency', text='Frequency (MHz)', anchor='w')
        self.tree_channels.heading('mode', text='Mode', anchor='w')
        self.tree_channels.heading('filter', text='Filter (Hz)', anchor='w')
        self.tree_channels.heading('description', text='Station Name', anchor='w')

        # 5. Bind single-click selection listener to jump frequency instantly
        self.tree_channels.bind('<<TreeviewSelect>>', self.action_on_channel_row_click)

        # 6. Instantiate communications controller loop
        self.sdr = SDRPlusPlusController(self.root)

        # 7. EXPLICIT BUTTON BINDINGS (Type-safe and crash-proof)
        self.builder.get_object('btn_connect').config(command=self.action_connect)
        self.builder.get_object('btn_delete').config(command=self.action_del_ch)
        self.builder.get_object('btn_start_scan').config(command=self.action_start_scan)
        self.builder.get_object('btn_stop_scan').config(command=self.sdr.stop_scan)
        self.builder.get_object('btn_filter_widen').config(command=self.action_filter_widen)
        self.builder.get_object('btn_filter_narrow').config(command=self.action_filter_narrow)
        self.builder.get_object('btn_filter_reset').config(command=self.action_filter_reset)
        self.builder.get_object('btn_force_bw').config(command=self.action_master_force_bw)

        # Ham Bands Matrix quick configuration lookups
        self.builder.get_object('btn_band_80m').config(command=lambda: self.action_quick_band(3500000, "LSB"))
        self.builder.get_object('btn_band_40m').config(command=lambda: self.action_quick_band(7000000, "LSB"))
        self.builder.get_object('btn_band_20m').config(command=lambda: self.action_quick_band(14000000, "USB"))
        self.builder.get_object('btn_band_2m').config(command=lambda: self.action_quick_band(144200000, "USB"))

        # Route background controller telemetry streams straight into UI fields
        self.sdr.on_frequency_change = self.update_frequency_telemetry
        self.sdr.on_mode_change = self.update_mode_telemetry

        # Seed initialization configurations from your type-safe config layer
        self.ent_scan_time.insert(0, str(gv.config.get_scan_station_time_ms()))
        self.ent_radio_ip.insert(0, str(gv.config.get_sdr_server_ip()))
        self.ent_radio_port.insert(0, str(gv.config.get_sdr_tcp_port()))

        self.refresh_listbox_view()
        self.update_smeter_loop()  # Kick off dynamic strength S-meter loop

    def update_frequency_telemetry(self, freq_hz):
        """Callback engine fired by background thread whenever VFO drifts."""
        freq_mhz = float(freq_hz) / 1_000_000
        self.lbl_val_freq.config(text=f"{freq_mhz:.4f} MHz")

    def update_mode_telemetry(self, mode_str):
        """Callback engine processing modulation changes from receiver stream."""
        self.lbl_val_mode.config(text=str(mode_str).upper())

    def action_on_channel_row_click(self, event):
        """Fires whenever a user clicks an item inside the Data Grid to instantly switch channels."""
        if not self.sdr.is_connected: return
        selected_item = self.tree_channels.selection()
        if not selected_item: return

        channel_name = self.tree_channels.item(selected_item, 'text')
        row_values = self.tree_channels.item(selected_item, 'values')

        if row_values and len(row_values) >= 2:
            try:
                freq_hz = int(float(row_values[0]) * 1_000_000)
                mode_str = str(row_values[1])
                print(f"[✔ Click Tune] Jumping VFO directly to Grid Selection: {channel_name} ({freq_hz} Hz)")
                self.sdr.set_frequency_hz(freq_hz)
                self.root.after(50, lambda: self.sdr.set_mode(mode_str))
            except Exception as e:
                print(f"[-] Grid selection tuning parse warning: {e}")

    def update_smeter_loop(self):
        """Simulates/reads dynamic RF signal variations and updates bar, ticks, and bottom numeric text."""
        if self.sdr.is_connected:
            # Generate realistic signal tracking value parameters
            dbfs_value = random.randint(45, 85) if getattr(self.sdr, 'is_scanning', False) else random.randint(15, 55)
            self.smeter_bar.config(value=dbfs_value)

            # Translate your bar value into standard S-Unit classifications
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

            # Calculate numerical dBFS conversion (-120.0 to 0.0 dBFS range)
            raw_dbfs = -120.0 + (float(dbfs_value) * 1.2)

            # Update the scale ticks row header
            self.lbl_smeter_ticks.config(text=f"S1 . S3 . S5 . S7 . S9 . +10 . +30  [{s_unit}]")

            # FIX: Updates live metrics at the bottom of the container layout
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
        if not self.sdr.is_connected:
            messagebox.showwarning("Offline", "Please connect to the SDR++ hardware rig first.")
            return
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
        mode = self.sdr.get_current_mode()
        fallbacks = self.sdr.get_all_mode_fallbacks()
        self.sdr.set_filter_width_hz(fallbacks.get(mode, 120000))

    def action_master_force_bw(self):
        if not self.sdr.is_connected: return
        try:
            target_bw = int(self.ent_force_bw.get().strip())
            self.sdr.set_filter_width_hz(target_bw)
        except ValueError:
            messagebox.showwarning("Warning", "Forced bandwidth window must be an integer.")

    def action_del_ch(self):
        selected = self.tree_channels.selection()
        if not selected: return
        lbl_target = self.tree_channels.item(selected, 'text')
        if self.sdr.delete_channel(lbl_target):
            self.ent_label.delete(0, tk.END)
            self.ent_freq.delete(0, tk.END)
            self.ent_filter.delete(0, tk.END)
            self.ent_desc.delete(0, tk.END)
            self.refresh_listbox_view()

    def refresh_listbox_view(self):
        """Clears and re-populates rows inside your 5-column scrollable data grid."""
        for item in self.tree_channels.get_children():
            self.tree_channels.delete(item)

        for ch in self.sdr.scan_channels:
            freq_mhz = ch.get("freq_hz", 0) / 1_000_000
            lbl = ch.get("label", "UNKN")
            mode = ch.get("mode", "WFM")
            filt = ch.get("filter", 120000)
            desc = ch.get("description", "No Station Name")

            # Formats row entries under the 5 columns beautifully
            self.tree_channels.insert('', tk.END, text=lbl, values=(f"{freq_mhz:.4f}", mode, filt, desc))

        self.combobox_sets['values'] = list(self.sdr.scan_sets_dict.keys())


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
