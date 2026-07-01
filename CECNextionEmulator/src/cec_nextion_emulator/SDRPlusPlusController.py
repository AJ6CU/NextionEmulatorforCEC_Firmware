import socket
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Union
import globalvars as gv


class SDRPlusPlusController:
    """
    An advanced object-oriented controller to interface with SDR++ using
    the Hamlib RigCTL network protocol wrapper driven natively by Tkinter's .after() loop.
    Part 1: Initialization, Disk Storage, and Local Configuration Cache Registries.
    """

    # HAM_BANDS = {
    #     '80m': (3500000, 'LSB', 2700),
    #     '40m': (7074000, 'USB', 3000),
    #     '20m': (14200000, 'USB', 2400),
    #     '15m': (21074000, 'USB', 3000),
    #     '10m': (28400000, 'USB', 2400),
    #     '2m': (145000000, 'FM', 12500)
    # }

    FACTORY_DEFAULTS = {
        'USB': 2400, 'LSB': 2400, 'CW': 500, 'CW_L': 500, 'CW_U': 500,
        'AM': 6000, 'NFM': 12500, 'FM': 12500, 'WFM': 180000
    }

    def __init__(self, root):
        self.root = root
        # self.host = gv.config.get("SDR Server IP", '127.0.0.1')
        # self.port = int(gv.config.get("SDR TCP Port", 4532))
        self.host = gv.config.get_sdr_server_ip()
        self.port = gv.config.get_sdr_tcp_port()
        self.sock = None
        self.is_connected = False
        self.is_running = False

        # Multi-Scan Set Architecture Properties
        self.scan_sets_dict: Dict[str, List[Dict[str, Union[int, str]]]] = {}
        self.active_scan_set: str = "DEFAULT SET"

        # State tracking cache variables
        self.current_frequency = 0
        self.current_mode = "UNKNOWN"
        self.current_filter_width = 2400
        self.current_signal_dbfs = -120.0

        # Mutatable Fallback Dictionary Registry
        self.DEFAULT_FILTER_FALLBACKS = dict(self.FACTORY_DEFAULTS)

        # Managed Scan Array targeting active subset pointer
        self.scan_channels: List[Dict[str, Union[int, str]]] = []
        self._load_channels_from_json()

        # Scanner runtime properties
        self.is_scanning = False
        self.scan_idx = 0
        self.scan_delay_ms = 2500

        # In-Memory Dictionary Logger Storage
        self.logged_signals: Dict[int, Dict[str, Union[str, int, float]]] = {}

        # Public system event callbacks
        self.on_frequency_change_primary = None
        self.on_frequency_change_secondary = None
        self.on_mode_change_primary = None
        self.on_mode_change_secondary = None
        self.on_filter_change = None
        self.on_scan_step = None
        self.on_disconnect = None
        self.on_incompatible_mode = None
        self.on_signal_change = None

    def connect(self, host="localhost", port=4532):
        """Establishes the connection and forces an immediate live hardware state query."""
        try:
            import socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2.0)
            self.sock.connect((host, port))
            self.is_connected = True

            # CRITICAL STARTUP SYNC: Force a blocking read of the exact real radio state
            # right now, before the asynchronous tkinter background loops begin.
            self.sock.sendall(b'm\n')
            mode_resp = self.sock.recv(1024).decode('utf-8').strip()
            clean_lines = mode_resp.split('\n')

            if clean_lines and len(clean_lines) >= 1:
                raw_mode = clean_lines[0].strip().upper()
                self.current_mode = "CW" if "CW" in raw_mode else ("LSB" if "LSB" in raw_mode else "USB")

                # Capture the true 3950 Hz filter size straight from the hardware buffer!
                if len(clean_lines) >= 2 and clean_lines[1].strip().isdigit():
                    self.current_filter_width = int(clean_lines[1].strip())
                else:
                    self.current_filter_width = 3950  # Better safe fallback matching your standard profile

            # Reset socket back to non-blocking or standard behavior for loop compatibility
            self.sock.settimeout(None)

            # Start your normal loop
            self.is_running = True
            self._tkinter_tick_loop()
            print(f"[+] Connected to SDR++. Synchronized Live Bandwidth: {self.current_filter_width} Hz")
            return True
        except Exception as e:
            print(f"[-] Connection initialization failed: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        self.stop_scan()
        self.is_running = False
        self.is_connected = False
        if self.sock:
            try:
                self.sock.close()
            except socket.error:
                pass

    def _handle_unexpected_disconnect(self):
        if self.is_connected:
            self.is_connected = False
            self.stop_scan()
            if self.on_disconnect: self.on_disconnect()

    def _load_channels_from_json(self):
        """Loads nested multi-scan sets from the unified application config profile."""
        try:
            # UNIFIED PATTERN: Read directly out of gv.config
            # self.scan_sets_dict = gv.config.get("Scan Channels Registry Queue", {})
            self.scan_sets_dict = gv.config.get_scan_channels_registry()
            if not isinstance(self.scan_sets_dict, dict) or not self.scan_sets_dict:
                self.scan_sets_dict = {"DEFAULT SET": []}
            if self.active_scan_set not in self.scan_sets_dict:
                self.active_scan_set = list(self.scan_sets_dict.keys())[0]
            self.scan_channels = self.scan_sets_dict[self.active_scan_set]
        except Exception as e:
            print(f"[-] Config Load Exception: {e}")
            self.scan_sets_dict = {"DEFAULT SET": []}
            self.scan_channels = []

    def _save_channels_to_json(self):
        """Appends active scan set updates via global configuration manager."""
        try:
            self.scan_sets_dict[self.active_scan_set] = self.scan_channels

            # UNIFIED: Hand the data directly to gv.config
            gv.config.set_scan_channels_registry(self.scan_sets_dict)

            print(f"[✔ Disk Sync] Saved active set: '{self.active_scan_set}'")
        except Exception as e:
            print(f"[-] Disk Sync Exception: {e}")

    def _save_all_channels_to_json(self):
        """Saves the entire registry tracking block via global configuration manager."""
        try:
            # UNIFIED: Hand the full dictionary to gv.config
            gv.config.set_scan_channels_registry(self.scan_sets_dict)

            print("[✔ Disk Sync] Successfully committed all master scan sets to gv.config")
        except Exception as e:
            print(f"[-] Master Disk Sync Exception: {e}")

    def change_active_scan_set(self, set_name: str) -> bool:
        """Swaps the active scanning target profile list cleanly to a different scan set."""
        clean_name = set_name.strip()
        if clean_name in self.scan_sets_dict:
            self.stop_scan()
            self.active_scan_set = clean_name
            self.scan_channels = self.scan_sets_dict[clean_name]
            print(f"[*] Controller: Swapped scanner target profile to set: '{clean_name}'")
            return True
        return False

    def create_new_scan_set(self, set_name: str, clone_from_set: str = None) -> bool:
        """Creates a brand new named scan set with option template copying cloning parameters."""
        clean_name = set_name.strip()
        if not clean_name or clean_name in self.scan_sets_dict:
            return False

        if clone_from_set and clone_from_set in self.scan_sets_dict:
            import copy
            self.scan_sets_dict[clean_name] = copy.deepcopy(self.scan_sets_dict[clone_from_set])
            print(f"[✔ Clone] Set '{clean_name}' successfully duplicated from template set: '{clone_from_set}'")
        else:
            self.scan_sets_dict[clean_name] = []
            print(f"[✔ Creation] Initialized empty scan set category bucket: '{clean_name}'")

        self._save_channels_to_json()
        return True

    def add_channel(self, label: str, freq_hz: int, mode: str, filter_hz: int, name: str) -> bool:
        clean_label = label.strip().upper()
        if not clean_label: return False
        for ch in self.scan_channels:
            if ch["label"] == clean_label: return False

        new_channel = {
            "label": clean_label, "freq_hz": int(freq_hz), "mode": mode.upper().strip(),
            "filter_hz": int(filter_hz), "name": name.strip() if name else f"Station {clean_label}"
        }
        self.scan_channels.append(new_channel)
        self._save_channels_to_json()
        return True

    def delete_channel(self, label: str) -> bool:
        clean_label = label.strip().upper()
        target_idx = -1
        for i, ch in enumerate(self.scan_channels):
            if ch["label"] == clean_label:
                target_idx = i
                break
        if target_idx != -1:
            was_scanning = self.is_scanning
            self.stop_scan()
            self.scan_channels.pop(target_idx)
            self._save_channels_to_json()
            if was_scanning and self.scan_channels:
                self.scan_idx = 0
                self.is_scanning = True
                self._tkinter_scan_tick()
            return True
        return False

    def list_all_channels(self) -> Dict[str, Dict[str, Union[int, str]]]:
        channels_dict = {}
        for ch in self.scan_channels:
            channels_dict[ch["label"]] = {
                "freq_hz": ch["freq_hz"], "mode": ch["mode"], "filter_hz": ch["filter_hz"], "name": ch["name"]
            }
        return channels_dict

    def get_all_mode_fallbacks(self) -> Dict[str, int]:
        return self.DEFAULT_FILTER_FALLBACKS

    def set_mode_fallback_width(self, mode: str, fallback_hz: int) -> bool:
        clean_mode = mode.upper().strip()
        if not clean_mode or int(fallback_hz) <= 0: return False
        self.DEFAULT_FILTER_FALLBACKS[clean_mode] = int(fallback_hz)
        if clean_mode in ["CW_L", "CW_U"]: self.DEFAULT_FILTER_FALLBACKS["CW"] = int(fallback_hz)
        if self.is_connected:
            if clean_mode == self.current_mode or (clean_mode in ["CW_L", "CW_U"] and self.current_mode == "CW"):
                self.set_filter_width_hz(int(fallback_hz))
        return True

    def set_frequency_hz(self, hz: int) -> bool:
        if not self.is_connected: return False
        try:
            self.sock.sendall(f"F {int(hz)}\n".encode('ascii'))
            self.sock.recv(1024)
            return True
        except socket.error:
            self._handle_unexpected_disconnect()
            return False

    #
    def set_mode(self, mode_str: str, passband_hz: int = 0):
        """Changes the radio modulation mode via Rigctl and triggers the mode callback."""
        if not self.is_connected or not self.sock: return

        # 1. Normalize the incoming string
        mode_str = mode_str.strip().upper()
        if "WFM" in mode_str:
            mode_str = "WFM"
        elif "FM" in mode_str:
            mode_str = "NFM"
        elif "RAW" in mode_str:
            mode_str = "AM"

        # 2. EVALUATE BEFORE ASSIGNMENT: Define change state tracker
        mode_changed = (mode_str != getattr(self, 'current_mode', ''))
        self.current_mode = mode_str

        # 3. Reclaim live bandwidth state safely
        if passband_hz > 0:
            self.current_filter_width = passband_hz
        else:
            passband_hz = getattr(self, 'current_filter_width', 3950)

        # 4. Format and dispatch standard Hamlib payload
        command = f"M {mode_str} {passband_hz}\n"
        try:
            self.sock.setblocking(True)
            self.sock.sendall(command.encode('utf-8'))
            self.sock.recv(1024)  # Flush standard acknowledgement response ("RPRT 0\n")

            # 5. EXECUTE CALLBACK: Notify the UI layer immediately on success
            if mode_changed and hasattr(self, 'on_mode_change_primary') and self.on_mode_change_primary:
                self.on_mode_change_primary(mode_str)
            if mode_changed and hasattr(self, 'on_mode_change_secondary') and self.on_mode_change_secondary:
                self.on_mode_change_secondary(mode_str)

        except socket.error:
            self._handle_unexpected_disconnect()

    def get_filter_width_hz(self) -> int:
        """Fetches the live active filter width tracking variable from the radio safely."""
        try:
            # Return the live background variable directly updated by the tick loop
            return int(self.current_filter_width)
        except Exception as e:
            print(f"[-] Error retrieving live filter width variable: {e}")
            return 2400 # Safe global fallback default if uninitialized


    #
    def set_filter_width_hz(self, width_hz: int):
        """Changes the radio filter width safely by using the supported Hamlib 'M' command."""
        if not self.is_connected: return
        try:
            # 1. Fetch the live mode string to keep it unchanged
            current_mode_str = self.current_mode if self.current_mode else "USB"

            # 2. Re-send the mode with our new target bandwidth
            command = f"M {current_mode_str} {width_hz}\n"
            self.sock.sendall(command.encode('utf-8'))
            self.sock.recv(1024)  # Flush the 'RPRT 0\n' acknowledgment

            # 3. Secure the state mirror immediately
            self.current_filter_width = width_hz
        except Exception as e:
            print(f"[-] Failed to push custom filter bandwidth target: {e}")

    def get_filter_width_hz(self) -> int:
        """Fetches the live active filter width tracking variable from the radio."""
        try:
            # Return the live background variable directly
            return int(self.current_filter_width)
        except Exception as e:
            print(f"[-] Error retrieving live filter width variable: {e}")
            return 120000



    def widen(self, step_hz: int = 500) -> bool:
        active_step = 50 if "CW" in self.current_mode or self.current_filter_width <= 500 else step_hz
        return self.set_filter_width_hz(self.current_filter_width + active_step)

    def narrow(self, step_hz: int = 500) -> bool:
        active_step = 50 if "CW" in self.current_mode or self.current_filter_width <= 500 else step_hz
        return self.set_filter_width_hz(self.current_filter_width - active_step)


    def start_memory_scan(self, delay_ms: int = None):
        """Begins scan loop, utilizing config file for delay."""
        if not self.is_connected or not self.scan_channels: return
        self.scan_delay_ms = int(delay_ms) if delay_ms is not None else gv.config.get_scan_station_time_ms()
        self.scan_idx = 0
        self.is_scanning = True
        self._tkinter_scan_tick()

    def set_scan_station_time_ms(self, milliseconds: int) -> bool:
        """Adjusts and saves scan dwell time to config."""
        try:
            self.scan_delay_ms = max(200, int(milliseconds))
            gv.config.set_Scan_On_Station_Time(self.scan_delay_ms)
            return True
        except Exception as e:
            print(f"[-] Timing Save Error: {e}")
            return False

    def stop_scan(self):
        self.is_scanning = False

    def _tkinter_scan_tick(self):
        if not self.is_scanning or not self.is_connected: return
        if self.scan_idx >= len(self.scan_channels): self.scan_idx = 0
        if not self.scan_channels:
            self.is_scanning = False
            return

        current_ch = self.scan_channels[self.scan_idx]
        self.set_frequency_hz(current_ch["freq_hz"])
        self.set_mode(current_ch["mode"], current_ch.get("filter_hz", 0))
        if self.on_scan_step: self.on_scan_step(current_ch)

        self.scan_idx = (self.scan_idx + 1) % len(self.scan_channels)

        # FIXED: Thread loops dynamically load the saved configurations live on every step
        self.root.after(self.scan_delay_ms, self._tkinter_scan_tick)

    # =========================================================================
    #  NEW INTEGRATION: AUTOMATED SCAN DELAY METHOD CONTROLLERS
    # =========================================================================
    def set_scan_station_time_ms(self, milliseconds: int) -> bool:
        """
        Dynamically adjusts the dwell time variable parameter for memory scans
        and commits the update cleanly back into your executable configuration python file [1.11].
        """
        clean_ms = max(200, int(milliseconds))  # Enforces a safe 200ms processing floor layout
        self.scan_delay_ms = clean_ms

        try:
            gv.config.set_scan_station_time_ms(clean_ms)
            print(f"[✔ Disk Sync] Scan On Station Time successfully committed to disk -> {clean_ms} ms")
            return True
        except Exception as e:
            print(f"[-] Disk Sync Exception: {e}")
            return False

    def get_system_volume(self) -> int:
        default_vol = 50
        if sys.platform == "darwin":
            try:
                cmd = "osascript -e 'output volume of (get volume settings)'"
                res = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                if res.isdigit(): return int(res)
            except Exception:
                return default_vol
        elif sys.platform == "win32":
            return default_vol
        elif sys.platform.startswith("linux"):
            try:
                res = subprocess.check_output("amixer sget Master", shell=True).decode('utf-8')
                if "[" in res: return int(res.split("[")[1].split("%]")[0])
            except Exception:
                return default_vol
        return default_vol

    def set_volume(self, volume_float: float) -> bool:
        vol_float = max(0.0, min(1.0, float(volume_float)))
        vol_percentage = int(vol_float * 100)
        if sys.platform == "darwin":
            try:
                subprocess.run(f"osascript -e 'set volume output volume {vol_percentage}'", shell=True, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        elif sys.platform == "win32":
            try:
                cmd = f'powershell -Command "$wsh = New-Object -ComObject WScript.Shell; [void]$wsh.SendKeys([char]174)*50; [void]$wsh.SendKeys([char]175)*{int(vol_percentage / 2)}"'
                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        elif sys.platform.startswith("linux"):
            try:
                subprocess.run(f"amixer -q sset Master {vol_percentage}%", shell=True, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        return False

    def mute(self) -> bool:
        if sys.platform == "darwin":
            try:
                subprocess.run("osascript -e 'set volume with output muted'", shell=True, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); return True
            except Exception:
                return False
        elif sys.platform == "win32":
            try:
                subprocess.run(
                    'powershell -Command "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)"',
                    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); return True
            except Exception:
                return False
        elif sys.platform.startswith("linux"):
            try:
                subprocess.run("amixer -q sset Master mute", shell=True, check=True, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL); return True
            except Exception:
                return False
        return False

    def unmute(self, restore_volume: float = 0.5) -> bool:
        if sys.platform == "darwin":
            try:
                subprocess.run("osascript -e 'set volume without output muted'", shell=True, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        elif sys.platform == "win32":
            try:
                subprocess.run(
                    'powershell -Command "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)"',
                    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        elif sys.platform.startswith("linux"):
            try:
                subprocess.run("amixer -q sset Master unmute", shell=True, check=True, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            except Exception:
                pass
        return self.set_volume(restore_volume)

    def _tkinter_tick_loop(self):
        """Asynchronous updater loop. Passively synchronizes state with SDR++ without overriding."""
        if not self.is_connected or not self.is_running: return
        try:
            if not self.is_scanning:
                # 1. Sync VFO Frequency
                self.sock.sendall(b'f\n')
                freq_resp = self.sock.recv(1024).decode('utf-8').strip().replace('\r', '').replace('RPRT 0', '').strip()
                if freq_resp.isdigit() and int(freq_resp) != self.current_frequency:
                    self.current_frequency = int(freq_resp)
                    if self.on_frequency_change_primary: self.on_frequency_change_primary(self.current_frequency)
                    if self.on_frequency_change_secondary: self.on_frequency_change_secondary(self.current_frequency)

                # 2. Sync VFO Mode and Dynamic Bandwidth (Passive Read Only)
                self.sock.sendall(b'm\n')
                mode_resp = self.sock.recv(1024).decode('utf-8').strip().replace('\r', '').replace('RPRT 0', '').strip()
                clean_lines = mode_resp.split('\n')

                if clean_lines and len(clean_lines) >= 1:
                    raw_mode = clean_lines[0].strip().upper()
                    mapped_mode = "CW" if "CW" in raw_mode else ("LSB" if "LSB" in raw_mode else "USB")

                    # Parse dynamic live bandwidth from line 2 if available
                    live_bandwidth = None
                    if len(clean_lines) >= 2 and clean_lines[1].strip().isdigit():
                        live_bandwidth = int(clean_lines[1].strip())

                    # Passive State Tracking: Update properties only if they changed on the radio
                    state_changed = False

                    if mapped_mode != self.current_mode:
                        self.current_mode = mapped_mode
                        if self.on_mode_change_primary: self.on_mode_change_primary(mapped_mode)
                        if self.on_mode_change_secondary: self.on_mode_change_secondary(mapped_mode)
                        state_changed = True

                    if live_bandwidth is not None and live_bandwidth != self.current_filter_width:
                        self.current_filter_width = live_bandwidth
                        if self.on_filter_change: self.on_filter_change(live_bandwidth)
                        state_changed = True

                    # Optional: Commit to global configuration tracking only if a change happened
                    if state_changed:
                        try:
                            gv.config.set_sdr_current_mode(self.current_mode)
                            gv.config.set_sdr_filter_width_hz(self.current_filter_width)
                        except Exception as e:
                            print(f"[-] Config local write skipped: {e}")

                # 3. Simulate S-Meter
                import random
                self.current_signal_dbfs = -70.0 + random.uniform(-5.0, 5.0)
                if self.on_signal_change: self.on_signal_change(self.current_signal_dbfs)

        except socket.error:
            self._handle_unexpected_disconnect()
            return

        self.root.after(200, self._tkinter_tick_loop)

