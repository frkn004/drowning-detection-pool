# 🎨 HAVUZ VİDEO ETİKET DÜZENLEME ARACI

**AirDrop İle Gelen Hazır Etiket Düzenleme Paketi**

## 📋 BU PAKET NEDİR?

- ✅ **4168 frame** Havuz_telefon_hasimcan.MOV'dan çıkarılmış
- ✅ **4168 etiket** YOLOv8x ile otomatik oluşturulmuş  
- ✅ **Advanced Editor** etiket düzenleme aracı
- 🎯 **Görev**: Otomatik etiketleri manuel olarak düzeltmek

## 🚀 HIZLI BAŞLANGIÇ

### 1. Gereklilikleri Kontrol Et
```bash
python --version  # Python 3.8+ olmalı
```

### 2. Gerekli Paketleri Yükle
```bash
pip install opencv-python numpy
```

### 3. Editörü Başlat
```bash
python ETIKET_DUZENLE.py
```

## 🎯 NE YAPMAN GEREKİYOR?

### Otomatik Etiketler Düzeltme
Tüm etiketler **"person_swimming"** olarak başlar. Sen bunları düzelteceksin:

1. **Havuz İçindeki Kişiler** → ✅ Değiştirme (zaten doğru)
2. **Havuz Kenarındaki Kişiler** → `3` tuşu (person_poolside - MAVİ)
3. **Boğulma Riski Olan Kişiler** → `2` tuşu (person_drowning - KIRMIZI)
4. **Yanlış Tespitler** → `DEL` tuşu (sil)
5. **Eksik Kişiler** → Sol drag ile yeni kutu çiz

## 🎮 KONTROLLER

### Mouse
- **SOL DRAG**: Yeni etiket kutusu çiz
- **SAĞ CLICK**: Etiket seç

### Klavye
- **1**: person_swimming (YEŞİL) - Havuzda yüzen
- **2**: person_drowning (KIRMIZI) - Boğulma riski  
- **3**: person_poolside (MAVİ) - Havuz kenarı
- **4**: pool_equipment (SARI) - Ekipman

### Navigasyon
- **SPACE/D**: Sonraki frame
- **A**: Önceki frame
- **Q/W**: Etiket seç
- **DEL/TAB**: Seçili etiketi sil
- **ESC**: Çıkış

## 📊 MEVCUT DURUM

```
📸 Frame: 5,354 adet (her saniyede 1)
🏷️  Etiket: 4,168 adet (YOLOv8x otomatik)  
⏱️  Video: ~86 dakika havuz videosu
🎯 Görev: Etiketleri manuel düzelt
```

## 📁 DOSYA YAPISI

```
9_TICKETv2/
├── ETIKET_DUZENLE.py     # 👈 BU DOSYAYI ÇALIŞTIR
├── advanced_editor.py    # Düzenleme aracı
├── classes.txt           # Sınıf tanımları
├── 01_frames/           # 4168 frame (JPG)
├── 02_labels/           # 4168 etiket (TXT)
└── AirDrop_README.md    # Bu dosya
```

## ⚠️  ÖNEMLİ NOTLAR

### Öncelikler
1. **Boğulma Riski** → EN ÖNEMLİ (2 tuşu - KIRMIZI)
2. **Havuz Dışı** → ÖNEMLİ (3 tuşu - MAVİ)  
3. **Yanlış Tespitler** → Sil (DEL tuşu)
4. **Eksik Kişiler** → Ekle (Sol drag)

### İpuçları
- **Otomatik kaydetme** aktif - değişiklikler anında kaydediliyor
- **Frame'ler arası atlama** hızlı çalışma için
- **Renk kodları** her sınıfın farklı rengi var
- **Zoom** büyük görüntülerde otomatik

### Performans
- **RAM**: En az 4GB (5354 frame için)
- **İşlemci**: Orta seviye yeterli
- **Ekran**: 1080p+ önerili (detay için)

## 🐛 SORUNLAR?

### "ModuleNotFoundError: No module named 'cv2'"
```bash
pip install opencv-python
```

### "ModuleNotFoundError: No module named 'numpy'"  
```bash
pip install numpy
```

### Editor açılmıyor
- Python 3.8+ kullandığından emin ol
- Terminal'den çalıştır: `python ETIKET_DUZENLE.py`

### Çok yavaş çalışıyor
- Daha az frame ile test et
- RAM'i kontrol et

## 📞 İLETİŞİM

Sorun olursa Furkan'a bildir.

---

**🎯 Hedef**: Boğulma tespiti için kaliteli etiket dataset'i oluşturmak  
**⏱️  Tahmini Süre**: 2-4 saat (hızına göre)  
**🏆 Sonuç**: Eğitim için hazır 4000+ etiketli frame


