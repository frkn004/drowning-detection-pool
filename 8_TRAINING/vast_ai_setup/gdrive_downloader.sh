#!/bin/bash
# 🔽 GOOGLE DRIVE DATASET DOWNLOADER FOR VAST.AI
# ===============================================

echo "🏊 VAST.AI GOOGLE DRIVE DATASET DOWNLOADER"
echo "=========================================="

# Exit on any error
set -e

# Function: Install required tools
install_requirements() {
    echo "📦 Gerekli araçlar yükleniyor..."
    
    # Update package list
    apt-get update
    
    # Install essential tools
    apt-get install -y wget curl unzip python3-pip
    
    # Install gdown for better Google Drive support
    pip3 install gdown
    
    echo "✅ Gerekli araçlar yüklendi"
}

# Function: Download from Google Drive using file ID
download_from_gdrive() {
    local file_id="$1"
    local output_path="$2"
    local file_name="$3"
    
    echo "🔽 İndiriliyor: $file_name"
    echo "📄 Dosya ID: $file_id"
    echo "📁 Hedef: $output_path"
    
    # Create output directory
    mkdir -p "$(dirname "$output_path")"
    
    # Download using gdown (better for large files)
    if command -v gdown &> /dev/null; then
        echo "📥 gdown ile indiriliyor..."
        gdown "https://drive.google.com/uc?id=$file_id" -O "$output_path"
    else
        echo "📥 wget ile indiriliyor..."
        wget --no-check-certificate "https://drive.google.com/uc?export=download&id=$file_id" -O "$output_path"
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ İndirme başarılı: $file_name"
        
        # Show file size
        file_size=$(du -h "$output_path" | cut -f1)
        echo "💾 Dosya boyutu: $file_size"
        
        return 0
    else
        echo "❌ İndirme başarısız: $file_name"
        return 1
    fi
}

# Function: Extract archives
extract_archive() {
    local archive_path="$1"
    local extract_to="$2"
    
    echo "📦 Açılıyor: $(basename "$archive_path")"
    
    # Create extraction directory
    mkdir -p "$extract_to"
    
    # Determine archive type and extract
    case "$archive_path" in
        *.tar.gz|*.tgz)
            tar -xzf "$archive_path" -C "$extract_to"
            ;;
        *.tar.bz2|*.tbz2)
            tar -xjf "$archive_path" -C "$extract_to"
            ;;
        *.tar.xz|*.txz)
            tar -xJf "$archive_path" -C "$extract_to"
            ;;
        *.tar)
            tar -xf "$archive_path" -C "$extract_to"
            ;;
        *.zip)
            unzip -q "$archive_path" -d "$extract_to"
            ;;
        *.7z)
            7z x "$archive_path" -o"$extract_to"
            ;;
        *)
            echo "⚠️ Bilinmeyen arşiv formatı: $archive_path"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        echo "✅ Açma başarılı: $(basename "$archive_path")"
        
        # Remove archive to save space
        echo "🗑️ Arşiv dosyası siliniyor: $(basename "$archive_path")"
        rm "$archive_path"
        
        return 0
    else
        echo "❌ Açma başarısız: $(basename "$archive_path")"
        return 1
    fi
}

# Function: Setup directory structure
setup_directories() {
    local base_dir="$1"
    
    echo "📁 Klasör yapısı oluşturuluyor..."
    
    # Create base directories
    mkdir -p "$base_dir"/{dataset,models,logs,checkpoints}
    mkdir -p "$base_dir"/dataset/{images,labels}/{train,val}
    
    echo "✅ Klasör yapısı hazır: $base_dir"
}

# Function: Verify download integrity
verify_download() {
    local file_path="$1"
    local expected_size="$2"  # Optional: expected file size in bytes
    
    if [ ! -f "$file_path" ]; then
        echo "❌ Dosya bulunamadı: $file_path"
        return 1
    fi
    
    local file_size=$(stat -c%s "$file_path")
    echo "📊 Dosya boyutu: $file_size bytes"
    
    # Check if file is not empty
    if [ "$file_size" -eq 0 ]; then
        echo "❌ Dosya boş: $file_path"
        return 1
    fi
    
    # Check expected size if provided
    if [ -n "$expected_size" ] && [ "$file_size" -ne "$expected_size" ]; then
        echo "⚠️ Dosya boyutu beklenen boyutla eşleşmiyor"
        echo "   Beklenen: $expected_size bytes"
        echo "   Gerçek: $file_size bytes"
    fi
    
    echo "✅ Dosya doğrulaması başarılı"
    return 0
}

# Function: Main download process
main_download() {
    local base_dir="/home/ubuntu/drowning_detection"
    
    echo "🚀 Ana download işlemi başlıyor..."
    echo "📁 Hedef klasör: $base_dir"
    
    # Setup directories
    setup_directories "$base_dir"
    
    # Dataset download configuration
    # ⚠️ BURAYA GOOGLE DRIVE DOSYA ID'LERİNİZİ EKLEYİN
    declare -A datasets=(
        ["5_TICKET_DATA"]="YOUR_5_TICKET_DATA_FILE_ID"
        ["9_TICKETv2"]="YOUR_9_TICKETV2_FILE_ID"
        ["MINI_DATASET"]="YOUR_MINI_DATASET_FILE_ID"
    )
    
    # Download each dataset
    for dataset_name in "${!datasets[@]}"; do
        file_id="${datasets[$dataset_name]}"
        
        if [ "$file_id" == "YOUR_"*"_FILE_ID" ]; then
            echo "⚠️ $dataset_name için Google Drive File ID ayarlanmamış"
            continue
        fi
        
        echo ""
        echo "📦 Dataset indiriliyor: $dataset_name"
        
        # Set paths
        archive_path="$base_dir/${dataset_name}.tar.gz"
        extract_to="$base_dir"
        
        # Download
        if download_from_gdrive "$file_id" "$archive_path" "$dataset_name"; then
            # Verify download
            if verify_download "$archive_path"; then
                # Extract
                if extract_archive "$archive_path" "$extract_to"; then
                    echo "🎉 $dataset_name başarıyla indirildi ve açıldı"
                else
                    echo "❌ $dataset_name açılırken hata oluştu"
                fi
            else
                echo "❌ $dataset_name download doğrulaması başarısız"
            fi
        else
            echo "❌ $dataset_name download başarısız"
        fi
    done
    
    echo ""
    echo "📊 İndirme işlemi tamamlandı"
    echo "📁 Dataset konumu: $base_dir"
    
    # Show directory structure
    echo ""
    echo "📋 Klasör yapısı:"
    ls -la "$base_dir"
    
    # Show disk usage
    echo ""
    echo "💾 Disk kullanımı:"
    du -sh "$base_dir"/*
}

# Function: Setup Google Drive file IDs
setup_file_ids() {
    echo "⚙️ GOOGLE DRIVE FILE ID KURULUMU"
    echo "================================"
    echo ""
    echo "📝 Google Drive dosyalarınızın File ID'lerini ayarlayın:"
    echo ""
    echo "1. Google Drive'da dosyaya sağ tıklayın"
    echo "2. 'Paylaş' > 'Genel erişim' > 'Linki olan herkes'"
    echo "3. Linki kopyalayın: https://drive.google.com/file/d/FILE_ID/view"
    echo "4. FILE_ID kısmını script'te güncelleyin"
    echo ""
    echo "📁 Bu script'i düzenleyin:"
    echo "   nano $0"
    echo ""
    echo "🔍 datasets dizisinde YOUR_*_FILE_ID değerlerini güncelleyin"
}

# Function: Show help
show_help() {
    echo "🆘 KULLANIM KILAVUZU"
    echo "==================="
    echo ""
    echo "Komutlar:"
    echo "  $0 install    - Gerekli araçları yükle"
    echo "  $0 setup      - File ID kurulum rehberi"
    echo "  $0 download   - Dataset'leri indir"
    echo "  $0 help       - Bu yardım mesajını göster"
    echo ""
    echo "Örnek kullanım:"
    echo "  1. chmod +x $0"
    echo "  2. $0 install"
    echo "  3. $0 setup    # File ID'leri ayarla"
    echo "  4. $0 download # İndirmeyi başlat"
}

# Main execution
case "${1:-help}" in
    "install")
        install_requirements
        ;;
    "setup")
        setup_file_ids
        ;;
    "download")
        main_download
        ;;
    "help"|*)
        show_help
        ;;
esac

echo ""
echo "🏊 Script tamamlandı!"


