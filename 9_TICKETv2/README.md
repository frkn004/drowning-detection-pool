# 🚀 HAVUZ VİDEO ETİKETLEME ARACI

**YOLOv8x ile Otomatik Video Etiketleme + Manuel Düzeltme Aracı**

## 📋 ÖZELLİKLER

- 🎬 **Video Frame Extraction**: Video'dan otomatik frame çıkarma
- 🤖 **YOLOv8x Auto-Detection**: Kişi tespiti ve otomatik etiketleme  
- 🎨 **Advanced Editor**: Mouse ve klavye ile manuel etiket düzeltme
- 🏊 **4 Sınıf Desteği**: Swimming, Drowning, Poolside, Equipment
- 💾 **YOLO Format**: Standart YOLO annotation formatı

## 🔧 GEREKLİLİKLER

### Sistem
- **Python 3.8+**
- **MacOS** (diğer sistemlerde test edilmedi)
- **En az 4GB RAM**
- **En az 5GB disk alanı**

### Python Paketleri
```bash
pip install -r requirements.txt
```

Temel paketler:
- `opencv-python` - Video işleme
- `ultralytics` - YOLOv8x model
- `numpy` - Sayısal işlemler
- `torch` - Deep learning

## 🚀 HIZLI BAŞLANGIÇ

### 1. Kurulum
```bash
# Gerekli paketleri yükle
pip install -r requirements.txt
```

### 2. Başlatma
```bash
# Ana scripti çalıştır
python BASLA.py
```

### 3. Kullanım
1. **Menüden seçim yap**:
   - `1` - Yeni video işle
   - `2` - Mevcut etiketleri düzenle  
   - `3` - Havuz_telefon_hasimcan.MOV ile devam et

2. **Advanced Editor Kontrolleri**:
   - `SOL DRAG` - Yeni etiket çiz
   - `SAĞ CLICK` - Etiket seç
   - `1-4` - Sınıf değiştir
   - `SPACE/D` - Sonraki frame
   - `A` - Önceki frame
   - `DEL/TAB` - Sil
   - `ESC` - Çıkış

## 📁 KLASÖR YAPISI

```
9_TICKETv2/
├── BASLA.py              # Ana başlatma scripti
├── advanced_editor.py    # Etiket düzenleme aracı
├── classes.txt           # Sınıf tanımları
├── requirements.txt      # Python gereklilikleri
├── README.md            # Bu dosya
├── models/
│   └── yolov8x.pt       # YOLOv8x model dosyası
├── scripts/
│   ├── extract_all_frames.py  # Frame çıkarma
│   └── auto_label_all.py       # Otomatik etiketleme
├── 01_frames/           # Çıkarılan frame'ler
├── 02_labels/           # YOLO format etiketler
└── 03_output/           # Çıktı dosyaları
```

## 🎯 SINIFLAR

1. **person_swimming** (0) - Havuzda yüzen kişi - YEŞİL
2. **person_drowning** (1) - Boğulma riski - KIRMIZI
3. **person_poolside** (2) - Havuz kenarındaki kişi - MAVİ  
4. **pool_equipment** (3) - Havuz ekipmanı - SARI

## 🔄 İŞ AKIŞI

### Otomatik İşlem
1. **Video yükle** → Frame extraction (her saniyede 1)
2. **YOLOv8x çalıştır** → Otomatik kişi tespiti
3. **Etiketler oluştur** → YOLO format (.txt dosyaları)

### Manuel Düzeltme
1. **Advanced Editor** → Etiketleri görselleştir
2. **Hatalı tespitleri düzelt** → Sınıf değiştir/sil
3. **Eksik kişileri ekle** → Yeni etiket çiz
4. **Kaydet** → Otomatik kaydetme

## 📊 MEVCUT DURUM

- ✅ **5354 frame** çıkarıldı (Havuz_telefon_hasimcan.MOV)
- ✅ **2400 frame** etiketlendi (YOLOv8x)
- ✅ **Advanced Editor** hazır
- 🔄 **Manuel düzeltme** bekleniyor

## ⚠️  DİKKAT EDİLECEKLER

- **Disk Alanı**: Büyük videolar çok yer kaplar
- **İşlem Süresi**: YOLOv8x yavaş çalışabilir
- **Etiket Kontrolü**: Otomatik etiketler kontrol edilmeli
- **Backup**: Önemli etiketleri yedekle

## 🐛 SORUN GİDERME

### Common Issues

1. **"No module named 'ultralytics'"**
   ```bash
   pip install ultralytics
   ```

2. **"No space left on device"**
   - Disk alanını temizle
   - Daha az frame çıkar

3. **YOLOv8x yavaş çalışıyor**
   - GPU sürücülerini kontrol et
   - Model boyutunu küçült (yolov8m.pt)

4. **Advanced Editor açılmıyor**
   - Python 3.8+ kullan
   - opencv-python'u güncelSynonymousle

## 👥 İLETİŞİM

Sorunlar için sistem yöneticisine başvurun.

---
**📅 Son Güncelleme**: Ocak 2025  
**🚀 Versiyon**: 1.0  
**👨‍💻 Geliştirici**: Drowning Detection Team



