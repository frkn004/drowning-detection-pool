#!/usr/bin/env python3
"""
🔗 GOOGLE DRIVE CONFIGURATION - UPDATED
======================================
Google Drive klasör ve dosya ID'leri
"""

# 📁 Ana Google Drive klasörü
MAIN_DRIVE_FOLDER = "https://drive.google.com/drive/u/6/folders/13CBL3-czwwxim49iz6NZ8t8Eq42YeyaW"
MAIN_FOLDER_ID = "13CBL3-czwwxim49iz6NZ8t8Eq42YeyaW"

# 📦 Dataset klasörleri (Google Drive File ID'lerini güncelleyin)
DATASET_FOLDERS = {
    "1_CODES": {
        "id": "YOUR_1_CODES_ID",  # Google Drive'dan alınacak
        "local_path": "1_CODES",
        "sync": False,
        "description": "Core kod modülleri"
    },
    "4_MODELS": {
        "id": "YOUR_4_MODELS_ID", 
        "local_path": "4_MODELS",
        "sync": False,
        "description": "YOLO model dosyaları (*.pt)"
    },
    "5_TİCKET_DATA": {
        "id": "YOUR_5_TICKET_DATA_ID",
        "local_path": "5_TİCKET_DATA", 
        "sync": False,
        "description": "1,814 frame dataset + labels"
    },
    "9_TICKETv2": {
        "id": "YOUR_9_TICKETV2_ID",
        "local_path": "9_TICKETv2",
        "sync": False,
        "description": "5,354 frame dataset + labels (ANA DATASET)"
    }
}

# 📤 Upload klasörleri (VAST.AI'dan Google Drive'a otomatik)
UPLOAD_FOLDERS = {
    "trained_models": {
        "local_path": "8_TRAINING/models",
        "drive_folder": "TRAINING_RESULTS/models",
        "auto_sync": True,
        "file_patterns": ["*.pt", "best_*.pt", "last_*.pt"],
        "description": "Eğitilmiş model dosyaları"
    },
    "training_logs": {
        "local_path": "8_TRAINING/logs", 
        "drive_folder": "TRAINING_RESULTS/logs",
        "auto_sync": True,
        "file_patterns": ["*.log", "*.txt", "*.csv"],
        "description": "Eğitim logları ve metrics"
    },
    "tensorboard_results": {
        "local_path": "8_TRAINING/runs",
        "drive_folder": "TRAINING_RESULTS/tensorboard", 
        "auto_sync": True,
        "file_patterns": ["*.jpg", "*.png", "*.json", "results.csv"],
        "description": "TensorBoard sonuçları ve grafikler"
    },
    "test_videos": {
        "local_path": "TEST_VIDEOS",
        "drive_folder": "TEST_RESULTS/input_videos",
        "auto_sync": True, 
        "file_patterns": ["*.mp4", "*.avi", "*.mov"],
        "description": "Test edilen videolar"
    },
    "test_results": {
        "local_path": "TEST_RESULTS",
        "drive_folder": "TEST_RESULTS/processed",
        "auto_sync": True,
        "file_patterns": ["*.mp4", "*.json", "*.csv", "*.txt"],
        "description": "Test video sonuçları"
    }
}

# 🔧 Google Drive API ayarları
GDRIVE_SETTINGS = {
    "chunk_size": 1024 * 1024,  # 1MB chunks
    "retry_count": 3,
    "timeout": 600,  # 10 dakika
    "auto_sync_interval": 300,  # 5 dakika
    "max_file_size": 2 * 1024 * 1024 * 1024,  # 2GB limit
    "exclude_patterns": ["*.tmp", "*.temp", "__pycache__", ".git"],
    "compress_before_upload": True,  # Büyük dosyalar için
    "backup_enabled": True
}

# 📋 Kullanım talimatları
USAGE_INSTRUCTIONS = """
🔗 FILE ID GÜNCELLEME:
1. Google Drive'a gidin: https://drive.google.com/drive/u/6/folders/13CBL3-czwwxim49iz6NZ8t8Eq42YeyaW
2. Her klasöre sağ tıklayın → Paylaş → Linki olan herkes
3. Linki kopyalayın ve File ID'sini çıkarın
4. Bu dosyada YOUR_*_ID kısımlarını gerçek ID'lerle değiştirin

🚀 VAST.AI'DA KULLANIM:
1. git clone https://github.com/frkn004/drowning-detection-pool.git
2. cd drowning-detection-pool
3. ./8_TRAINING/vast_ai_setup/setup.sh
4. Dataset'ler otomatik indirilir ve eğitim başlar
5. Sonuçlar otomatik Google Drive'a upload edilir
"""
