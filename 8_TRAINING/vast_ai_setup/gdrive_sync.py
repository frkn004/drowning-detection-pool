#!/usr/bin/env python3
"""
🔄 GOOGLE DRIVE AUTO SYNC SYSTEM
===============================
VAST.AI için otomatik Google Drive senkronizasyonu
"""

import os
import sys
import time
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from gdrive_config import (
    MAIN_FOLDER_ID, DATASET_FOLDERS, UPLOAD_FOLDERS, GDRIVE_SETTINGS
)

class GoogleDriveSync:
    def __init__(self, work_dir="/home/ubuntu/drowning_detection"):
        self.work_dir = Path(work_dir)
        self.log_file = self.work_dir / "gdrive_sync.log"
        self.config_file = self.work_dir / "gdrive_sync_config.json"
        self.running = False
        
        # Create directories
        self.work_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Logging sistemini kur"""
        import logging
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def install_requirements(self):
        """Gerekli paketleri yükle"""
        self.logger.info("📦 Gerekli paketler yükleniyor...")
        
        packages = [
            "gdown",
            "pydrive2", 
            "watchdog",
            "google-api-python-client",
            "google-auth-httplib2",
            "google-auth-oauthlib"
        ]
        
        for package in packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                self.logger.info(f"✅ {package} yüklendi")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"❌ {package} yüklenemedi: {e}")
                
    def download_from_gdrive(self, file_id, output_path, file_name):
        """Google Drive'dan dosya indir"""
        self.logger.info(f"🔽 İndiriliyor: {file_name}")
        
        try:
            # gdown ile indir
            cmd = [
                "gdown", 
                f"https://drive.google.com/uc?id={file_id}",
                "-O", str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                self.logger.info(f"✅ İndirildi: {file_name}")
                return True
            else:
                self.logger.error(f"❌ İndirme hatası: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"⏰ İndirme timeout: {file_name}")
            return False
        except Exception as e:
            self.logger.error(f"❌ İndirme hatası {file_name}: {e}")
            return False
            
    def upload_to_gdrive(self, file_path, drive_folder):
        """Dosyayı Google Drive'a upload et"""
        self.logger.info(f"🔼 Upload ediliyor: {file_path}")
        
        try:
            # rclone veya gdown kullanarak upload
            # Bu kısım Google Drive API ile yapılabilir
            
            # Basit yöntem: gdown'ın upload özelliği yoksa manuel link
            self.logger.warning(f"⚠️ Upload için manuel link gerekebilir: {file_path}")
            
            # TODO: Google Drive API ile gerçek upload
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Upload hatası {file_path}: {e}")
            return False
            
    def download_datasets(self):
        """Tüm dataset'leri indir"""
        self.logger.info("📦 Dataset'ler indiriliyor...")
        
        downloaded = 0
        total = len(DATASET_FOLDERS)
        
        for folder_name, config in DATASET_FOLDERS.items():
            file_id = config.get("id")
            local_path = self.work_dir / config.get("local_path")
            
            if file_id.startswith("YOUR_"):
                self.logger.warning(f"⚠️ {folder_name} için File ID ayarlanmamış")
                continue
                
            # Klasör zaten varsa atla
            if local_path.exists():
                self.logger.info(f"✅ {folder_name} zaten mevcut")
                downloaded += 1
                continue
                
            # Archive dosyasını indir
            archive_path = self.work_dir / f"{folder_name}.tar.gz"
            
            if self.download_from_gdrive(file_id, archive_path, folder_name):
                # Extract et
                if self.extract_archive(archive_path, self.work_dir):
                    downloaded += 1
                    
        self.logger.info(f"📊 Dataset indirme tamamlandı: {downloaded}/{total}")
        return downloaded == total
        
    def extract_archive(self, archive_path, extract_to):
        """Arşivi çıkar"""
        self.logger.info(f"📦 Çıkarılıyor: {archive_path}")
        
        try:
            import tarfile
            
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(path=extract_to)
                
            # Arşivi sil
            archive_path.unlink()
            
            self.logger.info(f"✅ Çıkarıldı: {archive_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Çıkarma hatası: {e}")
            return False
            
    def start_auto_sync(self):
        """Otomatik sync'i başlat"""
        self.logger.info("🔄 Otomatik sync başlatılıyor...")
        self.running = True
        
        # File watcher kurulum
        event_handler = SyncEventHandler(self)
        observer = Observer()
        
        # Upload klasörlerini izle
        for folder_name, config in UPLOAD_FOLDERS.items():
            local_path = self.work_dir / config.get("local_path")
            if local_path.exists():
                observer.schedule(event_handler, str(local_path), recursive=True)
                self.logger.info(f"👁️ İzleniyor: {local_path}")
                
        observer.start()
        
        try:
            while self.running:
                time.sleep(GDRIVE_SETTINGS["auto_sync_interval"])
                self.sync_pending_files()
                
        except KeyboardInterrupt:
            self.logger.info("⏹️ Sync durduruldu")
        finally:
            observer.stop()
            observer.join()
            
    def sync_pending_files(self):
        """Bekleyen dosyaları sync et"""
        # Bu metodda pending upload'ları kontrol et
        pass
        
    def stop_sync(self):
        """Sync'i durdur"""
        self.running = False

class SyncEventHandler(FileSystemEventHandler):
    def __init__(self, sync_manager):
        self.sync_manager = sync_manager
        
    def on_created(self, event):
        """Yeni dosya oluşturulduğunda"""
        if not event.is_directory:
            self.sync_manager.logger.info(f"📁 Yeni dosya: {event.src_path}")
            # TODO: Upload queue'ya ekle
            
    def on_modified(self, event):
        """Dosya değiştirildiğinde"""
        if not event.is_directory:
            self.sync_manager.logger.info(f"✏️ Dosya güncellendi: {event.src_path}")
            # TODO: Upload queue'ya ekle

def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Drive Sync System")
    parser.add_argument("--action", choices=["install", "download", "sync", "stop"], 
                       default="download", help="Yapılacak işlem")
    parser.add_argument("--work-dir", default="/home/ubuntu/drowning_detection",
                       help="Çalışma dizini")
    
    args = parser.parse_args()
    
    sync = GoogleDriveSync(args.work_dir)
    
    if args.action == "install":
        sync.install_requirements()
    elif args.action == "download":
        sync.download_datasets()
    elif args.action == "sync":
        sync.start_auto_sync()
    elif args.action == "stop":
        sync.stop_sync()

if __name__ == "__main__":
    main()


