"""Package Dalal Street AI backend and frontend into a ready-to-upload cPanel zip bundle."""

import os
import zipfile
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUTPUT = os.path.join(ROOT_DIR, "cpanel_dalal_backend.zip")

FILES_TO_INCLUDE = [
    "passenger_wsgi.py",
    "server.py",
    "config.py",
    "simulation.py",
    "cron_telegram_alerts.py",
    "requirements.txt",
    ".htaccess",
    ".env.example",
]

DIRS_TO_INCLUDE = [
    "agents",
    "data_ingestion",
    "screening",
    "risk",
    "data",
]

def make_cpanel_zip():
    print(f"Creating cPanel deployment archive: {ZIP_OUTPUT}...")
    
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 1. Add individual root files
        for fname in FILES_TO_INCLUDE:
            fpath = os.path.join(ROOT_DIR, fname)
            if os.path.exists(fpath):
                zipf.write(fpath, arcname=fname)
                print(f"  + Added file: {fname}")
            else:
                print(f"  ! Warning: {fname} not found")

        # 2. Add backend source directories (excluding __pycache__)
        for dirname in DIRS_TO_INCLUDE:
            dirpath = os.path.join(ROOT_DIR, dirname)
            if os.path.exists(dirpath):
                for root, dirs, files in os.walk(dirpath):
                    # Skip __pycache__
                    if "__pycache__" in root:
                        continue
                    for file in files:
                        if file.endswith((".pyc", ".pyo")):
                            continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, ROOT_DIR)
                        zipf.write(full_path, arcname=rel_path)
                        print(f"  + Added: {rel_path}")

        # 3. Add public_html/ folder with frontend assets
        frontend_src = os.path.join(ROOT_DIR, "frontend", "public")
        if os.path.exists(frontend_src):
            for root, dirs, files in os.walk(frontend_src):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_to_frontend = os.path.relpath(full_path, frontend_src)
                    arcname = os.path.join("public_html", rel_to_frontend)
                    zipf.write(full_path, arcname=arcname)
                    print(f"  + Added to public_html: {arcname}")

    file_size_mb = os.path.getsize(ZIP_OUTPUT) / (1024 * 1024)
    print(f"\nSuccessfully created cPanel bundle: {ZIP_OUTPUT} ({file_size_mb:.2f} MB)")

if __name__ == "__main__":
    make_cpanel_zip()
