#!/usr/bin/env python3
"""
🎨 ETİKET DÜZENLEME ARACI - TEK SCRIPT
=====================================
AirDrop ile gelen dosya için basit başlatma
Sadece etiket düzenleme yapar, yeni etiketleme yapmaz
"""

import os
import sys

def check_basic_requirements():
    """Temel gereklilikleri kontrol et"""
    print("🔍 Sistem kontrol ediliyor...")
    
    # Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ gerekli!")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # OpenCV
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV eksik! 'pip install opencv-python' çalıştır")
        return False
    
    # NumPy
    try:
        import numpy
        print(f"✅ NumPy {numpy.__version__}")
    except ImportError:
        print("❌ NumPy eksik! 'pip install numpy' çalıştır")
        return False
    
    return True

def check_data():
    """Veri dosyalarını kontrol et"""
    print("\n📁 Veri dosyaları kontrol ediliyor...")
    
    # Klasörler
    required_dirs = ["01_frames", "02_labels"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ {dir_name} klasörü bulunamadı!")
            return False
        
        file_count = len(os.listdir(dir_name))
        print(f"✅ {dir_name}: {file_count} dosya")
    
    # classes.txt
    if not os.path.exists("classes.txt"):
        print("❌ classes.txt bulunamadı!")
        return False
    print("✅ classes.txt")
    
    # advanced_editor.py
    if not os.path.exists("advanced_editor.py"):
        print("❌ advanced_editor.py bulunamadı!")
        return False
    print("✅ advanced_editor.py")
    
    return True

def launch_editor():
    """Advanced Editor'ü başlat"""
    print("\n🎨 ADVANCED EDITOR BAŞLATILIYOR...")
    print("=" * 50)
    
    # Mevcut durum
    frame_count = len(os.listdir("01_frames"))
    label_count = len(os.listdir("02_labels"))
    
    print(f"📊 Mevcut Durum:")
    print(f"   📸 Frame: {frame_count:,} adet")
    print(f"   🏷️  Etiket: {label_count:,} adet")
    print(f"   📈 Etiketleme: %{(label_count/frame_count)*100:.1f}")
    
    print(f"\n🎯 KONTROLLER:")
    print(f"   🖱️  SOL DRAG: Yeni etiket çiz")
    print(f"   🖱️  SAĞ CLICK: Etiket seç")
    print(f"   ⌨️  1: person_swimming (YEŞİL)")
    print(f"   ⌨️  2: person_drowning (KIRMIZI)")
    print(f"   ⌨️  3: person_poolside (MAVİ)")
    print(f"   ⌨️  4: pool_equipment (SARI)")
    print(f"   ⌨️  SPACE/D: Sonraki frame")
    print(f"   ⌨️  A: Önceki frame")
    print(f"   ⌨️  Q/W: Etiket seç")
    print(f"   ⌨️  DEL/TAB: Sil")
    print(f"   ⌨️  ESC: Çıkış")
    
    print(f"\n🔥 ÖNEMLİ:")
    print(f"   • Tüm etiketler 'person_swimming' olarak başlar")
    print(f"   • Havuz dışındaki kişiler → 3 (person_poolside)")
    print(f"   • Boğulma riski olanlar → 2 (person_drowning)")
    print(f"   • Yanlış tespitleri silin")
    print(f"   • Otomatik kaydetme aktif")
    
    input(f"\n🚀 ENTER ile Advanced Editor'ü başlat...")
    
    try:
        # Advanced Editor import ve çalıştır
        sys.path.append('.')
        import advanced_editor
        
        editor = advanced_editor.AdvancedEditor("01_frames", "02_labels", "classes.txt")
        editor.run()
        
        print(f"\n✅ Etiket düzenleme tamamlandı!")
        return True
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Kullanıcı tarafından durduruldu")
        return True
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print(f"💡 Çözüm: 'pip install opencv-python numpy' deneyin")
        return False

def main():
    """Ana fonksiyon"""
    
    print("🎨 ETİKET DÜZENLEME ARACI")
    print("=" * 50)
    print("📹 Havuz Telefon Hasımcan Video Etiketleri")
    print("🎯 Amaç: YOLOv8x etiketlerini manuel düzelt")
    print("=" * 50)
    
    # Sistem kontrol
    if not check_basic_requirements():
        print(f"\n❌ Sistem gereklilikleri karşılanmıyor!")
        input(f"🔚 ENTER ile çıkış...")
        return
    
    # Veri kontrol
    if not check_data():
        print(f"\n❌ Gerekli dosyalar eksik!")
        print(f"💡 Bu script frame'ler ve etiketlerle birlikte çalışır")
        input(f"🔚 ENTER ile çıkış...")
        return
    
    print(f"\n✅ Tüm kontroller başarılı!")
    
    # Editor başlat
    launch_editor()
    
    print(f"\n👋 Etiket düzenleme aracı kapatıldı")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Program durduruldu!")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        input(f"\n🔚 ENTER ile çıkış...")


