# hook-psutil.py
# Runtime hook untuk psutil di PyInstaller

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect semua submodule psutil
hiddenimports = collect_submodules('psutil')

# Collect data files jika ada
datas = collect_data_files('psutil')