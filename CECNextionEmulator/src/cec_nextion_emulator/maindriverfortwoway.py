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
        self.root.title("SDR++ Label-Based Control Deck")
        self.root.geometry("600x640")
        self.root.resizable(False, False)

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

        # Row 3: Bandwidth Filter Controls (Upgraded with Reset Button) []
        self.filter_frame = tk.LabelFrame(root, text=" Bandwidth Filters ", font=("Arial", 10, "bold"), padx=10, pady=5)
        self.filter_frame.pack(fill="x", padx=15, pady=5)

        self.btn_narrow = tk.Button(self.filter_frame, text="◀ Narrow (-200 Hz)", command=lambda: self.sdr.narrow(200),
                                    state="disabled")
        self.btn_narrow.grid(row=0, column=0, padx=4, pady=5, sticky="nsew")

        self.btn_widen = tk.Button(self.filter_frame, text="Widen (+200 Hz) ▶", command=lambda: self.sdr.widen(200),
                                   state="disabled")
        self.btn_widen.grid(row=0, column=1, padx=4, pady=5, sticky="nsew")

        self.btn_reset_flt = tk.Button(self.filter_frame, text="🔄 Reset (2400Hz)", command=self.do_reset_filter,
                                       state="disabled", fg="#2980b9")
        self.btn_reset_flt.grid(row=0, column=2, padx=4, pady=5, sticky="nsew")

        self.btn_query_flt = tk.Button(self.filter_frame, text="🔍 Query Size", command=self.do_query_filter,
                                       state="disabled")
        self.btn_query_flt.grid(row=0, column=3, padx=4, pady=5, sticky="nsew")

        self.filter_frame.columnconfigure(0, weight=2)
        self.filter_frame.columnconfigure(1, weight=2)
        self.filter_frame.columnconfigure(2, weight=2)
        self.filter_frame.columnconfigure(3, weight=1)

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
        self.box_channels = tk.Listbox(self.right_viewer, height=7, selectmode=tk.SINGLE, font=("Courier", 9))
        self.box_channels.pack(fill="both", expand=True, pady=2)
        self.refresh_listbox_view()

        # Row 5: Real-Time Signal Data Logger Frame
        self.log_frame = tk.LabelFrame(root, text=" Telemetry Data Logging Console (Dictionary Memory) ",
                                       font=("Arial", 10, "bold"), padx=10, pady=5)
        self.log_frame.pack(fill="x", padx=15, pady=5)

        self.txt_description = tk.Entry(self.log_frame, font=("Arial", 11), fg="grey")
        self.txt_description.insert(0, "Enter optional signal note (e.g. Police Dispatch)...")
        self.txt_description.bind("<FocusIn>", lambda e: self.txt_description.delete(0,
                                                                                     tk.END) if self.txt_description.get().startswith(
            "Enter optional") else None)
        self.txt_description.grid(row=0, column=0, columnspan=2, padx=5, pady=6, sticky="ew")

        self.btn_log_state = tk.Button(self.log_frame, text="💾 Snapshot & Log Current State", command=self.do_log,
                                       state="disabled", font=("Arial", 9, "bold"))
        self.btn_log_state.grid(row=1, column=0, padx=5, pady=4, sticky="nsew")

        self.btn_show_dict = tk.Button(self.log_frame, text="📋 Display Saved Log Dict", command=self.do_show_database,
                                       font=("Arial", 9))
        self.btn_show_dict.grid(row=1, column=1, padx=5, pady=4, sticky="nsew")
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.columnconfigure(1, weight=1)

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
        self.lbl_scan_indicator.pack(anchor="w", pady=4)

    # =========================================================================
    #  Part 2: UI FORM ACTIONS, LOG DISPLAY POPUPS, AND CALLBACK HOOKS
    # =========================================================================
    def do_connect(self):
        print("[*] Contacting SDR++ explicit IPv4 loopback socket interface...")
        if self.sdr.connect():
            self.lbl_status.config(text="ONLINE (IPv4)", fg="green")
            self.btn_connect.config(state="disabled")
            self.btn_narrow.config(state="normal")
            self.btn_widen.config(state="normal")
            self.btn_reset_flt.config(state="normal")  # Activate reset button
            self.btn_query_flt.config(state="normal")
            self.btn_log_state.config(state="normal")
            self.btn_start.config(state="normal")
        else:
            messagebox.showerror("Port Exception", "Connection rejected on Port 4532.")

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
            messagebox.showwarning("Value Error", "Verify numeric entries.")
            return

        if self.sdr.add_channel(lbl, freq, mode, filt, name):
            self.refresh_listbox_view()
            self.ent_label.delete(0, tk.END)
            self.ent_freq.delete(0, tk.END)
            self.ent_name.delete(0, tk.END)

    def action_del_ch(self):
        selected = self.box_channels.curselection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please click a channel in the listbox view pane to delete it.")
            return

        item_text = self.box_channels.get(selected)

        # FIXED: Safe element selection to extract short labels without syntax crashes
        if "]" in item_text:
            parts = item_text.split("]")
            lbl_target = parts[0].replace("[", "").strip()

            if self.sdr.delete_channel(lbl_target):
                self.refresh_listbox_view()
                if not self.sdr.scan_channels:
                    self.action_stop_scan()
                    self.btn_start.config(state="disabled")

    def do_reset_filter(self):
        """Forces the current active mode passband directly back to its factory default layout."""
        if self.sdr.is_connected:
            current_active_mode = self.sdr.current_mode
            if current_active_mode == "UNKNOWN":
                current_active_mode = "USB"

            # Dynamic factory standard lookup allocations
            target_width = 2400
            if "CW" in current_active_mode:
                target_width = 500
            elif current_active_mode in ["WFM"]:
                target_width = 180000
            elif current_active_mode in ["AM"]:
                target_width = 6000
            elif current_active_mode in ["FM", "NFM"]:
                target_width = 12500

            # Fire the explicit mode rewrite string command over the socket link
            self.sdr.set_mode(current_active_mode, target_width)
            self.lbl_mode_filter.config(text=f"Mode: {current_active_mode}  |  Filter Width: {target_width} Hz")

    def do_query_filter(self):
        active_width = self.sdr.get_filter_width_hz()
        messagebox.showinfo("SDR++ Bandwidth Metadata",
                            f"Current Filter Passband: {active_width} Hz\nActive Mode: {self.sdr.current_mode}")

    def do_log(self):
        desc = self.txt_description.get().strip()
        if desc.startswith("Enter optional") or not desc: desc = "Manual Log Entry"
        self.sdr.log_current_state(description=desc)
        self.txt_description.delete(0, tk.END)
        self.txt_description.insert(0, "✔ STATE SNAPSHOT CAPTURED!")
        self.root.after(1500, lambda: self.txt_description.delete(0, tk.END) or self.txt_description.insert(0,
                                                                                                            "Enter optional signal note (e.g. Police Dispatch)..."))

    def do_show_database(self):
        logs = self.sdr.get_all_logs()
        popup = tk.Toplevel(self.root)
        popup.title("Tracked In-Memory Signal Log Entries")
        popup.geometry("480x320")
        txt_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=("Courier", 10))
        txt_area.pack(fill="both", expand=True, padx=10, pady=10)
        if not logs:
            txt_area.insert(tk.END, "The signal telemetry log dictionary is completely empty.")
        else:
            txt_area.insert(tk.END, f"--- IN-MEMORY STATE LOGS ({len(logs)} KEYS STORED) ---\n\n")
            for hz_key, metadata in logs.items():
                txt_area.insert(tk.END, f"Key [{hz_key} Hz] ➔\n")
                for field, val in metadata.items(): txt_area.insert(tk.END, f"   {field}: {val}\n")
                txt_area.insert(tk.END, "-" * 45 + "\n")
        txt_area.config(state="disabled")

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
        txt_area.insert(tk.END, "--- RETURN VALUE DUMP: sdr.list_all_channels() ---\n\n")
        import json
        pretty_dict_string = json.dumps(channels_dictionary, indent=4)
        txt_area.insert(tk.END, pretty_dict_string)
        txt_area.config(state="disabled")

    def cb_frequency(self, hz):
        self.lbl_freq.config(text=f"{hz / 1e6:.6f} MHz")

    def cb_mode(self, mode):
        self.lbl_mode_filter.config(text=f"Mode: {mode}  |  Filter Width: {self.sdr.current_filter_width} Hz")

    def cb_filter(self, width_hz):
        self.lbl_mode_filter.config(text=f"Mode: {self.sdr.current_mode}  |  Filter Width: {width_hz} Hz")

    def cb_scan_advance(self, ch_info):
        self.lbl_freq.config(text=f"{ch_info['freq_hz'] / 1e6:.4f} MHz")
        self.lbl_mode_filter.config(text=f"Mode: {ch_info['mode']}  |  Filter Width: {ch_info['filter_hz']} Hz")
        self.lbl_scan_indicator.config(text=f"Scanner: ACTIVE ➔ Processing Label: '{ch_info['label']}'", fg="#2ecc71")

    def cb_disconnect(self):
        self.lbl_status.config(text="DISCONNECTED", fg="red")
        self.btn_connect.config(state="normal")
        self.btn_stop_scan.config(state="disabled")
        self.btn_start.config(state="disabled")
        self.btn_narrow.config(state="disabled")
        self.btn_widen.config(state="disabled")
        self.btn_reset_flt.config(state="disabled")
        self.btn_query_flt.config(state="disabled")
        self.btn_log_state.config(state="disabled")
        messagebox.showwarning("Network Disconnect", "Connection dropped.")


def main():
    root = tk.Tk()
    app = LabeledSDRDashboardApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: app.sdr.disconnect() or root.destroy())
    root.mainloop()


if __name__ == "__main__":
    main()
