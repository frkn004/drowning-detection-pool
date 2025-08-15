#!/bin/bash
# 🚀 VAST.AI DROWNING DETECTION COMPLETE SETUP SCRIPT

echo "🏊 DROWNING DETECTION MODEL TRAINING SETUP"
echo "==========================================="

# Set working directory
WORK_DIR="/home/ubuntu/drowning_detection"

# Update system
echo "📦 System güncellemesi..."
apt update && apt upgrade -y

# Install system dependencies
echo "🔧 Sistem bağımlılıkları..."
apt install -y \
    git \
    wget \
    curl \
    unzip \
    htop \
    tmux \
    tree \
    vim \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    rclone

# Python ve pip kontrolü
echo "🐍 Python kontrolü..."
python3 --version
pip3 --version

# Virtual environment oluştur
echo "🏗️ Virtual environment..."
python3 -m venv drowning_env
source drowning_env/bin/activate

# Requirements yükle
echo "📦 Python paketleri yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt

# Google Drive sync araçları
echo "🔗 Google Drive araçları..."
pip install gdown pydrive2 watchdog google-api-python-client google-auth-httplib2 google-auth-oauthlib

# PyTorch CUDA kontrolü
echo "🔥 CUDA kontrolü..."
python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}'); print(f'GPU Count: {torch.cuda.device_count()}')"

# Proje klasörü oluştur
echo "📁 Proje klasörleri..."
mkdir -p $WORK_DIR/{dataset,models,logs,checkpoints,TEST_VIDEOS,RESULTS}

# Git konfigürasyonu
echo "⚙️ Git konfigürasyonu..."
git config --global user.name "FURKAN-NISA"
git config --global user.email "training@drowning-detection.ai"

# Google Drive sync setup
echo "🔄 Google Drive sync kurulumu..."
cd $WORK_DIR
python3 vast_ai_setup/gdrive_sync.py --action install

# Dataset'leri indir
echo "📥 Dataset'ler indiriliyor..."
python3 vast_ai_setup/gdrive_sync.py --action download --work-dir $WORK_DIR

# YOLO test
echo "🤖 YOLO test..."
python3 -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('✅ YOLO başarıyla yüklendi!')"

# Otomatik sync'i background'da başlat
echo "🔄 Otomatik sync başlatılıyor..."
nohup python3 vast_ai_setup/gdrive_sync.py --action sync --work-dir $WORK_DIR > gdrive_sync.log 2>&1 &
echo $! > gdrive_sync.pid

# GPU bilgileri
echo "📊 GPU Bilgileri:"
nvidia-smi

echo ""
echo "✅ KURULUM TAMAMLANDI!"
echo "🚀 İKİ AŞAMALI EĞİTİM için:"
echo "   source drowning_env/bin/activate"
echo "   cd $WORK_DIR/8_TRAINING"
echo "   python scripts/run_two_stage_training.py  # 🎯 OTOMATIK"
echo ""
echo "   VEYA manuel:"
echo "   python scripts/train_stage1_person.py     # 1️⃣ Person detection"
echo "   python scripts/test_stage1_person.py      # 🧪 Test stage 1"
echo "   python scripts/train_stage2_behavior.py   # 2️⃣ Behavior classification"
echo ""
echo "📊 Monitoring için:"
echo "   tensorboard --logdir=runs/train --host=0.0.0.0 --port=6006"
echo "   tmux new-session -s training"
echo ""
echo "🔄 Google Drive sync durumu:"
echo "   tail -f $WORK_DIR/gdrive_sync.log"
echo "   kill \$(cat $WORK_DIR/gdrive_sync.pid)  # sync'i durdurmak için"