#!/bin/bash
# 🔽 DATASET DOWNLOAD SCRIPT FOR VAST.AI
# ==========================================

echo "🏊 DROWNING DETECTION DATASET DOWNLOAD"
echo "======================================"

# Dataset URLs (güncelleyeceğiniz linkler)
DATASET_5_URL="https://drive.google.com/uc?id=YOUR_5_TICKET_DATA_ID"
DATASET_9_URL="https://drive.google.com/uc?id=YOUR_9_TICKETV2_ID"

# Download directories
DOWNLOAD_DIR="$HOME/drowning_detection"
mkdir -p "$DOWNLOAD_DIR"

echo "📁 Download dizini: $DOWNLOAD_DIR"

# Function: Download from Google Drive
download_gdrive() {
    local url="$1"
    local output="$2"
    local filename="$3"
    
    echo "🔽 İndiriliyor: $filename"
    
    # Google Drive direct download
    wget --load-cookies /tmp/cookies.txt \
         "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate "$url" -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$(echo "$url" | sed -rn 's/.*id=([0-9A-Za-z_-]+).*/\1\n/p')" \
         -O "$output" && rm -rf /tmp/cookies.txt
    
    if [ $? -eq 0 ]; then
        echo "✅ İndirildi: $filename"
        return 0
    else
        echo "❌ İndirme hatası: $filename"
        return 1
    fi
}

# Download 5_TICKET_DATA
echo "📦 5_TICKET_DATA indiriliyor..."
if download_gdrive "$DATASET_5_URL" "$DOWNLOAD_DIR/5_TICKET_DATA.tar.gz" "5_TICKET_DATA"; then
    echo "📂 Açılıyor: 5_TICKET_DATA..."
    cd "$DOWNLOAD_DIR"
    tar -xzf 5_TICKET_DATA.tar.gz
    rm 5_TICKET_DATA.tar.gz
    echo "✅ 5_TICKET_DATA hazır!"
fi

# Download 9_TICKETv2
echo "📦 9_TICKETv2 indiriliyor..."
if download_gdrive "$DATASET_9_URL" "$DOWNLOAD_DIR/9_TICKETv2.tar.gz" "9_TICKETv2"; then
    echo "📂 Açılıyor: 9_TICKETv2..."
    cd "$DOWNLOAD_DIR"
    tar -xzf 9_TICKETv2.tar.gz
    rm 9_TICKETv2.tar.gz
    echo "✅ 9_TICKETv2 hazır!"
fi

# Verify downloads
echo "🔍 Doğrulama..."
ls -la "$DOWNLOAD_DIR"

echo ""
echo "✅ DATASET DOWNLOAD TAMAMLANDI!"
echo "📁 Dataset konumu: $DOWNLOAD_DIR"
echo "🚀 Eğitime başlamak için:"
echo "   cd $DOWNLOAD_DIR/8_TRAINING"
echo "   python scripts/prepare_dataset.py"


