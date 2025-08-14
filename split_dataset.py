#!/usr/bin/env python3
"""
✂️ DATASET SPLITTER FOR GITHUB
=============================
Büyük dataset'i GitHub'a upload edilebilir parçalara böler
"""

import os
import shutil
import math
from pathlib import Path

def split_dataset(source_dir, chunk_size_mb=400):
    """
    Dataset'i chunk'lara böl
    
    Args:
        source_dir: Kaynak dataset klasörü
        chunk_size_mb: Her chunk'ın maksimum boyutu (MB)
    """
    
    source_path = Path(source_dir)
    frames_dir = source_path / "01_frames"
    labels_dir = source_path / "02_labels"
    
    # Tüm dosyaları listele ve boyutlarını hesapla
    files_with_sizes = []
    
    for frame_file in frames_dir.glob("*.jpg"):
        frame_name = frame_file.stem
        label_file = labels_dir / f"{frame_name}.txt"
        
        if label_file.exists():
            frame_size = frame_file.stat().st_size
            label_size = label_file.stat().st_size
            total_size = frame_size + label_size
            
            files_with_sizes.append({
                'name': frame_name,
                'frame_path': frame_file,
                'label_path': label_file,
                'size': total_size
            })
    
    # Dosyaları boyuta göre sırala
    files_with_sizes.sort(key=lambda x: x['size'], reverse=True)
    
    print(f"📊 Toplam dosya çifti: {len(files_with_sizes)}")
    total_size = sum(f['size'] for f in files_with_sizes)
    total_size_mb = total_size / (1024 * 1024)
    print(f"💾 Toplam boyut: {total_size_mb:.1f}MB")
    
    # Chunk sayısını hesapla
    chunk_size_bytes = chunk_size_mb * 1024 * 1024
    num_chunks = math.ceil(total_size / chunk_size_bytes)
    print(f"📦 Gerekli chunk sayısı: {num_chunks}")
    
    # Chunk'ları oluştur
    chunks = []
    current_chunk = []
    current_size = 0
    
    for file_info in files_with_sizes:
        if current_size + file_info['size'] > chunk_size_bytes and current_chunk:
            # Mevcut chunk'ı kaydet
            chunks.append(current_chunk)
            current_chunk = []
            current_size = 0
        
        current_chunk.append(file_info)
        current_size += file_info['size']
    
    # Son chunk'ı ekle
    if current_chunk:
        chunks.append(current_chunk)
    
    print(f"✅ {len(chunks)} chunk oluşturuldu")
    
    # Chunk klasörlerini oluştur
    for i, chunk in enumerate(chunks, 1):
        chunk_dir = source_path.parent / f"{source_path.name}_CHUNK_{i:02d}"
        chunk_frames = chunk_dir / "01_frames"
        chunk_labels = chunk_dir / "02_labels"
        
        chunk_frames.mkdir(parents=True, exist_ok=True)
        chunk_labels.mkdir(parents=True, exist_ok=True)
        
        chunk_size = 0
        for file_info in chunk:
            # Frame kopyala
            shutil.copy2(file_info['frame_path'], chunk_frames / file_info['frame_path'].name)
            # Label kopyala  
            shutil.copy2(file_info['label_path'], chunk_labels / file_info['label_path'].name)
            chunk_size += file_info['size']
        
        # Classes dosyasını her chunk'a kopyala
        classes_file = source_path / "classes.txt"
        if classes_file.exists():
            shutil.copy2(classes_file, chunk_dir / "classes.txt")
        
        chunk_size_mb = chunk_size / (1024 * 1024)
        print(f"📦 Chunk {i:02d}: {len(chunk)} dosya, {chunk_size_mb:.1f}MB -> {chunk_dir}")
    
    print(f"\n✅ Dataset bölme tamamlandı!")
    print("🚀 GitHub'a upload etmek için:")
    for i in range(1, len(chunks) + 1):
        chunk_name = f"{source_path.name}_CHUNK_{i:02d}"
        print(f"   git add {chunk_name}/")
        print(f"   git commit -m 'Add dataset chunk {i}/{len(chunks)}'")
        print(f"   git push origin main")

def main():
    """Ana fonksiyon"""
    print("✂️ DATASET SPLITTER")
    print("==================")
    
    # Kaynak seçimi
    print("📊 Hangi dataset'i bölmek istiyorsunuz?")
    print("   1. 5_TİCKET_DATA (1.7GB)")
    print("   2. 9_TICKETv2 (3.5GB)")
    
    choice = input("Seçiminiz (1-2): ").strip()
    
    if choice == "1":
        source_dir = "5_TİCKET_DATA"
    elif choice == "2":
        source_dir = "9_TICKETv2"
    else:
        print("❌ Geçersiz seçim!")
        return
    
    # Chunk boyutu
    chunk_size = int(input("Chunk boyutu (MB, 400 önerilir): ") or "400")
    
    try:
        split_dataset(source_dir, chunk_size)
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    main()
