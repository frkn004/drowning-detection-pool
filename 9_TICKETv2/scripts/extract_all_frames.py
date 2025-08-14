#!/usr/bin/env python3
"""
🎬 TÜM FRAME EXTRACTION - Havuz_telefon_hasimcan.MOV
==================================================
Video'dan tüm frame'leri çıkar (her saniyede 1 frame)
"""

import cv2
import os
import sys
from pathlib import Path

def extract_all_frames_from_video():
    """Havuz_telefon_hasimcan.MOV'dan tüm frame'leri çıkar"""
    
    # Video yolu
    video_path = "../../0_DATA/Havuz_telefon_hasimcan.MOV"
    output_dir = "../01_frames"
    
    print("🎬 VIDEO FRAME EXTRACTION BAŞLIYOR")
    print("=" * 60)
    print(f"📹 Video: {video_path}")
    print(f"📁 Çıktı: {output_dir}")
    
    # Video kontrol
    if not os.path.exists(video_path):
        print(f"❌ Video bulunamadı: {video_path}")
        return False
    
    # Video aç
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Video açılamadı: {video_path}")
        return False
    
    # Video özellikleri
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps
    
    print(f"📊 Video Özellikleri:")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps:.1f}")
    print(f"   Total Frames: {total_frames}")
    print(f"   Duration: {duration:.1f} seconds")
    
    # Frame aralığını hesapla (her saniyede 1 frame)
    frame_step = int(fps)
    estimated_frames = total_frames // frame_step
    print(f"⏱️  Her {frame_step} frame'de bir çıkarılacak")
    print(f"📸 Tahmini çıkarılacak frame sayısı: {estimated_frames}")
    
    # Çıktı klasörünü oluştur
    os.makedirs(output_dir, exist_ok=True)
    
    extracted_count = 0
    frame_number = 0
    
    print(f"\n🔄 Frame extraction başlıyor...")
    
    # Frame çıkarma döngüsü
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Her 'frame_step' frame'de bir kaydet
        if frame_number % frame_step == 0:
            # Frame dosya adı (saniye bazında)
            second = frame_number // frame_step
            frame_filename = f"havuz_telefon_{second:04d}s.jpg"
            frame_path = os.path.join(output_dir, frame_filename)
            
            # Frame'i kaydet
            cv2.imwrite(frame_path, frame)
            extracted_count += 1
            
            # İlerleme göster
            if extracted_count % 20 == 0:
                progress = (frame_number / total_frames) * 100
                print(f"   📊 İşlenen: {extracted_count} frame ({progress:.1f}%)")
        
        frame_number += 1
    
    cap.release()
    
    print(f"\n🎉 Frame extraction tamamlandı!")
    print(f"   📸 Çıkarılan frame sayısı: {extracted_count}")
    print(f"   📁 Frames klasörü: {output_dir}")
    print(f"   ⏱️  Süre: {duration:.1f} saniye → {extracted_count} frame")
    
    return True

def main():
    """Ana fonksiyon"""
    
    print("🎬 HAVUZ TELEFON VİDEO FRAME EXTRACTION")
    print("=" * 60)
    
    # Frame extraction
    success = extract_all_frames_from_video()
    
    if success:
        print(f"\n✅ Frame extraction başarılı!")
        print(f"🔄 Sonraki adım: YOLOv8x ile otomatik etiketleme")
        print(f"   python scripts/auto_label_all.py")
    else:
        print("❌ Frame extraction başarısız!")
        return False
    
    return True

if __name__ == "__main__":
    main()
