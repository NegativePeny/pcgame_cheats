# PC Game Cheats Created by Vibe Coding

Kumpulan cheat, trainer, dan mod game PC yang dibuat dan di-reverse-engineer secara interaktif menggunakan pendekatan **Vibe Coding** bersama **Google Antigravity**.

---

## 🎮 Daftar Game & Cheat

| Game | Jenis Cheat / Mod | Teknologi | Fitur Utama | Dokumentasi |
| :--- | :--- | :--- | :--- | :--- |
| **Super Meat Boy** | Standalone GUI Trainer | Python 3 (`ctypes`, `wintypes`, `tkinter`) | Invincibility (God Mode), Unlimited Air Jump, Auto PID Attach, Audio Beep | [Buka README](Super%20Meat%20Boy/README.md) |
| **Cookie Clicker** | Native Mod (Steam / Web) | JavaScript (Cookie Clicker Mod API) | Free Upgrades (0 Cost), Free Buildings (0 Cost), Spend Bypass, Steam Achievements Safe | [Buka README](Cookie%20Clicker/README.md) |

---

## 📂 Struktur Proyek

```plaintext
PC-Game-Cheats-Created-by-Vibe-Coding/
├── Cookie Clicker/
│   ├── FreeUpgrades/
│   │   ├── info.txt           # Metadata mod Cookie Clicker
│   │   ├── main.js            # Script logic hook modding
│   │   └── paste.txt          # Path folder direktori mods local Steam
│   └── README.md              # Dokumentasi lengkap & panduan instalasi mod
│
├── Super Meat Boy/
│   ├── trainer.py             # Script utama trainer GUI & memory patcher
│   ├── run_trainer.bat        # Launcher one-click untuk Windows
│   ├── find_deaths.py         # Skrip analisis RVA & reverse engineering
│   └── README.md              # Dokumentasi lengkap & analisis teknis memory patching
│
└── readme.md                  # Dokumentasi utama repositori
```

---

## 🚀 Ringkasan Cara Penggunaan

### 1. Super Meat Boy
1. Jalankan game `SuperMeatBoy.exe`.
2. Masuk ke folder [`Super Meat Boy`](Super%20Meat%20Boy/) lalu klik ganda `run_trainer.bat` (atau `python trainer.py`).
3. Tekan **`F1`** untuk God Mode dan **`F2`** untuk Unlimited Jump langsung saat di dalam game.

### 2. Cookie Clicker
1. Buka folder mod lokal Cookie Clicker Steam:
   ```
   C:\Program Files (x86)\Steam\steamapps\common\Cookie Clicker\resources\app\mods\local
   ```
2. Salin folder [`Cookie Clicker/FreeUpgrades`](Cookie%20Clicker/FreeUpgrades/) ke lokasi tersebut.
3. Masuk ke menu **Options** -> **Manage mods** di dalam game, aktifkan mod, lalu restart game.

---

## ⚠️ Disclaimer

Seluruh proyek dan kode di repositori ini ditujukan untuk **tujuan edukasi, pembelajaran reverse engineering, dan penggunaan pribadi (single-player offline)**.