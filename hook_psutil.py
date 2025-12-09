# hook-psutil.py
# Runtime hook untuk psutil di PyInstaller

import os
import sys

# Pastikan psutil bisa menemukan file DLL-nya
if hasattr(sys, '_MEIPASS'):
    # Saat dijalankan dari PyInstaller
    os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ['PATH']