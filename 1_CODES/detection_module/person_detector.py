#!/usr/bin/env python3

"""
👥 KİŞİ TESPİT MODÜLÜ
====================
YOLO modeli ile kişi tespiti yapar.
"""

import cv2
import sys
import os
import time
import torch
import numpy as np
from datetime import datetime

# Config'i import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Paths, System

class PersonDetector:
    """
    🤖 YOLO tabanlı kişi tespiti sınıfı
    """
    
    def __init__(self):
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.confidence = 0.3
        self.iou_threshold = 0.3
        self.initialized = False
        
        print(f"🤖 PersonDetector başlatılıyor...")
        print(f"🖥️  Cihaz: {self.device}")
    
    def load_model(self, model_name="yolov8m.pt"):
        """YOLO modelini yükle"""
        try:
            from ultralytics import YOLO
            
            print(f"📦 Model yükleniyor: {model_name}")
            self.model = YOLO(model_name)
            self.model.to(self.device)
            
            # Test tespiti yap
            test_image = np.zeros((640, 640, 3), dtype=np.uint8)
            results = self.model(test_image, verbose=False)
            
            self.initialized = True
            print(f"✅ Model başarıyla yüklendi!")
            return True
            
        except Exception as e:
            print(f"❌ Model yükleme hatası: {e}")
            return False
    
    def detect_persons(self, frame):
        """
        Kare üzerinde kişi tespiti yap
        
        Args:
            frame: Video karesi
            
        Returns:
            list: Tespit listesi [(x1,y1,x2,y2,confidence), ...]
        """
        if not self.initialized:
            print("❌ Model yüklü değil!")
            return []
        
        try:
            # YOLO ile tespit
            results = self.model(
                frame, 
                conf=self.confidence,
                classes=[0],  # Sadece person class (0)
                verbose=False
            )
            
            detections = []
            
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        # Koordinatları al
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        
                        # Minimum alan kontrolü
                        area = (x2 - x1) * (y2 - y1)
                        if area > 500:  # Minimum 500 piksel
                            detections.append((
                                int(x1), int(y1), int(x2), int(y2), float(conf)
                            ))
            
            return detections
            
        except Exception as e:
            print(f"❌ Tespit hatası: {e}")
            return []
    
    def draw_detections(self, frame, detections):
        """
        Tespitleri kare üzerine çiz
        
        Args:
            frame: Video karesi
            detections: Tespit listesi
            
        Returns:
            frame: İşlenmiş kare
        """
        for i, (x1, y1, x2, y2, conf) in enumerate(detections):
            # Yeşil dikdörtgen çiz
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Etiket
            label = f"Person {i+1}: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Toplam tespit sayısı
        info_text = f"Tespit Edilen: {len(detections)} kisi"
        cv2.putText(frame, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame

def test_person_detection():
    """Kişi tespiti testini yap"""
    print("="*50)
    print("🧪 KİŞİ TESPİTİ TESTİ")
    print("="*50)
    
    # Detector'ı başlat
    detector = PersonDetector()
    
    # Model yükle
    if not detector.load_model():
        print("❌ Model yüklenemedi, test durduruluyor!")
        return False
    
    print("-" * 30)
    
    # Kamerayı aç
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Kamera açılamadı!")
        return False
    
    print("🎬 Kişi tespiti başlıyor... (ESC ile çık)")
    
    # Output video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(Paths.OUTPUT_DIR, f"person_detection_{timestamp}.mp4")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Kişi tespiti yap
            detections = detector.detect_persons(frame)
            
            # Tespitleri çiz
            frame = detector.draw_detections(frame, detections)
            
            # FPS bilgisi ekle
            elapsed = time.time() - start_time
            fps_text = f"FPS: {frame_count/elapsed:.1f}"
            cv2.putText(frame, fps_text, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Göster ve kaydet
            cv2.imshow('Person Detection Test', frame)
            out.write(frame)
            
            # ESC ile çık
            if cv2.waitKey(1) & 0xFF == 27:
                break
                
            # 30 saniye sonra otomatik dur
            if elapsed > 30:
                print("⏰ 30 saniye doldu, test sonlandırılıyor...")
                break
    
    except KeyboardInterrupt:
        print("⏹️  Test kullanıcı tarafından durduruldu")
    
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        elapsed = time.time() - start_time
        print(f"✅ Test tamamlandı!")
        print(f"📊 Toplam kare: {frame_count}")
        print(f"⏱️  Süre: {elapsed:.2f} saniye")
        print(f"💾 Video kaydedildi: {output_path}")
    
    return True

if __name__ == "__main__":
    test_person_detection()
