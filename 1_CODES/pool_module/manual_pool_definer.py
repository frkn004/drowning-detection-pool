#!/usr/bin/env python3

"""
🎯 MANUEL HAVUZ ALANI BELİRLEME
===============================
Video frame'i ve koordinat bilgisi ile havuz alanı belirle.
"""

import cv2
import os
import sys
import json
from datetime import datetime

# Ana dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Paths, get_project_info

def extract_frame_from_video(video_path, frame_time=10.0):
    """Video'dan belirli bir zamanda kare çıkar"""
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Video açılamadı: {video_path}")
        return None
    
    # Video özellikleri
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"📊 Video: {fps:.1f} FPS, {total_frames} kare")
    
    # Belirtilen zamana git
    frame_number = int(frame_time * fps)
    if frame_number >= total_frames:
        frame_number = total_frames // 2
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Kare okunamadı!")
        return None
    
    print(f"✅ {frame_time:.1f}. saniyedeki kare çıkarıldı")
    return frame

def save_frame_with_grid(frame, output_path):
    """Kareyi grid çizgileri ile kaydet"""
    
    height, width = frame.shape[:2]
    
    # Grid çizgilerini ekle
    grid_frame = frame.copy()
    
    # Dikey çizgiler (her 200 piksel)
    for x in range(0, width, 200):
        cv2.line(grid_frame, (x, 0), (x, height), (255, 255, 255), 1)
        cv2.putText(grid_frame, str(x), (x+5, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Yatay çizgiler (her 150 piksel)  
    for y in range(0, height, 150):
        cv2.line(grid_frame, (0, y), (width, y), (255, 255, 255), 1)
        cv2.putText(grid_frame, str(y), (5, y-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Video bilgilerini ekle
    cv2.putText(grid_frame, f"Video boyutu: {width}x{height}", 
               (10, height-60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(grid_frame, "Havuz koselerinin koordinatlarini not alin", 
               (10, height-30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    cv2.imwrite(output_path, grid_frame)
    print(f"📸 Grid'li kare kaydedildi: {output_path}")
    
    return grid_frame

def create_pool_area_manually():
    """Manuel havuz alanı oluştur"""
    
    info = get_project_info()
    
    # KAMERA 2 videosunu bul
    kamera2_video = None
    for video in info['videos']:
        if 'KAMERA 2' in video:
            kamera2_video = video
            break
    
    if not kamera2_video:
        print("❌ KAMERA 2 videosu bulunamadı!")
        return None
    
    print(f"🎬 Video: {os.path.basename(kamera2_video)}")
    
    # Video'dan kare çıkar
    frame = extract_frame_from_video(kamera2_video, frame_time=10.0)
    if frame is None:
        return None
    
    # Grid'li kareyi kaydet
    output_frame_path = os.path.join(Paths.OUTPUT_DIR, "kamera2_grid_frame.jpg")
    save_frame_with_grid(frame, output_frame_path)
    
    height, width = frame.shape[:2]
    
    print(f"\n📏 Video Boyutları: {width}x{height}")
    print(f"📸 Grid'li kare: {output_frame_path}")
    print(f"🔍 Bu dosyayı açıp havuz köşe koordinatlarını belirleyin!")
    print(f"\n📋 Koordinat Rehberi:")
    print(f"   �� Video 2304x1296 piksel")
    print(f"   📍 Sol üst: (0, 0)")
    print(f"   📍 Sağ alt: (2304, 1296)")
    print(f"   📏 Grid çizgileri 200x150 piksel aralıklarla")
    
    # Kullanıcıdan koordinat giriş
    points = []
    
    print(f"\n🖱️  Havuz köşe koordinatlarını girin:")
    print(f"   (Her satıra bir koordinat: x,y formatında)")
    print(f"   (Boş satır girince tamamlanır)")
    print(f"   (Örnek: 500,400)")
    
    while True:
        try:
            coord_input = input(f"   {len(points)+1}. nokta (x,y): ").strip()
            
            if not coord_input:  # Boş satır
                if len(points) >= 3:
                    break
                else:
                    print("   ⚠️  En az 3 nokta gerekli!")
                    continue
            
            # Koordinatları parse et
            if ',' in coord_input:
                x, y = map(int, coord_input.split(','))
            else:
                print(f"   ❌ Virgül ile ayırın! Örnek: 500,300")
                continue
            
            if 0 <= x <= width and 0 <= y <= height:
                points.append([x, y])
                print(f"   ✅ Eklendi: ({x}, {y})")
            else:
                print(f"   ❌ Geçersiz koordinat! 0-{width} ve 0-{height} arası olmalı!")
                
        except ValueError:
            print(f"   ❌ Geçersiz format! Örnek: 500,300")
        except KeyboardInterrupt:
            print(f"\n❌ İptal edildi!")
            return None
    
    if len(points) < 3:
        print("❌ En az 3 nokta gerekli!")
        return None
    
    # JSON dosyasına kaydet
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pool_data = {
        'video_name': os.path.basename(kamera2_video),
        'timestamp': timestamp,
        'polygon_points': points,
        'point_count': len(points)
    }
    
    pool_filename = f"pool_area_KAMERA2_MANUAL_{timestamp}.json"
    pool_filepath = os.path.join(Paths.OUTPUT_DIR, pool_filename)
    
    with open(pool_filepath, 'w', encoding='utf-8') as f:
        json.dump(pool_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Havuz alanı kaydedildi!")
    print(f"📁 Dosya: {pool_filename}")
    print(f"🔢 Nokta sayısı: {len(points)}")
    print(f"\n📋 Koordinatlar:")
    for i, (x, y) in enumerate(points, 1):
        print(f"   {i}. ({x}, {y})")
    
    return pool_filepath

if __name__ == "__main__":
    create_pool_area_manually()
