#!/usr/bin/env python3
"""
🚀 HAVUZ VİDEO ETİKETLEME ARACI - ANA BAŞLATICI
==============================================
AirDrop ile gelen dosya için otomatik başlatma scripti
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Gereklilikleri kontrol et"""
    print("🔍 Sistem gereklilikleri kontrol ediliyor...")
    
    # Python version check
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ gerekli!")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Required packages
    required_packages = ['cv2', 'ultralytics', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - eksik!")
    
    if missing_packages:
        print(f"\n⚠️  Eksik paketler bulundu: {missing_packages}")
        print(f"📦 Yüklemek için:")
        if 'cv2' in missing_packages:
            print(f"   pip install opencv-python")
        if 'ultralytics' in missing_packages:
            print(f"   pip install ultralytics")
        if 'numpy' in missing_packages:
            print(f"   pip install numpy")
        return False
    
    return True

def show_main_menu():
    """Ana menüyü göster"""
    print("\n" + "="*60)
    print("🚀 HAVUZ VİDEO ETİKETLEME ARACI")
    print("="*60)
    print("📹 Mevcut durum:")
    
    # Frame sayısını göster
    frames_dir = "01_frames"
    labels_dir = "02_labels"
    
    if os.path.exists(frames_dir):
        frame_count = len(list(Path(frames_dir).glob("*.jpg")))
        print(f"   📸 Frame: {frame_count} adet")
    else:
        frame_count = 0
        print(f"   📸 Frame: Henüz çıkarılmadı")
    
    if os.path.exists(labels_dir):
        label_count = len(list(Path(labels_dir).glob("*.txt")))
        print(f"   🏷️  Etiket: {label_count} adet")
    else:
        label_count = 0
        print(f"   🏷️  Etiket: Henüz oluşturulmadı")
    
    print("\n📋 Ne yapmak istiyorsunuz?")
    print("   1️⃣  Yeni video'dan frame çıkar ve etiketle")
    print("   2️⃣  Mevcut etiketleri düzenle (Advanced Editor)")
    print("   3️⃣  Havuz_telefon_hasimcan.MOV ile devam et")
    print("   4️⃣  Çıkış")
    
    return input("\n🎯 Seçiminiz (1-4): ").strip()

def extract_and_label_new_video():
    """Yeni video'dan frame çıkar ve etiketle"""
    print("\n🎬 YENİ VIDEO İŞLEME")
    print("-" * 40)
    
    # Video listesi
    video_dir = "0_DATA"
    if not os.path.exists(f"../{video_dir}"):
        print(f"❌ Video klasörü bulunamadı: {video_dir}")
        return False
    
    video_files = []
    for ext in ['.mp4', '.mov', '.avi', '.MOV']:
        video_files.extend(list(Path(f"../{video_dir}").glob(f"*{ext}")))
    
    if not video_files:
        print("❌ Video dosyası bulunamadı!")
        return False
    
    print("📹 Mevcut videolar:")
    for i, video in enumerate(video_files, 1):
        print(f"   {i}. {video.name}")
    
    try:
        choice = int(input(f"\n🎯 Video seçin (1-{len(video_files)}): ")) - 1
        if 0 <= choice < len(video_files):
            selected_video = video_files[choice]
            print(f"✅ Seçilen: {selected_video.name}")
            
            # Frame extraction
            print("\n🔄 Frame extraction başlıyor...")
            # Script çalıştır...
            
        else:
            print("❌ Geçersiz seçim!")
            return False
    except ValueError:
        print("❌ Geçersiz giriş!")
        return False
    
    return True

def launch_advanced_editor():
    """Advanced Editor'ü başlat"""
    print("\n🎨 ADVANCED EDITOR BAŞLATILIYOR")
    print("-" * 40)
    
    # Gerekli dosyaları kontrol et
    if not os.path.exists("01_frames"):
        print("❌ Frame klasörü bulunamadı! Önce video işleme yapın.")
        return False
    
    if not os.path.exists("02_labels"):
        print("❌ Label klasörü bulunamadı! Önce otomatik etiketleme yapın.")
        return False
    
    if not os.path.exists("classes.txt"):
        print("❌ classes.txt bulunamadı!")
        return False
    
    frame_count = len(list(Path("01_frames").glob("*.jpg")))
    label_count = len(list(Path("02_labels").glob("*.txt")))
    
    print(f"📊 Mevcut durum:")
    print(f"   📸 Frame: {frame_count}")
    print(f"   🏷️  Label: {label_count}")
    
    if frame_count == 0:
        print("❌ Frame bulunamadı!")
        return False
    
    print(f"\n🎨 Advanced Editor başlatılıyor...")
    print(f"📋 Kontroller:")
    print(f"   🖱️  SOL DRAG: Yeni etiket çiz")
    print(f"   🖱️  SAĞ CLICK: Etiket seç")
    print(f"   ⌨️  1-4: Class değiştir")
    print(f"   ⌨️  SPACE/D: Sonraki frame")
    print(f"   ⌨️  A: Önceki frame")
    print(f"   ⌨️  DEL/TAB: Sil")
    print(f"   ⌨️  ESC: Çıkış")
    
    input("\n🚀 ENTER ile devam edin...")
    
    # Advanced Editor'ü çalıştır
    try:
        import advanced_editor
        editor = advanced_editor.AdvancedEditor("01_frames", "02_labels", "classes.txt")
        editor.run()
        return True
    except Exception as e:
        print(f"❌ Editor hatası: {e}")
        return False

def continue_with_existing():
    """Mevcut Havuz_telefon_hasimcan.MOV ile devam et"""
    print("\n📹 HAVUZ_TELEFON_HASIMCAN.MOV İLE DEVAM")
    print("-" * 40)
    
    # Mevcut durumu kontrol et
    frame_count = len(list(Path("01_frames").glob("*.jpg"))) if os.path.exists("01_frames") else 0
    label_count = len(list(Path("02_labels").glob("*.txt"))) if os.path.exists("02_labels") else 0
    
    print(f"📊 Mevcut durum:")
    print(f"   📸 Frame: {frame_count}")
    print(f"   🏷️  Label: {label_count}")
    
    if frame_count > 0 and label_count > 0:
        print(f"✅ Etiketleme verisi mevcut!")
        print(f"🎨 Advanced Editor ile düzenleme yapabilirsiniz")
        
        choice = input(f"\n🎯 Advanced Editor başlatılsın mı? (y/n): ").lower()
        if choice in ['y', 'yes', 'evet', 'e']:
            return launch_advanced_editor()
    else:
        print(f"⚠️  Frame veya etiket verisi eksik!")
        print(f"🔄 Yeniden işleme yapmak gerekebilir")
    
    return True

def main():
    """Ana fonksiyon"""
    
    print("🚀 HAVUZ VİDEO ETİKETLEME ARACI BAŞLATILIYOR...")
    
    # Gereklilikler kontrolü
    if not check_requirements():
        print("\n❌ Sistem gereklilikleri karşılanmıyor!")
        print("📦 Gerekli paketleri yükleyip tekrar deneyin.")
        input("\n🔚 ENTER ile çıkış...")
        return
    
    print("✅ Tüm gereklilikler karşılandı!")
    
    # Ana döngü
    while True:
        choice = show_main_menu()
        
        if choice == '1':
            extract_and_label_new_video()
        elif choice == '2':
            launch_advanced_editor()
        elif choice == '3':
            continue_with_existing()
        elif choice == '4':
            print("\n👋 Çıkış yapılıyor...")
            break
        else:
            print("\n❌ Geçersiz seçim! Lütfen 1-4 arası bir sayı girin.")
        
        input("\n⏸️  ENTER ile ana menüye dön...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Program durduruldu!")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        input("\n🔚 ENTER ile çıkış...")



