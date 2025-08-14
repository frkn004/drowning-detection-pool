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
