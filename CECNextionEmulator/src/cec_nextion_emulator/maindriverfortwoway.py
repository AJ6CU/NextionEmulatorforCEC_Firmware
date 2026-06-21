import os
import shutil
import sys

# AUTO-CLEAR PRE-COMPILED CACHES ON STARTUP
try:
    if os.path.exists('__pycache__'):
        shutil.rmtree('__pycache__')
except Exception:
    pass

import tkinter as tk
from tkinter import messagebox, scrolledtext
from SDRPlusPlusController import SDRPlusPlusController


class LabeledSDRDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SDR++ Label-Based Master Control Deck")
        self.root.geometry("600x640")
        self.root.resizable(False, False)

        # Audio state cache trackers
        self.is_muted = False
        self.pre_mute_volume = 50  # Runtime fallback

        # Instantiate controller object on explicit IPv4 loopback
        self.sdr = SDRPlusPlusController(self.root, host="127.0.0.1", port=4532)
        self.sdr.on_frequency_change = self.cb_frequency
        self.sdr.on_mode_change = self.cb_mode
        self.sdr.on_filter_change = self.cb_filter
        self.sdr.on_scan_step = self.cb_scan_advance
        self.sdr.on_disconnect = self.cb_disconnect

        # Populate initial baseline channels into the object store
        self.sdr.add_channel("WX1", 162550000, "FM", 15000, "NOAA Weather 1")
        self.sdr.add_channel("HAM2", 145000000, "FM", 12500, "2m Hailing")
        self.sdr.add_channel("FT8", 7074000, "USB", 3000, "40m Ham Digital")

        # =========================================================================
        #  FRAMEWORK UI COMPONENT LAYOUT
        # =========================================================================
        # Row 1: Connection Frame
        self.conn_frame = tk.LabelFrame(root, text=" Connection Matrix ", font=("Arial", 10, "bold"), padx=10, pady=5)
        self.conn_frame.pack(fill="x", padx=15, pady=5)
        self.btn_connect = tk.Button(self.conn_frame, text="Connect to SDR++ (Port 4532)", command=self.do_connect,
                                     bg="#3498db", fg="white", font=("Arial", 10, "bold"))
        self.btn_connect.pack(side="left", fill="x", expand=True, pady=5)
        self.lbl_status = tk.Label(self.conn_frame, text="OFFLINE", fg="red", font=("Arial", 11, "bold"), width=12)
        self.lbl_status.pack(side="right", padx=5)

        # Row 2: Live Monitor Displays
        self.mon_frame = tk.LabelFrame(root, text=" Live Telemetry Readouts ", font=("Arial", 10, "bold"), padx=15,
                                       pady=8)
        self.mon_frame.pack(fill="x", padx=15, pady=5)
        self.lbl_freq = tk.Label(self.mon_frame, text="000.000000 MHz", font=("Courier", 20, "bold"), fg="#2c3e50")
        self.lbl_freq.pack(anchor="w")
        self.lbl_mode_filter = tk.Label(self.mon_frame, text="Mode: UNKNOWN  |  Filter Width: ---- Hz",
                                        font=("Arial", 11), fg="#7f8c8d")
        self.lbl_mode_filter.pack(anchor="w", pady=2)
        # Row 3: Action Trigger Launcher Buttons and Remote Volume Controls
        self.trigger_frame = tk.LabelFrame(root, text=" System Management Tools ", font=("Arial", 10, "bold"), padx=10,
                                           pady=5)
        self.trigger_frame.pack(fill="x", padx=15, pady=5)

        self.btn_open_filters = tk.Button(self.trigger_frame, text="🔍 Filter Console", command=self.open_filters_dialog,
                                          state="disabled", font=("Arial", 10, "bold"), fg="#2980b9")
        self.btn_open_filters.grid(row=0, column=0, padx=4, pady=5, sticky="ew")

        self.btn_open_settings = tk.Button(self.trigger_frame, text="🛠 Presets Manager",
                                           command=self.open_settings_dialog, state="disabled",
                                           font=("Arial", 10, "bold"), fg="#16a085")
        self.btn_open_settings.grid(row=0, column=1, padx=4, pady=5, sticky="ew")

        self.btn_mute_toggle = tk.Button(self.trigger_frame, text="🔊 Mute Audio", command=self.action_toggle_mute,
                                         state="disabled", font=("Arial", 10, "bold"), fg="#e67e22")
        self.btn_mute_toggle.grid(row=0, column=2, padx=4, pady=5, sticky="ew")

        self.sld_volume = tk.Scale(self.trigger_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="System Vol",
                                   command=self.cb_slider_volume_move, state="disabled", font=("Arial", 9))
        self.sld_volume.set(50)  # Initial safe layout parking point before connection sync
        self.sld_volume.grid(row=0, column=3, padx=6, pady=2, sticky="ew")

        self.trigger_frame.columnconfigure(0, weight=1)
        self.trigger_frame.columnconfigure(1, weight=1)
        self.trigger_frame.columnconfigure(2, weight=1)
        self.trigger_frame.columnconfigure(3, weight=2)

        # Row 4: Managed Channels Workspace Splitter
        self.channels_ui_frame = tk.LabelFrame(root, text=" Dynamic Channel Scan List Manager ",
                                               font=("Arial", 10, "bold"), padx=10, pady=5)
        self.channels_ui_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.left_editor = tk.Frame(self.channels_ui_frame)
        self.left_editor.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(self.left_editor, text="Short Label:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_label = tk.Entry(self.left_editor, width=15)
        self.ent_label.grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(self.left_editor, text="Freq (MHz):").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_freq = tk.Entry(self.left_editor, width=15)
        self.ent_freq.grid(row=1, column=1, sticky="w", pady=2)
        tk.Label(self.left_editor, text="Mode String:").grid(row=2, column=0, sticky="w", pady=2)
        self.ent_mode = tk.Entry(self.left_editor, width=15)
        self.ent_mode.grid(row=2, column=1, sticky="w", pady=2)
        self.ent_mode.insert(0, "FM")

        tk.Label(self.left_editor, text="Filter (Hz):").grid(row=3, column=0, sticky="w", pady=2)
        self.ent_filter = tk.Entry(self.left_editor, width=15)
        self.ent_filter.grid(row=3, column=1, sticky="w", pady=2)
        self.ent_filter.insert(0, "12500")

        tk.Label(self.left_editor, text="Station Name:").grid(row=4, column=0, sticky="w", pady=2)
        self.ent_name = tk.Entry(self.left_editor, width=15)
        self.ent_name.grid(row=4, column=1, sticky="w", pady=2)

        self.btn_add_label = tk.Button(self.left_editor, text="Add Channel Label", command=self.action_add_ch,
                                       font=("Arial", 9, "bold"))
        self.btn_add_label.grid(row=5, column=0, columnspan=2, sticky="ew", pady=6)

        self.btn_del_label = tk.Button(self.left_editor, text="Delete Selected Label", command=self.action_del_ch,
                                       font=("Arial", 9, "bold"), fg="red")
        self.btn_del_label.grid(row=6, column=0, columnspan=2, sticky="ew", pady=2)

        self.right_viewer = tk.Frame(self.channels_ui_frame)
        self.right_viewer.pack(side="right", fill="both", expand=True, padx=5)

        tk.Label(self.right_viewer, text="Active Scanner Queue:").pack(anchor="w")
        self.box_channels = tk.Listbox(self.right_viewer, height=6, selectmode=tk.SINGLE, font=("Courier", 9))
        self.box_channels.pack(fill="both", expand=True, pady=2)
        self.refresh_listbox_view()

        # Row 5: Dynamic Mode Fallback Width Editor (Dual-Row Stacked Grid Layout)
        self.fb_frame = tk.LabelFrame(root, text=" Dynamic Mode Fallback Width Editor ", font=("Arial", 10, "bold"),
                                      padx=10, pady=5)
        self.fb_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(self.fb_frame, text="Target Mode:").grid(row=0, column=0, sticky="w", padx=2, pady=4)
        self.ent_fb_mode = tk.Entry(self.fb_frame, width=8)
        self.ent_fb_mode.grid(row=0, column=1, sticky="w", padx=4, pady=4)
        self.ent_fb_mode.insert(0, "USB")

        tk.Label(self.fb_frame, text="New Default Width (Hz):").grid(row=0, column=2, sticky="w", padx=2, pady=4)
        self.ent_fb_width = tk.Entry(self.fb_frame, width=12)
        self.ent_fb_width.grid(row=0, column=3, sticky="w", padx=4, pady=4)
        self.ent_fb_width.insert(0, "2000")
        self.btn_update_fb = tk.Button(self.fb_frame, text="⚙ Update Fallback Bandwidth",
                                       command=self.action_update_fallback, state="disabled", font=("Arial", 9, "bold"))
        self.btn_update_fb.grid(row=1, column=0, columnspan=2, padx=4, pady=6, sticky="ew")

        self.btn_show_fb_dict = tk.Button(self.fb_frame, text="📋 Display Fallback Map Layout",
                                          command=self.action_display_fb_dict, font=("Arial", 9))
        self.btn_show_fb_dict.grid(row=1, column=2, columnspan=2, padx=4, pady=6, sticky="ew")

        self.fb_frame.columnconfigure(0, weight=1)
        self.fb_frame.columnconfigure(1, weight=1)
        self.fb_frame.columnconfigure(2, weight=1)
        self.fb_frame.columnconfigure(3, weight=1)

        # Row 6: Automation Scan Actions
        self.scan_ctrl_frame = tk.Frame(root, padx=15)
        self.scan_ctrl_frame.pack(fill="x", pady=5)
        self.btn_start = tk.Button(self.scan_ctrl_frame, text="▶ Run Scan", command=self.action_start_scan,
                                   state="disabled", bg="#2ecc71", font=("Arial", 10, "bold"))
        self.btn_start.pack(side="left", fill="x", expand=True, padx=3)
        self.btn_stop = tk.Button(self.scan_ctrl_frame, text="⏸ Pause", command=self.action_stop_scan, state="disabled",
                                  bg="#e74c3c", font=("Arial", 10, "bold"))
        self.btn_stop.pack(side="left", fill="x", expand=True, padx=3)
        self.btn_print_dict = tk.Button(self.scan_ctrl_frame, text="📋 Scan Dictionary",
                                        command=self.action_display_dict, font=("Arial", 10))
        self.btn_print_dict.pack(side="right", fill="x", expand=True, padx=3)

        self.lbl_scan_indicator = tk.Label(root, text="Scanner State: IDLE", font=("Arial", 10, "italic"), fg="#95a5a6",
                                           padx=20)
        self.lbl_scan_indicator.pack(anchor="w", pady=2)

    # =========================================================================
    #  Part 2: UI BUTTON INTERACTION DRIVERS AND AUDIO LOGIC HOOKS
    # =========================================================================
    def do_connect(self):
        print("[*] Contacting SDR++ explicit IPv4 loopback socket interface...")
        if self.sdr.connect():
            self.lbl_status.config(text="ONLINE (IPv4)", fg="green")
            self.btn_connect.config(state="disabled")
            self.sdr.on_incompatible_mode = self.cb_incompatible_mode_handler

            # FIXED: Read Mac volume at connection moment and seed frontend sliders
            startup_vol = self.sdr.get_system_volume()
            self.pre_mute_volume = startup_vol

            if hasattr(self, 'btn_open_filters'): self.btn_open_filters.config(state="normal")
            if hasattr(self, 'btn_open_settings'): self.btn_open_settings.config(state="normal")
            if hasattr(self, 'btn_mute_toggle'): self.btn_mute_toggle.config(state="normal")
            if hasattr(self, 'sld_volume'):
                self.sld_volume.config(state="normal")
                self.sld_volume.set(startup_vol)  # Snaps onto your true Mac mixer volume level instantly
            if hasattr(self, 'btn_update_fb'): self.btn_update_fb.config(state="normal")
            if hasattr(self, 'btn_start'): self.btn_start.config(state="normal")

            self.force_startup_presets_sync()
        else:
            messagebox.showerror("Port Exception", "Connection rejected on Port 4532.")

    def cb_slider_volume_move(self, val):
        if self.sdr.is_connected and not self.is_muted:
            target_float = float(val) / 100.0
            self.sdr.set_volume(target_float)

    def action_toggle_mute(self):
        if not self.sdr.is_connected: return
        if not self.is_muted:
            self.pre_mute_volume = self.sld_volume.get()
            if self.sdr.mute():
                self.is_muted = True
                self.sld_volume.set(0)
                self.sld_volume.config(state="disabled")
                self.btn_mute_toggle.config(text="🔇 Unmute Audio", fg="#e74c3c")
        else:
            self.sld_volume.config(state="normal")
            restore_vol_float = float(self.pre_mute_volume) / 100.0
            if self.sdr.unmute(restore_volume=restore_vol_float):
                self.is_muted = False
                self.sld_volume.set(self.pre_mute_volume)  # Restore visual pointer slider position
                self.btn_mute_toggle.config(text="🔊 Mute Audio", fg="#e67e22")
    def cb_incompatible_mode_handler(self, detected_mode, enforced_mode):
        print("\n" + "!" * 65)
        print(f"[⚠️ DUAL-WAY SECURITY INTERCEPT EVENT]")
        print(f"    SDR++ GUI State Shift Detected: '{detected_mode}'")
        print(f"    Hardware Compatibility Evaluation: [FAIL] - Radio does not possess '{detected_mode}' module.")
        print(f"    Action Matrix: Issuing loopback override to force SDR++ into: '{enforced_mode}'")
        print("!" * 65 + "\n")
        self.lbl_mode_filter.config(text=f"Mode Error: Locked Out '{detected_mode}' -> Enforcing {enforced_mode}", fg="orange")

    def refresh_listbox_view(self):
        self.box_channels.delete(0, tk.END)
        for ch in self.sdr.scan_channels:
            mhz = ch["freq_hz"] / 1_000_000
            self.box_channels.insert(tk.END, f"[{ch['label']}] {mhz:.3f}MHz - {ch['mode']}")

    def action_add_ch(self):
        lbl = self.ent_label.get().strip()
        try:
            freq = int(float(self.ent_freq.get().strip()) * 1_000_000)
            mode = self.ent_mode.get().strip()
            filt = int(self.ent_filter.get().strip())
            name = self.ent_name.get().strip()
        except ValueError:
            messagebox.showwarning("Value Error", "Verify entries.")
            return
        if self.sdr.add_channel(lbl, freq, mode, filt, name): self.refresh_listbox_view()

    def action_del_ch(self):
        selected = self.box_channels.curselection()
        if not selected: return
        item_text = self.box_channels.get(selected)
        if "]" in item_text:
            parts = item_text.split("]")
            if len(parts) >= 1:
                lbl_target = parts[0].replace("[", "").strip()
                if self.sdr.delete_channel(lbl_target): self.refresh_listbox_view()

    def action_update_fallback(self):
        target_mode = self.ent_fb_mode.get().strip().upper()
        try: target_width = int(self.ent_fb_width.get().strip())
        except ValueError: return
        self.sdr.set_mode_fallback_width(target_mode, target_width)

    def action_display_fb_dict(self):
        fb_dictionary = self.sdr.get_all_mode_fallbacks()
        popup = tk.Toplevel(self.root)
        popup.title("Active Fallback Map Dictionary")
        popup.geometry("400x280")
        txt_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=("Courier", 10))
        txt_area.pack(fill="both", expand=True, padx=10, pady=10)
        import json
        txt_area.insert(tk.END, json.dumps(fb_dictionary, indent=4))
        txt_area.config(state="disabled")

    def open_filters_dialog(self):
        flt_win = tk.Toplevel(self.root)
        flt_win.title("Live Bandwidth Filter Console")
        flt_win.geometry("420x160")
        flt_win.resizable(False, False)
        tk.Label(flt_win, text="Active VFO Passband Fine-Tuning Console", font=("Arial", 11, "bold")).pack(pady=10)
        btn_frame = tk.Frame(flt_win)
        btn_frame.pack(padx=15, pady=5, fill="x")
        tk.Button(btn_frame, text="◀ Narrow Filter", command=lambda: self.sdr.narrow(200)).grid(row=0, column=0, padx=4, pady=5, sticky="ew")
        tk.Button(btn_frame, text="Widen Filter ▶", command=lambda: self.sdr.widen(200)).grid(row=0, column=1, padx=4, pady=5, sticky="ew")
        tk.Button(btn_frame, text="🔄 Reset Defaults", command=self.do_reset_filter, fg="#2980b9").grid(row=0, column=2, padx=4, pady=5, sticky="ew")
        tk.Button(btn_frame, text="🔍 Query Size", command=self.do_query_filter).grid(row=0, column=3, padx=4, pady=5, sticky="ew")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.columnconfigure(3, weight=1)

    def open_settings_dialog(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Global Bandwidth Presets Manager")
        settings_win.geometry("380x300")
        settings_win.resizable(False, False)
        tk.Label(settings_win, text="Configure Startup Bandwidth Baselines", font=("Arial", 11, "bold")).pack(pady=10)
        grid_frame = tk.Frame(settings_win)
        grid_frame.pack(padx=20, fill="both", expand=True)
        active_fallbacks = self.sdr.get_all_mode_fallbacks()
        entry_widgets = {}
        modes_to_show = ["USB", "LSB", "CW", "AM", "FM", "WFM"]
        for row_idx, mode_name in enumerate(modes_to_show):
            tk.Label(grid_frame, text=f"{mode_name} Default (Hz):").grid(row=row_idx, column=0, sticky="w", pady=3)
            ent = tk.Entry(grid_frame, width=12)
            ent.grid(row=row_idx, column=1, sticky="w", padx=10, pady=3)
            ent.insert(0, str(active_fallbacks.get(mode_name, 2400)))
            entry_widgets[mode_name] = ent
        def save_and_force_apply():
            for mode, widget in entry_widgets.items():
                try: self.sdr.set_mode_fallback_width(mode, int(widget.get().strip()))
                except ValueError: return
            messagebox.showinfo("Success", "All baselines updated successfully.")
            settings_win.destroy()
        tk.Button(settings_win, text="Apply & Force-Overwrite All SDR++ Filters", command=save_and_force_apply, bg="#2ecc71", font=("Arial", 10, "bold")).pack(fill="x", padx=20, pady=12)

    def force_startup_presets_sync(self):
        current_presets = self.sdr.get_all_mode_fallbacks()
        for mode, width_hz in list(current_presets.items()):
            if mode in ["USB", "LSB", "CW", "AM", "FM", "WFM"]: self.sdr.set_mode_fallback_width(mode, width_hz)

    def do_reset_filter(self):
        if self.sdr.is_connected:
            current_active_mode = self.sdr.current_mode
            if current_active_mode == "UNKNOWN":
                display_text = self.lbl_mode_filter.cget("text")
                if "LSB" in display_text: current_active_mode = "LSB"
                elif "CW" in display_text: current_active_mode = "CW"
                else: current_active_mode = "USB"
            target_width = self.sdr.DEFAULT_FILTER_FALLBACKS.get(current_active_mode, 2400)
            self.sdr.set_filter_width_hz(target_width)

    def do_query_filter(self):
        active_width = self.sdr.get_filter_width_hz()
        messagebox.showinfo("SDR++ Bandwidth Metadata", f"Current Filter Passband: {active_width} Hz\nActive Mode: {self.sdr.current_mode}")

    def action_start_scan(self):
        if not self.sdr.scan_channels: return
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.sdr.start_memory_scan(delay_ms=2500)

    def action_stop_scan(self):
        self.sdr.stop_scan()
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.lbl_scan_indicator.config(text="Scanner State: IDLE / PAUSED", fg="#e67e22")

    def action_display_dict(self):
        channels_dictionary = self.sdr.list_all_channels()
        popup = tk.Toplevel(self.root)
        popup.title("Compiled Label Dictionary Output")
        popup.geometry("500x320")
        txt_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=("Courier", 10))
        txt_area.pack(fill="both", expand=True, padx=10, pady=10)
        import json
        pretty_dict_string = json.dumps(channels_dictionary, indent=4)
        txt_area.insert(tk.END, pretty_dict_string)
        txt_area.config(state="disabled")

    def cb_frequency(self, hz): self.lbl_freq.config(text=f"{hz / 1e6:.6f} MHz")
    def cb_mode(self, mode): self.lbl_mode_filter.config(text=f"Mode: {mode}  |  Filter Width: {self.sdr.current_filter_width} Hz")
    def cb_filter(self, width_hz): self.lbl_mode_filter.config(text=f"Mode: {self.sdr.current_mode}  |  Filter Width: {width_hz} Hz")
    def cb_scan_advance(self, ch_info):
        self.lbl_freq.config(text=f"{ch_info['freq_hz'] / 1e6:.4f} MHz")
        self.lbl_mode_filter.config(text=f"Mode: {ch_info['mode']}  |  Filter Width: {ch_info['filter_hz']} Hz")
        self.lbl_scan_indicator.config(text=f"Scanner: ACTIVE ➔ Processing Label: '{ch_info['label']}'", fg="#2ecc71")

    def cb_disconnect(self):
        self.lbl_status.config(text="DISCONNECTED", fg="red")
        self.btn_connect.config(state="normal")
        if hasattr(self, 'btn_stop'): self.btn_stop.config(state="disabled")
        if hasattr(self, 'btn_start'): self.btn_start.config(state="disabled")
        if hasattr(self, 'btn_open_filters'): self.btn_open_filters.config(state="disabled")
        if hasattr(self, 'btn_open_settings'): self.btn_open_settings.config(state="disabled")
        if hasattr(self, 'btn_mute_toggle'): self.btn_mute_toggle.config(state="disabled")
        if hasattr(self, 'sld_volume'): self.sld_volume.config(state="disabled")
        if hasattr(self, 'btn_update_fb'): self.btn_update_fb.config(state="disabled")
        messagebox.showwarning("Network Disconnect", "Connection dropped.")

def main():
    root = tk.Tk()
    app = LabeledSDRDashboardApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: app.sdr.disconnect() or root.destroy())
    root.mainloop()

if __name__ == "__main__":
    main()
