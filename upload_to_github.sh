#!/bin/bash
# 🚀 SELECTIVE GITHUB UPLOAD SCRIPT
# ================================

echo "🏊 DROWNING DETECTION GITHUB UPLOADER"
echo "====================================="

# Remove large directories from git
echo "🗑️ Büyük klasörleri git'ten çıkarıyor..."

# Remove mini dataset (too large)
git rm -r --cached MINI_DATASET_GITHUB/ 2>/dev/null || true

# Remove large model files  
git rm -r --cached 4_MODELS/ 2>/dev/null || true

# Remove large data directories
git rm -r --cached 9_TICKETv2/01_frames/ 2>/dev/null || true
git rm -r --cached 9_TICKETv2/02_labels/ 2>/dev/null || true
git rm -r --cached 5_TİCKET_DATA/01_frames/ 2>/dev/null || true
git rm -r --cached 5_TİCKET_DATA/02_labels/ 2>/dev/null || true

# Update .gitignore to exclude large files
echo "📝 .gitignore güncelleniyor..."

cat >> .gitignore << 'EOF'

# Large model files
4_MODELS/*.pt

# Large datasets  
MINI_DATASET_GITHUB/
9_TICKETv2/01_frames/
9_TICKETv2/02_labels/
5_TİCKET_DATA/01_frames/
5_TİCKET_DATA/02_labels/

# Archive files
*.tar.gz
*.zip

EOF

# Create dataset info files instead of actual datasets
echo "📋 Dataset bilgi dosyaları oluşturuluyor..."

# Create dataset info
cat > DATASET_INFO.md << 'EOF'
# 📊 DROWNING DETECTION DATASETS

## 📁 Dataset Locations

### 🔗 Google Drive Links
**Bu linkler VAST.AI'da otomatik download için kullanılacak:**

1. **5_TİCKET_DATA** (1.7GB)
   - Frames: 1,814 adet
   - Labels: 1,814 adet  
   - Google Drive ID: `YOUR_5_TICKET_DATA_ID`

2. **9_TICKETv2** (3.5GB) ⭐ **Ana Dataset**
   - Frames: 5,354 adet
   - Labels: 5,180 adet
   - Google Drive ID: `YOUR_9_TICKETV2_ID`

3. **MINI_DATASET_GITHUB** (114MB)
   - En kaliteli 200 frame
   - GitHub'a çok büyük, Google Drive'da
   - Google Drive ID: `YOUR_MINI_DATASET_ID`

### 🛠️ VAST.AI'da Kullanım

```bash
# 1. Repo clone et
git clone https://github.com/frkn004/drowning-detection-pool.git
cd drowning-detection-pool

# 2. Google Drive downloader çalıştır
chmod +x 8_TRAINING/vast_ai_setup/gdrive_downloader.sh
./8_TRAINING/vast_ai_setup/gdrive_downloader.sh install
./8_TRAINING/vast_ai_setup/gdrive_downloader.sh download

# 3. Eğitimi başlat
cd 8_TRAINING
python scripts/train_model.py
```

### 📋 Classes
```
0: person_swimming
1: person_drowning  
2: person_poolside
3: pool_equipment
```

### ⚡ Hızlı Başlangıç
- Dataset boyutu: 5.2GB toplam
- Tahmini download süresi: 10-15 dakika (VAST.AI)
- Eğitim süresi: 2-4 saat (Phase 1)
EOF

# Create model info
cat > MODEL_INFO.md << 'EOF'
# 🤖 DROWNING DETECTION MODELS

## 📦 Available Models

### 🎯 Base Models (Google Drive'da)
- `yolov8m.pt` - Baseline model
- `yolov8x.pt` - Large model  
- `yolo11x.pt` - Latest YOLO
- `yolo12m.pt` - Experimental

### 🏊 Trained Models (Eğitim sonrası)
- `best_phase1.pt` - Phase 1 en iyi model
- `best_phase2.pt` - Phase 2 en iyi model
- `best_phase3.pt` - Phase 3 en iyi model
- `best_phase4.pt` - Final production model

## 🚀 Model Download (VAST.AI'da)

Models otomatik olarak eğitim sırasında download edilir:

```bash
# YOLOv8 base model otomatik download
python scripts/train_model.py  # Otomatik yolov8m.pt indirir
```

## 📊 Expected Performance

| Phase | mAP50 Target | Training Time | Model Size |
|-------|--------------|---------------|------------|
| Phase 1 | >0.6 | 2-3 hours | ~50MB |
| Phase 2 | >0.75 | 8-12 hours | ~50MB |
| Phase 3 | >0.85 | 20-30 hours | ~50MB |
| Phase 4 | >0.90 | 40-60 hours | ~50MB |
EOF

# Stage changes
echo "📦 Değişiklikler hazırlanıyor..."
git add .gitignore DATASET_INFO.md MODEL_INFO.md
git add 8_TRAINING/ 1_CODES/ 2_DOCUMENTS/ 6_ANNOTATION_PROJECT/
git add *.py *.md *.png

# Only add small files from datasets
git add 9_TICKETv2/classes.txt 9_TICKETv2/README.md 9_TICKETv2/requirements.txt
git add 5_TİCKET_DATA/classes.txt 5_TİCKET_DATA/pool_area.json

# Commit
echo "💾 Commit oluşturuluyor..."
git commit -m "Upload core system without large datasets

- Added training scripts and configs
- Added Google Drive integration for datasets  
- Added documentation and info files
- Excluded large dataset files (will be downloaded from Google Drive)
- Total size optimized for GitHub upload"

# Push to GitHub
echo "🚀 GitHub'a upload ediliyor..."
git push -u origin main --force

echo ""
echo "✅ GITHUB UPLOAD TAMAMLANDI!"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. Google Drive'a dataset'leri upload edin"
echo "2. DATASET_INFO.md'deki File ID'leri güncelleyin" 
echo "3. VAST.AI'da git clone ile sistemi indirin"
echo "4. gdrive_downloader.sh ile dataset'leri indirin"
echo "5. Eğitimi başlatın"


