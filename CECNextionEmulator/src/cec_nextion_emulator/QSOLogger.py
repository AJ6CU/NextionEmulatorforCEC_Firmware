import csv
import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


class QSOLogger:
    """
    A unified, real-time logging class compatible with QRZ logbook uploads.
    Displays critical validation and system failures via Tkinter graphical message boxes.
    """

    def __init__(self, format_preference="csv", base_filename="qrz_logbook", app_id=None):
        self.app_id = app_id
        self.qrz_fields = ['call', 'band', 'mode', 'qso_date', 'time_on', 'freq', 'rst_sent', 'rst_rcvd']

        # Initialize a hidden Tkinter root window to prevent an empty GUI window from populating
        self._root = tk.Tk()
        self._root.withdraw()

        # Initialize state variables and set the filename cleanly using the helper logic
        self.format_preference = format_preference
        self.set_filename(base_filename)

    def set_filename(self, base_filename):
        """
        Dynamically changes the output file target on the fly.
        Automatically reapplies the file extension layout based on format_preference.
        """
        pref = str(self.format_preference).lower().strip() if self.format_preference else "csv"

        if pref in ['adi', 'adif']:
            self.format_type = "adif"
            self.filename = f"{base_filename}.adi"
            self.is_adif = True
        else:
            self.format_type = "csv"
            self.filename = f"{base_filename}.csv"
            self.is_adif = False

        print(f"Logger target updated. Current output destination: '{self.filename}'")

    def _show_gui_error(self, title, error_message):
        """Displays a graphical error modal using Tkinter."""
        messagebox.showerror(title, error_message)

    def _calculate_band_from_freq(self, freq_mhz):
        """Internal frequency-to-band string calculator."""
        try:
            f = float(freq_mhz)
            if 1.8 <= f <= 2.0:
                return "160m"
            elif 3.5 <= f <= 4.0:
                return "80m"
            elif 7.0 <= f <= 7.3:
                return "40m"
            elif 10.1 <= f <= 10.15:
                return "30m"
            elif 14.0 <= f <= 14.35:
                return "20m"
            elif 18.068 <= f <= 18.168:
                return "17m"
            elif 21.0 <= f <= 21.45:
                return "15m"
            elif 24.89 <= f <= 24.99:
                return "12m"
            elif 28.0 <= f <= 29.7:
                return "10m"
            elif 50.0 <= f <= 54.0:
                return "6m"
            elif 144.0 <= f <= 148.0:
                return "2m"
            elif 420.0 <= f <= 450.0:
                return "70cm"
            else:
                return "Custom"
        except (ValueError, TypeError):
            return "Unknown"

    def _extract_adif_field(self, record_str, field_name):
        """Internal tracking helper for parsing out existing ADIF tags."""
        marker = f"<{field_name}:"
        if marker not in record_str:
            return None
        try:
            start = record_str.index(marker) + len(marker)
            length_str = record_str[start:record_str.index(">", start)]
            length = int(length_str.split(":")) if ":" in length_str else int(length_str)
            data_start = record_str.index(">", start) + 1
            return record_str[data_start:data_start + length].strip()
        except Exception:
            return None

    def _create_file_backup(self):
        """Creates a timestamped copy of the active file before updates hit."""
        if not os.path.isfile(self.filename) or os.path.getsize(self.filename) == 0:
            return True
        try:
            base, ext = os.path.splitext(self.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{base}_backup_{timestamp}{ext}"
            shutil.copy2(self.filename, backup_filename)
            return True
        except Exception as e:
            self._show_gui_error("Backup System Failure", f"Failed to backup {self.filename}:\n{str(e)}")
            return False

    def _load_existing_qsos(self):
        """Scans the active target file dynamically to index historical records."""
        existing_records = set()
        if not os.path.isfile(self.filename):
            return existing_records

        try:
            with open(self.filename, mode='r', newline='', encoding='utf-8') as f:
                if self.is_adif:
                    content = f.read().lower()
                    records = content.split("<eor>")
                    for rec in records:
                        if not rec.strip():
                            continue
                        call = self._extract_adif_field(rec, "call")
                        qso_date = self._extract_adif_field(rec, "qso_date")
                        time_on = self._extract_adif_field(rec, "time_on")
                        band = self._extract_adif_field(rec, "band")
                        if call and qso_date and time_on and band:
                            existing_records.add((call.upper(), qso_date, time_on, band.lower()))
                else:
                    reader = csv.DictReader(f)
                    for row in reader:
                        unique_key = (
                            str(row.get('call', '')).upper(),
                            str(row.get('qso_date', '')),
                            str(row.get('time_on', '')),
                            str(row.get('band', '')).lower()
                        )
                        existing_records.add(unique_key)
        except Exception as e:
            self._show_gui_error("Log Read Error", f"Could not scan existing log database index:\n{str(e)}")
        return existing_records

    def append_qso(self, qso):
        """Validates, deduplicates, and saves a single QSO record down to disk."""
        try:
            required_keys = ['call', 'mode', 'qso_date', 'time_on', 'freq', 'rst_sent', 'rst_rcvd']
            missing_fields = [field for field in required_keys if field not in qso]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")

            calculated_band = self._calculate_band_from_freq(qso['freq'])
            band = str(qso.get('band', calculated_band)).lower().strip()
            if band in ["unknown", "custom"]:
                band = calculated_band

            call = str(qso['call']).upper().strip()
            qso_date = str(qso['qso_date']).strip()
            time_on = str(qso['time_on']).strip()

            qso_key = (call, qso_date, time_on, band)
        except Exception as e:
            self._show_gui_error("Data Validation Error", f"QSO formatting constraints violated:\n{str(e)}")
            return False

        existing_qsos = self._load_existing_qsos()
        if qso_key in existing_qsos:
            messagebox.showinfo("Duplicate QSO", f"Skipped contact: {call} on {band} already exists in log.")
            return False

        if not self._create_file_backup():
            return False

        sanitized_qso = qso.copy()
        sanitized_qso['call'] = call
        sanitized_qso['band'] = band

        try:
            file_exists = os.path.isfile(self.filename) and os.path.getsize(self.filename) > 0

            if self.is_adif:
                with open(self.filename, mode='a' if file_exists else 'w', encoding='utf-8') as f:
                    if not file_exists:
                        f.write("ADIF Real-Time Log File Class\n")
                        f.write("<EOH>\n\n")

                    adif_row = ""
                    for field in self.qrz_fields:
                        val = str(sanitized_qso[field])
                        adif_row += f"<{field}:{len(val)}>{val} "
                    if self.app_id:
                        app_str = str(self.app_id)
                        adif_row += f"<app_qrzlog_logid:{len(app_str)}>{app_str} "
                    f.write(adif_row + "<EOR>\n")
            else:
                has_valid_header = False
                if file_exists:
                    with open(self.filename, mode='r', newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        if next(reader, None) == self.qrz_fields:
                            has_valid_header = True

                final_fields = self.qrz_fields + ['app_qrzlog_logid'] if self.app_id else self.qrz_fields

                with open(self.filename, mode='a' if has_valid_header else 'w', newline='',
                          encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=final_fields, extrasaction='ignore')
                    if not has_valid_header:
                        writer.writeheader()
                    if self.app_id:
                        sanitized_qso['app_qrzlog_logid'] = self.app_id
                    writer.writerow(sanitized_qso)

            print(f"Successfully tracked contact {call} inside '{self.filename}'.")
            return True
        except Exception as e:
            self._show_gui_error("Write Failure", f"Critical crash writing record to disk:\n{str(e)}")
            return False


# ==========================================
# Execution Demo Setup
# ==========================================
if __name__ == "__main__":
    valid_record = {'call': 'W7AW', 'mode': 'FT8', 'qso_date': '20260605', 'time_on': '231000', 'freq': '14.074',
                    'rst_sent': '-12', 'rst_rcvd': '-15'}

    # Initialize with default name
    logger = QSOLogger(format_preference="csv", base_filename="june_log")
    logger.append_qso(valid_record)

    # Switch filename on the same instance to route the next contact somewhere else
    print("\n--- Changing Log File Destination ---")
    logger.set_filename("july_log")
    logger.append_qso(valid_record)
