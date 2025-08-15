#!/bin/bash
# 🧹 CLEAN GITHUB PUSH SCRIPT
# ===========================

echo "🧹 CLEAN GITHUB PUSH - BÜYÜK DOSYALAR OLMADAN"
echo "============================================="

# Git history'yi temizle
echo "🗑️ Git history temizleniyor..."
rm -rf .git
git init

# .gitignore'ı güncelle
echo "📝 .gitignore günceliniyor..."
cat > .gitignore << 'EOF'
# 🚫 BÜYÜK DOSYALAR - GITHUB'A UPLOAD ETMEYİN

# Video dosyaları
*.mp4
*.mov
*.MOV
*.avi

# Büyük model dosyaları
*.pt
4_MODELS/
9_TICKETv2/models/
drowning_detection_v12/
drowning_detection_v12_best.pt
drowning_detection_v12_working.pt
yolov8x.pt

# Büyük dataset klasörleri
0_DATA/
3_OUTPUT/
5_TİCKET_DATA/01_frames/
5_TİCKET_DATA/02_labels/
9_TICKETv2/01_frames/
9_TICKETv2/02_labels/
MINI_DATASET_GITHUB/

# Temp ve output
OUTPUT/
temp_frames/
runs/
logs/
checkpoints/

# System files
__pycache__/
*.pyc
*.pyo
.Python
*.so
.venv/
env/
.env
.DS_Store
Thumbs.db
*backup*
*kopyası*

# Archives
*.tar.gz
*.zip
*.7z
EOF

# README.md oluştur
echo "📋 README.md oluşturuluyor..."
cat > README.md << 'EOF'
# 🏊 Drowning Detection Pool System

## 🎯 Proje Açıklaması
YOLOv8/YOLOv12 tabanlı havuzda boğulma tespit sistemi. Real-time video analizi ile 4 sınıf tespit eder:

- **person_swimming** - Yüzen kişi
- **person_drowning** - Boğulan kişi  
- **person_poolside** - Havuz kenarındaki kişi
- **pool_equipment** - Havuz ekipmanı

## 🚀 Hızlı Başlangıç

### VAST.AI ile Eğitim
```bash
# 1. Repo clone
git clone https://github.com/frkn004/drowning-detection-pool.git
cd drowning-detection-pool

# 2. Setup script çalıştır
chmod +x 8_TRAINING/vast_ai_setup/setup.sh
./8_TRAINING/vast_ai_setup/setup.sh

# 3. Dataset indir (Google Drive'dan)
./8_TRAINING/vast_ai_setup/gdrive_downloader.sh download

# 4. Eğitimi başlat
cd 8_TRAINING
python scripts/train_model.py
```

## 📊 Dataset Bilgileri

**Not: Büyük dataset dosyaları Google Drive'da tutulmaktadır.**

- **5_TİCKET_DATA**: 1,814 frame + labels (1.7GB)
- **9_TICKETv2**: 5,354 frame + labels (3.5GB) 
- **Model dosyaları**: YOLOv8/YOLOv12 weights

## 🛠️ Klasör Yapısı

```
drowning-detection-pool/
├── 1_CODES/              # Core kodlar
├── 2_DOCUMENTS/          # Dökümantasyon  
├── 5_TİCKET_DATA/        # Dataset 1 (small files only)
├── 6_ANNOTATION_PROJECT/ # Annotation araçları
├── 8_TRAINING/           # Eğitim sistemi
├── 9_TICKETv2/           # Dataset 2 (small files only)
└── CODES/                # Video modülleri
```

## 📈 Eğitim Fazları

| Phase | Frame | Hedef mAP50 | Süre | 
|-------|-------|-------------|------|
| Phase 1 | 200 | >0.6 | 2-3 saat |
| Phase 2 | 500 | >0.75 | 8-12 saat |
| Phase 3 | 1000 | >0.85 | 20-30 saat |
| Phase 4 | 1500 | >0.9 | 40-60 saat |

## 🔗 Linkler

- **GitHub**: https://github.com/frkn004/drowning-detection-pool.git
- **VAST.AI Setup**: `8_TRAINING/vast_ai_setup/`
- **Google Drive**: Dataset'ler için (README'de linkler)

## 👥 Ekip
- **FURKAN**: Model geliştirme
- **NISA**: Dataset annotation

---
*Son güncelleme: Ağustos 2025*
EOF

# Sadece kod dosyalarını ekle
echo "📦 Kod dosyaları ekleniyor..."
git add .gitignore README.md
git add 1_CODES/
git add 2_DOCUMENTS/
git add 6_ANNOTATION_PROJECT/
git add 8_TRAINING/
git add CODES/
git add upload_to_github.sh
git add vast_ai_quick_setup.md

# Küçük dosyaları ekle (büyük olanları gitignore hariç tutar)
git add 5_TİCKET_DATA/classes.txt
git add 5_TİCKET_DATA/pool_area.json
git add 5_TİCKET_DATA/*.py

git add 9_TICKETv2/classes.txt
git add 9_TICKETv2/README.md
git add 9_TICKETv2/requirements.txt
git add 9_TICKETv2/*.py

git add *.py *.md *.png 2>/dev/null || true

# Commit
echo "💾 Commit oluşturuluyor..."
git commit -m "🏊 Drowning Detection System - Clean Upload

✅ Core system uploaded without large files
✅ Training scripts and configs included  
✅ VAST.AI integration ready
✅ Google Drive downloader included
✅ Documentation updated

📁 Large datasets available via Google Drive
🚀 Ready for VAST.AI training deployment"

# Remote ekle
echo "🔗 Remote ekleniyor..."
git remote add origin https://github.com/frkn004/drowning-detection-pool.git

# Push
echo "🚀 GitHub'a upload ediliyor..."
git push -u origin main --force

echo ""
echo "✅ CLEAN GITHUB PUSH TAMAMLANDI!"
echo "🔗 Repo: https://github.com/frkn004/drowning-detection-pool.git"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. Google Drive'a dataset'leri upload edin"
echo "2. VAST.AI'da repo clone edin"  
echo "3. Eğitimi başlatın"


