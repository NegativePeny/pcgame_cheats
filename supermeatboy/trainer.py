import ctypes
from ctypes import wintypes
import time
import threading
import sys
import os
import winsound
import tkinter as tk
from tkinter import ttk, messagebox

# Windows API constants
PROCESS_ALL_ACCESS = 0x1F0FFF
PAGE_EXECUTE_READWRITE = 0x40
VK_F1 = 0x70
VK_F2 = 0x71

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32
psapi = ctypes.windll.psapi

class SMBTrainer:
    def __init__(self):
        self.pid = None
        self.h_process = None
        self.base_address = None
        self.invincible = False
        self.unlimited_jump = False
        self.running = True

        # Verified Relative Virtual Addresses (RVAs) for SuperMeatBoy.exe:
        # 1. INVINCIBILITY (God Mode)
        # Completely bypasses obstacle (saws, spikes, enemies) collision death & vulnerability checks
        self.patches_invincibility = [
            # (RVA, patch_bytes, orig_bytes)
            (0x79921, b'\xE9\x91\x00\x00\x00\x90\x90', b'\x8B\x07\x8B\xCF\x8B\x40\x70'), # P1 obstacle collision bypass
            (0x1815C1, b'\xE9\x91\x00\x00\x00\x90\x90', b'\x8B\x07\x8B\xCF\x8B\x40\x70'), # P2 obstacle collision bypass
            (0x76580, b'\x31\xC0\xC3\x90\x90\x90', b'\xB8\x01\x00\x00\x00\xC3'),         # P1 is_vulnerable -> return 0
            (0x17E3E0, b'\x31\xC0\xC3\x90\x90\x90', b'\xB8\x01\x00\x00\x00\xC3'),        # P2 is_vulnerable -> return 0
            (0x827F0, b'\xC3', b'\x56'),                                                  # MeatBoyCharactor::Die
            (0x18E3B0, b'\xC3', b'\x56'),                                                 # MeatBoyCharactor2::Die
            (0x828D0, b'\xC3', b'\x55'),                                                  # KillPlayer
            (0x18E490, b'\xC3', b'\x55')                                                  # KillPlayer2
        ]

        # 2. UNLIMITED JUMP (Infinite Air Jump on each Space press - NO flying/rocket bug)
        # Removes the mid-air jump prohibition so pressing Space gives an air jump repeatedly
        self.patches_unlimited_jump = [
            (0x76596, b'\x90\x90\x90\x90', b'\xA8\x02\x75\x0E'),       # DefaultMeatBoy P1: remove in-air jump block
            (0x17E3F6, b'\x90\x90\x90\x90', b'\xA8\x02\x75\x0E'),      # DefaultMeatBoy P2: remove in-air jump block
            (0x6CDC5, b'\x90\x90', b'\x7D\x06'),                        # Char 1: remove jump count limit
            (0x73315, b'\x90\x90', b'\x7D\x06'),                        # Char 2: remove jump count limit
            (0x813D5, b'\x90\x90', b'\x7D\x06'),                        # Char 3: remove jump count limit
            (0xF93A5, b'\x90\x90', b'\x7D\x06'),                        # Char 4: remove jump count limit
            (0x17A8D5, b'\x90\x90', b'\x7D\x06'),                       # Char 5: remove jump count limit
            (0x17B7E5, b'\x90\x90', b'\x7D\x06'),                       # Char 6: remove jump count limit
            (0x185355, b'\x90\x90', b'\x7D\x06'),                       # Char 7: remove jump count limit
            (0x189105, b'\x90\x90', b'\x7D\x06')                        # Char 8: remove jump count limit
        ]

    def is_process_alive(self):
        if not self.h_process:
            return False
        exit_code = wintypes.DWORD()
        if kernel32.GetExitCodeProcess(self.h_process, ctypes.byref(exit_code)):
            return exit_code.value == 259 # STILL_ACTIVE
        return False

    def attach(self):
        snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [
                ('dwSize', wintypes.DWORD),
                ('cntUsage', wintypes.DWORD),
                ('th32ProcessID', wintypes.DWORD),
                ('th32DefaultHeapID', ctypes.c_void_p),
                ('th32ModuleID', wintypes.DWORD),
                ('cntThreads', wintypes.DWORD),
                ('th32ParentProcessID', wintypes.DWORD),
                ('pcPriClassBase', ctypes.c_long),
                ('dwFlags', wintypes.DWORD),
                ('szExeFile', ctypes.c_char * 260)
            ]
        pe = PROCESSENTRY32()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32)

        new_pid = None
        if kernel32.Process32First(snapshot, ctypes.byref(pe)):
            while True:
                exe_name = pe.szExeFile.decode('ascii', errors='ignore').lower()
                if 'supermeatboy' in exe_name:
                    new_pid = pe.th32ProcessID
                    break
                if not kernel32.Process32Next(snapshot, ctypes.byref(pe)):
                    break
        kernel32.CloseHandle(snapshot)

        if not new_pid:
            self.pid = None
            self.h_process = None
            self.base_address = None
            return False, "SuperMeatBoy.exe tidak ditemukan. Jalankan gamenya."

        if self.pid == new_pid and self.is_process_alive():
            return True, f"Terhubung (PID: {self.pid})"

        # Clean old handle if needed
        if self.h_process:
            kernel32.CloseHandle(self.h_process)

        self.pid = new_pid
        self.h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, self.pid)
        if not self.h_process:
            return False, f"Gagal membuka proses PID {self.pid}."

        h_mods = (wintypes.HMODULE * 1024)()
        cb_needed = wintypes.DWORD()
        if psapi.EnumProcessModules(self.h_process, ctypes.byref(h_mods), ctypes.sizeof(h_mods), ctypes.byref(cb_needed)):
            self.base_address = h_mods[0]
            # Ensure DoJump has original code (prevent continuous jetpack flying)
            self.write_bytes(self.base_address + 0x772B0, b'\x74\x69')
            self.write_bytes(self.base_address + 0x17EFF0, b'\x74\x69')

            # Re-apply any active cheats
            if self.invincible:
                for rva, patch, _ in self.patches_invincibility:
                    self.write_bytes(self.base_address + rva, patch)
            if self.unlimited_jump:
                for rva, patch, _ in self.patches_unlimited_jump:
                    self.write_bytes(self.base_address + rva, patch)

            return True, f"Terhubung ke SuperMeatBoy.exe (PID: {self.pid})"

        return False, "Gagal mendapatkan Base Address SuperMeatBoy.exe."

    def write_bytes(self, addr, data):
        if not self.h_process:
            return False
        old_protect = wintypes.DWORD()
        size = len(data)
        kernel32.VirtualProtectEx(self.h_process, addr, size, PAGE_EXECUTE_READWRITE, ctypes.byref(old_protect))
        written = wintypes.DWORD()
        kernel32.WriteProcessMemory(self.h_process, addr, data, size, ctypes.byref(written))
        temp = wintypes.DWORD()
        kernel32.VirtualProtectEx(self.h_process, addr, size, old_protect, ctypes.byref(temp))
        kernel32.FlushInstructionCache(self.h_process, addr, size)
        return written.value == size

    def toggle_invincibility(self):
        if not self.is_process_alive():
            ok, _ = self.attach()
            if not ok: return False
        self.invincible = not self.invincible
        for rva, patch, orig in self.patches_invincibility:
            addr = self.base_address + rva
            self.write_bytes(addr, patch if self.invincible else orig)
        
        try:
            winsound.Beep(1200 if self.invincible else 600, 150)
        except Exception:
            pass
        return self.invincible

    def toggle_unlimited_jump(self):
        if not self.is_process_alive():
            ok, _ = self.attach()
            if not ok: return False
        self.unlimited_jump = not self.unlimited_jump
        for rva, patch, orig in self.patches_unlimited_jump:
            addr = self.base_address + rva
            self.write_bytes(addr, patch if self.unlimited_jump else orig)
        
        try:
            winsound.Beep(1500 if self.unlimited_jump else 700, 150)
        except Exception:
            pass
        return self.unlimited_jump

    def cleanup(self):
        if self.is_process_alive() and self.base_address:
            for rva, _, orig in self.patches_invincibility:
                self.write_bytes(self.base_address + rva, orig)
            for rva, _, orig in self.patches_unlimited_jump:
                self.write_bytes(self.base_address + rva, orig)
            self.write_bytes(self.base_address + 0x772B0, b'\x74\x69')
            self.write_bytes(self.base_address + 0x17EFF0, b'\x74\x69')
            kernel32.CloseHandle(self.h_process)
            self.h_process = None


class TrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Super Meat Boy - Trainer")
        self.root.geometry("420x330")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e24")

        self.trainer = SMBTrainer()

        # Header
        title_lbl = tk.Label(
            root,
            text="SUPER MEAT BOY TRAINER",
            font=("Segoe UI", 14, "bold"),
            fg="#f25f5c",
            bg="#1e1e24"
        )
        title_lbl.pack(pady=(15, 5))

        # Status Label
        self.status_lbl = tk.Label(
            root,
            text="Menghubungkan ke game...",
            font=("Consolas", 9),
            fg="#cccccc",
            bg="#1e1e24",
            wraplength=380
        )
        self.status_lbl.pack(pady=(0, 15))

        # Card Frame
        card = tk.Frame(root, bg="#2b2d42", bd=0, relief="flat")
        card.pack(fill="x", padx=20, pady=5)

        # Invincibility Row
        f1_frame = tk.Frame(card, bg="#2b2d42")
        f1_frame.pack(fill="x", padx=15, pady=10)

        lbl_god = tk.Label(
            f1_frame,
            text="[F1] Invincibility (God Mode)",
            font=("Segoe UI", 11, "bold"),
            fg="#edf2f4",
            bg="#2b2d42"
        )
        lbl_god.pack(side="left")

        self.btn_god = tk.Button(
            f1_frame,
            text="OFF",
            width=8,
            font=("Segoe UI", 9, "bold"),
            bg="#4a4e69",
            fg="white",
            relief="flat",
            command=self.on_toggle_god
        )
        self.btn_god.pack(side="right")

        # Separator
        sep = tk.Frame(card, height=1, bg="#3d405b")
        sep.pack(fill="x", padx=10)

        # Unlimited Jump Row
        f2_frame = tk.Frame(card, bg="#2b2d42")
        f2_frame.pack(fill="x", padx=15, pady=10)

        lbl_jump = tk.Label(
            f2_frame,
            text="[F2] Unlimited Jump (Air Jump)",
            font=("Segoe UI", 11, "bold"),
            fg="#edf2f4",
            bg="#2b2d42"
        )
        lbl_jump.pack(side="left")

        self.btn_jump = tk.Button(
            f2_frame,
            text="OFF",
            width=8,
            font=("Segoe UI", 9, "bold"),
            bg="#4a4e69",
            fg="white",
            relief="flat",
            command=self.on_toggle_jump
        )
        self.btn_jump.pack(side="right")

        # Footer Info
        footer = tk.Label(
            root,
            text="Tekan F1 / F2 di dalam game untuk toggle langsung.\nUnlimited Jump: Tekan Spasi berulang kali saat di udara.",
            font=("Segoe UI", 8),
            fg="#8d99ae",
            bg="#1e1e24",
            justify="center"
        )
        footer.pack(side="bottom", pady=12)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        ok, msg = self.trainer.attach()
        self.status_lbl.config(text=msg, fg="#2ec4b6" if ok else "#e71d36")

        self.hotkey_thread = threading.Thread(target=self.hotkey_loop, daemon=True)
        self.hotkey_thread.start()

    def update_ui(self):
        if self.trainer.invincible:
            self.btn_god.config(text="ON", bg="#2ec4b6", fg="#011627")
        else:
            self.btn_god.config(text="OFF", bg="#4a4e69", fg="white")

        if self.trainer.unlimited_jump:
            self.btn_jump.config(text="ON", bg="#2ec4b6", fg="#011627")
        else:
            self.btn_jump.config(text="OFF", bg="#4a4e69", fg="white")

    def on_toggle_god(self):
        ok, msg = self.trainer.attach()
        self.status_lbl.config(text=msg, fg="#2ec4b6" if ok else "#e71d36")
        if not ok: return
        self.trainer.toggle_invincibility()
        self.update_ui()

    def on_toggle_jump(self):
        ok, msg = self.trainer.attach()
        self.status_lbl.config(text=msg, fg="#2ec4b6" if ok else "#e71d36")
        if not ok: return
        self.trainer.toggle_unlimited_jump()
        self.update_ui()

    def hotkey_loop(self):
        last_f1 = 0
        last_f2 = 0
        last_check = 0
        while self.trainer.running:
            # Check game status every 2 seconds
            if time.time() - last_check > 2.0:
                last_check = time.time()
                if not self.trainer.is_process_alive():
                    self.root.after(0, lambda: self.trainer.attach())

            if user32.GetAsyncKeyState(VK_F1) & 0x8000:
                if time.time() - last_f1 > 0.35:
                    last_f1 = time.time()
                    self.root.after(0, self.on_toggle_god)

            if user32.GetAsyncKeyState(VK_F2) & 0x8000:
                if time.time() - last_f2 > 0.35:
                    last_f2 = time.time()
                    self.root.after(0, self.on_toggle_jump)

            time.sleep(0.02)

    def on_close(self):
        self.trainer.running = False
        self.trainer.cleanup()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = TrainerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
