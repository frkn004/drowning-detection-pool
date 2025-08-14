#!/bin/bash
# 🚀 VAST.AI DROWNING DETECTION SETUP SCRIPT

echo "🏊 DROWNING DETECTION MODEL TRAINING SETUP"
echo "==========================================="

# Update system
echo "📦 System güncellemesi..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Sistem bağımlılıkları..."
sudo apt install -y \
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
    libgomp1

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

# PyTorch CUDA kontrolü
echo "🔥 CUDA kontrolü..."
python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}'); print(f'GPU Count: {torch.cuda.device_count()}')"

# Proje klasörü oluştur
echo "📁 Proje klasörleri..."
mkdir -p ~/drowning_detection/{dataset,models,logs,checkpoints}

# Git konfigürasyonu (isteğe bağlı)
echo "⚙️ Git konfigürasyonu..."
git config --global user.name "FURKAN-NISA"
git config --global user.email "training@drowning-detection.ai"

# YOLO test
echo "🤖 YOLO test..."
python3 -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('✅ YOLO başarıyla yüklendi!')"

# GPU bilgileri
echo "📊 GPU Bilgileri:"
nvidia-smi

echo ""
echo "✅ KURULUM TAMAMLANDI!"
echo "🚀 Eğitime başlamak için:"
echo "   source drowning_env/bin/activate"
echo "   cd ~/drowning_detection"
echo "   python train_model.py"
echo ""
echo "📊 Monitoring için:"
echo "   tensorboard --logdir=logs"
echo "   tmux new-session -s training"