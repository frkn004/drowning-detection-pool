#!/usr/bin/env python3

import cv2
import sys
import os
import time
from datetime import datetime

# Config'i import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Camera, Paths, System

def test_camera_access():
    """Kamera erişimini test et"""
    print("🔍 Kamera erişimi test ediliyor...")
    
    try:
        cap = cv2.VideoCapture(Camera.DEFAULT_DEVICE)
        
        if not cap.isOpened():
            print("❌ Kamera açılamadı!")
            return False
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"✅ Kamera başarıyla açıldı!")
        print(f"📊 Çözünürlük: {width}x{height}")
        print(f"🎬 FPS: {fps}")
        
        ret, frame = cap.read()
        if ret:
            print(f"✅ Test karesi alındı: {frame.shape}")
            os.makedirs(Paths.OUTPUT_DIR, exist_ok=True)
            test_image_path = os.path.join(Paths.OUTPUT_DIR, "camera_test.jpg")
            cv2.imwrite(test_image_path, frame)
            print(f"💾 Test karesi kaydedildi: {test_image_path}")
        else:
            print("❌ Test karesi alınamadı!")
            cap.release()
            return False
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Kamera testi hatası: {e}")
        return False

def test_available_cameras():
    """Kullanılabilir kameraları test et"""
    print("📷 Kullanılabilir kameralar aranıyor...")
    
    available_cameras = []
    
    for i in range(3):  # 0-2 arası test et
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append(i)
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    print(f"✅ Kamera {i}: {width}x{height}")
                cap.release()
        except:
            pass
    
    if available_cameras:
        print(f"📷 Toplam {len(available_cameras)} kamera bulundu: {available_cameras}")
    else:
        print("❌ Hiç kamera bulunamadı!")
    
    return available_cameras

def run_all_tests():
    """Tüm kamera testlerini çalıştır"""
    print("="*50)
    print(f"🧪 {System.PROJECT_NAME} - KAMERA TESTLERİ")
    print("="*50)
    
    # Test 1: Kullanılabilir kameralar
    cameras = test_available_cameras()
    print("-" * 30)
    
    if not cameras:
        print("❌ Kamera bulunamadığı için testler durduruluyor!")
        return False
    
    # Test 2: Kamera erişimi
    if not test_camera_access():
        print("❌ Kamera erişim testi başarısız!")
        return False
    
    print("-" * 30)
    print("✅ Kamera testleri tamamlandı!")
    print(f"📁 Çıktılar: {Paths.OUTPUT_DIR}")
    
    return True

if __name__ == "__main__":
    run_all_tests()
