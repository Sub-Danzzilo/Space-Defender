# 🚀 SPACE DEFENDER

> A Python-based 2D shoot 'em up game with single-player, local multiplayer, and online multiplayer modes

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [How to Play](#-how-to-play)
- [Online Multiplayer](#-online-multiplayer)
- [Game Mechanics](#-game-mechanics)
- [Strategy & Tips](#-strategy--tips)
- [Technical Details](#️-technical-details)
- [Troubleshooting](#-troubleshooting)
- [License & Credits](#-license--credits)

---

## 🎮 Overview

**Space Defender** adalah game shoot 'em up 2D yang dikembangkan dengan Python dan Pygame. Dalam game ini, pemain mengendalikan pesawat tempur untuk melawan gelombang musuh alien yang semakin kuat. Game ini menawarkan tiga mode permainan: singleplayer, local multiplayer (2 pemain di 1 komputer), dan online multiplayer melalui jaringan ZeroTier.

- **Platform**: Windows, macOS, Linux
- **Bahasa**: Python 3.8+
- **Framework**: Pygame 2.5+
- **Resolusi**: 800x600 @ 60 FPS

---

## ✨ Features

### 🎯 Game Modes

| Mode | Deskripsi |
| ------ | ----------- |
| **Singleplayer** | Bermain sendiri melawan gelombang musuh yang terus bertambah kuat |
| **Local Multiplayer** | Dua pemain di satu komputer dengan kontrol yang berbeda |
| **Online Multiplayer** | Bermain dengan teman melalui jaringan ZeroTier dengan koneksi real-time |

### 📊 Difficulty Levels

| Level | Kesulitan | Cocok Untuk |
| ------- | ----------- | ------------ |
| **Easy** | ⭐ | Pemula - musuh lebih lambat, pemain punya health lebih banyak |
| **Normal** | ⭐⭐ | Pemain Biasa - tingkat kesulitan standar yang seimbang |
| **Hard** | ⭐⭐⭐ | Pemain Berpengalaman - musuh lebih kuat dan cepat |
| **Extreme** | ⭐⭐⭐⭐⭐ | Expert - tantangan maksimal untuk pemain hardcore |

### 👾 Enemy Types (12+ Varian)

| Tipe | Karakteristik | Strategi |
| ------ | -------------- | ---------- |
| **Normal** | Musuh standar, gerak lurus | Mudah dihindari |
| **Fast** | Bergerak sangat cepat | Antisipasi jauh-jauh hari |
| **Bouncer** | Memantul kiri-kanan | Tembak di titik balik |
| **Red Shooter** | Menembakkan peluru balik | Prioritaskan! |
| **Kamikaze** | Mengejar saat dekat | Hindari dengan agresif |
| **Follower** | Mengikuti pergerakan pemain | Lakukan gerakan mendadak |
| **Tank** | HP tinggi, gerak lambat | Focus fire diperlukan |
| **Strong** | 3 HP, lebih tangguh | Butuh tembakan multiple |
| **Splitter** | Terbelah menjadi 2 saat mati | Hati-hati dengan splash |
| **Spiral** | Bergerak spiral/zigzag | Pola terprediksi |
| **Armored** | Armor keras (butuh 2 hit) | Tembak berulang kali |
| **Regenerator** | Regenerasi HP otomatis | Bunuh sebelum regenerate |

### 🎁 Power-Up System (7 Jenis)

| Power-Up | Efek | Durasi |
| ---------- | ------ | -------- |
| ⚡ **Rapid Fire** | Menembak 2x lebih cepat | 10 detik |
| 🐢 **Slow Enemies** | Memperlambat semua musuh 50% | 8 detik |
| 🌀 **Multiple Bullets** | Menembak 3 peluru sekaligus | 12 detik |
| ❤️ **Health Regen** | Menambah 1 HP (max 5) | Instant |
| 🏃 **Speed Boost** | Bergerak 2x lebih cepat | 10 detik |
| 🛡️ **Invincibility** | Kebal dari damage + visual shield | 15 detik |
| 💰 **Double Score** | Dapatkan 2x skor dari setiap kill | 15 detik |

### 🎨 Audio & Visual

- 🔊 **Sound Effects**: Tembak, ledakan, pickup power-up, ambient sound
- 🎵 **Music**: Musik dinamis untuk menu, gameplay, dan pause
- ✨ **Visual Effects**:  
  - Partikel ledakan dan damage
  - Animasi shield saat invincible
  - Bintang bergerak di background
  - UI dengan health bar, timer power-up, skor real-time

### ⚙️ Settings Menu

- 🔉 Pengaturan volume (musik dan SFX)
- 🎯 Pemilihan difficulty (Easy/Normal/Hard/Extreme)
- 🎮 Pemilihan scheme kontrol (WASD/Arrow Keys/IJKL)
- 📖 Menu help dengan scroll yang informatif
- 🖥️ Pengaturan resolusi dan visual preferences

---

## 💾 Installation

### Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **pip** (paket manager Python)
- **ZeroTier** (untuk online multiplayer) - [Download](https://www.zerotier.com/download/)

### Quick Start

```bash
# 1. Clone atau download repository
git clone <repository-url>
cd "Space Defender"

# 2. Install dependencies
pip install pygame psutil

# 3. Jalankan game
python main.py
```

### Struktur Folder yang Diperlukan

```bash
Space Defender/
├── main.py                  # Entry point game
├── assets/                  # Folder aset WAJIB ada
│   ├── images/             # Gambar sprite, background, UI
│   └── sounds/             # File audio (MP3/WAV)
├── *.py                    # File-file Python game
└── Space Defender.spec     # File PyInstaller (opsional)
```

> ⚠️ **Pastikan folder `assets/` ada dengan semua file gambar dan suara di dalamnya!**

---

## 🎮 How to Play

### Kontrol Singleplayer

| Aksi | Tombol |
| ------ | -------- |
| **Bergerak Atas** | W |
| **Bergerak Kiri** | A |
| **Bergerak Bawah** | S |
| **Bergerak Kanan** | D |
| **Menembak** | Otomatis (tidak perlu input) |
| **Pause/Menu** | ESC |
| **Resume** | ESC |

### Kontrol Local Multiplayer

| Aksi | Player 1 | Player 2 |
| ------ | ---------- | ---------- |
| **Atas** | W | ↑ |
| **Kiri** | A | ← |
| **Bawah** | S | ↓ |
| **Kanan** | D | → |
| **Alternatif P2** | - | I/J/K/L |
| **Pause Kedua Pemain** | ESC | ESC |

### Kontrol Umum (Semua Mode)

| Aksi | Tombol |
| ------ | -------- |
| **Navigasi Menu** | Mouse / Arrow Keys |
| **Klik Tombol** | Mouse / ENTER |
| **Scroll Menu** | Mouse Wheel / PgUp/PgDn |
| **Kembali** | ESC / Klik Back Button |

### Gameplay Tips

- 🎯 **Hindari bukan tembak**: Fokus pada hindaran lebih penting daripada damage
- 🎁 **Kumpulkan Power-Up**: Jangan sia-siakan power-up yang muncul
- 👾 **Prioritas Musuh**: Tembak Red Shooter terlebih dahulu (mereka menembak balik)
- 💪 **Strategi Multiplayer**: P1 jaga kiri, P2 jaga kanan untuk coverage maksimal
- ⚡ **Power-Up Combo**: Double Score + Multiple Bullets = Damage & Skor tinggi

---

## 🌐 Online Multiplayer

### Persiapan Awal

1. **Install ZeroTier** di kedua komputer
   - Download dari [ZeroTier.com](https://www.zerotier.com/download/)
   - Jalankan installer dan setup

2. **Buat/Bergabung Network ZeroTier**
   - Buka aplikasi ZeroTier
   - Cari/buat sebuah network (contoh: "SpaceDefender-Game")
   - Dapatkan ZeroTier IP (biasanya format `192.168.191.xxx`)
   - **PENTING**: Kedua pemain harus ada di network yang SAMA

3. **Verifikasi Koneksi**

   ```bash
   # Di cmd/terminal, test koneksi
   ping <zerotier-ip-teman>
   ```

   - Jika berhasil, lanjut ke step bermain
   - Jika gagal, periksa firewall (lihat Troubleshooting)

### Langkah-Langkah Bermain

#### 🖥️ Sebagai HOST (Pembuat Game)

1. Jalankan game → **START GAME** → **MULTIPLAYER** → **ONLINE MULTIPLAYER**
2. Klik **HOST GAME**
3. Game akan menampilkan IP Anda (contoh: `192.168.191.100`)
   - Jika IP tidak muncul, klik **REFRESH IP**
4. **Bagikan IP ini ke teman** (via chat, Discord, dll)
5. Tunggu hingga status berubah menjadi `⚫ PLAYER CONNECTED` (berwarna hijau)
6. Klik **START ONLINE GAME** untuk mulai

**Info yang dikirim ke Client**:

```bash
Beritahu teman:
- IP Address: 192.168.191.100
- Port: 7777 (default)
```

#### 👥 Sebagai CLIENT (Pemain yang Join)

1. Jalankan game → **START GAME** → **MULTIPLAYER** → **ONLINE MULTIPLAYER**
2. Klik **JOIN GAME**
3. Masukkan IP host di kolom input (contoh: `192.168.191.100`)
4. Klik **CONNECT TO HOST**
5. Tunggu hingga status berubah menjadi `✅ CONNECTED TO HOST` (berwarna hijau)
6. Tunggu host memulai game dengan klik **START ONLINE GAME**
7. Game dimulai!

**Selama Bermain**:

- **P1 (Host)**: Kontrol dengan WASD
- **P2 (Client)**: Kontrol dengan Arrow Keys
- **Pause**: Kedua pemain tekan ESC (pause bersama-sama)

### Troubleshooting Koneksi

#### ❌ Masalah: "Connection Refused"

```bash
Solusi:
1. ✓ Pastikan HOST sudah memilih "HOST GAME"
2. ✓ Pastikan IP yang dimasukkan benar (tanya ulang ke host)
3. ✓ Pastikan kedua PC terhubung ke network ZeroTier yang SAMA
4. ✓ Coba restart ZeroTier di kedua PC
```

#### ❌ Masalah: "Host Not Responding"

```bash
Solusi:
1. ✓ Periksa firewall (lihat "Solusi Firewall" di bawah)
2. ✓ Pastikan port 7777 tidak terblokir
3. ✓ Host harus tetap membuka game (jangan minimize/close)
4. ✓ Coba jalankan game sebagai Administrator
```

#### ❌ Masalah: "IP Address Not Detected"

```bash
Solusi:
1. ✓ Klik tombol "REFRESH IP" di host waiting screen
2. ✓ Tunggu 2-3 detik, IP akan muncul
3. ✓ Jika masih tidak muncul, restart ZeroTier
4. ✓ Pastikan ZeroTier sudah fully initialized
```

#### ❌ Masalah: "Game Tidak Sinkron / Lag"

```bash
Solusi:
1. ✓ Pastikan koneksi internet stabil (gunakan kabel jika mungkin)
2. ✓ Kurangi aplikasi lain yang menggunakan bandwidth
3. ✓ Pastikan kedua game menggunakan versi yang SAMA
4. ✓ Jika masih lag, firewall mungkin throttle koneksi
```

### 🔧 Solusi Firewall

#### Windows

1. Buka **Windows Defender Firewall**
   - Start → Cari "Firewall" → Klik "Windows Defender Firewall"
2. Klik **"Allow an app through firewall"**
3. Klik **"Change settings"** (mungkin perlu password)
4. Cari **Python.exe** atau **Space Defender.exe** (jika sudah dicompile)
   - Jika tidak ada, klik **"Allow another app"** → Browse
   - Pilih `python.exe` di folder instalasi Python
5. **Centang** kedua kolom: `Private` dan `Public`
6. Klik **OK**

#### macOS / Linux

```bash
# Untuk mengizinkan port 7777
sudo ufw allow 7777/tcp
sudo ufw allow 7777/udp

# Verifikasi
sudo ufw status
```

#### Alternatif: Disable Firewall (NOT RECOMMENDED)

⚠️ Hanya jika solusi di atas gagal:

- **Windows**: Disable Windows Defender Firewall temporary
- **macOS**: Disable firewall di System Preferences
- **Jangan lupa re-enable setelah selesai bermain!**

---

## 🎮 Game Mechanics

### Scoring System

| Aksi | Poin | Catatan |
| ------ | ------ | --------- |
| **Normal Enemy** | 10 | Dasar |
| **Fast Enemy** | 15 | Lebih sulit |
| **Bouncer/Spiral** | 15 | Pattern complex |
| **Red Shooter** | 25 | Berbahaya |
| **Kamikaze** | 20 | Mengejar |
| **Tank/Strong** | 30 | Tangguh |
| **Splitter** | 20 | Pertama terbilang |
| **Armored** | 25 | Armor sulit |
| **Regenerator** | 35 | Paling sulit |
| **Double Score Active** | **2x** Poin | Berlaku semua musuh |

### Enemy Wave Progression

```bash
Wave 1-3:   Normal + Fast enemies
Wave 4-6:   Tambah Bouncer + Red Shooter
Wave 7-10:  Tambah Kamikaze + Follower
Wave 11+:   Semua tipe musuh bisa muncul
            Semakin tinggi wave = semakin banyak enemy
```

### Combat Mechanics

#### Default Shooting

- Tembakan otomatis setiap 0.3 detik
- 1 peluru per tembakan

#### Dengan Power-Up Multiple Bullets

- 3 peluru per tembakan (fan pattern)
- Jarak 1.5x lebih lebar
- Sangat efektif untuk cluster musuh

#### Dengan Power-Up Rapid Fire

- Tembakan setiap 0.15 detik (2x lebih cepat)
- Damage output meningkat signifikan
- DPS: 20 → 40 per detik

### Movement & Collision

- **Player Speed**: 5 pixel/frame (default)
  - Dengan Speed Boost: 10 pixel/frame
- **Enemy Speed**: Berbeda per tipe musuh
  - Normal: 2 pixel/frame
  - Fast: 4 pixel/frame
  - Tank: 1 pixel/frame
- **Collision Detection**: AABB (Axis-Aligned Bounding Box)

---

## ⚙️ Technical Details

### System Requirements

| Komponen | Minimal | Recommended |
| ---------- | --------- | ------------- |
| **OS** | Windows 7+ / macOS 10.12+ / Linux | Windows 10+ / macOS 10.15+ / Linux Modern |
| **Python** | 3.8 | 3.10+ |
| **RAM** | 256 MB | 512 MB |
| **Storage** | 50 MB | 100 MB |
| **Display** | 800x600 | 1024x768+ |
| **Internet** | (Untuk online) | Kecepatan stabil 5+ Mbps |

### File Structure

```python
Space Defender/
│
├── 📄 main.py                    # Entry point aplikasi
├── 📄 game_manager.py            # Logika game utama & game loop
├── 📄 game_state_manager.py      # State machine (menu, gameplay, etc)
│
├── 👾 GAME ENTITIES
│   ├── player.py                 # Kelas Player
│   ├── enemy.py                  # Semua 12+ tipe musuh
│   ├── bullet.py                 # Sistem peluru
│   └── powerup.py                # Sistem power-up
│
├── 🎨 UI & RENDERING
│   ├── ui_renderer.py            # Rendering UI (HUD, text, etc)
│   ├── menu_pages.py             # Halaman menu (main, pause, etc)
│   ├── online_menu_pages.py      # Menu khusus online multiplayer
│   ├── game_over_page.py         # Screen game over
│   ├── intro_page.py             # Intro/splash screen
│   └── button.py                 # Komponen UI button
│
├── 🔊 AUDIO & VISUAL
│   ├── sound_manager.py          # Manajemen audio (BGM, SFX)
│   ├── image_manager.py          # Caching & manajemen gambar
│   └── divider_manager.py        # Efek visual particles
│
├── 🌐 NETWORK & GAMEPLAY LOGIC
│   ├── network_manager.py        # Socket connection, JSON protocol
│   ├── pause_manager.py          # Logika pause/resume
│   └── control_settings.py       # Manajemen kontrol player
│
├── 📊 UTILITIES
│   ├── utils.py                  # Helper functions umum
│   ├── hook_psutil.py            # Monitoring system resources
│   ├── slider.py                 # UI slider component
│   ├── radio_button.py           # UI radio button component
│   └── build_script.py           # Script build executable
│
├── 📁 assets/
│   ├── images/                   # Sprites, backgrounds, UI assets
│   │   ├── player.png
│   │   ├── enemies/
│   │   ├── powerups/
│   │   └── ...
│   └── sounds/                   # Audio files
│       ├── bgm_menu.mp3
│       ├── bgm_game.mp3
│       ├── sfx_*.wav
│       └── ...
│
├── 📦 build/                     # Output folder setelah build
│   ├── Space Defender/
│   └── Space Defender Console/
│
└── 📝 README.md                  # File ini
```

### Dependencies

```python
pygame==2.5.0              # Game library utama
psutil>=5.9.0              # System monitoring (CPU/Memory)
```

**Optional (untuk development)**:

```python
pyinstaller>=5.0           # Build executable (.exe)
```

### Network Protocol

**Architecture**: Client-Server dengan JSON-based events

**Port**: 7777 (TCP)

**Supported Messages**:

```json
{
  "event": "player_move",
  "data": {"x": 100, "y": 200}
}
```

### Performance

- **Frame Rate**: 60 FPS (locked)
- **Resolution**: 800x600 (fixed)
- **Typical CPU Usage**: 5-15% (single core)
- **Typical RAM Usage**: 100-150 MB
- **Network Latency**: ~50-100ms (ZeroTier, dapat bervariasi)

---

## 🏆 Strategy & Tips

### 💡 Tips untuk Pemula

1. **Hindari adalah prioritas utama**
   - Fokus menghindar daripada menembak
   - Gerak teratur membentuk pattern yang sulit diprediksi musuh

2. **Prioritaskan musuh berbahaya**
   - Red Shooter pertama (mereka menembak balik)
   - Kamikaze/Follower jika sudah dekat
   - Splitter hindari atau bunuh sebelum split

3. **Power-Up collection strategy**
   - Kumpulkan Health Regen saat HP rendah
   - Invincibility untuk emergency / saat banyak musuh
   - Hindari mengambil power-up jika tidak perlu (stay mobile)

4. **Multiplayer coordination**
   - **P1 (WASD)**: Jaga area kiri layar
   - **P2 (Arrow)**: Jaga area kanan layar
   - **Komunikasi**: "Incoming left!" / "I got right!"
   - **Support**: Bantu jika partner dalam bahaya

### ⚔️ Advanced Strategies

#### **Scoring Optimization**

```bash
Kombinasi Terbaik:
1. Tunggu Double Score power-up spawn
2. Ambil Multiple Bullets saat Double Score aktif
3. Fokus pada high-value enemies (Red Shooter, Regenerator)
4. Hasil: 50-70 poin per kill vs 10-35 normal
```

#### **Survival Tactics**

| Situasi | Taktik |
| --------- | -------- |
| **Banyak musuh cluster** | Ambil Multiple Bullets, gerak ke edge layar |
| **Kamikaze incoming** | Gerak unpredictable, gunakan Slow Enemies |
| **HP kritis** | Ambil Health atau Invincibility jika available |
| **Musuh tank** | Kumpul dengan Rapid Fire, fokus fire |
| **Red Shooter dekat** | Keep distance, use diagonal movement |

#### **Enemy-Specific Counter-Play**

| Tipe Musuh | Counter-Strategy |
| ----------- | ----------------- |
| **Normal/Fast** | Dodge dan tembak terus |
| **Bouncer** | Tembak saat di titik balik gerak |
| **Red Shooter** | Keep distance, dorong ke edge, tembak full |
| **Kamikaze** | Gerak unpredictable saat dekat, bisa use Slow |
| **Follower** | Lakukan sharp turn, mereka butuh delay response |
| **Tank** | Focus fire dengan teman (multiplayer) atau Rapid Fire |
| **Regenerator** | Bunuh sebelum regenerate, gunakan Rapid Fire |

### 📈 Progression Tips

#### Early Game (Wave 1-3)

- Fokus learn kontrol
- Kumpulkan sebanyak mungkin power-up
- Hindari risky situations

### Mid Game (Wave 4-10)

- Mulai aggressive positioning
- Gunakan edge strategically untuk trap musuh
- Plan untuk Double Score + Multiple Bullets

### Late Game (Wave 11+)

- Pure survival mode
- Prioritas Invincibility power-up
- Play defensively, avoid aggressive plays

---

## 🐛 Troubleshooting

### ❌ Game Crash / Tidak Bisa Start

**Masalah**: Game tidak bisa dijalankan atau crash saat startup

```python
Solusi:
1. ✓ Pastikan Python 3.8+ terinstall
   - Buka cmd, ketik: python --version
   
2. ✓ Install dependencies dengan benar
   - pip install pygame psutil
   
3. ✓ Pastikan folder assets/ ada dengan konten
   - Check: assets/images/, assets/sounds/
   
4. ✓ Cek error message di console
   - Copy error → Google atau lapor ke developer
   
5. ✓ Restart komputer (jika perlu)
```

### 🔊 Audio Tidak Berfungsi

**Masalah**: Game berjalan tapi tidak ada suara

```python
Solusi:
1. ✓ Cek volume di Settings dalam game
   - Pastikan tidak di 0%
   
2. ✓ Verifikasi file audio ada
   - Buka: assets/sounds/
   - Seharusnya ada file .mp3 atau .wav
   
3. ✓ Cek speaker/headphone
   - Windows volume mixer
   - Pastikan tidak muted
   
4. ✓ Coba restart Pygame mixer
   - Close game completely
   - Buka kembali game
   
5. ✓ Update audio drivers
   - Buka Device Manager
   - Update Sound card drivers
```

### ⚡ Performance Issue / Game Lag / FPS Drop

**Masalah**: Game jalan tapi lag atau FPS rendah

```bash
Solusi:
1. ✓ Tutup aplikasi background yang berat
   - Close Chrome/Firefox, Discord, video player
   - Cek Task Manager (Ctrl+Shift+Esc)
   
2. ✓ Kurangi visual quality (edit game_manager.py)
   - Reduce num_stars (background stars)
   - Disable particle effects temporarily
   
3. ✓ Check system resources
   - RAM usage tidak lebih dari 80%
   - CPU tidak penuh (0-50% ideal)
   
4. ✓ Jalankan game di administrator mode
   - Right-click python.exe → Run as Administrator
   
5. ✓ Lower resolution (dev mode)
   - Edit main.py: SCREEN_WIDTH/HEIGHT
   - Restart game
```

### 🎮 Controller/Input Issues

**Masalah**: Tombol tidak bekerja atau input lag

```bash
Solusi:
1. ✓ Verifikasi kontrol di Settings menu
   - Cek kontrol mapping (WASD/Arrow/IJKL)
   
2. ✓ Check keyboard
   - Test di aplikasi lain (Notepad)
   - Apakah tombol stuck?
   
3. ✓ Reconfigure controls
   - Go to Settings → Change control scheme
   - Test di menu sebelum play
   
4. ✓ Restart game
   - Close completely
   - Buka kembali
```

### 🌐 Online Connection Issues

Lihat setion **Troubleshooting Koneksi** di bagian [🌐 Online Multiplayer](#-online-multiplayer)

### 👾 Graphical Issues / Missing Sprites

**Masalah**: Gambar tidak muncul, texture putih/corrupted

```python
Solusi:
1. ✓ Pastikan assets folder lengkap
   - assets/images/ harus ada semua sprite files
   - assets/sounds/ harus ada semua audio files
   
2. ✓ Re-extract/copy assets
   - Jika download dari ZIP, extract proper
   - Pastikan file tidak corrupt
   
3. ✓ Update Pygame
   - pip install --upgrade pygame
   
4. ✓ Check graphics driver
   - Update dari manufacturer (NVIDIA/AMD/Intel)
```

### 🎯 Gameplay Logic Issues

**Masalah**: Game mekanik aneh / tidak normal

```python
Solusi:
1. ✓ Clear game cache
   - Delete __pycache__ folder
   - Restart Python
   
2. ✓ Verify game files
   - Re-download if corrupted
   
3. ✓ Check game version
   - Pastikan latest version
   
4. ✓ Test di safe mode
   - Jalankan dengan minimal settings
   - Disable power-ups/special effects
```

---

## 📞 Support & Feedback

### Melaporkan Bug

Jika menemukan bug, berikan informasi ini:

```python
1. Deskripsi bug detail
   - Kapan bug terjadi?
   - Apa yang Anda lakukan sebelumnya?
   - Apa hasil yang diharapkan vs actual?

2. System info
   - OS (Windows/Mac/Linux + versi)
   - Python version
   - Pygame version

3. Error message
   - Copy-paste error dari console

4. Cara reproduce
   - Langkah-langkah detail untuk reproduce bug
```

### Feature Request

Ingin ide fitur baru? Silakan share:

- Deskripsi fitur
- Kenapa fitur ini berguna
- Cara implementasinya (optional)

---

## 🔄 Version History

| Versi | Tanggal | Perubahan |
| ------- | --------- | ---------- |
| **Alpha v1** | 27 November 2025 | Initial Release |
| | | • 2+ enemy types |
| | | • 7+ powerup |
| | | • Singleplayer mode |
| **Alpha v2** | 29 November 2025 | Multiplayer Update |
| | | • Local Multiplayer |
| | | • 7+ enemy update types |
| | | • Bug fixed |
| **Alpha v3** | 30 November 2025 | Menu Update |
| | | • Added settings (Volume Control) |
| | | • Added How to Play |
| | | • Added Custom Control for Local Multiplayer |
| | | • Bug fixed |
| **Alpha v4** | 4 December 2025 | Difficulty & Online Update |
| | | • Added difficulty settings |
| | | • Added online multiplayer (Zerotier) |
| | | • Bug fixed |
| **Alpha v5** | 13 November 2025 | **STAY TUNED!!** |

---

## 📄 License & Credits

### License

Game ini dibuat untuk tujuan **pendidikan dan hiburan**. Kode sumber tersedia untuk dipelajari, dimodifikasi, dan dikembangkan lebih lanjut.

### Credits

**Developer**: Muhammad Riski  

**Tester**:

- Diva
- Khananta
- Rafi
- Asa

**Tujuan**: Tugas Algoritma dan Pemrograman

- Game Design & Programming
- Network Implementation
- Game Mechanics

**Assets**:

- **Graphics**: OpenGameArt.org, Kenney.nl
- **Music & SFX**: Free music archive, Creative Commons
- **Tools**: Python, Pygame, ZeroTier

**Inspirasi**:

- Classic shoot 'em up games (Space Invaders, Galaga)
- Modern game design patterns

---

## 🚀 Getting Started Quickly

### Untuk pemain baru

```python
1. Install & run
pip install pygame>
python main.py

2. Pilih SINGLEPLAYER di menu
3. Mulai dengan difficulty EASY
4. Pelajari kontrol WASD untuk gerak
5. Hindari musuh, kumpulkan power-up
6. Enjoy! 🎮
```

### Untuk multiplayer online

```python
1. Pastikan ZeroTier terinstall & network joined
2. Player 1 → START GAME → MULTIPLAYER → ONLINE → HOST GAME
3. Player 2 → JOIN GAME dengan IP dari Player 1
4. Player 1 klik START ONLINE GAME
5. Bermain! 🌐
```

### Untuk development/modding

```python
1. Edit enemy.py untuk customize musuh
2. Edit powerup.py untuk power-up baru
3. Edit assets untuk grafis & suara
4. Test changes dengan: python main.py
5. Bagikan modifikasi Anda! 🔧
```

---

## ❓ FAQ

**Q: Bisa main di mobile?**
A: Saat ini hanya untuk PC (Windows/Mac/Linux). Port ke mobile mungkin di masa depan.

**Q: Bisa offline multiplayer tanpa ZeroTier?**
A: Ya! Pilih LOCAL MULTIPLAYER untuk 2 pemain di 1 komputer. ZeroTier hanya untuk ONLINE.

**Q: Boleh modify game?**
A: Tentu! Edit file Python, customize sprite/sound, buat versi Anda sendiri.

**Q: Kenapa FPS jelek di laptop lama?**
A: Reduce visual quality di code, tutup app background, atau upgrade hardware.

**Q: Bisa battle dengan AI?**
A: Belum ada AI player. Hanya musuh NPC dan player control.

**Q: Leaderboard online?**
A: Tidak, untuk di versi Alpha v4. Mungkin di update mendatang.

---

## 🎉 Final Notes

Terima kasih telah memainkan **Space Defender**! Game ini dibuat dengan passion dan attention to detail. Semoga Anda menikmati experience bermainnya.

**Tips terakhir**:  

- Jangan give up saat sulit
- Terus practice untuk improve skill
- Ajak teman bermain multiplayer
- Share feedback & bug report

**Selamat Bermain!** 🚀⭐

---

**Versi**: Alpha v4  
**Terakhir diperbarui**: 12 Desember 2025  
**Status**: _STILL DEVELOPMENT_

Untuk pertanyaan, bug report, atau feature request → Hubungi developer melalui instagram (cek profil saya) atau check project repository.
