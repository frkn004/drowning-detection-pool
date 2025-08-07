#!/usr/bin/env python3

"""
🧪 VIDEO + KİŞİ TESPİTİ TESTİ
=============================
Video dosyaları üzerinde kişi tespiti yapar.
"""

import cv2
import sys
import os
import time
from datetime import datetime

# Modülleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Paths, System, Camera
from modules.video_processor import VideoProcessor
from modules.person_detector import PersonDetector

def test_video_person_detection(video_path, max_duration=30):
    """
    Video üzerinde kişi tespiti testi
    
    Args:
        video_path (str): Video dosyası yolu
        max_duration (int): Maksimum test süresi (saniye)
    """
    print(f"🧪 Video Kişi Tespiti: {os.path.basename(video_path)}")
    print("-" * 50)
    
    # Video processor'ı başlat
    video_proc = VideoProcessor()
    if not video_proc.load_video(video_path):
        return False
    
    # Person detector'ı başlat
    person_detector = PersonDetector()
    if not person_detector.load_model():
        video_proc.close()
        return False
    
    # Output video oluştur
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(Paths.OUTPUT_DIR, f"{video_name}_detection_{timestamp}.mp4")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, video_proc.fps, 
                         (video_proc.width, video_proc.height))
    
    print(f"💾 Çıktı video: {output_path}")
    print(f"🎬 İşleme başlıyor... (maksimum {max_duration} saniye)")
    
    # İşleme döngüsü
    start_time = time.time()
    frame_count = 0
    total_detections = 0
    processing_times = []
    
    try:
        while True:
            # Kare al
            ret, frame = video_proc.get_frame()
            if not ret:
                print("📹 Video sonu")
                break
            
            frame_count += 1
            frame_start = time.time()
            
            # Kişi tespiti yap
            detections = person_detector.detect_persons(frame)
            total_detections += len(detections)
            
            # Tespitleri çiz
            frame = person_detector.draw_detections(frame, detections)
            
            # İlerleme bilgisi ekle
            progress = video_proc.get_progress()
            elapsed = time.time() - start_time
            
            info_text = f"Kare: {frame_count} | Tespit: {len(detections)} | " \
                       f"Toplam: {total_detections} | {progress['percent']:.1f}%"
            cv2.putText(frame, info_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # FPS bilgisi
            fps_text = f"FPS: {frame_count/elapsed:.1f}"
            cv2.putText(frame, fps_text, (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Video'ya yaz
            out.write(frame)
            
            # Performans takibi
            frame_time = time.time() - frame_start
            processing_times.append(frame_time)
            
            # Her 100 karede bilgi ver
            if frame_count % 100 == 0:
                avg_fps = frame_count / elapsed
                avg_detection_time = sum(processing_times[-100:]) / len(processing_times[-100:])
                print(f"   📊 {frame_count} kare | {avg_fps:.1f} FPS | "
                      f"Tespit/kare: {avg_detection_time:.3f}s | "
                      f"Toplam tespit: {total_detections}")
            
            # Süre kontrolü
            if elapsed >= max_duration:
                print(f"⏰ {max_duration} saniye doldu, test sonlandırılıyor...")
                break
    
    except KeyboardInterrupt:
        print("⏹️  Test kullanıcı tarafından durduruldu")
    
    finally:
        video_proc.close()
        out.release()
        
    # Sonuçları hesapla
    elapsed_total = time.time() - start_time
    avg_fps = frame_count / elapsed_total if elapsed_total > 0 else 0
    avg_detections_per_frame = total_detections / frame_count if frame_count > 0 else 0
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    print("\n📊 TEST SONUÇLARI:")
    print(f"   🎬 İşlenen kare: {frame_count}")
    print(f"   ⏱️  Toplam süre: {elapsed_total:.2f} saniye")
    print(f"   🚀 Ortalama FPS: {avg_fps:.2f}")
    print(f"   👥 Toplam tespit: {total_detections}")
    print(f"   📈 Kare başına tespit: {avg_detections_per_frame:.2f}")
    print(f"   ⚡ Ortalama işleme süresi: {avg_processing_time:.3f}s/kare")
    print(f"   💾 Çıktı: {output_path}")
    
    return True

def run_all_video_tests():
    """Tüm test videolarında kişi tespiti yap"""
    print("="*60)
    print("🧪 VIDEO + KİŞİ TESPİTİ TOPLU TEST")
    print("="*60)
    
    # Test videolarını kontrol et
    test_videos = Camera.TEST_VIDEOS
    
    successful_tests = 0
    
    for i, video_path in enumerate(test_videos, 1):
        print(f"\n🎬 TEST {i}/{len(test_videos)}")
        
        if not os.path.exists(video_path):
            print(f"⚠️  Video bulunamadı: {video_path}")
            continue
        
        if test_video_person_detection(video_path, max_duration=20):
            successful_tests += 1
    
    print("\n" + "="*60)
    print(f"🎉 {successful_tests}/{len(test_videos)} test başarılı!")
    print(f"📁 Tüm çıktılar: {Paths.OUTPUT_DIR}")

if __name__ == "__main__":
    run_all_video_tests()
