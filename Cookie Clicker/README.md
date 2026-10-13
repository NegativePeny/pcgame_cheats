# Cookie Clicker - Free Upgrades & Free Buildings Mod

Modifikasi mandiri (*standalone mod*) untuk **Cookie Clicker** (Versi `v2.052` Steam & Web) menggunakan Modding API native game.

Cheat/Mod ini dibuat dengan Google Antigravity untuk memberikan akses upgrade dan bangunan secara gratis tanpa mengurangi saldo cookies, serta tetap mendukung pencapaian Steam (*Steam Achievements*).

---

## 📌 Informasi Mod

- **Nama Game**: Cookie Clicker
- **Versi Didukung**: `v2.052` (Steam Edition & Web)
- **Mod Name**: Free Upgrades
- **Mod ID**: `free upgrades`
- **Tipe Mod**: Native JavaScript Mod (`info.txt`, `main.js`)
- **Dukungan Steam Achievements**: Aktif (`AllowSteamAchievs: 1`)

---

## 🎯 Fitur Cheat / Mod

1. **Gratis Semua Upgrade (0 Cost)**:
   - Semua item Upgrade di toko (icon di panel kanan atas) memiliki harga `0 cookies`.
   - Method `canBuy` selalu mengembalikan status `true` sehingga upgrade langsung dapat dibeli kapan saja.

2. **Gratis Semua Bangunan / Buildings (0 Cost)**:
   - Seluruh jenis bangunan (Cursor, Grandma, Farm, Mine, Factory, Bank, Temple, Wizard Tower, Shipment, Alchemy Lab, Portal, Time Machine, Antimatter Condenser, Prism, Chancemaker, Fractal Engine, Javascript Console, Idleverse, Cortex Baker, You) memiliki harga `0 cookies`.
   - Dilengkapi *logic hook* otomatis: kalkulasi ulang harga atau penambahan bangunan baru akan otomatis di-reset menjadi `0`.

3. **Bypass Pengurangan Saldo (Spend Bypass)**:
   - Fungsi `Game.Spend` dimatikan fungsinya sehingga belanja apapun tidak akan pernah memotong cookies yang Anda miliki.

4. **Kompatibel & Aman untuk Steam Achievements**:
   - Berkat flag `"AllowSteamAchievs": 1` di dalam `info.txt`, mod ini tidak menonaktifkan perolehan achievement di Steam.

5. **In-game Notification**:
   - Memunculkan popup notifikasi `"FREE UPGRADE AKTIF!"` saat mod berhasil dimuat ke dalam sesi permainan.

---

## 📖 Panduan Penggunaan & Instalasi (Steam Edition)

### Cara Pemasangan:

1. **Buka Folder Mods Cookie Clicker**:
   - Jalankan Cookie Clicker di Steam.
   - Buka menu **Options** (Pengaturan), scroll ke bawah ke bagian **Mods**, lalu klik **Manage mods**.
   - Klik tombol **Open /mods folder**.
   - Atau langsung buka direktori berikut di Windows Explorer:
     ```
     C:\Program Files (x86)\Steam\steamapps\common\Cookie Clicker\resources\app\mods\local
     ```

2. **Salin Folder Mod**:
   - Salin (*copy*) folder **`FreeUpgrades`** dari repositori ini ke dalam direktori `mods\local\` tersebut.
   - Pastikan strukturnya menjadi:
     ```
     .../mods/local/FreeUpgrades/
         ├── info.txt
         ├── main.js
         └── paste.txt
     ```

3. **Aktifkan Mod di Game**:
   - Kembali ke jendela **Manage mods** di dalam game.
   - Klik tombol **Enable** pada baris mod **Free Upgrades**.
   - Klik **Restart with new changes**.
   - Game akan memuat ulang, dan notifikasi konfirmasi `"FREE UPGRADE AKTIF!"` akan muncul.

---

## 🌐 Cara Penggunaan di Versi Web / Browser (Opsional)

Jika Anda bermain di browser (tanpa folder mods Steam):
1. Buka game Cookie Clicker di browser.
2. Buka Console Developer (tekan **F12** atau `Ctrl + Shift + I` lalu pilih tab **Console**).
3. Buka file [`Cookie Clicker/FreeUpgrades/main.js`](FreeUpgrades/main.js), salin seluruh isinya, tempel ke Console browser, lalu tekan **Enter**.

---

## 🔬 Bagaimana Google Antigravity Membuat Mod Ini (Dokumentasi Teknis)

Proses perancangan mod ini melibatkan analisis struktur runtime internal Cookie Clicker:

### 1. Hooking pada Engine Objek Game
- Cookie Clicker mengekspos objek global `Game` di window scope.
- Semua upgrade mewarisi prototype `Game.Upgrade.prototype`. Dengan meng-override:
  ```javascript
  Game.Upgrade.prototype.getPrice = function() { return 0; };
  Game.Upgrade.prototype.canBuy = function() { return true; };
  ```
  semua upgrade seketika dapat diakses tanpa biaya.

### 2. Logic Hook Persistence untuk Bangunan
- Objek bangunan (`Game.Objects`) memiliki dynamic pricing yang dihitung ulang setiap kali bangunan dibeli ($Price_{baru} = BasePrice \times 1.15^N$).
- Untuk mencegah game menimpa harga kembali ke angka normal, Antigravity mendaftarkan hook siklus game:
  ```javascript
  Game.registerHook('logic', function() {
      for (var i in Game.Objects) {
          if (Game.Objects[i].getPrice() !== 0) {
              Game.Objects[i].getPrice = function() { return 0; };
          }
      }
  });
  ```

### 3. Bypass Pembelanjaan Bersih
- Fungsi inti transaksi adalah `Game.Spend(howmuch)`. Dengan me-neutralisir fungsi tersebut menjadi `noop` (`function() {}`), integritas saldo cookies pemain terjaga 100%.
