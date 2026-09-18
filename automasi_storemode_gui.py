
import os
import sys
import json
import time
import queue
import logging
import threading
import importlib
import subprocess
from datetime import datetime
from logging.handlers import RotatingFileHandler

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


LIBRARY_WAJIB = [
    ("customtkinter", "customtkinter"),
    ("pandas", "pandas"),
    ("openpyxl", "openpyxl"),
    ("pyautogui", "pyautogui"),
    ("pyperclip", "pyperclip"),
    ("pygetwindow", "pygetwindow"),
    ("keyboard", "keyboard"),
    ("PIL", "pillow"),
]
LIBRARY_OPSIONAL = [
    ("cv2", "opencv-python"),
    ("numpy", "numpy"),
    ("pytesseract", "pytesseract"),
]


def _modul_tersedia(nama_modul):
    try:
        importlib.import_module(nama_modul)
        return True
    except ImportError:
        return False


def pastikan_semua_library_terinstal():
    """Cek semua library yang dibutuhkan. Kalau ada yang belum terinstall,
    tampilkan jendela kecil ("Automasi Panel by Adi Nurputra - Persiapan")
    dan install otomatis lewat pip satu per satu, dengan log & progress
    yang terlihat, sebelum panel utama dibuka."""

    daftar_cek = LIBRARY_WAJIB + LIBRARY_OPSIONAL
    belum_ada = [(m, p) for m, p in daftar_cek if not _modul_tersedia(m)]

    if not belum_ada:
        return True  # semua sudah lengkap, langsung lanjut ke panel utama

    splash = tk.Tk()
    splash.title("Automasi Panel by Adi Nurputra - Persiapan")
    lebar, tinggi = 480, 340
    splash.geometry(f"{lebar}x{tinggi}")
    splash.resizable(False, False)
    splash.configure(bg="#1e1e1e")
    try:
        splash.eval("tk::PlaceWindow . center")
    except Exception:
        pass

    tk.Label(splash, text="Menyiapkan Automasi Panel by Adi Nurputra",
             bg="#1e1e1e", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=(16, 4))
    tk.Label(splash, text="Menginstall library yang belum tersedia, mohon tunggu...",
             bg="#1e1e1e", fg="#bbbbbb", font=("Segoe UI", 9)).pack(pady=(0, 10))

    progress = ttk.Progressbar(splash, orient="horizontal", length=430, mode="determinate")
    progress.pack(pady=(0, 10))
    progress["maximum"] = len(belum_ada)

    frame_log = tk.Frame(splash, bg="#1e1e1e")
    frame_log.pack(fill="both", expand=True, padx=16, pady=(0, 16))
    log_box = tk.Text(frame_log, bg="#111111", fg="#00e676", font=("Consolas", 9),
                       insertbackground="white", relief="flat")
    log_box.pack(fill="both", expand=True)
    log_box.configure(state="normal")

    def tulis_log(teks):
        log_box.insert("end", teks + "\n")
        log_box.see("end")
        splash.update()

    hasil_gagal = []

    def proses_install():
        tulis_log(f"Ditemukan {len(belum_ada)} library yang belum terinstall.\n")
        for i, (modul, paket) in enumerate(belum_ada, start=1):
            tulis_log(f"[{i}/{len(belum_ada)}] Menginstall '{paket}' ...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", paket]
                )
                tulis_log(f"    -> Berhasil menginstall '{paket}'.")
            except Exception as e:
                tulis_log(f"    -> GAGAL menginstall '{paket}': {e}")
                hasil_gagal.append(paket)
            progress["value"] = i
            splash.update()

        if hasil_gagal:
            tulis_log("\nSebagian library gagal terinstall otomatis:")
            for p in hasil_gagal:
                tulis_log(f"   - {p}")
            tulis_log("\nSilakan install manual dengan:")
            tulis_log(f"   pip install {' '.join(hasil_gagal)}")
            tulis_log("\nJendela ini akan tetap terbuka, aplikasi tetap akan dicoba dibuka...")
            splash.after(3500, splash.destroy)
        else:
            tulis_log("\nSemua library berhasil disiapkan. Membuka panel...")
            splash.after(900, splash.destroy)

    splash.after(200, proses_install)
    splash.mainloop()
    return len(hasil_gagal) == 0


# Jalankan pengecekan & instalasi otomatis SEBELUM mengimpor library pihak
# ketiga di bawah ini, supaya begitu baris import dijalankan, library-nya
# sudah pasti ada di sistem (kalau proses install di atas berhasil).
pastikan_semua_library_terinstal()

# --------------------------------------------------------------------------
# Import library GUI modern (customtkinter). Kalau tetap gagal terinstall
# otomatis (mis. tidak ada koneksi internet), beri instruksi yang jelas.
# --------------------------------------------------------------------------
try:
    import customtkinter as ctk
except ImportError:
    messagebox.showerror(
        "Automasi Panel by Adi Nurputra",
        "Library 'customtkinter' gagal diinstall otomatis (kemungkinan tidak ada "
        "koneksi internet).\n\nSilakan install manual lalu coba lagi:\n\n"
        "    pip install customtkinter",
    )
    sys.exit(1)

# --------------------------------------------------------------------------
# Import library automasi. Beberapa bersifat opsional (fitur tambahan saja).
# --------------------------------------------------------------------------
try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import pyautogui
    import pyperclip
    import pygetwindow as gw
    import keyboard
    AUTOMASI_TERSEDIA = True
except ImportError:
    AUTOMASI_TERSEDIA = False

try:
    from PIL import Image, ImageChops, ImageStat
    PIL_TERSEDIA = True
except ImportError:
    PIL_TERSEDIA = False

try:
    import pytesseract
    OCR_TERSEDIA = True
except ImportError:
    OCR_TERSEDIA = False

try:
    import cv2
    import numpy as np
    CV_TERSEDIA = True
except ImportError:
    CV_TERSEDIA = False


# ==============================================================================
# LOKASI FILE DATA (Konfigurasi, Kalibrasi, Riwayat, Log)
# ==============================================================================
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "macro_data")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
TEMPLATE_DIR = os.path.join(BASE_DIR, "template_kalibrasi")
PROGRESS_FILE = os.path.join(BASE_DIR, "progress_input.json")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "automasi_storemode.log")
LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 10

TARGET_LIST = [
    ("cari_sku", "Kolom 'Cari SKU'"),
    ("req_stock", "Kolom 'Request Stock'"),
    ("submit", "Tombol 'Submit'"),
]

DEFAULT_CONFIG = {
    "excel_file": r"D:\macro\data_request.xlsx",
    "kolom_sku": "SKU",
    "kolom_req": "Request Stock",
    "default_qty": "10",

    "target_exe_path": r"C:\Users\adi nurputra\AppData\Local\Microsoft\WindowsApps\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\WsaClient.exe",
    "target_launch_uri": "wsa://com.ruparupa.storemode.android",
    "window_titles": "Storemode, ruparupa, WsaClient",

    "stop_key": "esc",
    "pause_key": "f9",
    "kalibrasi_capture_key": "f8",

    "posisi": {
        "cari_sku": [0.50, 0.26],
        "req_stock": [0.65, 0.51],
        "submit": [0.50, 0.60],
    },

    "aktifkan_auto_kalibrasi": True,
    "template_half_w": 45,
    "template_half_h": 25,
    "match_threshold": 0.75,
    "skala_uji": [1.0, 0.95, 1.05, 0.9, 1.1],

    "delay_countdown": 3.0,
    "delay_load_sku": 2.5,
    "delay_after_submit": 3.0,
    "max_retry_fokus": 3,
    "delay_retry_fokus": 1.0,
    "max_retry_sku": 3,
    "delay_retry_sku": 1.5,

    "aktifkan_verifikasi": True,
    "tesseract_cmd": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    "ocr_region_notifikasi": [0.20, 0.05, 0.80, 0.20],
    "kata_kunci_sukses": ["berhasil", "success", "sukses", "terkirim", "submitted"],
    "kata_kunci_gagal": ["gagal", "error", "invalid", "tidak valid", "failed", "stok tidak"],
    "diff_region_form": [0.30, 0.45, 0.90, 0.65],
    "diff_threshold": 12,
}


# ==============================================================================
# MANAJEMEN KONFIGURASI
# ==============================================================================

def pastikan_folder_data():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)


def muat_config():
    pastikan_folder_data()
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg.update(data)
            if "posisi" in data:
                posisi_gabungan = dict(DEFAULT_CONFIG["posisi"])
                posisi_gabungan.update(data["posisi"])
                cfg["posisi"] = posisi_gabungan
        except Exception:
            pass
    return cfg


def simpan_config(cfg):
    pastikan_folder_data()
    tmp = CONFIG_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.replace(tmp, CONFIG_FILE)


def window_titles_list(cfg):
    return [t.strip() for t in cfg.get("window_titles", "").split(",") if t.strip()]


# ==============================================================================
# MANAJEMEN RIWAYAT (HISTORY)
# ==============================================================================

def muat_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def simpan_history(data):
    pastikan_folder_data()
    tmp = HISTORY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, HISTORY_FILE)


def tambah_history(sku, qty, status, keterangan=""):
    data = muat_history()
    data.append({
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sku": sku,
        "qty": qty,
        "status": status,
        "keterangan": keterangan,
    })
    # Batasi maksimal 5000 baris riwayat supaya file tidak membengkak
    if len(data) > 5000:
        data = data[-5000:]
    simpan_history(data)


def hapus_semua_history():
    simpan_history([])


# ==============================================================================
# PROGRESS / CHECKPOINT (RESUME ANTAR SESI)
# ==============================================================================

def muat_progress():
    if not os.path.exists(PROGRESS_FILE):
        return None
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "last_index" in data:
            return data
    except Exception:
        pass
    return None


def simpan_progress(last_index, total, gagal_permanen, sku_terakhir=None):
    pastikan_folder_data()
    data = {
        "last_index": last_index,
        "total": total,
        "sku_terakhir": sku_terakhir,
        "gagal_permanen": gagal_permanen,
        "waktu_update": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    tmp = PROGRESS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, PROGRESS_FILE)


def hapus_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            os.remove(PROGRESS_FILE)
        except Exception:
            pass


# ==============================================================================
# LOGGING: KE FILE + KE ANTREAN (UNTUK DITAMPILKAN DI GUI)
# ==============================================================================

class QueueLogHandler(logging.Handler):
    """Handler logging kustom yang mendorong tiap baris log ke queue.Queue,
    supaya jendela GUI bisa membacanya dan menampilkannya secara live."""

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            pass


def setup_logger(log_queue):
    pastikan_folder_data()
    logger = logging.getLogger("storemode_automasi")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    queue_handler = QueueLogHandler(log_queue)
    queue_handler.setLevel(logging.INFO)
    queue_handler.setFormatter(formatter)
    logger.addHandler(queue_handler)

    return logger


# ==============================================================================
# ENGINE OTOMASI (logika inti dari skrip asli, dibungkus jadi class terkontrol)
# ==============================================================================

class BerhentiDiminta(Exception):
    """Dipakai untuk keluar dari proses saat pengguna menekan Stop."""
    pass


class AutomationEngine:
    def __init__(self, cfg, logger, log_queue, on_status_change=None):
        self.cfg = cfg
        self.log = logger
        self.log_queue = log_queue
        self.on_status_change = on_status_change or (lambda **kw: None)

        self.stop_event = threading.Event()
        self.pause_event = threading.Event()  # set = sedang dijeda
        self.thread = None
        self.sedang_berjalan = False

        self.kalibrasi_batal_event = threading.Event()
        self.kalibrasi_thread = None
        self.kalibrasi_aktif = False

        if AUTOMASI_TERSEDIA:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.2
            if OCR_TERSEDIA and cfg.get("tesseract_cmd"):
                try:
                    pytesseract.pytesseract.tesseract_cmd = cfg["tesseract_cmd"]
                except Exception:
                    pass

    # ---------------------------------------------------------------- kontrol
    def minta_stop(self):
        self.stop_event.set()
        self.pause_event.clear()

    def toggle_pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.log.info(">> DILANJUTKAN. Melanjutkan penginputan...")
        else:
            self.pause_event.set()
            self.log.info("|| DIJEDA. Klik Lanjutkan untuk melanjutkan penginputan...")
        self.on_status_change()

    def _cek_stop(self):
        if self.stop_event.is_set():
            raise BerhentiDiminta("Dihentikan oleh pengguna.")

    def _tunggu_jika_pause(self):
        while self.pause_event.is_set():
            self._cek_stop()
            time.sleep(0.15)

    def _delay_aman(self, detik):
        interval = 0.05
        langkah = int(detik / interval)
        for _ in range(max(1, langkah)):
            self._cek_stop()
            self._tunggu_jika_pause()
            time.sleep(interval)

    # ------------------------------------------------------- window & mouse
    def _hitung_region_absolut(self, win, rel_region):
        x1, y1, x2, y2 = rel_region
        left = int(win.left + win.width * x1)
        top = int(win.top + win.height * y1)
        right = int(win.left + win.width * x2)
        bottom = int(win.top + win.height * y2)
        left = min(max(left, win.left), win.left + win.width - 1)
        top = min(max(top, win.top), win.top + win.height - 1)
        right = min(max(right, win.left + 1), win.left + win.width)
        bottom = min(max(bottom, win.top + 1), win.top + win.height)
        return left, top, max(right - left, 1), max(bottom - top, 1)

    def _ambil_screenshot_region(self, win, rel_region):
        region = self._hitung_region_absolut(win, rel_region)
        return pyautogui.screenshot(region=region)

    def _ambil_patch_sekitar_titik(self, win, abs_x, abs_y):
        half_w = self.cfg["template_half_w"]
        half_h = self.cfg["template_half_h"]
        left = abs_x - half_w
        top = abs_y - half_h
        left = int(min(max(left, win.left), win.left + win.width - 1))
        top = int(min(max(top, win.top), win.top + win.height - 1))
        w = int(min(2 * half_w, win.left + win.width - left))
        h = int(min(2 * half_h, win.top + win.height - top))
        return pyautogui.screenshot(region=(left, top, max(w, 1), max(h, 1)))

    def _dapatkan_jendela_target(self):
        keywords = window_titles_list(self.cfg)
        for title in gw.getAllTitles():
            if any(k.lower() in title.lower() for k in keywords if k):
                try:
                    win = gw.getWindowsWithTitle(title)[0]
                    if win.isMinimized:
                        win.restore()
                    win.activate()
                    self._delay_aman(0.5)
                    return win
                except Exception:
                    pass
        return None

    def jalankan_dan_deteksi_target(self, timeout=30):
        self.log.info("[*] Memeriksa apakah aplikasi target sudah terbuka...")
        win = self._dapatkan_jendela_target()
        if win:
            self.log.info("[+] Aplikasi sudah terbuka dan terdeteksi di layar.")
            return win

        self.log.warning("[!] Aplikasi belum terbuka. Membuka aplikasi secara otomatis...")
        try:
            exe = self.cfg.get("target_exe_path", "").strip()
            uri = self.cfg.get("target_launch_uri", "").strip()
            args = [exe]
            if uri:
                args += ["/launch", uri]
            subprocess.Popen(args)
        except Exception as e:
            self.log.warning(f"[!] Gagal meluncurkan aplikasi secara otomatis: {e}")
            return None

        self.log.info("[*] Menunggu aplikasi target terdeteksi...")
        mulai = time.time()
        while time.time() - mulai < timeout:
            self._delay_aman(1.0)
            win = self._dapatkan_jendela_target()
            if win:
                self.log.info("[+] Aplikasi berhasil diluncurkan dan terdeteksi siap!")
                return win
        self.log.warning("[!] Timeout: Aplikasi gagal terbuka atau jendela tidak ditemukan.")
        return None

    def _judul_cocok(self, judul, keywords):
        if not judul:
            return False
        return any(k.lower() in judul.lower() for k in keywords if k)

    def _pastikan_fokus(self, win):
        keywords = window_titles_list(self.cfg)
        max_retry = self.cfg["max_retry_fokus"]
        for percobaan in range(1, max_retry + 1):
            win_aktif = gw.getActiveWindow()
            if win_aktif is not None and self._judul_cocok(win_aktif.title, keywords):
                try:
                    return gw.getWindowsWithTitle(win_aktif.title)[0]
                except IndexError:
                    return win_aktif

            self.log.warning(f"    [!] Jendela target tidak sedang aktif (percobaan {percobaan}/{max_retry}). Fokus ulang...")
            win_baru = self._dapatkan_jendela_target()
            if win_baru is None:
                self._delay_aman(self.cfg["delay_retry_fokus"])
                continue

            win_aktif = gw.getActiveWindow()
            if win_aktif is not None and self._judul_cocok(win_aktif.title, keywords):
                return win_baru
            self._delay_aman(self.cfg["delay_retry_fokus"])
        return None

    def _click_relative(self, win, rel_x, rel_y):
        rel_x = min(max(rel_x, 0.0), 1.0)
        rel_y = min(max(rel_y, 0.0), 1.0)
        abs_x = int(win.left + (win.width * rel_x))
        abs_y = int(win.top + (win.height * rel_y))
        abs_x = min(max(abs_x, win.left), win.left + win.width - 1)
        abs_y = min(max(abs_y, win.top), win.top + win.height - 1)
        pyautogui.click(abs_x, abs_y)
        self._delay_aman(0.15)

    @staticmethod
    def format_clean_string(val, default_val=""):
        if pd is not None and pd.isna(val):
            return str(default_val)
        if val == "" or val is None:
            return str(default_val)
        if isinstance(val, (float, int)):
            return str(int(val))
        val_str = str(val).strip()
        if val_str.endswith(".0"):
            val_str = val_str[:-2]
        return val_str

    def _input_teks_via_clipboard(self, teks, timeout_sinkron=1.0):
        teks = str(teks)
        pyperclip.copy(teks)
        mulai = time.time()
        while True:
            try:
                isi = pyperclip.paste()
            except Exception:
                isi = None
            if isi == teks:
                break
            if time.time() - mulai > timeout_sinkron:
                pyperclip.copy(teks)
                time.sleep(0.1)
                break
            time.sleep(0.03)

        pyautogui.hotkey("ctrl", "a")
        self._delay_aman(0.05)
        pyautogui.press("backspace")
        self._delay_aman(0.05)
        pyautogui.hotkey("ctrl", "v")
        self._delay_aman(0.1)

    # -------------------------------------------------------- auto-kalibrasi
    def _pil_ke_cv_gray(self, img_pil):
        return cv2.cvtColor(np.array(img_pil.convert("RGB")), cv2.COLOR_RGB2GRAY)

    def _cocokkan_template(self, win, key):
        path = os.path.join(TEMPLATE_DIR, f"template_{key}.png")
        if not os.path.exists(path):
            return None
        try:
            template_gray = self._pil_ke_cv_gray(Image.open(path))
        except Exception:
            return None

        th, tw = template_gray.shape[:2]
        query_gray = self._pil_ke_cv_gray(self._ambil_screenshot_region(win, (0.0, 0.0, 1.0, 1.0)))

        best_val, best_loc, best_wh = -1.0, None, (tw, th)
        for skala in self.cfg["skala_uji"]:
            tw_s = max(int(tw * skala), 1)
            th_s = max(int(th * skala), 1)
            if tw_s >= query_gray.shape[1] or th_s >= query_gray.shape[0]:
                continue
            templ_resized = cv2.resize(template_gray, (tw_s, th_s))
            hasil = cv2.matchTemplate(query_gray, templ_resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(hasil)
            if max_val > best_val:
                best_val, best_loc, best_wh = max_val, max_loc, (tw_s, th_s)

        if best_loc is None:
            return None
        return best_val, best_loc, best_wh

    def auto_kalibrasi_ulang(self, win):
        if not self.cfg.get("aktifkan_auto_kalibrasi", True):
            return False
        if not CV_TERSEDIA:
            self.log.info("[auto-kalibrasi] opencv-python tidak tersedia, dilewati (pakai posisi tersimpan).")
            return False

        self.log.info("[*] Menjalankan auto-kalibrasi (mendeteksi posisi elemen di aplikasi)...")
        posisi_lama = self.cfg["posisi"]
        posisi_baru = dict(posisi_lama)
        ada_perubahan = False
        ada_yang_gagal = False

        for key, label in TARGET_LIST:
            hasil = self._cocokkan_template(win, key)
            if hasil is None:
                self.log.warning(f"    [!] Template untuk '{label}' belum ada -> perlu kalibrasi manual.")
                ada_yang_gagal = True
                continue

            skor, (loc_x, loc_y), (tw, th) = hasil
            if skor < self.cfg["match_threshold"]:
                self.log.warning(f"    [!] '{label}' tidak terdeteksi yakin (skor={skor:.2f}). Pakai posisi lama.")
                ada_yang_gagal = True
                continue

            center_x = win.left + loc_x + tw / 2
            center_y = win.top + loc_y + th / 2
            rel_x = round(min(max((center_x - win.left) / win.width, 0.0), 1.0), 4)
            rel_y = round(min(max((center_y - win.top) / win.height, 0.0), 1.0), 4)

            lama = posisi_lama.get(key)
            if lama and (abs(rel_x - lama[0]) > 0.001 or abs(rel_y - lama[1]) > 0.001):
                ada_perubahan = True
            posisi_baru[key] = [rel_x, rel_y]
            self.log.info(f"    [+] '{label}' terdeteksi, skor={skor:.2f} -> posisi ({rel_x}, {rel_y})")

        self.cfg["posisi"] = posisi_baru
        if ada_perubahan:
            simpan_config(self.cfg)
            self.log.info("[+] Auto-kalibrasi selesai, posisi klik disesuaikan & disimpan.")
        elif ada_yang_gagal:
            self.log.info("[~] Auto-kalibrasi sebagian: elemen gagal terdeteksi memakai posisi tersimpan.")
        else:
            self.log.info("[+] Auto-kalibrasi selesai, semua posisi masih sesuai.")
        return ada_yang_gagal

    # ---------------------------------------------------------- verifikasi
    def _baca_teks_ocr(self, image):
        if not OCR_TERSEDIA:
            return None
        try:
            teks = pytesseract.image_to_string(image, lang="ind+eng")
            return teks.lower().strip()
        except Exception as e:
            self.log.warning(f"    [!] OCR gagal dijalankan (cek instalasi Tesseract): {e}")
            return None

    @staticmethod
    def _skor_perbedaan_gambar(img_a, img_b):
        try:
            if img_a.size != img_b.size:
                img_b = img_b.resize(img_a.size)
            diff = ImageChops.difference(img_a.convert("RGB"), img_b.convert("RGB"))
            stat = ImageStat.Stat(diff)
            return sum(stat.mean) / len(stat.mean)
        except Exception:
            return None

    def _verifikasi_hasil_submit(self, win, snapshot_sebelum):
        if not self.cfg.get("aktifkan_verifikasi", True):
            return "tidak_diketahui"

        win = self._pastikan_fokus(win)
        if win is None:
            return "tidak_diketahui"

        img_notif = self._ambil_screenshot_region(win, self.cfg["ocr_region_notifikasi"])
        teks = self._baca_teks_ocr(img_notif)
        if teks:
            if any(kw in teks for kw in self.cfg["kata_kunci_gagal"]):
                self.log.info(f"    [OCR] Indikasi GAGAL pada notifikasi: \"{teks[:60]}...\"")
                return "gagal"
            if any(kw in teks for kw in self.cfg["kata_kunci_sukses"]):
                self.log.info(f"    [OCR] Indikasi SUKSES pada notifikasi: \"{teks[:60]}...\"")
                return "sukses"

        if snapshot_sebelum is not None:
            img_sesudah = self._ambil_screenshot_region(win, self.cfg["diff_region_form"])
            skor = self._skor_perbedaan_gambar(snapshot_sebelum, img_sesudah)
            if skor is not None:
                self.log.info(f"    [DIFF] Skor perbedaan area form: {skor:.2f} (ambang: {self.cfg['diff_threshold']})")
                return "sukses" if skor >= self.cfg["diff_threshold"] else "gagal"

        return "tidak_diketahui"

    def _proses_satu_sku(self, win, sku, qty):
        self._tunggu_jika_pause()
        posisi = self.cfg["posisi"]

        win = self._pastikan_fokus(win)
        if win is None:
            raise RuntimeError("Jendela target tidak aktif/tidak ditemukan sebelum cari SKU.")

        self._click_relative(win, *posisi["cari_sku"])
        self._input_teks_via_clipboard(sku)
        pyautogui.press("enter")
        self._delay_aman(self.cfg["delay_load_sku"])

        win = self._pastikan_fokus(win)
        if win is None:
            raise RuntimeError("Jendela target tidak aktif/tidak ditemukan setelah cari SKU.")

        self._click_relative(win, *posisi["req_stock"])
        self._input_teks_via_clipboard(qty)
        self._delay_aman(0.2)

        win = self._pastikan_fokus(win)
        if win is None:
            raise RuntimeError("Jendela target tidak aktif/tidak ditemukan sebelum submit.")

        snapshot_sebelum = None
        if self.cfg.get("aktifkan_verifikasi", True):
            try:
                snapshot_sebelum = self._ambil_screenshot_region(win, self.cfg["diff_region_form"])
            except Exception:
                snapshot_sebelum = None

        self._click_relative(win, *posisi["submit"])
        self._delay_aman(self.cfg["delay_after_submit"])

        status = self._verifikasi_hasil_submit(win, snapshot_sebelum)
        if status == "gagal":
            raise RuntimeError("Verifikasi OCR/screenshot-diff mendeteksi submit GAGAL.")
        elif status == "tidak_diketahui":
            self.log.info("    [~] Status submit tidak dapat dipastikan. Dianggap OK.")
        return win

    # ------------------------------------------------------------- start/stop
    def mulai(self, lanjutkan_progress=None):
        if self.sedang_berjalan:
            return
        self.stop_event.clear()
        self.pause_event.clear()
        self.sedang_berjalan = True
        self.thread = threading.Thread(target=self._run, args=(lanjutkan_progress,), daemon=True)
        self.thread.start()

    def _run(self, lanjutkan_progress):
        try:
            self._run_inti(lanjutkan_progress)
        except BerhentiDiminta:
            self.log.warning("[!] PROSES DIHENTIKAN OLEH PENGGUNA.")
            self.log.info("    Progress sudah tersimpan, klik Mulai lagi untuk melanjutkan.")
        except FileNotFoundError:
            self.log.error(f"[ERROR] File Excel '{self.cfg['excel_file']}' tidak ditemukan.")
        except KeyError as e:
            self.log.error(f"[ERROR] Kolom header {e} tidak ditemukan dalam sheet Excel.")
        except Exception:
            self.log.exception("[ERROR] Terjadi kesalahan tidak terduga.")
        finally:
            self.sedang_berjalan = False
            self.on_status_change()

    def _run_inti(self, lanjutkan_progress):
        if pd is None:
            raise RuntimeError("Library pandas belum terinstall (pip install pandas openpyxl).")
        if not AUTOMASI_TERSEDIA:
            raise RuntimeError("Library pyautogui/keyboard/pygetwindow/pyperclip belum terinstall.")

        self.log.info("=" * 60)
        self.log.info("SESI BARU DIMULAI")
        self.log.info("=" * 60)

        df = pd.read_excel(self.cfg["excel_file"])
        df = df.dropna(subset=[self.cfg["kolom_sku"]])
        if df.empty:
            self.log.warning("[!] File Excel tidak berisi data SKU yang valid.")
            return

        sku_list = df[self.cfg["kolom_sku"]].tolist()
        kolom_req = self.cfg["kolom_req"]
        req_list = df[kolom_req].tolist() if kolom_req in df.columns else [self.cfg["default_qty"]] * len(sku_list)
        total_data = len(sku_list)
        self.log.info(f"Total SKU pada file Excel: {total_data} item")

        win = self.jalankan_dan_deteksi_target()
        if not win:
            self.log.warning("[!] Gagal mendeteksi/membuka aplikasi target. Proses dihentikan.")
            return

        self.auto_kalibrasi_ulang(win)

        start_idx = 0
        gagal_permanen = []
        if lanjutkan_progress:
            start_idx = lanjutkan_progress.get("last_index", 0)
            gagal_permanen = lanjutkan_progress.get("gagal_permanen", [])
        else:
            hapus_progress()

        if start_idx >= total_data:
            self.log.info("[+] Semua SKU pada progress tersimpan sudah selesai diproses sebelumnya.")
            hapus_progress()
            return

        self.log.info(f"Penginputan otomatis dimulai dalam {self.cfg['delay_countdown']:.0f} detik...")
        for i in range(int(self.cfg["delay_countdown"]), 0, -1):
            self.log.info(f"Mulai dalam {i}...")
            self._delay_aman(1.0)

        self.log.info(f"[+] Memulai penginputan data otomatis dari SKU ke-{start_idx + 1}...")
        self.on_status_change(total=total_data, index=start_idx)

        for idx in range(start_idx, total_data):
            self._cek_stop()
            self._tunggu_jika_pause()

            raw_sku = sku_list[idx]
            raw_req = req_list[idx]
            sku = self.format_clean_string(raw_sku)
            qty = self.format_clean_string(raw_req, default_val=self.cfg["default_qty"])

            self.log.info(f"[{idx + 1}/{total_data}] Memproses SKU: {sku} | Request Stock: {qty}")
            self.on_status_change(total=total_data, index=idx, sku=sku)

            berhasil = False
            error_terakhir = ""
            for percobaan in range(1, self.cfg["max_retry_sku"] + 1):
                try:
                    win = self._proses_satu_sku(win, sku, qty)
                    self.log.info(f"    --> Sukses Submit SKU: {sku}")
                    berhasil = True
                    break
                except BerhentiDiminta:
                    raise
                except Exception as e:
                    error_terakhir = str(e)
                    self.log.warning(f"    [X] Gagal input SKU {sku} (percobaan {percobaan}/{self.cfg['max_retry_sku']}): {e}")
                    if percobaan < self.cfg["max_retry_sku"]:
                        self._delay_aman(self.cfg["delay_retry_sku"])
                        win_retry = self._dapatkan_jendela_target()
                        if win_retry is not None:
                            win = win_retry

            if berhasil:
                tambah_history(sku, qty, "Sukses")
            else:
                self.log.warning(f"    [!!] SKU {sku} GAGAL PERMANEN setelah {self.cfg['max_retry_sku']}x percobaan.")
                gagal_permanen.append(sku)
                tambah_history(sku, qty, "Gagal Permanen", error_terakhir)

            simpan_progress(idx + 1, total_data, gagal_permanen, sku_terakhir=sku)
            self.on_status_change(total=total_data, index=idx + 1, sku=sku)

        hapus_progress()
        self.log.info("=" * 60)
        if gagal_permanen:
            self.log.info(f" SELESAI DENGAN {len(gagal_permanen)} SKU GAGAL PERMANEN.")
        else:
            self.log.info(" SUCCESS: Semua data SKU di Excel telah berhasil diinput!")
        self.log.info("=" * 60)

    # -------------------------------------------------------------- kalibrasi
    def mulai_kalibrasi(self, on_progress, on_selesai):
        """Kalibrasi interaktif: untuk tiap target, tunggu pengguna arahkan
        mouse lalu tekan tombol capture (default F8). on_progress dipanggil
        tiap update (label target, koordinat mouse). on_selesai(hasil_posisi_atau_None)
        dipanggil di akhir."""
        if self.kalibrasi_aktif:
            return
        self.kalibrasi_batal_event.clear()
        self.kalibrasi_aktif = True

        def _thread():
            posisi_baru = {}
            win = self._dapatkan_jendela_target()
            if win is None:
                self.log.warning("[!] Aplikasi target belum terdeteksi. Buka aplikasinya dahulu sebelum kalibrasi.")
                self.kalibrasi_aktif = False
                on_selesai(None)
                return

            capture_key = self.cfg["kalibrasi_capture_key"]
            stop_key = self.cfg["stop_key"]

            for key, label in TARGET_LIST:
                on_progress(label=label, key=key, mouse=pyautogui.position())
                tertangkap = False
                while not tertangkap:
                    if self.kalibrasi_batal_event.is_set():
                        self.log.warning("[!] Kalibrasi dibatalkan oleh pengguna.")
                        self.kalibrasi_aktif = False
                        on_selesai(None)
                        return
                    if keyboard.is_pressed(stop_key):
                        self.log.warning("[!] Kalibrasi dibatalkan oleh pengguna (tombol stop).")
                        self.kalibrasi_aktif = False
                        on_selesai(None)
                        return
                    if keyboard.is_pressed(capture_key):
                        win_terbaru = self._dapatkan_jendela_target() or win
                        mouse_x, mouse_y = pyautogui.position()
                        rel_x = round(min(max((mouse_x - win_terbaru.left) / max(win_terbaru.width, 1), 0.0), 1.0), 4)
                        rel_y = round(min(max((mouse_y - win_terbaru.top) / max(win_terbaru.height, 1), 0.0), 1.0), 4)
                        posisi_baru[key] = [rel_x, rel_y]

                        if CV_TERSEDIA:
                            try:
                                patch = self._ambil_patch_sekitar_titik(win_terbaru, mouse_x, mouse_y)
                                patch.save(os.path.join(TEMPLATE_DIR, f"template_{key}.png"))
                            except Exception as e:
                                self.log.warning(f"    -> Gagal simpan template untuk '{label}': {e}")

                        self.log.info(f"[+] Ditangkap: {label} = ({rel_x}, {rel_y})")
                        while keyboard.is_pressed(capture_key):
                            time.sleep(0.05)
                        tertangkap = True
                    else:
                        on_progress(label=label, key=key, mouse=pyautogui.position())
                        time.sleep(0.08)

            self.cfg["posisi"] = posisi_baru
            simpan_config(self.cfg)
            self.log.info("[+] Kalibrasi manual selesai & disimpan.")
            self.kalibrasi_aktif = False
            on_selesai(posisi_baru)

        self.kalibrasi_thread = threading.Thread(target=_thread, daemon=True)
        self.kalibrasi_thread.start()

    def batalkan_kalibrasi(self):
        self.kalibrasi_batal_event.set()


# ==============================================================================
# GUI - TEMA & KOMPONEN
# ==============================================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

WARNA_SUKSES = "#2ecc71"
WARNA_GAGAL = "#e74c3c"
WARNA_INFO = "#3b82f6"
WARNA_WARN = "#f39c12"


class KartuStatus(ctk.CTkFrame):
    """Kartu kecil untuk menampilkan satu metrik (mis. Status, SKU saat ini)."""

    def __init__(self, master, judul, nilai_awal="-", **kwargs):
        super().__init__(master, corner_radius=14, fg_color=("gray90", "gray17"), **kwargs)
        self.label_judul = ctk.CTkLabel(self, text=judul, font=ctk.CTkFont(size=12), text_color=("gray40", "gray60"))
        self.label_judul.pack(anchor="w", padx=16, pady=(12, 0))
        self.label_nilai = ctk.CTkLabel(self, text=nilai_awal, font=ctk.CTkFont(size=20, weight="bold"))
        self.label_nilai.pack(anchor="w", padx=16, pady=(0, 12))

    def set_nilai(self, teks, warna=None):
        self.label_nilai.configure(text=teks)
        if warna:
            self.label_nilai.configure(text_color=warna)


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, engine: AutomationEngine, cfg, app):
        super().__init__(master, fg_color="transparent")
        self.engine = engine
        self.cfg = cfg
        self.app = app

        self.grid_columnconfigure((0, 1, 2), weight=1)

        judul = ctk.CTkLabel(self, text="Kontrol", font=ctk.CTkFont(size=22, weight="bold"))
        judul.grid(row=0, column=0, columnspan=3, sticky="w", padx=4, pady=(0, 16))

        # --- kartu status
        self.kartu_status = KartuStatus(self, "STATUS")
        self.kartu_status.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self.kartu_status.set_nilai("Siap", WARNA_INFO)

        self.kartu_progress = KartuStatus(self, "PROGRESS")
        self.kartu_progress.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)

        self.kartu_sku = KartuStatus(self, "SKU SAAT INI")
        self.kartu_sku.grid(row=1, column=2, sticky="nsew", padx=4, pady=4)

        # --- progress bar
        self.progress_bar = ctk.CTkProgressBar(self, height=14, corner_radius=8)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=4, pady=(12, 16))

        # --- tombol kontrol
        frame_tombol = ctk.CTkFrame(self, fg_color="transparent")
        frame_tombol.grid(row=3, column=0, columnspan=3, sticky="w", padx=4, pady=(0, 16))

        self.btn_mulai = ctk.CTkButton(
            frame_tombol, text="▶  Mulai", width=140, height=42, corner_radius=10,
            fg_color=WARNA_SUKSES, hover_color="#27ae60", font=ctk.CTkFont(size=14, weight="bold"),
            command=self.klik_mulai,
        )
        self.btn_mulai.pack(side="left", padx=(0, 10))

        self.btn_pause = ctk.CTkButton(
            frame_tombol, text="⏸  Jeda", width=140, height=42, corner_radius=10,
            fg_color=WARNA_WARN, hover_color="#d68910", font=ctk.CTkFont(size=14, weight="bold"),
            command=self.klik_pause, state="disabled",
        )
        self.btn_pause.pack(side="left", padx=10)

        self.btn_stop = ctk.CTkButton(
            frame_tombol, text="⏹  Berhenti", width=140, height=42, corner_radius=10,
            fg_color=WARNA_GAGAL, hover_color="#c0392b", font=ctk.CTkFont(size=14, weight="bold"),
            command=self.klik_stop, state="disabled",
        )
        self.btn_stop.pack(side="left", padx=10)

        # --- log live
        label_log = ctk.CTkLabel(self, text="Log Aktivitas", font=ctk.CTkFont(size=14, weight="bold"))
        label_log.grid(row=4, column=0, columnspan=3, sticky="w", padx=4)

        self.textbox_log = ctk.CTkTextbox(self, corner_radius=12, font=ctk.CTkFont(family="Consolas", size=12))
        self.textbox_log.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=4, pady=(4, 4))
        self.textbox_log.configure(state="disabled")
        self.grid_rowconfigure(5, weight=1)

        self.after(150, self._poll_log_queue)
        self._perbarui_tombol()

    # ---------------------------------------------------------------- aksi
    def klik_mulai(self):
        if not os.path.exists(self.cfg["excel_file"]):
            messagebox.showerror("File Excel tidak ditemukan",
                                  f"File Excel berikut tidak ditemukan:\n{self.cfg['excel_file']}\n\n"
                                  "Silakan atur path yang benar di tab Pengaturan.")
            return
        if not os.path.exists(CONFIG_FILE):
            if not messagebox.askyesno("Belum Kalibrasi",
                                        "Aplikasi belum pernah dikalibrasi. Sebaiknya lakukan kalibrasi "
                                        "terlebih dahulu di tab Kalibrasi.\n\nTetap lanjutkan dengan posisi default?"):
                return

        lanjutkan_progress = None
        progress_lama = muat_progress()
        if progress_lama:
            pesan = (
                f"Ditemukan progress sesi sebelumnya:\n\n"
                f"Terakhir update : {progress_lama.get('waktu_update')}\n"
                f"Sudah diproses  : {progress_lama.get('last_index')} dari {progress_lama.get('total')} SKU\n"
                f"SKU terakhir    : {progress_lama.get('sku_terakhir')}\n\n"
                "Lanjutkan dari posisi terakhir?"
            )
            if messagebox.askyesno("Lanjutkan Progress?", pesan):
                lanjutkan_progress = progress_lama
            else:
                hapus_progress()

        self.engine.mulai(lanjutkan_progress=lanjutkan_progress)
        self._perbarui_tombol()

    def klik_pause(self):
        self.engine.toggle_pause()
        self._perbarui_tombol()

    def klik_stop(self):
        self.engine.minta_stop()
        self._perbarui_tombol()

    def _perbarui_tombol(self):
        berjalan = self.engine.sedang_berjalan
        dijeda = self.engine.pause_event.is_set()

        self.btn_mulai.configure(state="disabled" if berjalan else "normal")
        self.btn_pause.configure(
            state="normal" if berjalan else "disabled",
            text="▶  Lanjutkan" if dijeda else "⏸  Jeda",
            fg_color=WARNA_INFO if dijeda else WARNA_WARN,
        )
        self.btn_stop.configure(state="normal" if berjalan else "disabled")

        if berjalan and dijeda:
            self.kartu_status.set_nilai("Dijeda", WARNA_WARN)
        elif berjalan:
            self.kartu_status.set_nilai("Berjalan", WARNA_SUKSES)
        else:
            self.kartu_status.set_nilai("Siap", WARNA_INFO)

    def perbarui_status(self, total=None, index=None, sku=None):
        if total:
            self.kartu_progress.set_nilai(f"{index or 0} / {total}")
            self.progress_bar.set((index or 0) / total)
        if sku:
            self.kartu_sku.set_nilai(sku)
        self._perbarui_tombol()

    def _poll_log_queue(self):
        try:
            while True:
                msg = self.app.log_queue.get_nowait()
                self.textbox_log.configure(state="normal")
                self.textbox_log.insert("end", msg + "\n")
                self.textbox_log.see("end")
                self.textbox_log.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(150, self._poll_log_queue)


class PengaturanFrame(ctk.CTkFrame):
    def __init__(self, master, cfg, on_save):
        super().__init__(master, fg_color="transparent")
        self.cfg = cfg
        self.on_save = on_save
        self.entries = {}

        self.grid_columnconfigure(0, weight=1)
        judul = ctk.CTkLabel(self, text="Pengaturan", font=ctk.CTkFont(size=22, weight="bold"))
        judul.grid(row=0, column=0, sticky="w", padx=4, pady=(0, 16))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        scroll.grid_columnconfigure(0, weight=1)

        self._bagian(scroll, "Sumber Data Excel")
        self._baris_path(scroll, "excel_file", "File Excel (data SKU)", filetypes=[("Excel files", "*.xlsx *.xls")])
        self._baris_teks(scroll, "kolom_sku", "Nama Kolom SKU")
        self._baris_teks(scroll, "kolom_req", "Nama Kolom Request Stock")
        self._baris_teks(scroll, "default_qty", "Qty Default (jika kolom kosong)")

        self._bagian(scroll, "Aplikasi Target")
        self._baris_path(scroll, "target_exe_path", "Path Aplikasi (.exe)", filetypes=[("Executable", "*.exe"), ("Semua file", "*.*")])
        self._baris_teks(scroll, "target_launch_uri", "URI / Argumen Launch (opsional)")
        self._baris_teks(scroll, "window_titles", "Kata Kunci Judul Jendela (pisahkan koma)")

        btn_tes = ctk.CTkButton(scroll, text="🔍 Tes Deteksi Jendela", command=self._tes_deteksi, width=200)
        btn_tes.pack(anchor="w", pady=(4, 16))

        self._bagian(scroll, "Waktu Tunggu (detik)")
        self._baris_teks(scroll, "delay_countdown", "Hitung Mundur Sebelum Mulai")
        self._baris_teks(scroll, "delay_load_sku", "Tunggu Setelah Cari SKU")
        self._baris_teks(scroll, "delay_after_submit", "Tunggu Setelah Submit")
        self._baris_teks(scroll, "max_retry_sku", "Maks. Percobaan Ulang per SKU")

        self._bagian(scroll, "Fitur Tambahan")
        self.var_auto_kalibrasi = tk.BooleanVar(value=cfg.get("aktifkan_auto_kalibrasi", True))
        ctk.CTkSwitch(scroll, text="Aktifkan Auto-Kalibrasi (template matching)",
                       variable=self.var_auto_kalibrasi).pack(anchor="w", pady=6)

        self.var_verifikasi = tk.BooleanVar(value=cfg.get("aktifkan_verifikasi", True))
        ctk.CTkSwitch(scroll, text="Aktifkan Verifikasi Hasil Submit (OCR / diff gambar)",
                       variable=self.var_verifikasi).pack(anchor="w", pady=6)

        self._baris_path(scroll, "tesseract_cmd", "Path Tesseract-OCR (tesseract.exe)",
                          filetypes=[("Executable", "*.exe"), ("Semua file", "*.*")])

        info_lib = []
        if pd is None:
            info_lib.append("pandas")
        if not AUTOMASI_TERSEDIA:
            info_lib.append("pyautogui/keyboard/pygetwindow/pyperclip")
        if not CV_TERSEDIA:
            info_lib.append("opencv-python & numpy (opsional)")
        if not OCR_TERSEDIA:
            info_lib.append("pytesseract (opsional)")
        if info_lib:
            teks_info = "Library belum terpasang: " + ", ".join(info_lib)
            ctk.CTkLabel(scroll, text=teks_info, text_color=WARNA_WARN, wraplength=700, justify="left").pack(anchor="w", pady=(12, 0))

        btn_simpan = ctk.CTkButton(
            self, text="💾  Simpan Pengaturan", height=42, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"), command=self._simpan,
        )
        btn_simpan.grid(row=2, column=0, sticky="w", pady=(16, 0))

        self.label_status_simpan = ctk.CTkLabel(self, text="", text_color=WARNA_SUKSES)
        self.label_status_simpan.grid(row=3, column=0, sticky="w", pady=(6, 0))

    def _bagian(self, master, teks):
        ctk.CTkLabel(master, text=teks, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(16, 6))

    def _baris_teks(self, master, key, label):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(fill="x", pady=4)
        ctk.CTkLabel(frame, text=label, width=280, anchor="w").pack(side="left")
        entry = ctk.CTkEntry(frame, corner_radius=8)
        entry.insert(0, str(self.cfg.get(key, "")))
        entry.pack(side="left", fill="x", expand=True)
        self.entries[key] = entry

    def _baris_path(self, master, key, label, filetypes):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(fill="x", pady=4)
        ctk.CTkLabel(frame, text=label, width=280, anchor="w").pack(side="left")
        entry = ctk.CTkEntry(frame, corner_radius=8)
        entry.insert(0, str(self.cfg.get(key, "")))
        entry.pack(side="left", fill="x", expand=True)

        def browse():
            path = filedialog.askopenfilename(filetypes=filetypes)
            if path:
                entry.delete(0, "end")
                entry.insert(0, path)

        ctk.CTkButton(frame, text="Pilih...", width=90, command=browse).pack(side="left", padx=(8, 0))
        self.entries[key] = entry

    def _tes_deteksi(self):
        if not AUTOMASI_TERSEDIA:
            messagebox.showwarning("Tidak tersedia", "Library pygetwindow belum terinstall.")
            return
        keywords = [t.strip() for t in self.entries["window_titles"].get().split(",") if t.strip()]
        ditemukan = []
        for title in gw.getAllTitles():
            if any(k.lower() in title.lower() for k in keywords if k):
                ditemukan.append(title)
        if ditemukan:
            messagebox.showinfo("Jendela Ditemukan", "Jendela yang cocok:\n\n" + "\n".join(ditemukan))
        else:
            messagebox.showwarning("Tidak Ditemukan", "Tidak ada jendela terbuka yang cocok dengan kata kunci tersebut.")

    def _simpan(self):
        try:
            self.cfg["excel_file"] = self.entries["excel_file"].get().strip()
            self.cfg["kolom_sku"] = self.entries["kolom_sku"].get().strip()
            self.cfg["kolom_req"] = self.entries["kolom_req"].get().strip()
            self.cfg["default_qty"] = self.entries["default_qty"].get().strip()
            self.cfg["target_exe_path"] = self.entries["target_exe_path"].get().strip()
            self.cfg["target_launch_uri"] = self.entries["target_launch_uri"].get().strip()
            self.cfg["window_titles"] = self.entries["window_titles"].get().strip()
            self.cfg["delay_countdown"] = float(self.entries["delay_countdown"].get())
            self.cfg["delay_load_sku"] = float(self.entries["delay_load_sku"].get())
            self.cfg["delay_after_submit"] = float(self.entries["delay_after_submit"].get())
            self.cfg["max_retry_sku"] = int(self.entries["max_retry_sku"].get())
            self.cfg["tesseract_cmd"] = self.entries["tesseract_cmd"].get().strip()
            self.cfg["aktifkan_auto_kalibrasi"] = self.var_auto_kalibrasi.get()
            self.cfg["aktifkan_verifikasi"] = self.var_verifikasi.get()
        except ValueError:
            messagebox.showerror("Input Tidak Valid", "Pastikan kolom waktu tunggu / angka diisi dengan angka yang benar.")
            return

        simpan_config(self.cfg)
        self.on_save(self.cfg)
        self.label_status_simpan.configure(text="✓ Pengaturan tersimpan.")
        self.after(2500, lambda: self.label_status_simpan.configure(text=""))


class KalibrasiFrame(ctk.CTkFrame):
    def __init__(self, master, engine: AutomationEngine, cfg):
        super().__init__(master, fg_color="transparent")
        self.engine = engine
        self.cfg = cfg

        judul = ctk.CTkLabel(self, text="Kalibrasi Posisi Klik", font=ctk.CTkFont(size=22, weight="bold"))
        judul.pack(anchor="w", pady=(0, 8))

        capture_key = cfg["kalibrasi_capture_key"].upper()
        stop_key = cfg["stop_key"].upper()
        teks_info = (
            f"Kalibrasi dipakai supaya program tahu di mana harus mengklik pada aplikasi target.\n"
            f"Untuk tiap target di bawah: buka & arahkan aplikasi target, arahkan kursor mouse ke posisi yang "
            f"tepat, lalu tekan tombol keyboard [{capture_key}]. Tekan [{stop_key}] kapan saja untuk membatalkan."
        )
        ctk.CTkLabel(self, text=teks_info, wraplength=760, justify="left", text_color=("gray30", "gray70")).pack(anchor="w", pady=(0, 16))

        self.kartu_posisi = {}
        frame_target = ctk.CTkFrame(self, fg_color="transparent")
        frame_target.pack(fill="x", pady=(0, 16))
        for key, label in TARGET_LIST:
            kartu = KartuStatus(frame_target, label.upper())
            kartu.pack(side="left", expand=True, fill="both", padx=4)
            self.kartu_posisi[key] = kartu
        self._perbarui_kartu_posisi()

        self.label_progress_kalibrasi = ctk.CTkLabel(
            self, text="Klik 'Mulai Kalibrasi' untuk memulai.", font=ctk.CTkFont(size=15, weight="bold")
        )
        self.label_progress_kalibrasi.pack(anchor="w", pady=(8, 4))

        self.label_mouse = ctk.CTkLabel(self, text="Posisi mouse: -", text_color=("gray40", "gray60"))
        self.label_mouse.pack(anchor="w", pady=(0, 16))

        frame_tombol = ctk.CTkFrame(self, fg_color="transparent")
        frame_tombol.pack(anchor="w")
        self.btn_mulai_kalibrasi = ctk.CTkButton(
            frame_tombol, text="🎯  Mulai Kalibrasi", height=42, corner_radius=10, width=180,
            font=ctk.CTkFont(size=14, weight="bold"), command=self._mulai_kalibrasi,
        )
        self.btn_mulai_kalibrasi.pack(side="left", padx=(0, 10))

        self.btn_batal_kalibrasi = ctk.CTkButton(
            frame_tombol, text="✕  Batalkan", height=42, corner_radius=10, width=140,
            fg_color=WARNA_GAGAL, hover_color="#c0392b", command=self._batalkan_kalibrasi, state="disabled",
        )
        self.btn_batal_kalibrasi.pack(side="left")

        self._polling_aktif = False

    def _perbarui_kartu_posisi(self):
        for key, label in TARGET_LIST:
            pos = self.cfg["posisi"].get(key)
            teks = f"({pos[0]}, {pos[1]})" if pos else "belum diatur"
            self.kartu_posisi[key].set_nilai(teks)

    def _mulai_kalibrasi(self):
        if not AUTOMASI_TERSEDIA:
            messagebox.showwarning("Tidak tersedia", "Library pyautogui/keyboard/pygetwindow belum terinstall.")
            return
        self.btn_mulai_kalibrasi.configure(state="disabled")
        self.btn_batal_kalibrasi.configure(state="normal")
        self._polling_aktif = True

        def on_progress(label, key, mouse):
            pass  # progress teks diperbarui lewat polling _poll_progress di bawah

        def on_selesai(hasil):
            self._polling_aktif = False
            self.btn_mulai_kalibrasi.configure(state="normal")
            self.btn_batal_kalibrasi.configure(state="disabled")
            self._perbarui_kartu_posisi()
            if hasil:
                self.label_progress_kalibrasi.configure(text="✓ Kalibrasi selesai & tersimpan.", text_color=WARNA_SUKSES)
            else:
                self.label_progress_kalibrasi.configure(text="Kalibrasi dibatalkan / gagal.", text_color=WARNA_WARN)

        self._target_index_terakhir = None
        self.engine.mulai_kalibrasi(on_progress, on_selesai)
        self._poll_progress()

    def _poll_progress(self):
        if not self._polling_aktif:
            return
        if AUTOMASI_TERSEDIA:
            try:
                x, y = pyautogui.position()
                self.label_mouse.configure(text=f"Posisi mouse: ({x}, {y})")
            except Exception:
                pass
        # tampilkan target yang sedang menunggu ditangkap (heuristik sederhana:
        # target pertama yang posisinya belum sama dengan hasil terakhir)
        capture_key = self.cfg["kalibrasi_capture_key"].upper()
        self.label_progress_kalibrasi.configure(
            text=f"Arahkan mouse ke target yang diminta lalu tekan [{capture_key}]  (lihat log di tab Kontrol)",
            text_color=WARNA_INFO,
        )
        self.after(150, self._poll_progress)

    def _batalkan_kalibrasi(self):
        self.engine.batalkan_kalibrasi()


class HistoryFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        judul = ctk.CTkLabel(self, text="Riwayat Penginputan", font=ctk.CTkFont(size=22, weight="bold"))
        judul.pack(anchor="w", pady=(0, 16))

        frame_tombol = ctk.CTkFrame(self, fg_color="transparent")
        frame_tombol.pack(fill="x", pady=(0, 12))
        ctk.CTkButton(frame_tombol, text="🔄  Muat Ulang", width=140, command=self.muat_ulang).pack(side="left", padx=(0, 10))
        ctk.CTkButton(frame_tombol, text="🗑  Hapus Semua Riwayat", width=180, fg_color=WARNA_GAGAL,
                      hover_color="#c0392b", command=self.hapus_semua).pack(side="left")

        # Treeview (pakai ttk karena butuh tabel kolom, distyle agar senada tema gelap)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b",
                         foreground="white", rowheight=28, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white",
                         font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", "#3b82f6")])

        kolom = ("waktu", "sku", "qty", "status", "keterangan")
        self.tree = ttk.Treeview(self, columns=kolom, show="headings", height=18)
        for k, lebar in zip(kolom, (150, 140, 70, 130, 300)):
            self.tree.heading(k, text=k.capitalize())
            self.tree.column(k, width=lebar, anchor="w")
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        self.label_ringkasan = ctk.CTkLabel(self, text="", text_color=("gray30", "gray70"))
        self.label_ringkasan.pack(anchor="w", pady=(10, 0))

        self.muat_ulang()

    def muat_ulang(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = muat_history()
        for item in reversed(data):  # terbaru di atas
            tag = "sukses" if item.get("status") == "Sukses" else "gagal"
            self.tree.insert("", "end", values=(
                item.get("waktu", ""), item.get("sku", ""), item.get("qty", ""),
                item.get("status", ""), item.get("keterangan", ""),
            ), tags=(tag,))
        self.tree.tag_configure("sukses", foreground="#2ecc71")
        self.tree.tag_configure("gagal", foreground="#e74c3c")

        total = len(data)
        sukses = sum(1 for d in data if d.get("status") == "Sukses")
        gagal = total - sukses
        self.label_ringkasan.configure(text=f"Total: {total}  |  Sukses: {sukses}  |  Gagal: {gagal}")

    def hapus_semua(self):
        if not messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus SEMUA riwayat? Tindakan ini tidak bisa dibatalkan."):
            return
        hapus_semua_history()
        self.muat_ulang()


# ==============================================================================
# APLIKASI UTAMA (SIDEBAR NAVIGASI)
# ==============================================================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Automasi Panel by Adi Nurputra")
        self.geometry("820x600")
        self.minsize(720, 560)

        self.cfg = muat_config()
        self.log_queue = queue.Queue()
        self.logger = setup_logger(self.log_queue)
        self.engine = AutomationEngine(self.cfg, self.logger, self.log_queue, on_status_change=self._on_status_change)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._buat_sidebar()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.frame_dashboard = DashboardFrame(self.container, self.engine, self.cfg, self)
        self.frame_pengaturan = PengaturanFrame(self.container, self.cfg, on_save=self._on_config_saved)
        self.frame_kalibrasi = KalibrasiFrame(self.container, self.engine, self.cfg)
        self.frame_history = HistoryFrame(self.container)

        for frame in (self.frame_dashboard, self.frame_pengaturan, self.frame_kalibrasi, self.frame_history):
            frame.grid(row=0, column=0, sticky="nsew")

        self._tampilkan("dashboard")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _buat_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=190, corner_radius=0, fg_color=("gray92", "gray14"))
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="⚙ Automasi\nPanel", font=ctk.CTkFont(size=19, weight="bold"),
                     justify="left").pack(anchor="w", padx=18, pady=(24, 2))
        ctk.CTkLabel(sidebar, text="by Adi Nurputra", font=ctk.CTkFont(size=11),
                     text_color=("gray40", "gray60"), justify="left").pack(anchor="w", padx=18, pady=(0, 20))

        self.tombol_nav = {}
        menu = [
            ("dashboard", "🏠  Kontrol"),
            ("pengaturan", "🛠  Pengaturan"),
            ("kalibrasi", "🎯  Kalibrasi"),
            ("history", "📜  Riwayat"),
        ]
        for key, teks in menu:
            btn = ctk.CTkButton(
                sidebar, text=teks, anchor="w", height=44, corner_radius=10,
                fg_color="transparent", text_color=("gray20", "gray90"),
                hover_color=("gray80", "gray25"), font=ctk.CTkFont(size=14),
                command=lambda k=key: self._tampilkan(k),
            )
            btn.pack(fill="x", padx=14, pady=4)
            self.tombol_nav[key] = btn

        status_lib = "Siap" if AUTOMASI_TERSEDIA and pd is not None else "Cek Pengaturan"
        warna = WARNA_SUKSES if AUTOMASI_TERSEDIA and pd is not None else WARNA_WARN
        ctk.CTkLabel(sidebar, text=f"● {status_lib}", text_color=warna,
                     font=ctk.CTkFont(size=12)).pack(side="bottom", pady=20)

    def _tampilkan(self, key):
        frame_map = {
            "dashboard": self.frame_dashboard,
            "pengaturan": self.frame_pengaturan,
            "kalibrasi": self.frame_kalibrasi,
            "history": self.frame_history,
        }
        frame_map[key].tkraise()
        if key == "history":
            self.frame_history.muat_ulang()
        for k, btn in self.tombol_nav.items():
            btn.configure(fg_color=("gray80", "gray25") if k == key else "transparent")

    def _on_config_saved(self, cfg):
        self.cfg = cfg
        self.engine.cfg = cfg

    def _on_status_change(self, **kwargs):
        # dipanggil dari thread automasi -> jadwalkan ke main thread GUI
        self.after(0, lambda: self.frame_dashboard.perbarui_status(**kwargs))

    def _on_close(self):
        if self.engine.sedang_berjalan:
            if not messagebox.askyesno("Otomasi Sedang Berjalan", "Proses otomasi masih berjalan. Berhenti dan tutup aplikasi?"):
                return
            self.engine.minta_stop()
        self.destroy()


def main():
    pastikan_folder_data()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
