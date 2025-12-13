import PyInstaller.__main__
import os
import sys

def build_exe():
    print("🔨 Building Space Defender...")
    
    # Dapatkan path absolut
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    
    os.chdir(base_dir)
    
    # Periksa apakah assets folder ada
    if not os.path.exists(assets_dir):
        print("❌ Assets folder not found!")
        print(f"   Expected at: {assets_dir}")
        return
    
    print(f"📁 Base directory: {base_dir}")
    print(f"📂 Assets directory: {assets_dir}")
    
    # List semua file Python yang diperlukan
    python_files = [
        "main.py",
        "game_manager.py", 
        "player.py",
        "enemy.py",
        "bullet.py",
        "powerup.py",
        "sound_manager.py",
        "image_manager.py",
        "button.py",
        "menu_pages.py",
        "game_over_page.py",
        "game_state_manager.py",
        "ui_renderer.py",
        "divider_manager.py",
        "pause_manager.py",
        "intro_page.py",
        "utils.py",
        "network_manager.py",
        "online_menu_pages.py",
        "slider.py",
        "radio_button.py"
    ]
    
    # Periksa file yang hilang
    missing_files = []
    for file in python_files:
        full_path = os.path.join(base_dir, file)
        if not os.path.exists(full_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing {len(missing_files)} files:")
        for f in missing_files:
            print(f"   - {f}")
        print("\n⚠️ Make sure all Python files are in the same directory!")
        return
    
    print(f"✅ All {len(python_files)} Python files found")
    
    # Konfigurasi PyInstaller untuk SINGLE EXE
    pyinstaller_args = [
        "main.py",  # Entry point
        "--name=Space Defender",  # Nama executable
        
        # ===== KONFIGURASI SINGLE EXE =====
        "--onefile",            # Hanya satu file EXE
        "--windowed",           # No console window  
        "--noconsole",          # Hide console
        
        # Masukkan assets ke dalam EXE
        "--add-data=assets;assets",
        
        # Optimasi
        "--optimize=2",
        "--clean",
        
        # Exclude modules besar
        "--exclude-module=tcl",
        "--exclude-module=tk",
        "--exclude-module=_tkinter",
        
        # Koleksi untuk pygame
        "--collect-all=pygame"
    ]
    
    # UPX untuk kompresi
    upx_dir = r"D:\SOFTWARE\upx-5.0.2-win64"
    if os.path.exists(upx_dir):
        pyinstaller_args.append(f"--upx-dir={upx_dir}")
        print("✅ UPX detected, compression enabled")
    
    # Icon
    icon_path = os.path.join(assets_dir, "images", "icon.ico")
    if os.path.exists(icon_path):
        pyinstaller_args.append(f"--icon={icon_path}")
        print(f"✅ Icon found")
    
    # Hidden imports
    hidden_imports = [
        "json", 
        "pygame", "pygame._view", "pygame.mixer", "pygame.mixer_music",
        "socket", "threading", "json", "logging", "platform", "subprocess",
        "random", "math", "sys", "os", "time", "re", "traceback",
        "enum"
    ]
    
    # Tambahkan psutil hanya kalau terinstall (optional)
    try:
        __import__("psutil")
        hidden_imports.append("psutil")
        print("✅ psutil detected and will be included")
    except ImportError:
        print("⚠️ psutil not found — building without it (use fallback)")
    
    for module in hidden_imports:
        pyinstaller_args.append(f"--hidden-import={module}")
    
    # Jika ingin gunakan hook_psutil.py yang ada di project/hooks
    hooks_dir = os.path.join(base_dir, "hooks")
    if os.path.isdir(hooks_dir):
        pyinstaller_args.append(f"--additional-hooks-dir={hooks_dir}")
        print("✅ Using additional hooks dir:", hooks_dir)
    
    # Sertakan psutil sebagai hidden import (pastikan terinstall)
    pyinstaller_args.append("--hidden-import=psutil")
    
    # Debug mode
    if "--debug" in sys.argv:
        pyinstaller_args.remove("--windowed")
        pyinstaller_args.remove("--noconsole")
        pyinstaller_args.append("--console")
        print("🔧 Debug mode enabled")
    
    # Tampilkan konfigurasi
    print(f"\n📋 Build Configuration:")
    print(f"  Mode: Single EXE (onefile)")
    print(f"  Assets included: YES")
    print(f"  Output: Space Defender.exe")
    print(f"  Size estimate: 30-60 MB")
    
    try:
        print("\n🚀 Starting build process...")
        print("⏳ This may take 3-10 minutes...")
        
        # Jalankan PyInstaller
        PyInstaller.__main__.run(pyinstaller_args)
        
        print("\n" + "="*50)
        print("✅ Build successful!")
        print("="*50)
        
        # Cek hasil
        dist_path = os.path.join(base_dir, "dist", "Space Defender.exe")
        if os.path.exists(dist_path):
            file_size = os.path.getsize(dist_path) / (1024 * 1024)
            print(f"\n📁 EXE location: {dist_path}")
            print(f"📦 File size: {file_size:.2f} MB")
            print(f"📊 Assets included: YES")
            
            # ===== TIDAK ADA COPY ASSETS KE DIST! =====
            
            if "--debug" in sys.argv:
                print("\n🎮 Testing EXE...")
                os.system(f'"{dist_path}"')
            else:
                print("\n🎮 Build complete!")
                print("You can now share 'Space Defender.exe' as a single file.")
        else:
            print("❌ EXE not found!")
            
    except Exception as e:
        print(f"\n❌ Build failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()