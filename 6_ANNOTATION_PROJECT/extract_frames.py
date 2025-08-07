#!/usr/bin/env python3
"""
🎬 FRAME EXTRACTION FOR ANNOTATION
===================================
KAMERA 2 videosundan annotation için frame çıkarma
"""

import cv2
import os
import sys
from datetime import datetime

def extract_frames_for_annotation(video_path, output_dir, interval=2, max_frames=None):
    """
    Video'dan annotation için frame çıkar
    
    Args:
        video_path: Video dosyası yolu
        output_dir: Çıktı klasörü
        interval: Saniye cinsinden aralık (default: 3 saniye)
        max_frames: Maksimum çıkarılacak frame sayısı
    """
    
    print(f"🎬 Video açılıyor: {video_path}")
    
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
    
    # Frame aralığını hesapla
    frame_step = int(fps * interval)
    print(f"⏱️  Her {interval} saniyede bir frame ({frame_step} frame atlayarak)")
    
    # Çıktı klasörünü oluştur
    os.makedirs(output_dir, exist_ok=True)
    
    extracted_frames = []
    frame_count = 0
    
    # Frame çıkarma döngüsü
    max_frame_limit = max_frames * frame_step if max_frames else total_frames
    for frame_idx in range(0, min(total_frames, max_frame_limit), frame_step):
        if max_frames and frame_count >= max_frames:
            break
            
        # Frame pozisyonunu ayarla
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if not ret:
            print(f"⚠️  Frame {frame_idx} okunamadı, geçiliyor...")
            continue
        
        # Frame dosya adı
        timestamp = frame_idx / fps
        frame_filename = f"frame_{frame_count+1:03d}_{timestamp:.1f}s.jpg"
        frame_path = os.path.join(output_dir, frame_filename)
        
        # Frame'i kaydet
        cv2.imwrite(frame_path, frame)
        extracted_frames.append(frame_path)
        frame_count += 1
        
        print(f"✅ Frame {frame_count}/{max_frames}: {frame_filename} ({timestamp:.1f}s)")
    
    cap.release()
    
    print(f"\n🎉 Frame çıkarma tamamlandı!")
    print(f"   Toplam çıkarılan: {len(extracted_frames)} frame")
    print(f"   Çıktı klasörü: {output_dir}")
    
    return extracted_frames

def main():
    """Ana fonksiyon"""
    import sys
    
    # Komut satırından parametreleri al
    if len(sys.argv) < 3:
        print("❌ Kullanım: python extract_frames.py [video_path] [output_dir]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("🎯 Annotation Frame Extraction Başlıyor...")
    print("=" * 50)
    
    # Frame çıkarma (tüm video)
    extracted_frames = extract_frames_for_annotation(
        video_path=video_path,
        output_dir=output_dir,
        interval=2,      # 2 saniyede bir
        max_frames=None  # Tüm video
    )
    
    if extracted_frames:
        print(f"\n📋 Çıkarılan Frameler:")
        for i, frame_path in enumerate(extracted_frames[:5], 1):
            print(f"   {i}. {os.path.basename(frame_path)}")
        
        if len(extracted_frames) > 5:
            print(f"   ... ve {len(extracted_frames) - 5} frame daha")
        
        print(f"\n🚀 Sonraki adım: LabelImg ile annotation")
        print(f"   Klasör: ANNOTATION_PROJECT/01_frames/")
    else:
        print("❌ Frame çıkarma başarısız!")

if __name__ == "__main__":
    main() 