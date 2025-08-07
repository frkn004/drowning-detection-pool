# 🤖 DROWNING DETECTION MODEL EĞİTİMİ

## 📋 EĞİTİM KLASÖRÜ YAPISI

```
8_TRAINING/
├── dataset/          # Eğitim veri seti
│   ├── images/       # Frame görüntüleri
│   ├── labels/       # YOLO annotation dosyaları
│   ├── train/        # Eğitim seti (80%)
│   ├── val/          # Validation seti (20%)
│   └── test/         # Test seti (isteğe bağlı)
├── scripts/          # Eğitim scriptleri
│   ├── train_model.py       # Ana eğitim scripti
│   ├── prepare_dataset.py   # Dataset hazırlama
│   ├── validate_model.py    # Model doğrulama
│   └── export_model.py      # Model export
├── configs/          # Konfigürasyon dosyaları
│   ├── dataset.yaml         # Dataset konfigürasyonu
│   ├── training.yaml        # Eğitim parametreleri
│   └── classes.yaml         # Sınıf tanımları
├── logs/             # Eğitim logları
├── models/           # Eğitilmiş modeller
│   ├── best.pt       # En iyi model
│   ├── last.pt       # Son model
│   └── checkpoints/  # Ara kayıtlar
└── vast_ai_setup/    # VAST.AI kurulum dosyaları
    ├── requirements.txt     # Python paketleri
    ├── setup.sh            # Kurulum scripti
    ├── ssh_config.txt      # SSH bağlantı bilgileri
    └── sync_data.sh        # Data senkronizasyon
```

## 🎯 EĞİTİM HEDEFİ

**Proje:** YOLOv12 tabanlı özel boğulma tespit modeli  
**Sınıflar:** 4 sınıf (person_swimming, person_drowning, person_poolside, pool_equipment)  
**Dataset:** 1,500 frame (~10,500 annotation)  
**Hedef:** Production-ready drowning detection model  

## 🚀 PHASE PLANI

### Phase 1: Mini Dataset (Bu Hafta)
- **Frame Sayısı:** 200 en kaliteli frame
- **Annotation:** ~1,400 etiket
- **Hedef:** Baseline model establishment
- **Süre:** 2-3 gün

### Phase 2: Extended Dataset (Gelecek Hafta)  
- **Frame Sayısı:** 500 frame
- **Annotation:** ~3,500 etiket
- **Hedef:** Gelişmiş accuracy
- **Süre:** 5-7 gün

### Phase 3: Production Dataset
- **Frame Sayısı:** 1,000 frame
- **Annotation:** ~7,000 etiket
- **Hedef:** Production model
- **Süre:** 10-14 gün

### Phase 4: Final Dataset
- **Frame Sayısı:** 1,500 frame (tümü)
- **Annotation:** ~10,500 etiket
- **Hedef:** Final production model
- **Süre:** 2-3 hafta

## 📊 BAŞLANGIÇ DURUMU

**Tarih:** 5 Ağustos 2025  
**Mevcut Frame:** 1,500 adet  
**Tamamlanan Etiket:** 500 annotation  
**Kalan İş:** 1,000 frame etiketlemesi  
**Ekip:** FURKAN + NISA  
**Donanım:** VAST.AI (RTX 4070/A100)  

---

*📅 Oluşturulma Tarihi: 5 Ağustos 2025*  
*👥 Sorumlu: FURKAN & NISA*  
*🎯 Durum: Başlangıç Hazırlığı*