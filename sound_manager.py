# ========== SOUND_MANAGER.PY ==========
# File untuk mengelola semua sound effects dan musik latar

import pygame
import numpy as np
import os
from utils import resource_path

class SoundManager:
    """Mengelola semua sound effects dan musik"""
    def __init__(self):
        self.sounds = {}
        self.sfx_volume = 0.5
        self.music_volume = 0.5
        self.sounds_loaded = 0
        self.sounds_created = 0
        
        # Dictionary untuk melacak kapan terakhir kali sound diputar
        self.last_played = {}
        self.pause_music_sound = None  # <-- TAMBAH INI

        self.music_position = 0  # Menyimpan posisi musik saat pause (dalam milidetik)
        self.music_playing = False

        # PERBAIKAN: Terapkan volume awal secara eksplisit
        self._apply_volumes()
        
        self.load_or_create_sounds()
    
    def load_or_create_sounds(self):
        """Load suara dari file atau buat sintetis jika file tidak ada"""
        print("=== LOADING SOUND EFFECTS ===")
        
        # ===== SUARA: PELURU KELUAR =====
        if self._load_sound('shoot', 'assets/sounds/shoot.wav'):
            pass
        else:
            print("Creating shoot sound...")
            self.sounds['shoot'] = self.create_shoot_sound()
            self.sounds_created += 1
        
        # ===== SUARA: MUSUH TERBUNUH (LEDAKAN) =====
        if self._load_sound('explosion', 'assets/sounds/explosion.wav'):
            pass
        else:
            print("Creating explosion sound...")
            self.sounds['explosion'] = self.create_explosion_sound()
            self.sounds_created += 1
        
        # ===== SUARA: PLAYER KENA DAMAGE =====
        if self._load_sound('player_hit', 'assets/sounds/player_hit.wav'):
            pass
        else:
            print("Creating player hit sound...")
            self.sounds['player_hit'] = self.create_player_hit_sound()
            self.sounds_created += 1
        
        # ===== SUARA: GAME OVER ===== (GANTI DARI 'death')
        if self._load_sound('game_over', 'assets/sounds/game_over.wav'):
            pass
        else:
            print("Creating game over sound...")
            self.sounds['game_over'] = self.create_game_over_sound()
            self.sounds_created += 1

        # ===== MUSIK: PAUSE =====
        if self._load_sound('pause_music', 'assets/sounds/pause_music.wav'):
            print("✅ Pause music loaded")
        else:
            print("⚠️ Pause music file not found, will create procedurally when needed")
        
        # ===== SUARA: POWERUP DIAMBIL =====
        if self._load_sound('powerup', 'assets/sounds/powerup.wav'):
            pass
        else:
            print("Creating powerup sound...")
            self.sounds['powerup'] = self.create_powerup_sound()
            self.sounds_created += 1
        
        # ===== SUARA: TEMBAKAN MUSUH =====
        if self._load_sound('enemy_shoot', 'assets/sounds/enemy_shoot.wav'):
            pass
        else:
            print("Creating enemy shoot sound...")
            self.sounds['enemy_shoot'] = self.create_enemy_shoot_sound()
            self.sounds_created += 1
        
        # ===== MUSIK: MENU LATAR =====
        try:
            if os.path.exists('assets/sounds/menu_music.wav'):
                pygame.mixer.music.load('assets/sounds/menu_music.wav')
                print("✓ Loaded: assets/sounds/menu_music.wav")
                self.sounds_loaded += 1
            else:
                print("✗ Missing: assets/sounds/menu_music.wav")
        except Exception as e:
            print(f"✗ Error loading menu music: {e}")
        
        # ===== SUMMARY =====
        print(f"=== SOUNDS SUMMARY ===")
        print(f"Loaded from files: {self.sounds_loaded}")
        print(f"Created procedurally: {self.sounds_created}")
        print(f"Total sound effects: {len(self.sounds)}")
        print("======================")
    
    def _load_sound(self, sound_name, file_path):
        """Helper untuk load sound dengan error handling - FIXED untuk .exe"""
        try:
            abs_path = resource_path(file_path)
            
            # Debug: print path untuk troubleshooting
            print(f"🔊 Trying to load: {file_path}")
            print(f"📁 Absolute path: {abs_path}")
            print(f"📁 File exists: {os.path.exists(abs_path)}")
            
            if os.path.exists(abs_path):
                self.sounds[sound_name] = pygame.mixer.Sound(abs_path)
                self.sounds_loaded += 1
                print(f"✅ Successfully loaded: {file_path}")
                return True
            else:
                print(f"❌ Missing sound: {file_path}")
                return False
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return False
    
    def save_procedural_sounds(self):
        """Simpan suara procedural ke folder sounds (untuk development)"""
        if not os.path.exists('sounds'):
            os.makedirs('sounds')
        
        # Note: Pygame tidak memiliki fungsi save untuk Sound objects
        # Jadi kita akan generate array dan save menggunakan scipy/wave jika diperlukan
        print("Note: Procedural sounds cannot be saved directly in Pygame")
        print("Consider using external libraries like scipy.io.wavfile for saving")
    
    # ========== SOUND GENERATOR (SINTETIS) ==========
    
    def create_shoot_sound(self):
        """Generate suara tembakan player - VERSI LEBIH BAGUS"""
        try:
            sample_rate = 22050
            duration = 0.15
            frames = int(sample_rate * duration)
            
            # ===== BUAT LASER YANG TAJAM =====
            time = np.linspace(0, duration, frames)
            
            # Main frequency (high untuk laser)
            main_freq = 800  # Hz
            main_wave = np.sin(2.0 * np.pi * main_freq * time)
            
            # Harmonic untuk "brightness"
            harmonic_freq = 1600  # Hz
            harmonic_wave = np.sin(2.0 * np.pi * harmonic_freq * time)
            
            # ===== COMBINE =====
            arr = (main_wave * 0.8 + harmonic_wave * 0.2)
            
            # ===== ENVELOPE CEPAT =====
            envelope = np.ones(frames)
            attack_frames = int(frames * 0.05)  # Sangat cepat
            envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
            
            decay_frames = frames - attack_frames
            envelope[attack_frames:] = np.exp(-8 * np.linspace(0, 1, decay_frames))
            
            arr = arr * envelope
            
            # ===== HIGH-PASS FILTER =====
            for i in range(2, frames):
                arr[i] = 0.9 * arr[i] - 0.1 * arr[i-1]
            
            arr = (arr * 32767 * 0.7).astype(np.int16)
            arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
            
            return pygame.sndarray.make_sound(arr)
        except Exception as e:
            print(f"Error creating shoot sound: {e}")
            return pygame.mixer.Sound(buffer=b'\x00' * 1000)
        
    def create_enemy_shoot_sound(self):
        """Generate suara tembakan musuh - VERSI LEBIH BAGUS"""
        try:
            sample_rate = 22050
            duration = 0.25  # Sedikit lebih panjang
            frames = int(sample_rate * duration)
            
            # ===== BUAT MULTI-FREQUENCY LASER =====
            time = np.linspace(0, duration, frames)
            
            # Frekuensi utama (lebih rendah dari player)
            main_freq = 350  # Hz
            main_wave = np.sin(2.0 * np.pi * main_freq * time)
            
            # Frekuensi harmonik untuk "tekstur"
            harmonic_freq = 700  # Hz (2x main)
            harmonic_wave = np.sin(2.0 * np.pi * harmonic_freq * time)
            
            # Noise untuk "static" effect
            noise = np.random.normal(0, 0.1, frames)
            
            # ===== COMBINE WAVES =====
            arr = (main_wave * 0.7 + harmonic_wave * 0.2 + noise * 0.1)
            
            # ===== APPLY ENVELOPE KHUSUS =====
            envelope = np.ones(frames)
            
            # Very quick attack (5% pertama)
            attack_frames = int(frames * 0.05)
            envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
            
            # Slow decay (95% sisanya) 
            decay_frames = frames - attack_frames
            envelope[attack_frames:] = np.exp(-3 * np.linspace(0, 1, decay_frames))
            
            arr = arr * envelope
            
            # ===== ADD FILTER UNTUK EFEK "SPACE GUN" =====
            # High-pass filter sederhana
            for i in range(2, frames):
                arr[i] = 0.8 * arr[i] - 0.2 * arr[i-1]
            
            # Normalize dan convert ke 16-bit
            arr = (arr * 32767 * 0.6).astype(np.int16)  # Volume lebih rendah
            arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)  # Stereo
            
            return pygame.sndarray.make_sound(arr)
        except Exception as e:
            print(f"Error creating enemy_shoot sound: {e}")
            return pygame.mixer.Sound(buffer=b'\x00' * 1000)
        
    def create_player_hit_sound(self):
        """Player Hit V1: Heavy impact dengan metallic ring - SANGAT NENDANG"""
        try:
            sample_rate = 22050
            duration = 0.4
            frames = int(sample_rate * duration)
            time = np.linspace(0, duration, frames)
            
            # ===== COMPONENT 1: HEAVY LOW-END IMPACT =====
            # Frekuensi sangat rendah untuk "punch"
            impact_freq = np.linspace(80, 30, frames)  # Pitch drop dramatis
            impact_wave = np.sin(2.0 * np.pi * impact_freq * time)
            
            # ===== COMPONENT 2: METALLIC RING =====
            # Frekuensi tinggi yang berdecay untuk efek metal
            ring_freq = 1200
            ring_wave = np.sin(2.0 * np.pi * ring_freq * time)
            
            # ===== COMPONENT 3: DISTORTION NOISE =====
            # Noise untuk texture
            noise = np.random.normal(0, 0.4, frames)
            # Filter noise agar lebih "crunchy"
            for i in range(5, frames):
                noise[i] = 0.7 * noise[i] + 0.3 * noise[i-5]
            
            # ===== COMBINE WITH EMPHASIS ON LOW END =====
            arr = (impact_wave * 0.8 + ring_wave * 0.3 + noise * 0.2)
            
            # ===== AGGRESSIVE ENVELOPE =====
            envelope = np.ones(frames)
            
            # Ultra-fast attack (2%)
            attack_frames = int(frames * 0.02)
            envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
            
            # Two-stage decay: fast initial + slower tail
            decay1_frames = int(frames * 0.3)
            decay2_frames = frames - attack_frames - decay1_frames
            
            # Stage 1: Very fast decay
            envelope[attack_frames:attack_frames+decay1_frames] = np.exp(-12 * np.linspace(0, 1, decay1_frames))
            
            # Stage 2: Slower decay dengan oscillation kecil
            if decay2_frames > 0:
                tail = np.exp(-2 * np.linspace(0, 1, decay2_frames))
                # Tambahkan sedikit oscillation untuk metallic feel
                tail_osc = 0.1 * np.sin(2.0 * np.pi * 15 * np.linspace(0, 1, decay2_frames)) * tail
                envelope[attack_frames+decay1_frames:] = tail + tail_osc
            
            arr = arr * envelope
            
            # ===== HEAVY DISTORTION =====
            arr = np.tanh(arr * 3)  # Hard clipping
            
            # ===== FINAL TOUCH: COMPRESSION =====
            arr = arr * (1 + 0.5 * (1 - envelope))  # Dynamic compression
            
            # Convert ke 16-bit
            arr = (arr * 32767 * 0.9).astype(np.int16)
            arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
            
            print("✓ Created Player Hit V1 (Heavy Impact)")
            return pygame.sndarray.make_sound(arr)
        except Exception as e:
            print(f"Error creating player_hit V1: {e}")
            return self.create_fallback_sound()
    
    def create_fallback_sound(self):
        """Fallback sound jika semua method error"""
        print("Using fallback player hit sound")
        return pygame.mixer.Sound(buffer=b'\x00' * 1000)
    
    def create_explosion_sound(self):
        """Generate suara ledakan - VERSI LEBIH BAGUS"""
        try:
            sample_rate = 22050
            duration = 0.8  # Lebih panjang untuk ledakan
            frames = int(sample_rate * duration)
            
            # ===== BUAT EXPLOSION MULTI-COMPONENT =====
            time = np.linspace(0, duration, frames)
            
            # Component 1: Low frequency boom
            boom_freq = np.linspace(80, 40, frames)  # Pitch drop
            boom_wave = np.sin(2.0 * np.pi * boom_freq * time)
            
            # Component 2: Mid frequency crackle
            crackle_freq = np.linspace(400, 200, frames)
            crackle_wave = np.sin(2.0 * np.pi * crackle_freq * time)
            
            # Component 3: White noise untuk "debris"
            noise = np.random.normal(0, 0.3, frames)
            
            # ===== COMBINE DENGAN WEIGHT =====
            arr = (boom_wave * 0.5 + crackle_wave * 0.3 + noise * 0.2)
            
            # ===== COMPLEX ENVELOPE =====
            envelope = np.ones(frames)
            
            # Very quick attack
            attack_frames = int(frames * 0.1)
            envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
            
            # Exponential decay dengan "tail"
            decay_frames = frames - attack_frames
            envelope[attack_frames:] = np.exp(-4 * np.linspace(0, 1, decay_frames))
            
            # Add small bump di decay untuk realism
            bump_position = attack_frames + int(decay_frames * 0.3)
            bump_duration = int(decay_frames * 0.1)
            if bump_position + bump_duration < frames:
                bump = np.hanning(bump_duration * 2)[:bump_duration] * 0.3
                envelope[bump_position:bump_position + bump_duration] += bump
            
            arr = arr * envelope
            
            # ===== COMPRESSION UNTUK LEDAKAN YANG KUAT =====
            arr = np.tanh(arr * 1.5)  # Harder clipping
            
            # Normalize dan convert
            arr = (arr * 32767 * 0.9).astype(np.int16)
            arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
            
            return pygame.sndarray.make_sound(arr)
        except Exception as e:
            print(f"Error creating explosion sound: {e}")
            return pygame.mixer.Sound(buffer=b'\x00' * 1000)
    
    def create_game_over_sound(self):
        """Game Over Sound: Dramatic descending tone dengan finality"""
        try:
            sample_rate = 22050
            duration = 2.0  # Lebih panjang untuk dramatic effect
            frames = int(sample_rate * duration)
            time = np.linspace(0, duration, frames)
            
            # ===== COMPONENT 1: DRAMATIC PITCH DROP =====
            # Dari tinggi ke sangat rendah
            start_freq = 400
            end_freq = 80
            freq_sweep = np.linspace(start_freq, end_freq, frames)
            main_wave = np.sin(2.0 * np.pi * freq_sweep * time)
            
            # ===== COMPONENT 2: HARMONIC SWEEP =====
            harmonic_sweep = np.linspace(800, 160, frames)
            harmonic_wave = np.sin(2.0 * np.pi * harmonic_sweep * time)
            
            # ===== COMPONENT 3: LOW RUMBLE =====
            rumble_freq = np.linspace(60, 30, frames)
            rumble_wave = np.sin(2.0 * np.pi * rumble_freq * time)
            
            # ===== COMBINE =====
            arr = (main_wave * 0.6 + harmonic_wave * 0.3 + rumble_wave * 0.4)
            
            # ===== DRAMATIC ENVELOPE =====
            envelope = np.ones(frames)
            
            # Slow attack (20%)
            attack_frames = int(frames * 0.2)
            envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
            
            # Hold briefly (10%)
            hold_frames = int(frames * 0.1)
            envelope[attack_frames:attack_frames+hold_frames] = 1.0
            
            # Long, dramatic decay (70%)
            decay_frames = frames - attack_frames - hold_frames
            decay_env = np.exp(-1.5 * np.linspace(0, 1, decay_frames))
            
            # Add final "drop" di akhir decay
            drop_position = int(decay_frames * 0.7)
            if drop_position < len(decay_env):
                decay_env[drop_position:] *= 0.3  # Volume drop drastic
            
            envelope[attack_frames+hold_frames:] = decay_env
            
            arr = arr * envelope
            
            # ===== ADD REVERB EFFECT =====
            # Simple delay-based reverb
            delay_frames = int(0.1 * sample_rate)  # 100ms delay
            if frames > delay_frames:
                wet = np.zeros(frames)
                wet[delay_frames:] = arr[:-delay_frames] * 0.4
                arr = arr * 0.7 + wet * 0.3
            
            # ===== LOW-PASS FILTER UNTUK EFEK "FADE OUT" =====
            for i in range(2, frames):
                arr[i] = 0.98 * arr[i] + 0.02 * arr[i-1]
            
            arr = (arr * 32767 * 0.8).astype(np.int16)
            arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
            
            print("✓ Created Game Over Sound (Dramatic)")
            return pygame.sndarray.make_sound(arr)
        except Exception as e:
            print(f"Error creating game_over sound: {e}")
            return self.create_fallback_sound()
    
    def create_powerup_sound(self):
        sample_rate = 22050
        duration = 0.5
        frames = int(sample_rate * duration)
        time = np.linspace(0, duration, frames)
        
        # Pulsating low frequency
        freq = 180
        wave = np.sin(2.0 * np.pi * freq * time)
        
        # Two-pulse envelope
        envelope = np.zeros(frames)
        pulse1 = np.hanning(int(frames * 0.3))
        pulse2 = np.hanning(int(frames * 0.2)) * 0.5
        
        envelope[:len(pulse1)] = pulse1
        start2 = int(frames * 0.25)
        end2 = start2 + len(pulse2)
        if end2 < frames:
            envelope[start2:end2] = np.maximum(envelope[start2:end2], pulse2)
        
        arr = wave * envelope
        arr = (arr * 32767 * 0.4).astype(np.int16)
        arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
        return pygame.sndarray.make_sound(arr)
    
    # ========== SOUND CONTROL ==========
    
    def play_sound(self, sound_name, cooldown=0):
        """Mainkan sound effect dengan cooldown - PERBAIKAN: Support cooldown=0"""
        if sound_name in self.sounds:
            try:
                current_time = pygame.time.get_ticks()
                
                if cooldown > 0:
                    last_played = self.last_played.get(sound_name, 0)
                    if current_time - last_played < cooldown:
                        return
                
                # Volume sudah diatur di _apply_volumes, jadi tidak perlu set lagi
                self.sounds[sound_name].play()
                self.last_played[sound_name] = current_time
            except:
                pass
    def play_preview_sound(self):
        """Mainkan sound preview untuk SFX slider - METHOD BARU"""
        self.play_sound('player_hit', cooldown=0)  # No cooldown untuk preview
    
    def play_menu_music(self):
        """Mainkan musik menu (loop infinite) - DIPERBAIKI"""
        try:
            print("🎵 Playing menu music...")
            
            # PERBAIKAN: Hentikan semua musik sebelumnya
            self.stop_music()
            
            music_path = resource_path('assets/sounds/menu_music.wav')
            
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                print("✅ Menu music started")
            else:
                print("❌ Menu music file not found")
        except Exception as e:
            print(f"❌ Error playing menu music: {e}")

    def play_game_music(self, start_pos=0):
        """Mainkan musik in-game dengan posisi yang bisa ditentukan"""
        try:
            print(f"🎵 Playing game music from position: {start_pos}ms")
            
            music_path = resource_path('assets/sounds/game_music.wav')
            
            if os.path.exists(music_path):
                # Stop musik sebelumnya
                pygame.mixer.music.stop()
                
                # Load musik
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                
                # Mainkan dari posisi tertentu
                pygame.mixer.music.play(-1, start=start_pos/1000.0)  # start dalam detik
                self.music_playing = True
                print(f"✅ Game music started from {start_pos}ms")
            else:
                print("❌ Game music file not found")
        except Exception as e:
            print(f"❌ Error playing game music: {e}")
    
    def stop_music(self):
        """Hentikan musik dan reset posisi"""
        try:
            pygame.mixer.music.stop()
            self.music_position = 0
            self.music_playing = False
        except:
            pass

    def stop_all_music(self):
        """Hentikan semua musik dan suara - METHOD BARU"""
        self.stop_music()
        self.stop_pause_music()
        # Juga hentikan semua sound effects yang sedang diputar
        for sound in self.sounds.values():
            sound.stop()
    
    def set_music_volume(self, volume):
        """Ubah volume musik (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except:
            pass
    
    def set_sfx_volume(self, volume):
        """Ubah volume sound effects (0.0 - 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def pause_music(self):
        """Pause musik dan simpan posisi saat ini"""
        try:
            if pygame.mixer.music.get_busy():
                # Simpan posisi musik saat ini (dalam milidetik)
                self.music_position = pygame.mixer.music.get_pos()
                pygame.mixer.music.pause()
                self.music_playing = False
                print(f"⏸️ Music paused at position: {self.music_position}ms")
        except Exception as e:
            print(f"⚠️ Error pausing music: {e}")
    
    def unpause_music(self):
        """Resume musik dari posisi terakhir"""
        try:
            if not pygame.mixer.music.get_busy():
                # Mainkan ulang dari posisi yang disimpan
                self.play_game_music(self.music_position)
                print(f"▶️ Music resumed from position: {self.music_position}ms")
            else:
                pygame.mixer.music.unpause()
        except Exception as e:
            print(f"⚠️ Error unpausing music: {e}")

    def is_sfx_muted(self):
        """Cek apakah SFX dimute"""
        return self.sfx_volume <= 0.0

    def is_music_muted(self):
        """Cek apakah musik dimute"""
        return self.music_volume <= 0.0

    def create_procedural_menu_music(self):
        """Buat musik menu procedural jika file tidak ada"""
        try:
            print("Creating procedural menu music...")
            # Simple ambient space music untuk menu
            # Implementation bisa ditambahkan jika diperlukan
            pass
        except Exception as e:
            print(f"Error creating procedural menu music: {e}")

    def create_procedural_game_music(self):
        """Buat musik game procedural jika file tidak ada"""
        try:
            print("Creating procedural game music...")
            # Simple action music untuk game
            # Implementation bisa ditambahkan jika diperlukan
            pass
        except Exception as e:
            print(f"Error creating procedural game music: {e}")

    def set_master_volume(self, volume):
        """Set master volume (0.0 - 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        self._apply_volumes()

    def set_sfx_volume(self, volume):
        """Set SFX volume (0.0 - 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._apply_volumes()

    def set_music_volume(self, volume):
        """Set music volume (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        self._apply_volumes()

    def _apply_volumes(self):
        """Terapkan semua volume settings - PERBAIKAN UNTUK PAUSE MUSIC"""
        # Apply music volume
        pygame.mixer.music.set_volume(self.music_volume)
        
        # Apply volume untuk pause music jika ada
        if 'pause_music' in self.sounds:
            self.sounds['pause_music'].set_volume(self.music_volume)
        
        # Apply volumes to all sound effects
        for sound_name, sound in self.sounds.items():
            if sound_name != 'pause_music':  # Jangan timpa volume pause music
                sound.set_volume(self.sfx_volume)

    def get_volumes(self):
        """Dapatkan semua volume settings dalam persen - PERBAIKAN: Tanpa master"""
        return {
            'sfx': int(self.sfx_volume * 100),
            'music': int(self.music_volume * 100)
        }

    def set_sfx_volume(self, volume):
        """Set SFX volume (0.0 - 1.0) - PERBAIKAN: Pastikan nilai tepat"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._apply_volumes()

    def set_music_volume(self, volume):
        """Set music volume (0.0 - 1.0) - PERBAIKAN: Pastikan nilai tepat"""
        self.music_volume = max(0.0, min(1.0, volume))
        self._apply_volumes()

    def reset_to_default(self):
        """Reset semua volume ke nilai default"""
        self.master_volume = 0.8
        self.sfx_volume = 0.8
        self.music_volume = 0.8
        self._apply_volumes()

    def reset_music_state(self):
        """Reset state musik ke kondisi awal - METHOD BARU"""
        try:
            pygame.mixer.music.stop()
            # Unload any loaded music to ensure clean state
            pygame.mixer.music.unload()
        except:
            pass

    def play_pause_music(self):
        """Mainkan musik pause sebagai Sound object terpisah - REVISI BARU"""
        try:
            print("🎵 Loading pause music (Sound object)...")
            
            # PERBAIKAN: Gunakan Sound object, bukan pygame.mixer.music
            music_path = resource_path('assets/sounds/pause_music.wav')
            
            print(f"📁 Pause music path: {music_path}")
            print(f"📁 File exists: {os.path.exists(music_path)}")
            
            if os.path.exists(music_path):
                # Load sebagai Sound object
                if 'pause_music' not in self.sounds:
                    self.sounds['pause_music'] = pygame.mixer.Sound(music_path)
                
                # Atur volume
                self.sounds['pause_music'].set_volume(self.music_volume)
                
                # Mainkan dengan loop (-1 = infinite loop)
                self.sounds['pause_music'].play(-1)
                print("✅ Pause music started (Sound object)")
            else:
                print("❌ Pause music file not found, creating procedurally...")
                self.create_procedural_pause_music_sound()
        except Exception as e:
            print(f"❌ Error playing pause music: {e}")

    def stop_pause_music(self):
        """Hentikan musik pause (Sound object) - REVISI BARU"""
        try:
            if 'pause_music' in self.sounds:
                self.sounds['pause_music'].stop()
                print("⏸️ Pause music stopped (Sound object)")
        except Exception as e:
            print(f"⚠️ Error stopping pause music: {e}")

    def create_procedural_pause_music_sound(self):
        """Buat musik pause procedural sebagai Sound object - REVISI BARU"""
        try:
            print("Creating procedural pause music (Sound object)...")
            # Musik ambient yang tenang untuk pause
            sample_rate = 22050
            duration = 2.0  # Durasi loop
            frames = int(sample_rate * duration)
            time = np.linspace(0, duration, frames)
            
            # Nada tenang dan berulang
            freq1 = 440  # A4
            freq2 = 329.6  # E4
            
            wave1 = 0.3 * np.sin(2.0 * np.pi * freq1 * time)
            wave2 = 0.2 * np.sin(2.0 * np.pi * freq2 * time)
            
            # Envelope halus
            envelope = np.ones(frames)
            attack = int(frames * 0.1)
            release = int(frames * 0.1)
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[-release:] = np.linspace(1, 0, release)
            
            arr = (wave1 + wave2) * envelope
            
            # Convert ke sound
            arr = (arr * 32767 * 0.3).astype(np.int16)
            arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
            
            # Buat Sound object dan simpan
            pause_sound = pygame.sndarray.make_sound(arr)
            pause_sound.set_volume(self.music_volume)
            self.sounds['pause_music'] = pause_sound
            
            # Mainkan dengan loop
            pause_sound.play(-1)
            print("✅ Procedural pause music started (Sound object)")
            
        except Exception as e:
            print(f"Error creating procedural pause music: {e}")