# 🏊 HAVUZ GÜVENLİK SİSTEMİ - Drowning Detection Pool

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-green.svg)](https://opencv.org)
[![YOLO](https://img.shields.io/badge/YOLO-v8%2Fv11%2Fv12-red.svg)](https://ultralytics.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **🚀 AI Destekli Havuz Güvenlik Sistemi** - YOLOv8/v11/v12 modellerini kullanarak havuzlarda boğulma tespiti yapan gelişmiş Python uygulaması.

---

## 📋 İÇİNDEKİLER

1. [🎯 Proje Hakkında](#-proje-hakkında)
2. [✨ Özellikler](#-özellikler)
3. [⚙️ Sistem Gereksinimleri](#️-sistem-gereksinimleri)
4. [🔧 Kurulum](#-kurulum)
5. [🚀 Hızlı Başlangıç](#-hızlı-başlangıç)
6. [📖 Kullanım Kılavuzu](#-kullanım-kılavuzu)
7. [🧪 Test Etme](#-test-etme)
8. [📊 Model Bilgileri](#-model-bilgileri)
9. [🛠️ Sorun Giderme](#️-sorun-giderme)
10. [👥 Katkıda Bulunanlar](#-katkıda-bulunanlar)

---

## 🎯 PROJE HAKKINDA

**Havuz Güvenlik Sistemi**, havuzlarda güvenliği artırmak için geliştirilmiş AI tabanlı bir görüntü işleme sistemidir. YOLO (You Only Look Once) deep learning modellerini kullanarak:

- ✅ **Kişi Tespiti** - Havuz alanındaki kişileri gerçek zamanlı tespit
- ✅ **Boğulma Analizi** - Hareket analizi ile boğulma belirtilerini tespit  
- ✅ **Havuz Alanı Tanımlama** - İnteraktif araçlarla havuz sınırlarını belirleme
- ✅ **Multi-Model Desteği** - 10 farklı YOLO modeli ile karşılaştırma
- ✅ **Video İşleme** - Batch video processing ve test otomasyonu

### 🏆 Teknik Özellikler
- **10 YOLO Modeli** (v8/v11/v12) eş zamanlı test
- **GPU/CPU Adaptif** işleme
- **Real-time Tracking** algoritmaları
- **JSON-based** havuz alanı kaydetme
- **Professional Logging** sistemi
- **Modular Architecture** kolay genişletme

---

## ✨ ÖZELLİKLER

### 🤖 **Model Yönetimi** (FURKAN)
```python
# 10 farklı model otomatik seçimi
PREFERRED_MODELS = [
    "yolov12m_drowning_best.pt",  # Özel eğitilmiş model
    "yolov8m.pt",                 # Genel amaçlı
    "yolo11l.pt"                  # Alternatif
]
```

### 🎬 **Video İşleme** (NISA)
- **Multi-Video Testing** - Batch processing desteği
- **Pool Zone Definition** - İnteraktif havuz alanı seçimi
- **5-Minute Tests** - Uzun süreli performans testleri
- **Real-Time Tracking** - 1:32 dakikalık tracking testleri

### 📊 **Analiz Araçları**
- **Performance Benchmarking** - FPS ve accuracy ölçümü
- **Test Logging** - Detaylı test sonuçları
- **Output Management** - Organize sonuç klasörleri
- **Quality Validation** - Otomatik kalite kontrolü

---

## ⚙️ SİSTEM GEREKSİNİMLERİ

### 🖥️ **Minimum Gereksinimler**
- **İşletim Sistemi:** Windows 10/11, macOS 10.14+, Linux Ubuntu 18.04+
- **Python:** 3.8 veya üzeri
- **RAM:** 8 GB (16 GB önerilen)
- **Disk:** 10 GB boş alan
- **CPU:** Intel i5 / AMD Ryzen 5 veya üzeri

### 🚀 **Önerilen Gereksinimler**
- **GPU:** NVIDIA GTX 1060 / RTX 3060 veya üzeri (CUDA desteği)
- **RAM:** 16 GB veya üzeri
- **SSD:** Hızlı video işleme için

### 📦 **Yazılım Bağımlılıkları**
```
Python 3.8+
OpenCV 4.5+
PyTorch 1.12.0+
Ultralytics 8.0.0+
NumPy 1.22.0+
```

---

## 🔧 KURULUM

### 1️⃣ **Repository'yi Klonlayın**
```bash
git clone <repository-url>
cd "Drowning detection pool"
```

### 2️⃣ **Python Sanal Ortam Oluşturun**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux  
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ **Gerekli Paketleri Yükleyin**
```bash
# Ana bağımlılıklar
pip install ultralytics>=8.0.0
pip install opencv-python>=4.5.0
pip install torch torchvision
pip install numpy>=1.22.0
pip install matplotlib
pip install tqdm

# GPU desteği için (isteğe bağlı)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4️⃣ **YOLO Modellerini İndirin**
Modeller `MODELS/` klasöründe bulunuyor:
- `yolov8x.pt`, `yolov8m.pt`, `yolov8l.pt`, `yolov8n.pt`
- `yolo11l.pt`, `yolo11x.pt`  
- `yolo12m.pt`, `yolo12x.pt`
- `yolov12m_drowning_best.pt` (özel eğitilmiş)

### 5️⃣ **Test Videolarını Hazırlayın**
`DATA/` klasörüne video dosyalarınızı ekleyin:
- Desteklenen formatlar: `.mp4`, `.mov`, `.avi`
- Örnek videolar: `KAMERA 1.mp4`, `KAMERA 2 KISA DATA.mov`

---

## 🚀 HIZLI BAŞLANGIÇ

### 📁 **Klasör Yapısını Kontrol Edin**
```
Drowning detection pool/
├── CODES/          # Ana kod dosyaları
├── DATA/           # Video dosyaları
├── MODELS/         # YOLO model dosyaları  
├── OUTPUT/         # Test sonuçları
└── DOCUMENTS/      # Dokümantasyon
```

### ⚡ **İlk Testi Çalıştırın**

#### 1. Havuz Alanı Tanımlayın
```bash
cd CODES
python -m pool_module.pool_area_definer
```

#### 2. Kişi Tespiti Test
```bash
python -m tests.test_video_person_detection
```

#### 3. Model Karşılaştırması  
```bash
python -m video_module.all_models_pool_tracker
```

### 🎬 **Video İşleme**
```bash
# 5 dakikalık havuz testi
python -m video_module.multi_video_pool_tester

# Real-time tracking
python -m video_module.enhanced_pool_tracker
```

---

## 📖 KULLANIM KILAVUZU

### 🏊 **1. Havuz Alanı Tanımlama**

#### 🖱️ **İnteraktif Tanımlama**
```bash
cd CODES
python -m pool_module.visual_pool_definer
```

**Kontroller:**
- **Sol tık:** Havuz köşesi ekle
- **Sağ tık:** Son noktayı sil
- **C tuşu:** Tanımlamayı tamamla
- **ESC:** İptal et

#### 📄 **JSON Çıktı Örneği**
```json
{
  "video_name": "KAMERA_1.mp4",
  "timestamp": "20250724_140958", 
  "polygon_points": [[100, 50], [800, 50], [800, 600], [100, 600]],
  "point_count": 4
}
```

### 🤖 **2. Model Testleri**

#### 🔄 **Tüm Modelleri Test Etme**
```bash
python -m video_module.all_models_pool_tracker
```

Bu komut:
- 10 modeli paralel test eder
- Her model için ayrı klasör oluşturur
- Performance metriklerini karşılaştırır
- Detaylı log dosyaları üretir

#### 📊 **Tek Model Testi**
```bash
python -m video_module.single_model_tester
```

#### 🏊 **Havuz Alanı ile Test**
```bash
python -m video_module.pool_zone_tester
```

### 🎬 **3. Video İşleme Modları**

#### ⏱️ **Hızlı Test (30 saniye)**
```bash
python -m tests.test_video_person_detection
```

#### 🕐 **Orta Test (2 dakika)**  
```bash
python -m video_module.real_video_tester
```

#### 🕔 **Uzun Test (5 dakika)**
```bash
python -m video_module.multi_video_pool_tester  
```

#### 🏃 **Tracking Test (1:32 dakika)**
```bash
python -m video_module.enhanced_pool_tracker
```

### ⚙️ **4. Konfigürasyon Ayarları**

`CODES/core/config.py` dosyasında:

```python
# Tespit eşikleri
CONFIDENCE_THRESHOLD = 0.3    # Güven eşiği
IOU_THRESHOLD = 0.3          # IoU eşiği  
MIN_AREA = 500               # Minimum tespit alanı

# Tercih edilen modeller
PREFERRED_MODELS = [
    "yolov12m_drowning_best.pt",
    "yolov8m.pt", 
    "yolo11l.pt"
]
```

---

## 🧪 TEST ETME

### 📋 **Test Senaryoları**

| Test Türü | Süre | Dosya | Açıklama |
|-----------|------|-------|-----------|
| **Hızlı Test** | 30s | `test_video_person_detection.py` | Kişi tespit kontrolü |
| **Model Test** | 2dk | `real_video_tester.py` | Tek model performansı |
| **Havuz Test** | 2dk | `pool_zone_tester.py` | Havuz alanı filtresi |
| **Uzun Test** | 5dk | `multi_video_pool_tester.py` | Batch processing |
| **Tracking** | 1:32dk | `enhanced_pool_tracker.py` | Kişi takibi |
| **10 Model** | 10dk+ | `all_models_pool_tracker.py` | Model karşılaştırması |

### 📊 **Test Sonuçları**

Test sonuçları `OUTPUT/` klasöründe organize edilir:

```
OUTPUT/
├── 5MIN_yolov8x_KAMERA_1_20250724_141738/
│   ├── 5min_pool_result.mp4      # İşlenmiş video
│   └── 5min_pool_log.txt         # Test logu
├── TRACK_yolov8x_KAMERA_1_20250724_150347/
│   ├── enhanced_pool_tracking.mp4 # Tracking videosu
│   └── enhanced_tracking_log.txt  # Tracking logu
└── pool_area_KAMERA_1_20250724_140958.json # Havuz alanı
```

### 📈 **Log Dosyası Örneği**
```
🏊 TEST BAŞLIYOR - 2024-07-24 14:17:38
📹 Video: KAMERA_1.mp4 (1920x1080 @ 30.0 FPS)
🤖 Model: yolov8x.pt
⏱️  Test süresi: 300 saniye

📊 İşleme durumu:
   ✅ 0:30 - 900 kare işlendi (30.0 FPS)
   ✅ 1:00 - 1800 kare işlendi (30.0 FPS)
   ✅ 1:30 - 2700 kare işlendi (30.0 FPS)
   ...

🎯 SONUÇLAR:
   📊 Toplam kare: 9000
   👥 Kişi tespiti: 3247 kare
   🏊 Havuz içi: 2891 kare
   ⚡ Ortalama FPS: 28.5
   💾 Çıktı boyutu: 125.4 MB
```

---

## 📊 MODEL BİLGİLERİ

### 🤖 **Desteklenen YOLO Modelleri**

| Model | Boyut | Hız | Doğruluk | Kullanım |
|-------|-------|-----|----------|----------|
| **YOLOv8n** | 6MB | ⚡⚡⚡ | ⭐⭐ | Hızlı test |
| **YOLOv8m** | 50MB | ⚡⚡ | ⭐⭐⭐ | Genel amaçlı |
| **YOLOv8l** | 87MB | ⚡ | ⭐⭐⭐⭐ | Yüksek doğruluk |
| **YOLOv8x** | 136MB | ⚡ | ⭐⭐⭐⭐⭐ | Maximum doğruluk |
| **YOLOv11l** | 87MB | ⚡⚡ | ⭐⭐⭐⭐ | Optimize edilmiş |
| **YOLOv12m** | 50MB | ⚡⚡ | ⭐⭐⭐⭐ | Yeni nesil |
| **Drowning Best** | 50MB | ⚡⚡ | ⭐⭐⭐⭐⭐ | **Özel eğitilmiş** |

### 🎯 **Model Seçim Kriterleri**

```python
# Otomatik model seçimi algoritması
def get_best_model():
    # 1. Öncelik: Özel eğitilmiş model
    if "yolov12m_drowning_best.pt" in available:
        return "yolov12m_drowning_best.pt"
    
    # 2. Genel amaçlı model  
    if "yolov8m.pt" in available:
        return "yolov8m.pt"
        
    # 3. Alternatif model
    return "yolo11l.pt"
```

### ⚙️ **Model Parametreleri**

```python
# Optimize edilmiş detection parametreleri
CONFIDENCE_THRESHOLD = 0.3   # %30 güven eşiği
IOU_THRESHOLD = 0.3         # %30 IoU eşiği
MIN_AREA = 500              # 500 piksel minimum alan
```

---

## 🛠️ SORUN GİDERME

### ❌ **Yaygın Hatalar ve Çözümleri**

#### 🐍 **Python/Paket Hataları**
```bash
# Hata: ModuleNotFoundError: No module named 'ultralytics'
pip install ultralytics

# Hata: OpenCV import sorunu
pip uninstall opencv-python
pip install opencv-python-headless

# Hata: CUDA not available
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 📹 **Video İşleme Hataları**
```python
# Hata: Video açılamadı
# Çözüm: Video formatını kontrol edin (.mp4, .mov, .avi)
# Çözüm: Video dosya yolunu kontrol edin

# Hata: Kare okunamadı  
# Çözüm: Video dosyası bozuk olabilir
# Çözüm: Codec eksik olabilir (K-Lite Codec Pack)
```

#### 🤖 **Model Yükleme Hataları**
```python
# Hata: Model bulunamadı
# Çözüm: MODELS/ klasöründe model dosyasını kontrol edin
# Çözüm: Model dosya adını config.py'de kontrol edin

# Hata: CUDA out of memory
# Çözüm: Batch size'ı küçültün  
# Çözüm: Düşük çözünürlüklü video kullanın
```

#### 🏊 **Havuz Alanı Hataları**
```python
# Hata: Havuz alanı bulunamadı
# Çözüm: pool_area_definer.py ile yeniden tanımlayın
# Çözüm: JSON dosyasının OUTPUT/ klasöründe olduğunu kontrol edin

# Hata: Polygon noktaları geçersiz
# Çözüm: En az 3 nokta gerekli
# Çözüm: Noktaların video sınırları içinde olduğunu kontrol edin
```

### 🔧 **Performance Optimizasyonu**

#### ⚡ **Hızlandırma İpuçları**
```python
# GPU kullanımını etkinleştirin
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Video çözünürlüğünü düşürün
resize_factor = 0.5  # %50 küçültme

# Confidence threshold'u artırın
CONFIDENCE_THRESHOLD = 0.5  # Daha az tespit, daha hızlı

# Kare atlama kullanın
process_every_nth_frame = 2  # Her 2. kareyi işle
```

#### 💾 **Bellek Optimizasyonu**
```python
# Batch size'ı küçültün
batch_size = 1

# Video buffer'ını sınırlayın  
max_frames_in_memory = 100

# Çıktı videosunu sıkıştırın
fourcc = cv2.VideoWriter_fourcc(*'H264')  # Daha küçük dosya
```

### 📞 **Destek**

Sorun yaşıyorsanız:
1. **Log dosyalarını** kontrol edin (`OUTPUT/` klasöründe)
2. **Python version** kontrol edin (`python --version`)
3. **GPU driver** güncel mi kontrol edin
4. **Disk alanı** yeterli mi kontrol edin
5. **Antivirus** yazılımının Python'u engellemediğini kontrol edin

---

## 👥 KATKIDA BULUNANLAR

### 👨‍💻 **FURKAN** - Model Geliştirme & Optimizasyon
- 🤖 10 YOLO modeli entegrasyonu
- ⚙️ Detection parametre optimizasyonu  
- 🏗️ Sistem mimarisi tasarımı
- 📈 Performance tracking sistemleri
- 🚀 GPU/CPU adaptive processing

**Katkıları:**
- `core/config.py` - Merkezi konfigürasyon sistemi
- `detection_module/person_detector.py` - YOLO detection modülü
- `video_module/all_models_pool_tracker.py` - Multi-model tracker
- `video_module/enhanced_pool_tracker.py` - Gelişmiş tracking

### 👩‍💻 **NISA** - Eğitim Hazırlık & Test Aşamaları  
- 🎬 Video test sistemi geliştirme
- 🏊 Havuz alanı tanımlama araçları
- 📋 Test senaryoları ve validation
- 📊 Data processing ve output management
- 🧪 Quality validation sistemleri

**Katkıları:**
- `pool_module/` - Tüm havuz alanı modülleri
- `video_module/multi_video_pool_tester.py` - Batch video tester  
- `video_module/real_video_tester.py` - Real video processor
- `tests/test_video_person_detection.py` - Video test framework

---

## 📄 LİSANS

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

---

## 🚀 SONRAKI ADIMLAR

### 🔮 **Geliştirilecek Özellikler**
- [ ] **Real-time Streaming** desteği
- [ ] **Web Interface** (Flask/FastAPI)
- [ ] **Mobile App** (React Native)  
- [ ] **Cloud Deployment** (AWS/Azure)
- [ ] **Advanced Drowning AI** (RNN/LSTM)
- [ ] **Multi-Camera** sync support
- [ ] **Alert System** (Email/SMS/Push)

### 🏢 **Production Hazırlığı**  
- [ ] **Docker** containerization
- [ ] **Kubernetes** deployment  
- [ ] **CI/CD** pipeline
- [ ] **Load Testing** ve scaling
- [ ] **Security** audit
- [ ] **Documentation** completion

---

## 🙏 TEŞEKKÜRLER

Bu proje aşağıdaki açık kaynak projelerden yararlanmıştır:

- **[Ultralytics](https://ultralytics.com/)** - YOLOv8/v11/v12 implementation
- **[OpenCV](https://opencv.org/)** - Computer vision library
- **[PyTorch](https://pytorch.org/)** - Deep learning framework

---

**📧 İletişim:** Sorularınız için lütfen proje deposunda issue açın.  
**🌟 Beğenin:** Proje işinize yaradıysa ⭐ vermeyi unutmayın!

---

*Son güncelleme: 2024-07-25 | Versiyon: 2.0.0 | Durum: Aktif Geliştirme* 