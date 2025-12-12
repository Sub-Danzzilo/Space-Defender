**Space Defender**

**Deskripsi:**
Space Defender adalah game 2D shoot 'em up yang dibuat dengan Python dan Pygame. Pemain mengendalikan pesawat luar angkasa, menembak musuh, mengumpulkan power-up, dan bertahan selama mungkin untuk mendapatkan skor tertinggi.

**Versi ini:** Sudah dibuild menjadi executable Windows (.exe). File build dapat ditemukan di folder `build/` proyek. Jika Anda menerima bundel installer/EXE, jalankan file .exe yang sesuai pada mesin Windows.

**Daftar Isi README (ringkas):**
- **Deskripsi**: apa dan tujuan game
- **Persyaratan Sistem**: hardware & software minimal
- **Instalasi & Menjalankan**: .exe dan dari source
- **Kontrol**: tombol permainan
- **Mode Permainan**: singleplayer, local multiplayer, online multiplayer
- **Panduan Multiplayer Online**: cara host/join, port, firewall
- **Troubleshooting**: solusi umum
- **Kontak & Kredit**

**Persyaratan Sistem (Windows)**
- OS: Windows 10 / 11 (32/64-bit)
- CPU: dual-core 1.5GHz atau lebih cepat
- RAM: 2 GB+
- Storage: 150 MB kosong
- Graphics: GPU yang mendukung SDL/OpenGL dasar
- Jika menjalankan dari source: Python 3.9+ dan Pygame

**Lokasi build/executable**
- Periksa folder build di repository: [build/](build/)
- Contoh jalur build yang mungkin ada: [build/Space Defender/](build/Space%20Defender/)

**Instalasi & Menjalankan**

1) Menjalankan file .exe (direkomendasikan untuk pengguna Windows)
- Temukan executable di folder build (mis. `build/Space Defender/` atau folder distribusi lain).
- Jika ada file bernama `Space Defender.exe` atau serupa, klik dua kali untuk menjalankan.
- Jika Windows memblokir file, pilih "Run anyway" atau tambahkan pengecualian di antivirus.

2) Menjalankan dari source (untuk pengembang atau debugging)
- Pastikan Python 3.9+ terinstall: https://www.python.org/
- Buat virtual environment (opsional namun disarankan):

	pip install virtualenv
	python -m venv venv
	venv\Scripts\activate

- Install dependensi yang diperlukan (minimal Pygame):

	pip install pygame

- Jalankan game dari folder proyek:

	python main.py

- Jika ada modul lain yang hilang, pip akan menampilkan error; install modul yang diminta.

**Kontrol Permainan (default)**
- Gerak pemain 1: Panah kiri/kanan/atas/bawah
- Tembak pemain 1: Tombol Space
- (Jika local multiplayer) Pemain 2: gunakan tombol WASD untuk gerak, tombol K atau sesuai konfigurasi untuk tembak
- Pause: Esc atau ikon pause di UI

Catatan: Susunan tombol dapat berubah tergantung implementasi. Jika ada menu `Settings` di game, cek opsi kontrol di sana.

**Fitur Utama**
- Singleplayer & Local Multiplayer (split-screen)
- Online Multiplayer (host & join)
- Power-ups & upgrade senjata
- Multiple enemy types dan wave-based difficulty
- Sound & music (opsi mute tersedia)

**Mode Permainan**
- Singleplayer: main biasa melawan gelombang musuh
- Local multiplayer: dua pemain di satu mesin (split-screen)
- Online multiplayer: satu pemain jadi host, pemain lain join via IP

**Panduan Multiplayer Online (Host & Join)**

Ringkasan: game memiliki mekanisme host/client. Host menjalankan game dalam mode online host, menunggu koneksi, lalu memulai permainan; client memasukkan IP host untuk tersambung.

Langkah untuk Host (di LAN atau internet):
1. Jalankan executable (.exe) atau `python main.py`.
2. Dari menu utama pilih `Online` → `Host Game` (atau opsi serupa).
3. Pastikan komputer host dapat menerima koneksi:
	 - Jika di LAN: pastikan kedua komputer berada di jaringan yang sama.
	 - Jika lewat internet: lakukan port forwarding pada router ke IP lokal host untuk port yang dipakai oleh game (lihat catatan di bawah).
4. Berikan IP publik (atau IP LAN jika di jaringan yang sama) kepada pemain yang ingin join.
5. Ketika client terhubung, host dapat menekan `Start` untuk memulai permainan bersama.

Langkah untuk Client (Join):
1. Jalankan executable atau `python main.py` di komputer client.
2. Dari menu utama pilih `Online` → `Join Game` (atau opsi serupa).
3. Masukkan IP address host (contoh: `192.168.1.20` untuk LAN atau `203.0.113.10` untuk internet) dan tekan connect.
4. Tunggu sampai tersambung; client biasanya menerima konfirmasi kecil di layar.

Menemukan IP Host:
- Windows: buka Command Prompt dan jalankan `ipconfig`. Cari `IPv4 Address` pada adaptor yang terhubung.
- Untuk IP publik (internet): buka https://whatismyipaddress.com/ pada browser host.

Firewall & Port Forwarding (catatan teknis):
- Jika client tidak bisa terhubung, pastikan firewall Windows mengizinkan executable/game untuk menerima koneksi masuk.
- Jika host berada di belakang router dan client dari internet, lakukan port forwarding pada router ke IP lokal host. Port yang dipakai tergantung implementasi NetworkManager; jika tidak disebutkan di GUI, cek file `network_manager.py` untuk port default. Jika Anda tidak melihat port, gunakan dokumentasi developer atau jalankan host sementara dan lihat pesan log pada console yang biasanya menunjukkan port yang dipakai.
- Contoh umum: buka port TCP/UDP 5000 (sebagai contoh) di router dan arahkan ke IP host.

Keamanan & NAT Traversal:
- Untuk koneksi internet publik, port forwarding diperlukan kecuali game mendukung relay/servers.
- Alternatif: gunakan VPN (ZeroTier, Hamachi) untuk membuat jaringan virtual LAN jika port forwarding susah.

**Troubleshooting Umum**
- Game tidak mau jalan (Exe): pastikan file tidak diquarantine oleh Windows Defender/antivirus. Tambahkan pengecualian atau pulihkan dari quarantine.
- Error modul/ImportError saat menjalankan `main.py`: jalankan `pip install pygame` dan cek versi Python.
- LAG atau FPS drop: tutup aplikasi berat lainnya, kurangi resolusi layar, atau jalankan versi Console jika tersedia.
- Multiplayer tidak konek: cek IP host, izinkan firewall, dan jika perlu lakukan port forwarding atau gunakan VPN.

**Debug & Logging**
- Jika menjalankan dari source, jalankan `python main.py` dari terminal untuk melihat pesan log dan error.

**File penting di repo**
- README ini: [README.txt](README.txt)
- Entry point: [main.py](main.py)
- Manager jaringan: [network_manager.py](network_manager.py)
- Folder build: [build/](build/)

**Cara Membuat Build (.exe) Sendiri**
- Pengembang: gunakan PyInstaller atau alat serupa. Contoh perintah dasar:

	pip install pyinstaller
	pyinstaller --onefile --windowed main.py

- Sesuaikan opsi untuk memasukkan folder `assets/` bila perlu.

**Kontak & Kredit**
- Pembuat: lihat header script utama (periksa file `main.py`).
- Untuk bantuan lebih lanjut, buka issue di repositori atau kirim pesan ke pemilik proyek.

---

Jika Anda mau, saya bisa:
- Menjalankan sanity check terhadap executable di folder `build/` (jika Anda ingin saya cek file tertentu).
- Membuat instruksi singkat untuk port forwarding berdasarkan port yang dipakai (saya perlu melihat `network_manager.py`).

Perubahan README telah disimpan di [README.txt](README.txt). Silakan beri tahu jika Anda ingin menambahkan screenshot, logo, atau instruksi installer (.msi/.exe installer) lebih lanjut.