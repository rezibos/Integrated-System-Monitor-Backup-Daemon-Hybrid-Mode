# 🖥️ Integrated System Monitor & Backup Daemon (Hybrid Mode)

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Mode](https://img.shields.io/badge/mode-hybrid-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Final Project - Sistem Operasi** **Proyek: Rancang Bangun System Daemon (Boot & Real-time)**

---

## 👨‍🎓 Informasi Project

| Field | Detail |
|-------|--------|
| **Kelompok** | Cukip |
| **Program Studi** | Teknik Informatika |
| **Universitas** | Universitas Maritim Raja Ali Haji |
| **Tahun** | 2025 |

### 👥 Anggota Kelompok

| No | Nama | NIM |
|----|------|-----|
| 1 | Muhammad Faiz | 2401020040 |
| 2 | Fachrezi Bachri | 2401020010 |
| 3 | Haikal Fachry Akbar | 2401020027 |
| 4 | Willy Hadipermana | 2401020019 |

---

## 📋 Deskripsi Project

**Integrated System Monitor** adalah daemon cerdas dengan arsitektur **Hybrid** yang menggabungkan keamanan data dan monitoring performa. Aplikasi ini bekerja dalam dua fase otomatis:

1.  **🚀 Fase Boot (One-Time):**
    Saat sistem menyala, daemon langsung mengamankan data dengan **Auto-Backup** dan memeriksa kesehatan sistem (**Update Checker**).
2.  **⚡ Fase Monitoring (Real-time):**
    Setelah tugas boot selesai, daemon beralih ke mode monitoring untuk memantau penggunaan **CPU, RAM, dan Disk** secara live yang ditampilkan pada Web Dashboard.

---

## ✨ Fitur Utama

### 1. 🛡️ Boot-Time Protection (Berjalan Sekali saat Start)
* **📦 Auto-Backup:** Otomatis mem-zip folder penting setiap kali komputer dinyalakan.
* **🔍 Update Audit:** Mendeteksi paket OS yang usang (Support: Arch Linux/Pacman & Debian/Apt).
* **📝 Boot Logging:** Mencatat kondisi update sistem ke file log permanen.

### 2. 📈 Real-Time Monitoring (Berjalan Terus-menerus)
* **🔥 CPU Usage:** Kalkulasi load processor secara akurat menggunakan `/proc/stat`.
* **💾 Memory Stats:** Monitor penggunaan RAM real-time dari `/proc/meminfo`.
* **💿 Disk Usage:** Tracking kapasitas penyimpanan sistem.
* **⏱️ Uptime:** Penampil waktu nyala sistem yang presisi.

### 3. 🌐 Web Dashboard Modern
* **⚡ Auto-Refresh:** Data diperbarui setiap 5 detik tanpa reload page.
* **📊 Visual Cards:** Progress bar interaktif untuk Resource Usage.
* **📱 Responsive:** Tampilan rapi di Desktop maupun Mobile.

---

## 💻 Code Highlights

Berikut adalah potongan kode inti yang menangani fungsi-fungsi krusial sistem.

### 🧠 1. Algoritma Kalkulasi CPU Real-time
Menggunakan teknik *differential sampling* dari kernel file `/proc/stat` untuk mendapatkan persentase penggunaan CPU yang akurat.

```python
def get_cpu_usage(self):
    # Mengambil snapshot data CPU pertama
    with open('/proc/stat', 'r') as f:
        line1 = f.readline()
    
    time.sleep(1)  # Sampling interval 1 detik
    
    # Mengambil snapshot kedua
    with open('/proc/stat', 'r') as f:
        line2 = f.readline()

    # Parsing raw data kernel
    p1 = [int(x) for x in line1.split()[1:]]
    p2 = [int(x) for x in line2.split()[1:]]

    # Menghitung selisih aktivitas (Delta)
    busy1 = sum(p1[0:3]) + sum(p1[5:8])
    total1 = sum(p1)
    busy2 = sum(p2[0:3]) + sum(p2[5:8])
    total2 = sum(p2)

    # Kalkulasi persentase
    delta_total = total2 - total1
    delta_busy = busy2 - busy1
    return round((delta_busy / delta_total) * 100, 1)
````

### 📦 2. Automated Backup Logic

Menggunakan library `zipfile` untuk mengompresi direktori target secara rekursif saat boot.

```python
def perform_backup_once(self):
    # Generate nama file unik dengan Timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backup_{timestamp}.zip"
    filepath = os.path.join(self.backup_dir, filename)

    # Proses Kompresi (ZIP_DEFLATED)
    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(self.backup_source):
            for file in files:
                p = os.path.join(root, file)
                # Menulis file ke dalam archive
                zipf.write(p, os.path.relpath(p, self.backup_source))
```

### 📝 3. System Update Checker

Mendeteksi distribusi Linux dan menjalankan perintah native (`checkupdates` atau `apt`) untuk membuat laporan log.

```python
def check_updates_once(self):
    packages = []
    # Deteksi OS (Arch Linux)
    if os.path.exists('/etc/arch-release'):
        cmd = ['checkupdates'] 
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parsing output terminal ke object
        for line in res.stdout.strip().split('\n'):
            p = line.split()
            packages.append({
                'name': p[0],
                'current': p[1],
                'new': p[3]
            })
    # Hasil akan ditulis ke file log updates_TIMESTAMP.log
```

-----

## 🗂️ Struktur Direktori

```text
log-monitor/
├── 📄 integrated_daemona.py       # 🧠 Main Daemon (Python)
├── 📄 setup_complete.sh           # ⚙️ Auto-Installer Script
├── 📄 README.md                   # 📖 Dokumentasi
│
├── 📁 output/                     # 📂 Hasil Output Daemon
│   ├── 📁 backups/                # 📦 File Backup (.zip)
│   └── 📁 logs/                   # 📝 Log Update Sistem
│
└── 📁 web/                        # 🌐 Dashboard Web
    ├── 📄 index.html              # Interface Utama
    ├── 📄 data.json               # Live Data Feed (JSON)
    ├── 📁 css/
    └── 📁 js/
```

-----

## 🚀 Instalasi & Penggunaan

### Prerequisites

  * Linux OS (Arch / Debian / Ubuntu / Manjaro)
  * Python 3.8+
  * Akses Root/Sudo

### Langkah 1: Setup Direktori

```bash
# Masuk ke direktori project (sesuaikan path)
cd /home/firaz/SO_LATIHAN/log-monitor

# Pastikan script memiliki izin eksekusi
chmod +x integrated_daemona.py setup_complete.sh
```

### Langkah 2: Konfigurasi Path

Buka file `integrated_daemona.py` dan sesuaikan variabel konfigurasi di bagian awal class:

```python
self.base_dir = '/home/firaz/SO_LATIHAN/log-monitor'
self.backup_source = '/home/firaz/Downloads/Data Dumy Back Up'
```

### Langkah 3: Install Service (Otomatis)

Gunakan script installer yang telah disediakan untuk mengatur systemd service secara otomatis.

```bash
sudo bash setup_complete.sh
```

*Script ini akan membuat file service, reload systemd, dan mengaktifkan daemon.*

### Langkah 4: Jalankan Dashboard

Untuk memantau grafik, jalankan web server sederhana:

```bash
cd web/
python3 -m http.server 8080
```

Buka browser dan akses: **http://localhost:8080**

-----

## 📸 Monitoring Commands

Gunakan perintah berikut di terminal untuk debugging:

| Perintah | Fungsi |
|----------|--------|
| `sudo systemctl status integrated-monitor` | Cek status service daemon |
| `sudo journalctl -u integrated-monitor -f` | Lihat log daemon real-time |
| `ls -lh output/backups/` | Cek daftar file backup |
| `cat output/logs/*.log` | Baca log update sistem |

-----

## 📄 License

MIT License - Free untuk tujuan edukasi.

-----

**© 2025 Kelompok Cukip - Universitas Maritim Raja Ali Haji**

```
```