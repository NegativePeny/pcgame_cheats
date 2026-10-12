# Super Meat Boy Trainer (v1.25 / Race Mode Edition)

Trainer mandiri (*standalone*) berbasis GUI dan Global Hotkey untuk game **Super Meat Boy** (Versi `1.25` / *Race Mode Edition*).

Cheat ini dibuat secara native menggunakan Python dan Windows API tanpa memerlukan Cheat Engine.

---

## 📌 Informasi Game

- **Nama Game**: Super Meat Boy
- **Versi Didukung**: `v1.25` / Race Mode Edition
- **Executable**: `SuperMeatBoy.exe` (32-bit x86 WOW64)
- **Teknologi Trainer**: Python 3 standard library (`ctypes`, `wintypes`, `tkinter`, `winsound`)

---

## 🎯 Fitur Cheat

1. **[F1] Invincibility (God Mode)**:
   - Karakter Meat Boy kebal 100% terhadap semua rintangan mematikan seperti gergaji putar (*saws*), duri (*spikes*), proyektil, laser, lava, dan musuh.
   - Karakter tidak akan hancur menjadi darah/daging (*meat splatter*) dan stage tidak akan reset saat menyentuh obstacle.
2. **[F2] Unlimited Jump (Multi Air Jump)**:
   - Karakter dapat melompat berkali-kali di udara tanpa batas setiap kali tombol spasi ditekan (tap).
   - **Bebas dari bug melayang/terbang**: Menahan spasi tidak akan membuat karakter meluncur seperti jetpack. Setiap ketukan spasi menghasilkan 1 lompatan baru di udara sehingga ketinggian dapat diatur bertahap sesuai ketukan tombol.

---

## 📖 Panduan Penggunaan untuk Orang Awam / Pemula

Tidak perlu menginstall Cheat Engine atau software tambahan lain. Anda hanya perlu Python di komputer Anda.

### Persyaratan:
- Sistem Operasi: Windows 7 / 8 / 10 / 11.
- Python 3 terinstal di sistem (bawaan installer Python resmi).

### Langkah-langkah:
1. **Buka Game Terlebih Dahulu**:
   - Jalankan `SuperMeatBoy.exe` seperti biasa sampai masuk ke game atau menu utama.
2. **Jalankan Trainer**:
   - Klik ganda (double-click) file **`run_trainer.bat`**, atau jalankan lewat terminal:
     ```bash
     python trainer.py
     ```
3. **Periksa Status Koneksi**:
   - Jendela aplikasi kecil akan muncul dengan tulisan:  
     `Terhubung ke SuperMeatBoy.exe (PID: xxxx)` berwarna hijau.
4. **Gunakan Cheat di Dalam Game**:
   - Masuk ke level permainan.
   - Anda tidak perlu keluar game (*tab-out*). Tekan shortcut berikut langsung dari keyboard saat bermain:
     - Tekan **`F1`** untuk mengaktifkan/menonaktifkan **Invincibility (God Mode)**.
     - Tekan **`F2`** untuk mengaktifkan/menonaktifkan **Unlimited Jump**.
5. **Indikator Audio**:
   - Saat cheat diaktifkan, akan terdengar suara beep bernada tinggi (*High Beep*).
   - Saat cheat dinonaktifkan, akan terdengar suara beep bernada rendah (*Low Beep*).
   - Tombol pada jendela trainer juga akan berubah status dari `OFF` (abu-abu) menjadi `ON` (hijau toska).

---

## 🔬 Bagaimana Google Antigravity Membuat Cheat Ini (Dokumentasi Teknis & Reverse Engineering)

Berikut adalah riwayat analisis teknis dan proses reverse engineering yang dilakukan oleh **Google Antigravity** dalam membangun trainer ini:

### 1. Deteksi Proses & Arsitektur
- Mendeteksi proses game yang aktif: `SuperMeatBoy.exe` (Path: `D:\Games\Super Meat Boy Race Mode Edition\SuperMeatBoy.exe`).
- Memeriksa arsitektur binary: game berjalan sebagai modul 32-bit x86 di bawah subsistem WOW64 pada OS 64-bit.
- Menentukan Base Address aktif di memori RAM via `EnumProcessModules`. Walaupun ImageBase default PE adalah `0x400000`, fitur ASLR (*Address Space Layout Randomization*) Windows menggeser modul ke `0x7B0000`. Seluruh patch harus dihitung menggunakan **Relative Virtual Address (RVA)** agar dinamis terhadap ASLR.

### 2. Analisis Struktur Binary & PE Header
- Membaca header PE binary:
  - Section `.text`: Virtual Address `0x1000`, Raw File Address `0x400`.
  - Section `.rdata`: Virtual Address `0x35D000`, Raw File Address `0x35C200`.
- Rumus konversi alamat:  
  $$\text{Target In-Memory} = \text{Base Address} + (\text{Virtual Address} - 0x400000)$$

### 3. Mengapa Cheat Engine Lawas Tidak Bekerja pada Versi Ini
- Pada cheat table komunitas lama (misalnya buatan Geri era 2010), AOB script menargetkan kode lama sebelum *Race Mode Edition / Update 1.25*.
- Pada versi *Race Mode Edition*, struktur data karakter dan game loop diperluas (offset data karakter bergeser sebesar `+0xA0` byte, jump counter bergeser dari `0x9A8` ke `0xA48`). Selain itu, engine menduplikasi class logic untuk Player 1 (`SMB_1`) dan Player 2 / Race Mode (`SMB_2`).

### 4. Reverse Engineering Fitur 1: Invincibility (God Mode)
#### Masalah Awal:
Awalnya diasumsikan fungsi kematian dipicu oleh virtual method `MeatBoyCharactor::Die` (`0x4827F0`) dan `KillPlayer` (`0x4828D0`). Namun saat di-patch dengan `ret` (`0xC3`), karakter tetap mati saat menabrak gergaji (*saws*) atau duri (*spikes*).

#### Penelusuran & Solusi:
Melalui disassembly loop `Update()` milik class karakter (pada VA `0x479921` untuk Player 1 dan `0x5815C1` untuk Player 2):
```asm
0x004798E2: call 0x4D9870               ; Cek tabrakan dengan hazard lingkungan
0x004798E7: cmp eax, 1
0x004798EA: je 0x479921                 ; Jika kena hazard -> lompat ke blok damage
0x004798FF: call 0x483EC0               ; Cek tabrakan dengan musuh/saw
0x00479904: cmp eax, 1
0x00479907: je 0x479921                 ; Jika kena musuh -> lompat ke blok damage
...
0x00479921: mov eax, dword ptr [edi]    ; Blok eksekusi damage
0x00479925: mov eax, [eax + 0x70]       ; Panggil fungsi is_vulnerable() (0x476580)
0x00479928: call eax
0x0047992A: cmp eax, 1
0x0047992D: jne 0x4799B7                ; Jika tidak vulnerable -> skip ke frame normal
0x00479960: push 0xE
0x00479964: call 0x478910               ; Mainkan animasi meat splatter & trigger reset stage!
```

Ditemukan bahwa tabrakan obstacle langsung mengeksekusi blok animasi kematian di `0x479921` / `0x5815C1`. Jika karakter tidak vulnerable, engine melompat ke `0x4799B7` / `0x581657` (blok frame normal tanpa damage).

**Patch yang Diterapkan**:
1. Patch entry point collision handler di RVA `0x79921` (P1) dan `0x1815C1` (P2) menjadi instruksi `jmp` langsung (`\xE9\x91\x00\x00\x00\x90\x90`) menuju `0x4799B7` dan `0x581657`.
2. Patch fungsi `is_vulnerable()` di RVA `0x76580` dan `0x17E3E0` dari `mov eax, 1; ret` menjadi `xor eax, eax; ret` (`\x31\xC0\xC3`).
3. Tetap mem-patch `Die()` dan `KillPlayer()` sebagai lapisan perlindungan cadangan (*fallback*).

**Hasil**: Karakter Meat Boy sepenuhnya kebal terhadap semua duri, gergaji, musuh, dan proyektil.

---

### 5. Reverse Engineering Fitur 2: Unlimited Jump (Air Jump Tanpa Bug Terbang)
#### Masalah Awal:
Saat bypass dilakukan langsung pada fungsi `DoJump` (`0x4772B0` / `0x57EFF0` diubah menjadi `nop nop`), Meat Boy bisa melompat di udara, tetapi saat tombol spasi ditahan, karakter meluncur ke atas tanpa henti seperti roket/jetpack (*bug terbang*).

#### Penelusuran & Solusi:
Dilakukan disassembly pada virtual method `can_jump()` milik `DefaultMeatBoy` (`0x476590` untuk P1 dan `0x57E3F0` untuk P2):
```asm
0x00476590: mov eax, [ecx + 0x7B4]     ; Ambil bitmask status input & gerakan
0x00476596: test al, 2                 ; Cek apakah karakter SUDAH di udara?
0x00476598: jne 0x4765A8               ; Jika ya -> return 0 (TOLAK LOMPAT)
0x0047659A: test al, 0x20              ; Cek apakah tombol spasi ditekan?
0x0047659C: je 0x4765A8                ; Jika tidak -> return 0
0x0047659E: test al, al                ; Cek sign bit (edge detector tombol: baru ditekan frame ini)
0x004765A0: jns 0x4765A8               ; Jika tombol ditahan dari frame lalu -> return 0
0x004765A2: mov eax, 1                 ; Izinkan lompat
0x004765A7: ret 
0x004765A8: xor eax, eax               ; Tolak lompat
0x004765AA: ret
```

**Penjelasan Logika**:
- `test al, 2; jne fail` adalah pemblokir lompatan di udara.
- `test al, al; jns fail` adalah **edge detector input**. Ini yang membedakan antara "menekan tombol baru (tap)" dengan "menahan tombol terus menerus (hold)".
- Patch sebelumnya salah karena mem-bypass `DoJump` secara keseluruhan sehingga edge detector ini dilewati.

**Patch yang Diterapkan**:
1. Mengembalikan `DoJump()` ke kondisi asli (`\x74\x69` / `je`).
2. Menghapus **hanya** pengecekan in-air (`test al, 2; jne fail` di RVA `0x76596` dan `0x17E3F6`) dengan mengganti `\xA8\x02\x75\x0E` menjadi 4 byte NOP (`\x90\x90\x90\x90`).
3. Menghapus batas lompatan karakter lain di RVA `0x6CDC5`, `0x73315`, dll (`\x7D\x06` $\rightarrow$ `\x90\x90`).

**Hasil**: Edge detector tetap aktif. Karakter hanya melompat sekali setiap kali tombol spasi ditekan (*tap*). Menahan spasi tidak akan membuatnya terbang, dan pemain bisa menekan spasi berulang kali di udara untuk mencapai ketinggian tanpa batas.

---

### 6. Arsitektur Injeksi Memori Native (Tanpa Cheat Engine)
Trainer ditulis murni menggunakan Python Standard Library (`ctypes`):
- **`OpenProcess`** (`PROCESS_ALL_ACCESS = 0x1F0FFF`): Membuka handle memori target proses `SuperMeatBoy.exe`.
- **`VirtualProtectEx`** (`PAGE_EXECUTE_READWRITE = 0x40`): Membuka proteksi memori halaman kode mesin (*code section*) agar dapat dimodifikasi secara dinamis.
- **`WriteProcessMemory`**: Menulis opcode baru langsung ke RAM target.
- **`FlushInstructionCache`**: Membersihkan instruksi cache CPU agar opcode baru segera terbaca.
- **`GetAsyncKeyState`** (`user32.dll`): Membaca status tombol keyboard `F1` & `F2` secara asinkron di background thread.
- **Auto-Reconnect**: Menggunakan `GetExitCodeProcess` untuk mendeteksi apabila game ditutup/di-restart, sehingga trainer dapat otomatis menyambung kembali ke PID game yang baru.
