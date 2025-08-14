#!/usr/bin/env python3
"""
📦 MINI DATASET CREATOR FOR GITHUB
=====================================
GitHub'a upload etmek için küçük sample dataset oluşturur
"""

import os
import shutil
import random
from pathlib import Path

def create_mini_dataset(source_dir, target_dir, max_files=200):
    """
    GitHub'a upload edilecek mini dataset oluştur
    
    Args:
        source_dir: Kaynak dataset klasörü (9_TICKETv2 vs)
        target_dir: Hedef mini dataset klasörü  
        max_files: Maksimum dosya sayısı
    """
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Kaynak klasörler
    frames_dir = source_path / "01_frames"
    labels_dir = source_path / "02_labels"
    
    # Hedef klasörler
    mini_frames = target_path / "01_frames"
    mini_labels = target_path / "02_labels"
    
    # Klasörleri oluştur
    mini_frames.mkdir(parents=True, exist_ok=True)
    mini_labels.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Kaynak: {source_path}")
    print(f"📁 Hedef: {target_path}")
    
    # Tüm frame dosyalarını listele
    frame_files = list(frames_dir.glob("*.jpg"))
    print(f"📸 Toplam frame: {len(frame_files)}")
    
    # En kaliteli frame'leri seç (dosya boyutuna göre)
    print("🎯 En kaliteli frame'ler seçiliyor...")
    frame_sizes = []
    for frame in frame_files:
        if frame.exists():
            size = frame.stat().st_size
            frame_sizes.append((frame, size))
    
    # Büyükten küçüğe sırala
    frame_sizes.sort(key=lambda x: x[1], reverse=True)
    
    # En iyi N tanesini seç
    selected_frames = frame_sizes[:max_files]
    
    print(f"✅ Seçilen frame sayısı: {len(selected_frames)}")
    
    # Dosyaları kopyala
    copied_count = 0
    for frame_path, _ in selected_frames:
        frame_name = frame_path.stem
        
        # Frame kopyala
        source_frame = frame_path
        target_frame = mini_frames / f"{frame_name}.jpg"
        
        # Label kopyala
        source_label = labels_dir / f"{frame_name}.txt"
        target_label = mini_labels / f"{frame_name}.txt"
        
        try:
            # Frame kopyala
            shutil.copy2(source_frame, target_frame)
            
            # Label varsa kopyala
            if source_label.exists():
                shutil.copy2(source_label, target_label)
                copied_count += 1
            else:
                print(f"⚠️ Label bulunamadı: {frame_name}")
                
        except Exception as e:
            print(f"❌ Hata {frame_name}: {e}")
    
    # Classes dosyasını kopyala
    classes_file = source_path / "classes.txt"
    if classes_file.exists():
        shutil.copy2(classes_file, target_path / "classes.txt")
        print("📋 Classes.txt kopyalandı")
    
    print(f"\n✅ Mini dataset oluşturuldu!")
    print(f"📊 Kopyalanan dosya çifti: {copied_count}")
    print(f"📁 Konum: {target_path}")
    
    # Boyut kontrolü
    mini_size = sum(f.stat().st_size for f in target_path.rglob('*') if f.is_file())
    mini_size_mb = mini_size / (1024 * 1024)
    print(f"💾 Toplam boyut: {mini_size_mb:.1f}MB")
    
    if mini_size_mb < 100:
        print("✅ GitHub'a upload edilebilir (<100MB)")
    else:
        print("⚠️ Hala büyük, dosya sayısını azaltın")
    
    return copied_count

def main():
    """Ana fonksiyon"""
    print("📦 MINI DATASET CREATOR")
    print("======================")
    
    # Kaynak seçimi
    print("📊 Kaynak dataset seçin:")
    print("   1. 5_TİCKET_DATA (1.7GB)")
    print("   2. 9_TICKETv2 (3.5GB)")
    
    choice = input("Hangi dataset'i kullanmak istiyorsunuz? (1-2): ").strip()
    
    if choice == "1":
        source_dir = "5_TİCKET_DATA"
    elif choice == "2":
        source_dir = "9_TICKETv2"
    else:
        print("❌ Geçersiz seçim! Varsayılan olarak 9_TICKETv2 kullanılıyor.")
        source_dir = "9_TICKETv2"
    
    # Hedef klasör
    target_dir = f"MINI_DATASET_{source_dir}"
    
    # Dosya sayısı
    max_files = int(input("Maksimum dosya sayısı (200 önerilir): ") or "200")
    
    # Mini dataset oluştur
    try:
        create_mini_dataset(source_dir, target_dir, max_files)
        
        print(f"\n🎉 Başarılı!")
        print(f"📁 Mini dataset: {target_dir}")
        print("🚀 GitHub'a upload etmek için:")
        print(f"   git add {target_dir}/")
        print("   git lfs track '*.jpg'")
        print("   git add .gitattributes")
        print("   git commit -m 'Add mini dataset'")
        print("   git push origin main")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    main()
