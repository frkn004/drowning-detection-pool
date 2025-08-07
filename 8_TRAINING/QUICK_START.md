# 🚀 DROWNING DETECTION MODEL EĞİTİMİ - HIZLI BAŞLANGIÇ

## ⚡ HIZLI BAŞLANGIÇ (5 ADIM)

### 1️⃣ **VAST.AI KURULUM** (10 dakika)
```bash
# VAST.AI'dan GPU instance kiralayın
# SSH bağlantısı kurun
ssh -p [PORT] root@[HOST] -L 8888:localhost:8888 -L 6006:localhost:6006

# Setup scriptini çalıştırın
cd 8_TRAINING/vast_ai_setup
chmod +x setup.sh
./setup.sh
```

### 2️⃣ **DATASET HAZIRLAMA** (5 dakika)
```bash
# Dataset'i hazırlayın (Phase 1 için)
cd scripts
python prepare_dataset.py
# Seçim: 1 (Phase 1 - 200 frame)
# Validation split: 0.2
```

### 3️⃣ **İLK EĞİTİM BAŞLATMA** (2-3 saat)
```bash
# Tmux session açın
tmux new-session -s training

# Virtual environment aktif edin
source drowning_env/bin/activate

# Eğitimi başlatın
python train_model.py
# Seçim: 1 (Phase 1)
```

### 4️⃣ **MONİTORİNG** (Real-time)
```bash
# Yeni terminal açın
# TensorBoard başlatın
tensorboard --logdir=runs/train --host=0.0.0.0 --port=6006

# Browser'da açın: http://localhost:6006
```

### 5️⃣ **SONUÇ KONTROLÜ** (10 dakika)
```bash
# Eğitim bitince model kontrolü
ls models/best_phase1.pt

# Validation sonuçları
cat logs/training_*.log | tail -20
```

---

## 📋 PHASE 1 CHECKLIST

### ✅ **Ön Hazırlık**
- [ ] VAST.AI account oluşturuldu
- [ ] SSH key hazırlandı  
- [ ] GPU instance kiralandı (RTX 4070/A100)
- [ ] Setup scripti çalıştırıldı

### ✅ **Dataset Hazırlığı**
- [ ] 5_TİCKET_DATA klasörü VAST.AI'ya upload edildi
- [ ] prepare_dataset.py çalıştırıldı
- [ ] 200 frame seçildi
- [ ] Train/val split yapıldı (160/40)

### ✅ **Eğitim Süreci**
- [ ] tmux session açıldı
- [ ] train_model.py başlatıldı
- [ ] TensorBoard monitoring aktif
- [ ] GPU kullanımı kontrol edildi

### ✅ **Sonuç Değerlendirmesi**
- [ ] mAP50 > 0.6 başarıldı
- [ ] Model dosyası kaydedildi
- [ ] Log dosyaları incelendi
- [ ] Phase 2 için hazırlık yapıldı

---

## 🔧 KOMUT REFERANSLARİ

### **SSH Bağlantısı**
```bash
# İlk bağlantı
ssh -p [PORT] root@[HOST] -L 8888:localhost:8888 -L 6006:localhost:6006

# Dosya upload
scp -P [PORT] -r ../5_TİCKET_DATA root@[HOST]:~/drowning_detection/

# Dosya download
scp -P [PORT] root@[HOST]:~/drowning_detection/models/best_*.pt ./models/
```

### **Tmux Kullanımı**
```bash
# Yeni session
tmux new-session -s training

# Session'dan çıkış (eğitim devam eder)
Ctrl+B, sonra D

# Session'a geri dönüş
tmux attach-session -t training

# Session listesi
tmux list-sessions
```

### **Monitoring Komutları**
```bash
# GPU durumu
nvidia-smi
watch -n 1 nvidia-smi

# Disk kullanımı
df -h

# Memory kullanımı
free -h

# Process monitoring
htop
```

### **Training Komutları**
```bash
# Dataset hazırla
python scripts/prepare_dataset.py

# Model eğit
python scripts/train_model.py

# Model validate et
python scripts/validate_model.py models/best_phase1.pt

# TensorBoard
tensorboard --logdir=runs/train --host=0.0.0.0 --port=6006
```

---

## 🚨 SORUN GİDERME

### **SSH Bağlantı Sorunu**
```bash
# Host key problemi
ssh-keygen -R [HOST]

# Permission sorunu
chmod 600 ~/.ssh/id_rsa

# Port forwarding test
telnet localhost 8888
```

### **CUDA/GPU Sorunu**
```bash
# CUDA test
python -c "import torch; print(torch.cuda.is_available())"

# GPU memory temizle
python -c "import torch; torch.cuda.empty_cache()"

# Driver kontrol
nvidia-smi
```

### **Dataset Sorunu**
```bash
# Dataset yapısı kontrol
tree dataset/ | head -20

# Label dosyası kontrol
head -5 dataset/labels/train/*.txt

# Image-label eşleşmesi
ls dataset/images/train/ | wc -l
ls dataset/labels/train/ | wc -l
```

### **Training Sorunu**
```bash
# Log kontrol
tail -f logs/training_*.log

# Memory sorunu - batch size küçült
# configs/training.yaml: batch: 8 -> 4

# Disk space kontrol
df -h
```

---

## 💰 MALİYET TAKİBİ

### **VAST.AI Maliyet Hesaplama**
```bash
# Günlük maliyet: $0.50-1.50/saat
# Phase 1: 2-3 saat = $1-5
# Phase 2: 8-12 saat = $4-18
# Phase 3: 20-30 saat = $10-45
# Phase 4: 40-60 saat = $20-90

# Toplam beklenen: $35-158
```

### **Auto-Stop Ayarlama**
```bash
# VAST.AI dashboard'da:
# Settings > Auto-stop after: 4 hours
# Budget limit: $50
```

---

## 📞 DESTEK

### **Acil Durum Komutları**
```bash
# Eğitimi durdur
pkill -f train_model.py

# Tmux session'ı sonlandır
tmux kill-session -t training

# VAST.AI instance'ı durdur
# Dashboard'dan Stop instance
```

### **Backup Komutları**
```bash
# Model backup
cp models/best_*.pt backup/

# Log backup
cp logs/*.log backup/

# Config backup
cp -r configs/ backup/
```

---

## 🎯 BEKLENTİLER

### **Phase 1 Başarı Kriterleri**
- ✅ **mAP50 > 0.6** - Baseline başarılı
- ✅ **Training loss < 2.0** - Convergence uygun
- ✅ **Val/Train gap < 0.5** - Overfitting yok
- ✅ **FPS > 20** - Hız kabul edilebilir

### **Sonraki Adımlar**
1. Phase 1 başarılıysa → Phase 2'ye geç
2. Phase 1 başarısızsa → Hyperparameter tuning
3. Dataset quality sorunu → Re-annotation
4. Technical problem → Sorun giderme

---

**🚀 HAZIRSAN EĞİTİME BAŞLAYALIM!**

*Son güncelleme: 5 Ağustos 2025*  
*Next action: VAST.AI kiralama*