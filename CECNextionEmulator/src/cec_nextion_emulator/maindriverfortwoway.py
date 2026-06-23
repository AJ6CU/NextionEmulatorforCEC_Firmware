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
from tkinter import ttk  # Themed Notebook management loops library
import globalvars as gv
from SDRPlusPlusController import SDRPlusPlusController


class LabeledSDRDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SDR++ Label-Based Master Control Deck")

        # Fluid layout structural geometry sizes
        self.root.geometry("660x780")
        self.root.minsize(660, 720)
        self.root.resizable(True, True)

        # Enforce high-contrast dark charcoal appearance theme profiles
        self.THEME_BG = "#1e272e"
        self.THEME_FG = "#ffffff"
        self.root.config(bg=self.THEME_BG)

        # Format native style properties to prevent grey tab outline leakage
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TNotebook", background=self.THEME_BG, borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#2c3e50", foreground="white", font=("Arial", 9, "bold"),
                             padding=[10, 4])
        self.style.map("TNotebook.Tab", background=[("selected", "#34495e")], foreground=[("selected", "#00f0ff")])

        # State tracker parameters
        self.is_muted = False
        self.pre_mute_volume = 50
        self.is_connected_flag = False

        # Instantiate controller object utilizing live central gv.config allocations
        self.sdr = SDRPlusPlusController(self.root)

        self.sdr.on_frequency_change = self.cb_frequency
        self.sdr.on_mode_change = self.cb_mode
        self.sdr.on_filter_change = self.cb_filter
        self.sdr.on_scan_step = self.cb_scan_advance
        self.sdr.on_disconnect = self.cb_disconnect

        # Populate dynamic startup channels grid maps cache arrays
        self.sdr.add_channel("WX1", 14032000, "CW", 15000, "NOAA Weather 1")
        self.sdr.add_channel("HAM2", 3532000, "CW", 12500, "2m Hailing")
        self.sdr.add_channel("FT8", 7074000, "USB", 3000, "40m Ham Digital")

        # =========================================================================
        #  FRAMEWORK UI MONITOR READOUT GRAPHICS GRID LAYOUTS
        # =========================================================================
        # Row 1: Connection Frame Matrix
        self.conn_frame = tk.LabelFrame(root, text=" Connection Matrix ", font=("Arial", 10, "bold"), padx=10, pady=5,
                                        bg=self.THEME_BG, fg=self.THEME_FG)
        self.conn_frame.pack(fill="x", padx=15, pady=5)
        self.btn_connect = tk.Button(self.conn_frame, text="Connect to SDR++ (Port 4532)", command=self.do_connect,
                                     fg="#1a252f", font=("Arial", 10, "bold"), highlightbackground=self.THEME_BG,
                                     padx=10)
        self.btn_connect.pack(side="left", fill="x", expand=True, pady=5)
        self.lbl_status = tk.Label(self.conn_frame, text="OFFLINE", fg="#ff4d4d", font=("Arial", 11, "bold"),
                                   bg=self.THEME_BG, width=12)
        self.lbl_status.pack(side="right", padx=5)

        # Row 2: Live Monitor Displays Board
        self.mon_frame = tk.LabelFrame(root, text=" Live Telemetry Readouts ", font=("Arial", 10, "bold"), padx=15,
                                       pady=8, bg="black", fg="white")
        self.mon_frame.pack(fill="x", padx=15, pady=5)
        self.lbl_freq = tk.Label(self.mon_frame, text="000.000000 MHz", font=("Courier", 22, "bold"), fg="#00f0ff",
                                 bg="black")
        self.lbl_freq.pack(anchor="w")
        self.lbl_mode_filter = tk.Label(self.mon_frame, text="Mode: UNKNOWN  |  Filter Width: ---- Hz",
                                        font=("Arial", 12, "bold"), fg="#3498db", bg="black")
        self.lbl_mode_filter.pack(anchor="w", pady=2)

        self.lbl_signal = tk.Label(
            self.mon_frame,
            text="Scale: S1 S3 S5 S7 S9 +20 +40\nMeter: [░░░░░░░░░░░░░░░░░░░░░░] -120.0 dBFS (S0 SILENT)",
            font=("Courier", 11, "bold"), fg="#2ecc71", bg="black", justify="left", anchor="w"
        )
        self.lbl_signal.pack(anchor="w", pady=2)
        # Row 3: UNIFIED System Management Tools
        self.trigger_frame = tk.LabelFrame(root, text=" System Management Tools ", font=("Arial", 10, "bold"), padx=10,
                                           pady=5, bg=self.THEME_BG, fg=self.THEME_FG)
        self.trigger_frame.pack(fill="x", padx=15, pady=5)

        self.btn_open_filters = tk.Button(self.trigger_frame, text="🔍 Filter Console", command=self.open_filters_dialog,
                                          state="disabled", font=("Arial", 10, "bold"), fg="#1a252f",
                                          highlightbackground=self.THEME_BG)
        self.btn_open_filters.grid(row=0, column=0, padx=4, pady=5, sticky="ew")

        self.btn_open_settings = tk.Button(self.trigger_frame, text="🛠 Presets Manager",
                                           command=self.open_settings_dialog, state="disabled",
                                           font=("Arial", 10, "bold"), fg="#1a252f", highlightbackground=self.THEME_BG)
        self.btn_open_settings.grid(row=0, column=1, padx=4, pady=5, sticky="ew")

        self.btn_mute_toggle = tk.Button(self.trigger_frame, text="🔊 Mute Audio", command=self.action_toggle_mute,
                                         state="disabled", font=("Arial", 10, "bold"), fg="#1a252f",
                                         highlightbackground=self.THEME_BG)
        self.btn_mute_toggle.grid(row=0, column=2, padx=4, pady=5, sticky="ew")

        self.sld_volume = tk.Scale(self.trigger_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="System Vol",
                                   command=self.cb_slider_volume_move, state="disabled", font=("Arial", 9),
                                   bg=self.THEME_BG, fg=self.THEME_FG, highlightbackground=self.THEME_BG)
        self.sld_volume.set(50)
        self.sld_volume.grid(row=0, column=3, padx=6, pady=2, sticky="ew")

        self.trigger_frame.columnconfigure(0, weight=1)
        self.trigger_frame.columnconfigure(1, weight=1)
        self.trigger_frame.columnconfigure(2, weight=1)
        self.trigger_frame.columnconfigure(3, weight=2)

        # Row 3.5: INTEGRATED AMATEUR RADIO QUICK BAND CHANGER ARRAY
        self.band_frame = tk.LabelFrame(root, text=" Amateur Radio Quick Band Changer ", font=("Arial", 10, "bold"),
                                        padx=10, pady=5, bg=self.THEME_BG, fg=self.THEME_FG)
        self.band_frame.pack(fill="x", padx=15, pady=5)

        bands_data = [
            ("80m", 3500000), ("40m", 7074000), ("20m", 14200000),
            ("15m", 21074000), ("10m", 28400000), ("2m", 145000000)
        ]
        self.band_buttons = {}
        for col_idx, (name, hz) in enumerate(bands_data):
            btn = tk.Button(self.band_frame, text=name, command=lambda freq=hz: self.sdr.set_frequency_hz(freq),
                            state="disabled", font=("Arial", 9, "bold"), fg="#1a252f",
                            highlightbackground=self.THEME_BG)
            btn.grid(row=0, column=col_idx, padx=3, pady=4, sticky="ew")
            self.band_frame.columnconfigure(col_idx, weight=1)
            self.band_buttons[name] = btn

        # =========================================================================
        #  FIXED PLACEMENT: FOOTER PACKED FIRST TO SECURE VISIBILITY ON BASELINE
        # =========================================================================
        self.footer_frame = tk.Frame(root, padx=15, pady=5, bg=self.THEME_BG)
        self.footer_frame.pack(fill="x", side="bottom")

        self.scan_ctrl_frame = tk.Frame(self.footer_frame, bg=self.THEME_BG)
        self.scan_ctrl_frame.pack(fill="x", pady=2)

        self.btn_start = tk.Button(self.scan_ctrl_frame, text="▶ Run Scan", command=self.action_start_scan,
                                   state="disabled", bg="#2ecc71", font=("Arial", 10, "bold"), fg="#1a252f",
                                   highlightbackground=self.THEME_BG)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=3)

        self.btn_stop = tk.Button(self.scan_ctrl_frame, text="⏸ Pause", command=self.action_stop_scan, state="disabled",
                                  bg="#e74c3c", font=("Arial", 10, "bold"), fg="#1a252f",
                                  highlightbackground=self.THEME_BG)
        self.btn_stop.pack(side="left", fill="x", expand=True, padx=3)

        self.btn_print_dict = tk.Button(self.scan_ctrl_frame, text="📋 Scan Dictionary",
                                        command=self.action_display_dict, font=("Arial", 10), fg="#1a252f",
                                        highlightbackground=self.THEME_BG)
        self.btn_print_dict.pack(side="right", fill="x", expand=True, padx=3)

        self.lbl_scan_indicator = tk.Label(self.footer_frame, text="Scanner State: IDLE", font=("Arial", 10, "italic"),
                                           fg="#ecf0f1", bg=self.THEME_BG)
        self.lbl_scan_indicator.pack(anchor="w", side="top", pady=(5, 10))
        # =========================================================================
        #  SPACE-SAVING MULTI-TAB NOTEBOOK LAYOUT STACK MANAGER
        # =========================================================================
        self.notebook = ttk.Notebook(root, height=340)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=5)

        # --- TAB 1: MEMORY SCANNER QUEUE PANEL MANAGEMENT ---
        self.tab1_frame = tk.Frame(self.notebook, bg=self.THEME_BG, padx=10, pady=10)
        self.notebook.add(self.tab1_frame, text=" Memory Scanner Queue ")

        self.set_row1_frame = tk.Frame(self.tab1_frame, bg=self.THEME_BG)
        self.set_row1_frame.pack(fill="x", side="top", pady=2)
        tk.Label(self.set_row1_frame, text="Active Scan Set:", font=("Arial", 9, "bold"), bg=self.THEME_BG,
                 fg=self.THEME_FG).pack(side="left", padx=2)
        self.active_set_var = tk.StringVar(value=self.sdr.active_scan_set)
        initial_sets_list = list(self.sdr.scan_sets_dict.keys()) if self.sdr.scan_sets_dict else ["DEFAULT SET"]
        self.opt_scan_sets = tk.OptionMenu(self.set_row1_frame, self.active_set_var, *initial_sets_list,
                                           command=self.action_switch_scan_set)
        self.opt_scan_sets.config(highlightbackground=self.THEME_BG)
        self.opt_scan_sets.pack(side="left", padx=5)

        self.set_row2_frame = tk.Frame(self.tab1_frame, bg=self.THEME_BG)
        self.set_row2_frame.pack(fill="x", side="top", pady=2)
        tk.Label(self.set_row2_frame, text="New Set Name:", bg=self.THEME_BG, fg=self.THEME_FG).pack(side="left",
                                                                                                     padx=2)
        self.ent_new_set_name = tk.Entry(self.set_row2_frame, width=12, highlightbackground=self.THEME_BG)
        self.ent_new_set_name.pack(side="left", padx=2)
        tk.Label(self.set_row2_frame, text="Copy From:", bg=self.THEME_BG, fg=self.THEME_FG).pack(side="left", padx=5)
        self.clone_set_var = tk.StringVar(value="None (Blank Set)")
        self.opt_clone_source = tk.OptionMenu(self.set_row2_frame, self.clone_set_var, "None (Blank Set)",
                                              *initial_sets_list)
        self.opt_clone_source.config(highlightbackground=self.THEME_BG)
        self.opt_clone_source.pack(side="left", padx=2)
        self.btn_create_set = tk.Button(self.set_row2_frame, text="➕ Create Set", command=self.action_create_scan_set,
                                        font=("Arial", 9, "bold"), fg="#1a252f", highlightbackground=self.THEME_BG)
        self.btn_create_set.pack(side="left", padx=6)

        tk.Frame(self.tab1_frame, height=2, bd=1, relief=tk.SUNKEN, bg=self.THEME_BG).pack(fill="x", side="top", pady=6)

        self.left_editor = tk.Frame(self.tab1_frame, bg=self.THEME_BG)
        self.left_editor.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(self.left_editor, text="Short Label:", bg=self.THEME_BG, fg=self.THEME_FG).grid(row=0, column=0,
                                                                                                 sticky="w", pady=2)
        self.ent_label = tk.Entry(self.left_editor, width=15, highlightbackground=self.THEME_BG)
        self.ent_label.grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(self.left_editor, text="Freq (MHz):", bg=self.THEME_BG, fg=self.THEME_FG).grid(row=1, column=0,
                                                                                                sticky="w", pady=2)
        self.ent_freq = tk.Entry(self.left_editor, width=15, highlightbackground=self.THEME_BG)
        self.ent_freq.grid(row=1, column=1, sticky="w", pady=2)

        tk.Label(self.left_editor, text="Mode String:", bg=self.THEME_BG, fg=self.THEME_FG).grid(row=2, column=0,
                                                                                                 sticky="w", pady=2)
        self.ent_mode = tk.Entry(self.left_editor, width=15, highlightbackground=self.THEME_BG)
        self.ent_mode.grid(row=2, column=1, sticky="w", pady=2)
        self.ent_mode.insert(0, "FM")

        tk.Label(self.left_editor, text="Filter (Hz):", bg=self.THEME_BG, fg=self.THEME_FG).grid(row=3, column=0,
                                                                                                 sticky="w", pady=2)
        self.ent_filter = tk.Entry(self.left_editor, width=15, highlightbackground=self.THEME_BG)
        self.ent_filter.grid(row=3, column=1, sticky="w", pady=2)
        self.ent_filter.insert(0, "12500")

        tk.Label(self.left_editor, text="Station Name:", bg=self.THEME_BG, fg=self.THEME_FG).grid(row=4, column=0,
                                                                                                  sticky="w", pady=2)
        self.ent_name = tk.Entry(self.left_editor, width=15, highlightbackground=self.THEME_BG)
        self.ent_name.grid(row=4, column=1, sticky="w", pady=2)

        self.btn_add_label = tk.Button(self.left_editor, text="Add Channel Label", command=self.action_add_ch,
                                       font=("Arial", 9, "bold"), fg="#1a252f", highlightbackground=self.THEME_BG)
        self.btn_add_label.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)

        # Right Panel Display: Channel Queue View Registry Listbox
        self.right_viewer = tk.Frame(self.tab1_frame, bg=self.THEME_BG)
        self.right_viewer.pack(side="right", fill="both", expand=True, padx=5)

        tk.Label(self.right_viewer, text="Active Scanner Queue:", bg=self.THEME_BG, fg=self.THEME_FG).pack(anchor="w")
        self.box_channels = tk.Listbox(self.right_viewer, height=5, selectmode=tk.SINGLE, font=("Courier", 9),
                                       highlightbackground=self.THEME_BG)
        self.box_channels.pack(fill="both", expand=True, pady=2)
        self.refresh_listbox_view()

        self.btn_del_label = tk.Button(self.right_viewer, text="Delete Selected Label", command=self.action_del_ch,
                                       font=("Arial", 9, "bold"), fg="#1a252f", highlightbackground=self.THEME_BG)
        self.btn_del_label.pack(fill="x", pady=4)

        # Instantiate Selection Context Mouse Menus for list clicks
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Delete Station Entry Node", command=self.action_del_ch)
        self.box_channels.bind("<Button-2>" if sys.platform == "darwin" else "<Button-3>",
                               self.show_listbox_context_menu)
        # --- TAB 2: BANDWIDTH INDEPENDENT SETTINGS LAYER ---
        self.tab2_frame = tk.Frame(self.notebook, bg=self.THEME_BG, padx=15, pady=15)
        self.notebook.add(self.tab2_frame, text=" Bandwidth ")

        self.fb_frame = tk.LabelFrame(self.tab2_frame, text=" Dynamic Fallback Settings ", font=("Arial", 10, "bold"),
                                      padx=10, pady=10, bg=self.THEME_BG, fg=self.THEME_FG)
        self.fb_frame.pack(fill="both", expand=True)

        tk.Label(self.fb_frame, text="Target Mode:", bg=self.THEME_BG, fg=self.THEME_FG).grid(row=0, column=0,
                                                                                              sticky="w", padx=2,
                                                                                              pady=6)
        self.ent_fb_mode = tk.Entry(self.fb_frame, width=8, highlightbackground=self.THEME_BG)
        self.ent_fb_mode.grid(row=0, column=1, sticky="w", padx=4, pady=6)
        self.ent_fb_mode.insert(0, "USB")

        tk.Label(self.fb_frame, text="New Default Width (Hz):", bg=self.THEME_BG, fg=self.THEME_FG).grid(row=1,
                                                                                                         column=0,
                                                                                                         sticky="w",
                                                                                                         padx=2, pady=6)
        self.ent_fb_width = tk.Entry(self.fb_frame, width=12, highlightbackground=self.THEME_BG)
        self.ent_fb_width.grid(row=1, column=1, sticky="w", padx=4, pady=6)
        self.ent_fb_width.insert(0, "2000")

        self.btn_update_fb = tk.Button(self.fb_frame, text="⚙ Update Fallback Bandwidth",
                                       command=self.action_update_fallback, state="disabled", font=("Arial", 9, "bold"),
                                       fg="#1a252f", highlightbackground=self.THEME_BG)
        self.btn_update_fb.grid(row=2, column=0, padx=4, pady=8, sticky="ew")
        self.btn_show_fb_dict = tk.Button(self.fb_frame, text="📋 Display Fallback Map Layout",
                                          command=self.action_display_fb_dict, font=("Arial", 9, "bold"), fg="#1a252f",
                                          highlightbackground=self.THEME_BG)
        self.btn_show_fb_dict.grid(row=2, column=1, padx=4, pady=8, sticky="ew")
        self.fb_frame.columnconfigure(0, weight=1)
        self.fb_frame.columnconfigure(1, weight=1)

        # --- TAB 3: SCANNER TIMERS DWELL LAYER (NEW DETACHED PANEL) ---
        self.tab3_frame = tk. Frame(self.notebook, bg=self.THEME_BG, padx=15, pady=15)
        self.notebook.add(self.tab3_frame, text=" Scanner Timers ")

        self.timer_frame = tk.LabelFrame(self.tab3_frame, text=" Operational Dwell Configurations ",
                                         font=("Arial", 10, "bold"), padx=10, pady=10, bg=self.THEME_BG,
                                         fg=self.THEME_FG)
        self.timer_frame.pack(fill="both", expand=True)

        tk.Label(self.timer_frame, text="Scan Delay Period (ms):", bg=self.THEME_BG, fg=self.THEME_FG).grid(row=0, column=0, sticky="w", padx=2, pady=8)
        self.ent_scan_time = tk.Entry(self.timer_frame, width=15, highlightbackground=self.THEME_BG)
        self.ent_scan_time.grid(row=0, column=1, sticky="w", padx=4, pady=8)

        # UNIFIED PATTERN: Read directly out of gv.config with an active fallback default
        starting_delay = gv.config.get_scan_station_time_ms()
        self.ent_scan_time.insert(0, str(starting_delay))

        self.btn_update_scan_time = tk.Button(self.timer_frame, text="⏱ Save Scan Station Delay",
                                              command=self.action_update_scan_dwell_time, state="disabled",
                                              font=("Arial", 9, "bold"), fg="#1a252f",
                                              highlightbackground=self.THEME_BG)
        self.btn_update_scan_time.grid(row=1, column=0, columnspan=2, padx=4, pady=10, sticky="ew")
        self.timer_frame.columnconfigure(0, weight=1)
        self.timer_frame.columnconfigure(1, weight=1)

    # =========================================================================
    #  Part 2: UI BUTTON FUNCTION DISPATCHERS AND NETWORKING CORE GATES
    # =========================================================================
    def do_connect(self):
        if self.is_connected_flag: return
        print("[*] Contacting SDR++ explicit IPv4 loopback socket interface...")
        if self.sdr.connect():
            self.is_connected_flag = True
            self.lbl_status.config(text="ONLINE (IPv4)", fg="#2ecc71")
            self.btn_connect.config(text="CONNECTED (IPv4 LINK ACTIVE)", fg="#1e7e34", state="normal")
            self.sdr.on_incompatible_mode = self.cb_incompatible_mode_handler
            self.sdr.on_signal_change = self.cb_signal_handler

            startup_vol = self.sdr.get_system_volume()
            self.pre_mute_volume = startup_vol

            if hasattr(self, 'btn_open_filters'): self.btn_open_filters.config(state="normal")
            if hasattr(self, 'btn_open_settings'): self.btn_open_settings.config(state="normal")
            if hasattr(self, 'btn_mute_toggle'): self.btn_mute_toggle.config(state="normal")
            if hasattr(self, 'sld_volume'):
                self.sld_volume.config(state="normal")
                self.sld_volume.set(startup_vol)
            if hasattr(self, 'btn_update_fb'): self.btn_update_fb.config(state="normal")
            if hasattr(self, 'btn_update_scan_time'): self.btn_update_scan_time.config(state="normal")
            if hasattr(self, 'btn_start'): self.btn_start.config(state="normal")

            # Unlock the direct band switcher keys array dynamically
            for name, btn_obj in self.band_buttons.items(): btn_obj.config(state="normal")

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
                self.sld_volume.set(self.pre_mute_volume)
                self.btn_mute_toggle.config(text="🔊 Mute Audio", fg="#e67e22")

    def action_switch_scan_set(self, selected_set):
        if self.sdr.change_active_scan_set(selected_set):
            self.refresh_listbox_view()
            self.lbl_scan_indicator.config(text=f"Swapped Scan Set Profile to: '{selected_set}'", fg="#3498db")

    def action_create_scan_set(self):
        new_name = self.ent_new_set_name.get().strip()
        if not new_name: return
        source_template = self.clone_set_var.get()
        if source_template == "None (Blank Set)": source_template = None
        if self.sdr.create_new_scan_set(new_name, clone_from_set=source_template):
            self.ent_new_set_name.delete(0, tk.END)
            self.rebuild_dropdown_menus()
            self.active_set_var.set(new_name)
            self.action_switch_scan_set(new_name)
            messagebox.showinfo("Success", f"Scan Set '{new_name}' synchronized successfully!")
        else:
            messagebox.showwarning("Error", "Scan set validation conflict.")

    def rebuild_dropdown_menus(self):
        all_sets = list(self.sdr.scan_sets_dict.keys())
        menu_active = self.opt_scan_sets["menu"]
        menu_active.delete(0, "end")
        for set_key in all_sets:
            menu_active.add_command(label=set_key, command=lambda value=set_key: self.active_set_var.set(value) or self.action_switch_scan_set(value))
        menu_clone = self.opt_clone_source["menu"]
        menu_clone.delete(0, "end")
        menu_clone.add_command(label="None (Blank Set)", command=lambda: self.clone_set_var.set("None (Blank Set)"))
        for set_key in all_sets:
            menu_clone.add_command(label=set_key, command=lambda value=set_key: self.clone_set_var.set(value))

    def show_listbox_context_menu(self, event):
        try:
            self.box_channels.selection_clear(0, tk.END)
            clicked_idx = self.box_channels.nearest(event.y)
            self.box_channels.selection_set(clicked_idx)
            self.box_channels.activate(clicked_idx)
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally: self.context_menu.grab_release()

    def action_del_ch(self):
        selected = self.box_channels.curselection()
        if not selected: return
        item_text = self.box_channels.get(selected)
        if "]" in item_text:
            parts = item_text.split("]")
            if len(parts) >= 1:
                lbl_target = parts[0].replace("[", "").strip()
                if self.sdr.delete_channel(lbl_target):
                    # 1. Clear text inputs cleanly
                    self.ent_label.delete(0, tk.END)
                    self.ent_freq.delete(0, tk.END)

                    # 2. Re-render the visual display lists smoothly
                    self.refresh_listbox_view()

    def action_display_dict(self):
        """Generates a structured multi-set JSON code diagnostic readout array popup."""
        channels_dictionary = self.sdr.scan_sets_dict
        popup = tk.Toplevel(self.root)
        popup.title("Compiled Label Dictionary Output")
        popup.geometry("500x320")
        txt_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=("Courier", 10), bg="black", fg="#2ecc71")
        txt_area.pack(fill="both", expand=True, padx=10, pady=10)
        import json
        pretty_dict_string = json.dumps(channels_dictionary, indent=4)
        txt_area.insert(tk.END, pretty_dict_string)
        txt_area.config(state="disabled")

    def force_startup_presets_sync(self):
        """
        Queries your baseline custom configuration database upon a successful connection
        and forcefully applies those exact bandwidth metrics across all modes in SDR++.
        """
        current_presets = self.sdr.get_all_mode_fallbacks()
        for mode, width_hz in list(current_presets.items()):
            if mode in ["USB", "LSB", "CW", "AM", "FM", "WFM"]:
                self.sdr.set_mode_fallback_width(mode, width_hz)

    def do_query_filter(self):
        """
        Queries the current active VFO filter width from the controller
        and presents a clean, informative pop-up alert dialog message box.
        """
        active_width = self.sdr.get_filter_width_hz()
        messagebox.showinfo(
            "SDR++ Bandwidth Metadata",
            f"Current Filter Passband: {active_width} Hz\nActive Mode: {self.sdr.current_mode}"
        )


    def do_reset_filter(self):
        """
        Resets the active filter passband bandwidth back to its factory
        or user-configured fallback preset baseline.
        """
        if self.sdr.is_connected:
            current_active_mode = self.sdr.current_mode
            if current_active_mode == "UNKNOWN":
                display_text = self.lbl_mode_filter.cget("text")
                if "LSB" in display_text:
                    current_active_mode = "LSB"
                elif "CW" in display_text:
                    current_active_mode = "CW"
                else:
                    current_active_mode = "USB"

            target_width = self.sdr.DEFAULT_FILTER_FALLBACKS.get(current_active_mode, 2400)
            self.sdr.set_filter_width_hz(target_width)

    def action_start_scan(self):
        """
        Public UI callback method triggered by the Run Scan button.
        Locks the button state and hands control to the SDR memory loop thread.
        """
        if not self.sdr.scan_channels: return
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.sdr.start_memory_scan()

    def action_stop_scan(self):
        """
        Public UI callback method triggered by the Pause button.
        Halts the active memory sweeping loops safely and updates the layout text.
        """
        self.sdr.stop_scan()
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.lbl_scan_indicator.config(text="Scanner State: IDLE / PAUSED", fg="#e67e22")


    # =========================================================================
    #  DOWNSTREAM INTERCEPT TELEMETRY EVENT HOOK RUNTIME CALLBACKS
    # =========================================================================
    def cb_frequency(self, hz):
        self.lbl_freq.config(text=f"{hz / 1e6:.6f} MHz")

    def cb_mode(self, mode):
        self.lbl_mode_filter.config(text=f"Mode: {mode}  |  Filter Width: {self.sdr.current_filter_width} Hz",
                                    fg="#3498db")

    def cb_filter(self, width_hz):
        active_mode = self.sdr.current_mode
        if active_mode == "UNKNOWN": active_mode = "USB"
        self.lbl_mode_filter.config(text=f"Mode: {active_mode}  |  Filter Width: {int(width_hz)} Hz", fg="#3498db")





    def cb_signal_handler(self, dbfs_value):
        """Converts incoming RF dbfs metrics into a monospaced, calibrated S-Unit index layout row grid."""
        clamped_val = max(-115.0, min(-15.0, float(dbfs_value)))
        total_ticks = 22
        active_ticks = int(((clamped_val - (-115.0)) / (-15.0 - (-115.0))) * total_ticks)
        active_ticks = max(0, min(total_ticks, active_ticks))
        bar_graphic = "█" * active_ticks + "░" * (total_ticks - active_ticks)
        scale_header = "S1 S3 S5 S7 S9 +20 +40"

        if dbfs_value >= -57.0:
            status_tag = f"S9 +{int(dbfs_value - (-57.0))}dB" if dbfs_value > -57.0 else "S9 STRONG"
        elif dbfs_value >= -69.0:
            status_tag = "S7-S8 MOD"
        elif dbfs_value >= -87.0:
            status_tag = "S4-S6 FAIR"
        elif dbfs_value >= -105.0:
            status_tag = "S1-S3 WEAK"
        else:
            status_tag = "S0 SILENT"

        fixed_status_tag = f"{status_tag:<14}"
        self.lbl_signal.config(
            text=f"Scale: {scale_header}\n"
                 f"Meter: [{bar_graphic}] {dbfs_value:6.1f} dBFS ({fixed_status_tag})",
            font=("Courier", 11, "bold")
        )

    def cb_scan_advance(self, ch_info):
        self.lbl_freq.config(text=f"{ch_info['freq_hz'] / 1e6:.4f} MHz")
        self.lbl_mode_filter.config(text=f"Mode: {ch_info['mode']}  |  Filter Width: {ch_info['filter_hz']} Hz",
                                    fg="#2ecc71")
        self.lbl_scan_indicator.config(text=f"Scanner: ACTIVE ➔ Processing Label: '{ch_info['label']}'", fg="#2ecc71")

    def cb_disconnect(self):
        self.is_connected_flag = False
        self.lbl_status.config(text="DISCONNECTED", fg="red")
        self.btn_connect.config(text="Connect to SDR++ (Port 4532)", state="normal", fg="#1a252f")
        if hasattr(self, 'btn_stop'): self.btn_stop.config(state="disabled")
        if hasattr(self, 'btn_start'): self.btn_start.config(state="disabled")
        if hasattr(self, 'btn_open_filters'): self.btn_open_filters.config(state="disabled")
        if hasattr(self, 'btn_open_settings'): self.btn_open_settings.config(state="disabled")
        if hasattr(self, 'btn_mute_toggle'): self.btn_mute_toggle.config(state="disabled")
        if hasattr(self, 'sld_volume'): self.sld_volume.config(state="disabled")
        if hasattr(self, 'btn_update_fb'): self.btn_update_fb.config(state="disabled")
        if hasattr(self, 'btn_update_scan_time'): self.btn_update_scan_time.config(state="disabled")
        messagebox.showwarning("Network Disconnect", "Connection dropped.")

    def open_settings_dialog(self):
        def save_and_force_apply():
            for mode, widget in entry_widgets.items():
                try:
                    self.sdr.set_mode_fallback_width(mode, int(widget.get().strip()))
                except ValueError:
                    return
            messagebox.showinfo("Success", "All baselines updated successfully.")
            settings_win.destroy()
        """Spawns the global configuration baseline manager popup window panel."""
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


        tk.Button(settings_win, text="Apply & Force-Overwrite All SDR++ Filters", command=save_and_force_apply,
                  bg="#2ecc71", font=("Arial", 10, "bold")).pack(fill="x", padx=20, pady=12)



    def action_update_fallback(self):
        """Public UI event callback method to update a specific mode's baseline width."""
        target_mode = self.ent_fb_mode.get().strip().upper()
        try:
            target_width = int(self.ent_fb_width.get().strip())
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid integer for the bandwidth filter width.")
            return
        if self.sdr.set_mode_fallback_width(target_mode, target_width):
            messagebox.showinfo("Success",
                                f"Default fallback bandwidth for {target_mode} updated to {target_width} Hz.")

    def action_display_fb_dict(self):
        """Spawns a scrolling sub-window popup dialog displaying the current live default fallback bandwidth dictionary."""
        fb_dictionary = self.sdr.get_all_mode_fallbacks()
        popup = tk.Toplevel(self.root)
        popup.title("Active Fallback Map Dictionary")
        popup.geometry("400x280")

        txt_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=("Courier", 10), bg="black", fg="#2ecc71")
        txt_area.pack(fill="both", expand=True, padx=10, pady=10)

        import json
        pretty_fb_string = json.dumps(fb_dictionary, indent=4)
        txt_area.insert(tk.END, pretty_fb_string)
        txt_area.config(state="disabled")

    def action_update_scan_dwell_time(self):
        """UI Event callback to extract user input text and update the scan timer values."""
        try:
            target_ms = int(self.ent_scan_time.get().strip())
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid integer baseline number for milliseconds.")
            return
        if self.sdr.set_scan_station_time_ms(target_ms):
            messagebox.showinfo("Success", f"Scanning stay duration safely modified to: {target_ms} ms")

    def action_add_ch(self):
        """
        Extracts user text inputs from the form, converts MHz entries to Hz,
        and safely appends the new channel node into your active Scan Set listbox queue.
        """
        lbl = self.ent_label.get().strip().upper()
        try:
            # FIXED: Converts the user's float input (e.g. 7.074) cleanly to an integer Hz count
            freq = int(float(self.ent_freq.get().strip()) * 1_000_000)
            mode = self.ent_mode.get().strip().upper()
            filt = int(self.ent_filter.get().strip())
            name = self.ent_name.get().strip()
        except ValueError:
            messagebox.showwarning("Value Error", "Please verify entries. Freq and Filter must be numeric numbers.")
            return

        # Push the verified parameters down to your controller script memory registers
        if self.sdr.add_channel(lbl, freq, mode, filt, name):
            self.refresh_listbox_view()
            # Clear fields to allow rapid-fire user additions
            self.ent_label.delete(0, tk.END)
            self.ent_freq.delete(0, tk.END)
            self.ent_name.delete(0, tk.END)

    def refresh_listbox_view(self):
        """
        Flushes and rewrites the active scanner queue Listbox layout frame.
        Guarantees that only the channel nodes stored within your currently
        chosen Scan Set profile group display on your screen.
        """
        # Clear out every single existing row item in the UI widget container
        self.box_channels.delete(0, tk.END)

        # Sequentially loop through and print your active channel sets telemetry metrics
        for ch in self.sdr.scan_channels:
            mhz = ch["freq_hz"] / 1_000_000
            self.box_channels.insert(tk.END, f"[{ch['label']}] {mhz:.3f}MHz - {ch['mode']}")

    def cb_incompatible_mode_handler(self, detected_mode, enforced_mode):
        """
        Catches invalid mode shifts made directly inside the SDR++ desktop interface.
        Throws a console alert warning and forces an automatic loopback override.
        """
        print("\n" + "!" * 65)
        print(f"[⚠️ DUAL-WAY SECURITY INTERCEPT EVENT]")
        print(f"    SDR++ GUI State Shift Detected: '{detected_mode}'")
        print(f"    Hardware Compatibility Evaluation: [FAIL] - Radio does not possess '{detected_mode}' module.")
        print(f"    Action Matrix: Issuing loopback override to force SDR++ into: '{enforced_mode}'")
        print("!" * 65 + "\n")

        # Flash an orange layout alert state warning straight into your telemetry readout monitor bar
        self.lbl_mode_filter.config(text=f"Mode Error: Locked Out '{detected_mode}' -> Enforcing {enforced_mode}",
                                    fg="orange")

    def open_filters_dialog(self):
        """Spawns an interactive standalone sub-window console for Widen/Narrow/Reset/Query."""
        flt_win = tk.Toplevel(self.root)
        flt_win.title("Live Bandwidth Filter Console")
        flt_win.geometry("420x160")
        flt_win.resizable(False, False)
        tk.Label(flt_win, text="Active VFO Passband Fine-Tuning Console", font=("Arial", 11, "bold")).pack(pady=10)

        btn_frame = tk.Frame(flt_win)
        btn_frame.pack(padx=15, pady=5, fill="x")
        tk.Button(btn_frame, text="◀ Narrow Filter", command=lambda: self.sdr.narrow(200)).grid(row=0, column=0, padx=4,
                                                                                                pady=5, sticky="ew")
        tk.Button(btn_frame, text="Widen Filter ▶", command=lambda: self.sdr.widen(200)).grid(row=0, column=1, padx=4,
                                                                                              pady=5, sticky="ew")
        tk.Button(btn_frame, text="🔄 Reset Defaults", command=self.do_reset_filter, fg="#2980b9").grid(row=0, column=2,
                                                                                                       padx=4, pady=5,
                                                                                                       sticky="ew")
        tk.Button(btn_frame, text="🔍 Query Size", command=self.do_query_filter).grid(row=0, column=3, padx=4, pady=5,
                                                                                     sticky="ew")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.columnconfigure(3, weight=1)



# =========================================================================
#  MAIN SYSTEM THREAD RUNTIME INITIALIZATION BLOCK
# =========================================================================
def main():
    root = tk.Tk()

    # UNIFIED STARTUP: Import your manager, assign it to gv.config before continuing!
    # import globalvars as gv
    from configuration import ConfigurationManager
    gv.config = ConfigurationManager()

    app = LabeledSDRDashboardApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: app.sdr.disconnect() or root.destroy())
    root.mainloop()


if __name__ == "__main__":
    main()
