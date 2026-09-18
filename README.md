# Automasi Panel by Adi Nurputra

Aplikasi desktop (Windows) dengan antarmuka GUI modern untuk mengotomasi proses input stok/SKU ke aplikasi Storemode () yang berjalan di Windows Subsystem for Android (WSA) — atau aplikasi Windows lain sejenis yang bisa dikendalikan lewat klik posisi relatif pada jendela.

Awalnya berupa skrip CLI (`auto_storemode_v4.py`), kini dibungkus menjadi panel GUI lengkap dengan kontrol Start/Pause/Stop, pengaturan, kalibrasi visual, riwayat proses, dan auto-install dependensi.

## ✨ Fitur

- **Kontrol otomasi** — tombol Mulai / Jeda / Berhenti, progress bar, dan log aktivitas real-time.
- **Pengaturan fleksibel** — pilih file Excel sumber data, nama kolom SKU/Qty, path aplikasi target, kata kunci judul jendela, dan waktu tunggu — semua lewat GUI, tanpa edit kode.
- **Kalibrasi visual** — tentukan posisi klik (Cari SKU, Request Stock, Submit) secara interaktif dengan arahkan mouse + tekan tombol capture, lengkap dengan auto-kalibrasi ulang (template matching) bila tampilan aplikasi sedikit berubah/bergeser.
- **Riwayat (history)** — tabel riwayat tiap SKU yang diproses (waktu, SKU, qty, status, keterangan), bisa dimuat ulang dan dihapus semua langsung dari GUI.
- **Resume otomatis** — bila proses terhenti di tengah jalan, sesi berikutnya bisa melanjutkan dari SKU terakhir.
- **Verifikasi hasil submit** — opsional, memakai OCR (Tesseract) dan perbandingan screenshot untuk memastikan submit berhasil/gagal.
- **Auto-install dependensi** — saat pertama dijalankan, semua library Python yang dibutuhkan otomatis dicek & diinstall lewat pip, lengkap dengan progress window.

## 🖥️ Kebutuhan Sistem

- **Windows 10/11** (memakai `pyautogui`, `pygetwindow`, `keyboard` untuk kontrol mouse/keyboard & deteksi jendela — tidak berjalan di Linux/macOS).
- Python 3.9+ (bila menjalankan dari source, bukan dari `.exe`).
- Koneksi internet saat pertama kali dijalankan (untuk auto-install library).
- (Opsional) [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki) untuk fitur verifikasi hasil submit lewat OCR.

## 🚀 Instalasi & Menjalankan

### Opsi 1 — Jalankan dari source

```bash
git clone https://github.com/<username>/<nama-repo>.git
cd <nama-repo>
python automasi_storemode_gui.py
```

Semua dependensi (`customtkinter`, `pandas`, `pyautogui`, dll.) akan otomatis terinstall saat pertama kali dijalankan. Atau install manual lebih dulu:

```bash
pip install -r requirements.txt
```

### Opsi 2 — Build jadi file `.exe`

```bash
build_exe.bat
```

File hasil build ada di `dist\AutomasiPanel_AdiNurputra.exe` — tinggal jalankan tanpa perlu Python terinstall.

## 📂 Struktur Data

Semua data (konfigurasi, hasil kalibrasi, riwayat, dan log) disimpan otomatis di folder `macro_data/` di sebelah file program:

```
macro_data/
├── config.json              # pengaturan & posisi kalibrasi
├── history.json             # riwayat proses input
├── progress_input.json      # checkpoint untuk resume
├── template_kalibrasi/      # potongan gambar hasil kalibrasi
└── logs/                    # log lengkap tiap sesi
```

## ⚠️ Disclaimer

Proyek ini dibuat untuk kebutuhan otomasi internal/pribadi. Gunakan sesuai kebijakan penggunaan aplikasi target masing-masing. Penulis tidak bertanggung jawab atas penyalahgunaan alat ini.

## 👤 Dibuat oleh

**Adi Nurputra**
