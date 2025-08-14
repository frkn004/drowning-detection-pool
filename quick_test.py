#!/usr/bin/env python3
"""
🧪 HIZLI MODEL TESİ
=================
Yeni eğitilmiş modeli hızlıca test edelim
"""

import cv2
import os
import time
from ultralytics import YOLO
from datetime import datetime

def quick_model_test():
    print("🧪 HIZLI MODEL TEST BAŞLIYOR")
    print("="*50)
    
    # Video ve model yolları
    video_path = "0_DATA/Havuz_S23_Ultra.mp4"  # Test videosu
    new_model = "drowning_detection_v12_working.pt"  # YENİ MODEL (VAST backup)
    old_model = "4_MODELS/yolov8x.pt"  # ESKİ MODEL
    
    # Videoyu kontrol et
    if not os.path.exists(video_path):
        print(f"❌ Video bulunamadı: {video_path}")
        return
    
    if not os.path.exists(new_model):
        print(f"❌ Yeni model bulunamadı: {new_model}")
        return
    
    print(f"📹 Video: {video_path}")
    print(f"🆕 Yeni Model: {new_model}")
    print(f"🔄 Eski Model: {old_model}")
    print()
    
    # Video aç
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Video açılamadı!")
        return
    
    # Video özellikleri
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"📊 Video: {width}x{height} @ {fps:.1f} FPS")
    
    # YENİ MODEL TESİ
    print("\n🆕 YENİ MODEL TESİ BAŞLIYOR...")
    test_model(cap, new_model, "YENİ_MODEL", 60)  # 60 saniye = 2 dakika
    
    # Videoyu başa sar
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # ESKİ MODEL TESİ
    print("\n🔄 ESKİ MODEL TESİ BAŞLIYOR...")
    test_model(cap, old_model, "ESKİ_MODEL", 60)  # 60 saniye = 2 dakika
    
    cap.release()
    print("\n✅ TÜM TESTLER TAMAMLANDI!")

def test_model(cap, model_path, model_name, duration_seconds):
    """Tek model testi"""
    try:
        # Model yükle
        print(f"🤖 Model yükleniyor: {model_path}")
        model = YOLO(model_path)
        
        # Çıktı video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"3_OUTPUT/TEST_{model_name}_{timestamp}.mp4"
        
        # Video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Test başlat
        start_time = time.time()
        frame_count = 0
        detection_count = 0
        
        print(f"⏰ {duration_seconds} saniye test başlatılıyor...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            elapsed = time.time() - start_time
            if elapsed >= duration_seconds:
                break
            
            frame_count += 1
            
            # YOLO tespiti
            results = model(frame, conf=0.3, classes=[0], verbose=False)  # Sadece person
            
            # Tespitleri çiz
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        detection_count += 1
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        conf = float(box.conf.item())
                        
                        # Yeşil kutu çiz
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f"{conf:.2f}", (x1, y1-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Bilgi ekle
            progress = (elapsed / duration_seconds) * 100
            info_text = f"{model_name} | Frame: {frame_count} | Tespit: {len(boxes) if boxes is not None else 0} | %{progress:.1f}"
            cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Kaydet
            out.write(frame)
            
            # İlerleme göster
            if frame_count % 30 == 0:  # Her saniye
                print(f"   ⏱️  {elapsed:.1f}s - {frame_count} kare - {detection_count} tespit")
        
        out.release()
        
        # Sonuçları göster
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time
        
        print(f"✅ {model_name} TEST SONUÇLARI:")
        print(f"   ⏱️  Süre: {total_time:.1f} saniye")
        print(f"   🎬 Kare: {frame_count}")
        print(f"   🎯 Tespit: {detection_count}")
        print(f"   🚀 FPS: {avg_fps:.1f}")
        print(f"   💾 Video: {output_path}")
        print()
        
    except Exception as e:
        print(f"❌ {model_name} test hatası: {e}")

if __name__ == "__main__":
    quick_model_test()
