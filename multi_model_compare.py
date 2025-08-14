#!/usr/bin/env python3
"""
🏆 3 MODEL KARŞILAŞTIRMA TESTİ
=============================
YENİ vs 8x vs best.pt karşılaştırması
"""

import cv2
import os
import time
import json
import numpy as np
from ultralytics import YOLO
from datetime import datetime

class MultiModelCompare:
    def __init__(self):
        self.pool_polygon = None
        
    def load_pool_area(self, video_path):
        """KAMERA 1 havuz alanını yükle"""
        pool_files = []
        if os.path.exists("3_OUTPUT"):
            for file in os.listdir("3_OUTPUT"):
                if file.startswith("pool_area_") and file.endswith(".json"):
                    if "KAMERA_1" in file or "KAMERA 1" in file:
                        pool_files.append(file)
        
        if pool_files:
            pool_files.sort(reverse=True)
            pool_file = os.path.join("3_OUTPUT", pool_files[0])
            print(f"📄 Havuz alanı: {pool_files[0]}")
            
            try:
                with open(pool_file, 'r') as f:
                    pool_data = json.load(f)
                self.pool_polygon = np.array(pool_data['polygon_points'], dtype=np.int32)
                print(f"✅ Havuz alanı yüklendi: {len(self.pool_polygon)} nokta")
                return True
            except:
                print("❌ Havuz alanı okunamadı")
        
        print("❌ KAMERA 1 havuz alanı bulunamadı!")
        return False
    
    def is_point_in_pool(self, x, y):
        """Nokta havuz içinde mi?"""
        if self.pool_polygon is None:
            return False
        result = cv2.pointPolygonTest(self.pool_polygon, (x, y), False)
        return result >= 0
    
    def test_single_model(self, video_path, model_path, model_name, duration_seconds=120):
        """Tek model testi"""
        print(f"\n🤖 {model_name} TEST BAŞLIYOR...")
        
        # Model yükle
        try:
            model = YOLO(model_path)
            print(f"✅ {model_name} yüklendi")
        except Exception as e:
            print(f"❌ {model_name} yüklenemedi: {e}")
            return None
        
        # Video aç
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Video açılamadı!")
            return None
        
        # Video özellikleri
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Çıktı video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"3_OUTPUT/COMPARE_{model_name}_{timestamp}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Sayaçlar
        start_time = time.time()
        frame_count = 0
        pool_detections = 0
        outside_detections = 0
        
        print(f"⏰ {duration_seconds} saniye test...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            elapsed = time.time() - start_time
            if elapsed >= duration_seconds:
                break
            
            frame_count += 1
            
            # Havuz alanını çiz - PARLAK SARI
            if self.pool_polygon is not None:
                cv2.polylines(frame, [self.pool_polygon], True, (0, 255, 255), 4)  # Kalın sarı çizgi
                overlay = frame.copy()
                cv2.fillPoly(overlay, [self.pool_polygon], (0, 255, 255))  # Sarı dolgu
                cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)  # %25 şeffaflık
            
            # HAVUZ İÇİ TESPİT (Çok düşük threshold)
            # YENİ_MODEL için tüm insan sınıfları (0,1,2), diğerleri için sadece 0
            if "drowning_detection" in model_path:
                pool_results = model(frame, conf=0.01, classes=[0,1,2], verbose=False)  # person_swimming, drowning, poolside
            else:
                pool_results = model(frame, conf=0.01, classes=[0], verbose=False)  # person
            
            # HAVUZ DIŞI TESPİT (Normal threshold)  
            if "drowning_detection" in model_path:
                outside_results = model(frame, conf=0.01, classes=[0,1,2], verbose=False)  # person_swimming, drowning, poolside
            else:
                outside_results = model(frame, conf=0.01, classes=[0], verbose=False)  # person
            
            # Havuz içi tespitleri işle
            frame_pool_count = 0
            for r in pool_results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        conf = float(box.conf.item())
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        
                        if self.is_point_in_pool(center_x, center_y):
                            frame_pool_count += 1
                            pool_detections += 1
                            # PARLAK YEŞİL kutu (havuz içi)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)  # Kalın yeşil
                            cv2.putText(frame, f"POOL {conf:.2f}", (x1, y1-15), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 3)  # Kalın yazı
                            # Merkez noktası
                            cv2.circle(frame, (center_x, center_y), 6, (0, 255, 0), -1)
            
            # Havuz dışı tespitleri işle
            frame_outside_count = 0
            for r in outside_results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        conf = float(box.conf.item())
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        
                        if not self.is_point_in_pool(center_x, center_y):
                            frame_outside_count += 1
                            outside_detections += 1
                            # PARLAK KIRMIZI kutu (havuz dışı)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Kırmızı
                            cv2.putText(frame, f"OUT {conf:.2f}", (x1, y1-15), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.circle(frame, (center_x, center_y), 4, (0, 0, 255), -1)
            
            # BÜYÜK BİLGİ PANELİ - SİYAH ARKA PLAN
            progress = (elapsed / duration_seconds) * 100
            cv2.rectangle(frame, (10, 10), (700, 140), (0, 0, 0), -1)  # Siyah arka plan
            cv2.rectangle(frame, (10, 10), (700, 140), (255, 255, 255), 3)  # Beyaz çerçeve
            
            # Model adı - BÜYÜK
            cv2.putText(frame, f"MODEL: {model_name}", 
                       (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            
            # Anlık sayaçlar - RENKLI
            cv2.putText(frame, f"Havuz Ici: {frame_pool_count} (conf>0.01)", 
                       (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Havuz Disi: {frame_outside_count} (conf>0.01)", 
                       (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # İlerleme çubuğu
            cv2.putText(frame, f"Süre: {elapsed:.1f}s / {duration_seconds}s (%{progress:.0f})", 
                       (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            out.write(frame)
            
            # İlerleme
            if frame_count % 20 == 0:  # Her saniyede
                print(f"   ⏱️ {elapsed:.1f}s - Havuz: {pool_detections}, Dış: {outside_detections}")
        
        cap.release()
        out.release()
        
        # Sonuçlar
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time
        
        result = {
            'model_name': model_name,
            'duration': total_time,
            'frames': frame_count,
            'fps': avg_fps,
            'pool_detections': pool_detections,
            'outside_detections': outside_detections,
            'total_detections': pool_detections + outside_detections,
            'video_path': output_path
        }
        
        print(f"✅ {model_name} TAMAMLANDI!")
        print(f"   🎬 Kare: {frame_count}")
        print(f"   🏊 Havuz: {pool_detections}")
        print(f"   🚶 Dış: {outside_detections}")
        print(f"   🚀 FPS: {avg_fps:.1f}")
        print(f"   💾 Video: {os.path.basename(output_path)}")
        
        return result
    
    def compare_all_models(self, video_path, duration=120):
        """3 modeli karşılaştır"""
        models = [
            ("drowning_detection_v12_working.pt", "YENİ_MODEL"),
            ("4_MODELS/yolov8x.pt", "YOLO8X"),
            ("3_OUTPUT/VAST_BACKUP_20250809_231454/best.pt", "BEST_PT")
        ]
        
        print("🏆 3 MODEL KARŞILAŞTIRMA TESTİ")
        print("=" * 60)
        print(f"📹 Video: {video_path}")
        print(f"⏰ Test süresi: {duration} saniye")
        print(f"🏊 Havuz içi conf: >0.01 (ÇOK DÜŞÜK)")
        print(f"🚶 Havuz dışı conf: >0.01 (ÇOK DÜŞÜK)")
        print()
        
        results = []
        
        for model_path, model_name in models:
            if os.path.exists(model_path):
                result = self.test_single_model(video_path, model_path, model_name, duration)
                if result:
                    results.append(result)
            else:
                print(f"❌ Model bulunamadı: {model_path}")
        
        # KARŞILAŞTIRMA TABLOSU
        if results:
            print(f"\n🏆 KARŞILAŞTIRMA SONUÇLARI:")
            print("=" * 80)
            print(f"{'Model':<12} {'Havuz':<8} {'Dış':<8} {'Toplam':<8} {'FPS':<6} {'Video'}")
            print("-" * 80)
            
            for r in results:
                print(f"{r['model_name']:<12} {r['pool_detections']:<8} "
                      f"{r['outside_detections']:<8} {r['total_detections']:<8} "
                      f"{r['fps']:<6.1f} {os.path.basename(r['video_path'])}")
            
            # EN İYİ SONUÇLAR
            best_pool = max(results, key=lambda x: x['pool_detections'])
            best_total = max(results, key=lambda x: x['total_detections'])
            best_fps = max(results, key=lambda x: x['fps'])
            
            print(f"\n🥇 EN İYİ SONUÇLAR:")
            print(f"🏊 En çok havuz tespiti: {best_pool['model_name']} ({best_pool['pool_detections']} tespit)")
            print(f"📊 En çok toplam tespit: {best_total['model_name']} ({best_total['total_detections']} tespit)")
            print(f"⚡ En hızlı model: {best_fps['model_name']} ({best_fps['fps']:.1f} FPS)")

def main():
    comparer = MultiModelCompare()
    
    video_path = "0_DATA/KAMERA 1.mp4"
    
    # Havuz alanını yükle
    if comparer.load_pool_area(video_path):
        # 3 model karşılaştırması başlat
        comparer.compare_all_models(video_path, duration=120)
    else:
        print("❌ Havuz alanı yüklenemedi!")

if __name__ == "__main__":
    main()
