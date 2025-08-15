# 🚀 VAST.AI HIZLI SETUP KILAVUZU

## 1️⃣ SSH BAĞLANTI
VAST.AI instance'ınıza SSH ile bağlanın:

```bash
# VAST.AI'dan aldığınız SSH komutu
ssh -p [PORT] root@[HOST] -L 8888:localhost:8888 -L 6006:localhost:6006
```

## 2️⃣ SİSTEM KURULUM
```bash
# Sistem güncelle
apt update && apt upgrade -y

# Gerekli araçları yükle  
apt install -y git wget curl unzip python3-pip

# gdown yükle (Google Drive için)
pip3 install gdown

# Git clone
git clone https://github.com/frkn004/drowning-detection-pool.git
cd drowning-detection-pool
```

## 3️⃣ GOOGLE DRIVE'DAN DATASET İNDİR

### Yöntem A: gdown ile (Basit)
```bash
# Dataset klasörü oluştur
mkdir -p datasets

# Google Drive'dan dataset indir (File ID'leri güncelleyin)
gdown "1abc123def456ghi789jkl" -O datasets/9_TICKETv2.tar.gz
gdown "1xyz789abc123def456ghi" -O datasets/5_TICKET_DATA.tar.gz

# Extract et
cd datasets
tar -xzf 9_TICKETv2.tar.gz
tar -xzf 5_TICKET_DATA.tar.gz
cd ..
```

### Yöntem B: Otomatik Script ile
```bash
# Script'i çalıştır
chmod +x 8_TRAINING/vast_ai_setup/gdrive_downloader.sh
./8_TRAINING/vast_ai_setup/gdrive_downloader.sh install
./8_TRAINING/vast_ai_setup/gdrive_downloader.sh download
```

## 4️⃣ EĞİTİM ORTAMI HAZIRLA
```bash
# Virtual env oluştur
python3 -m venv drowning_env
source drowning_env/bin/activate

# Requirements yükle
pip install -r 8_TRAINING/vast_ai_setup/requirements.txt

# CUDA test
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

## 5️⃣ EĞİTİMİ BAŞLAT
```bash
# Eğitim klasörüne git
cd 8_TRAINING

# Dataset hazırla
python scripts/prepare_dataset.py
# Seçim: 2 (9_TICKETv2 dataset)

# Tmux session aç
tmux new-session -s training

# Eğitimi başlat
python scripts/train_model.py
# Seçim: 1 (Phase 1)
```

## 6️⃣ MONİTORİNG
```bash
# Yeni terminal açın ve TensorBoard başlatın
tensorboard --logdir=runs/train --host=0.0.0.0 --port=6006

# Browser'da: http://localhost:6006
```

## 🔧 GOOGLE DRIVE FILE ID'LERİ
Google Drive dosyalarınızın linklerinden File ID'leri alın:

**Link örneği:**
```
https://drive.google.com/file/d/1abc123def456ghi789jkl/view?usp=sharing
```

**File ID:**
```
1abc123def456ghi789jkl
```

Script'teki `YOUR_*_FILE_ID` kısımlarını bu ID'lerle değiştirin.

## ⚡ HIZLI BAŞLANGIÇ KOMUTLARI
```bash
# Tek komutla kurulum
curl -fsSL https://raw.githubusercontent.com/frkn004/drowning-detection-pool/main/8_TRAINING/vast_ai_setup/setup.sh | bash

# Manuel kurulum
git clone https://github.com/frkn004/drowning-detection-pool.git
cd drowning-detection-pool
chmod +x 8_TRAINING/vast_ai_setup/setup.sh
./8_TRAINING/vast_ai_setup/setup.sh
```


