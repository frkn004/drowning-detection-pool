#!/usr/bin/env python3
"""
🔗 GOOGLE DRIVE FILE ID UPDATER
==============================
Google Drive'daki dosyaların ID'lerini otomatik olarak konfigürasyona ekler
"""

import os
import re
from pathlib import Path

# Google Drive ana klasörü
MAIN_FOLDER_URL = "https://drive.google.com/drive/u/6/folders/13CBL3-czwwxim49iz6NZ8t8Eq42YeyaW"

def extract_file_id_from_url(url):
    """URL'den file ID'sini çıkar"""
    patterns = [
        r'/folders/([a-zA-Z0-9-_]+)',
        r'/file/d/([a-zA-Z0-9-_]+)',
        r'id=([a-zA-Z0-9-_]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_folder_contents():
    """Google Drive klasör içeriğini al (manual olarak)"""
    print("🔍 Google Drive klasör içeriği:")
    print("=" * 50)
    
    # Manual olarak gözlemlenen klasörler
    folders = {
        "1_CODES": {
            "name": "1_CODES",
            "type": "folder", 
            "description": "Core kod modülleri"
        },
        "4_MODELS": {
            "name": "4_MODELS", 
            "type": "folder",
            "description": "YOLO model dosyaları"
        },
        "5_TİCKET_DATA": {
            "name": "5_TİCKET_DATA",
            "type": "folder", 
            "description": "1,814 frame dataset"
        },
        "9_TICKETv2": {
            "name": "9_TICKETv2",
            "type": "folder",
            "description": "5,354 frame dataset (ana)"
        }
    }
    
    return folders

def generate_file_id_instructions():
    """File ID alma talimatları oluştur"""
    instructions = """
🔗 GOOGLE DRIVE FILE ID ALMA KILAVUZU
===================================

Google Drive'daki her klasör için File ID alması gerekiyor:

1. Google Drive'ı açın: https://drive.google.com/drive/u/6/folders/13CBL3-czwwxim49iz6NZ8t8Eq42YeyaW

2. Her klasöre sağ tıklayın → "Paylaş"

3. "Erişim" kısmında "Kısıtlı" yerine "Linki olan herkes" seçin

4. "Linki kopyala" butonuna tıklayın

5. Kopyalanan linkten File ID'sini alın:

   Örnek link: https://drive.google.com/drive/folders/1abc123def456ghi789jkl?usp=sharing
   File ID: 1abc123def456ghi789jkl

6. Aşağıdaki klasörler için bu işlemi yapın:

"""
    
    folders = get_folder_contents()
    
    for folder_name, info in folders.items():
        instructions += f"""
   📁 {folder_name}
      Açıklama: {info['description']}
      Link: [Buraya Google Drive linkini yapıştırın]
      File ID: [Buraya File ID'yi yazın]
"""
    
    instructions += """

7. File ID'leri aldıktan sonra, aşağıdaki dosyayı güncelleyin:
   8_TRAINING/vast_ai_setup/gdrive_config.py

8. DATASET_FOLDERS dictionary'sindeki YOUR_*_ID kısımlarını gerçek ID'lerle değiştirin.

ÖRNEK:
------
"5_TİCKET_DATA": {
    "id": "1abc123def456ghi789jkl",  # ← Buraya gerçek ID
    "local_path": "5_TİCKET_DATA",
    "sync": False
},
"""
    
    return instructions

def update_config_template():
    """Config dosyasını güncellenmiş template ile değiştir"""
    config_path = Path("8_TRAINING/vast_ai_setup/gdrive_config.py")
    
    if not config_path.exists():
        print(f"❌ Config dosyası bulunamadı: {config_path}")
        return False
        
    # Yeni config içeriği
    new_config = f'''#!/usr/bin/env python3
"""
🔗 GOOGLE DRIVE CONFIGURATION - UPDATED
======================================
Google Drive klasör ve dosya ID'leri
"""

# 📁 Ana Google Drive klasörü
MAIN_DRIVE_FOLDER = "{MAIN_FOLDER_URL}"
MAIN_FOLDER_ID = "{extract_file_id_from_url(MAIN_FOLDER_URL)}"

# 📦 Dataset klasörleri (Google Drive File ID'lerini güncelleyin)
DATASET_FOLDERS = {{
    "1_CODES": {{
        "id": "YOUR_1_CODES_ID",  # Google Drive'dan alınacak
        "local_path": "1_CODES",
        "sync": False,
        "description": "Core kod modülleri"
    }},
    "4_MODELS": {{
        "id": "YOUR_4_MODELS_ID", 
        "local_path": "4_MODELS",
        "sync": False,
        "description": "YOLO model dosyaları (*.pt)"
    }},
    "5_TİCKET_DATA": {{
        "id": "YOUR_5_TICKET_DATA_ID",
        "local_path": "5_TİCKET_DATA", 
        "sync": False,
        "description": "1,814 frame dataset + labels"
    }},
    "9_TICKETv2": {{
        "id": "YOUR_9_TICKETV2_ID",
        "local_path": "9_TICKETv2",
        "sync": False,
        "description": "5,354 frame dataset + labels (ANA DATASET)"
    }}
}}

# 📤 Upload klasörleri (VAST.AI'dan Google Drive'a otomatik)
UPLOAD_FOLDERS = {{
    "trained_models": {{
        "local_path": "8_TRAINING/models",
        "drive_folder": "TRAINING_RESULTS/models",
        "auto_sync": True,
        "file_patterns": ["*.pt", "best_*.pt", "last_*.pt"],
        "description": "Eğitilmiş model dosyaları"
    }},
    "training_logs": {{
        "local_path": "8_TRAINING/logs", 
        "drive_folder": "TRAINING_RESULTS/logs",
        "auto_sync": True,
        "file_patterns": ["*.log", "*.txt", "*.csv"],
        "description": "Eğitim logları ve metrics"
    }},
    "tensorboard_results": {{
        "local_path": "8_TRAINING/runs",
        "drive_folder": "TRAINING_RESULTS/tensorboard", 
        "auto_sync": True,
        "file_patterns": ["*.jpg", "*.png", "*.json", "results.csv"],
        "description": "TensorBoard sonuçları ve grafikler"
    }},
    "test_videos": {{
        "local_path": "TEST_VIDEOS",
        "drive_folder": "TEST_RESULTS/input_videos",
        "auto_sync": True, 
        "file_patterns": ["*.mp4", "*.avi", "*.mov"],
        "description": "Test edilen videolar"
    }},
    "test_results": {{
        "local_path": "TEST_RESULTS",
        "drive_folder": "TEST_RESULTS/processed",
        "auto_sync": True,
        "file_patterns": ["*.mp4", "*.json", "*.csv", "*.txt"],
        "description": "Test video sonuçları"
    }}
}}

# 🔧 Google Drive API ayarları
GDRIVE_SETTINGS = {{
    "chunk_size": 1024 * 1024,  # 1MB chunks
    "retry_count": 3,
    "timeout": 600,  # 10 dakika
    "auto_sync_interval": 300,  # 5 dakika
    "max_file_size": 2 * 1024 * 1024 * 1024,  # 2GB limit
    "exclude_patterns": ["*.tmp", "*.temp", "__pycache__", ".git"],
    "compress_before_upload": True,  # Büyük dosyalar için
    "backup_enabled": True
}}

# 📋 Kullanım talimatları
USAGE_INSTRUCTIONS = """
🔗 FILE ID GÜNCELLEME:
1. Google Drive'a gidin: {MAIN_FOLDER_URL}
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
'''
    
    # Dosyayı güncelle
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(new_config)
        
    print(f"✅ Config dosyası güncellendi: {config_path}")
    return True

def main():
    """Ana fonksiyon"""
    print("🔗 GOOGLE DRIVE FILE ID UPDATER")
    print("=" * 40)
    
    # Ana klasör ID'sini kontrol et
    main_id = extract_file_id_from_url(MAIN_FOLDER_URL)
    print(f"📁 Ana klasör ID: {main_id}")
    
    # Klasör içeriğini göster
    folders = get_folder_contents()
    print(f"📦 {len(folders)} klasör tespit edildi")
    
    # Talimatları oluştur
    instructions = generate_file_id_instructions()
    
    # Talimatları dosyaya kaydet
    instructions_file = Path("GOOGLE_DRIVE_SETUP_INSTRUCTIONS.md")
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"📄 Talimatlar kaydedildi: {instructions_file}")
    
    # Config'i güncelle
    update_config_template()
    
    print(f"""
✅ KURULUM TAMAMLANDI!

📋 SONRAKI ADIMLAR:
1. {instructions_file} dosyasını okuyun
2. Google Drive'dan File ID'leri alın  
3. 8_TRAINING/vast_ai_setup/gdrive_config.py dosyasını güncelleyin
4. VAST.AI'da setup.sh script'ini çalıştırın

🔗 Google Drive: {MAIN_FOLDER_URL}
""")

if __name__ == "__main__":
    main()
