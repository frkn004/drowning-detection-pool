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
