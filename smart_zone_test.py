#!/usr/bin/env python3
"""
🏊 AKILLI ZONE TESTİ
===================
Havuz içi/dışı farklı hassasiyet ile test
"""

import cv2
import os
import time
import json
import numpy as np
from ultralytics import YOLO
from datetime import datetime

class SmartZoneTracker:
    def __init__(self):
        self.pool_polygon = None
        
    def load_or_create_pool_area(self, video_path):
        """Havuz alanını yükle veya oluştur"""
        video_name = os.path.basename(video_path)
        
        # Mevcut havuz alanı dosyalarını ara
        pool_files = []
        if os.path.exists("3_OUTPUT"):
            for file in os.listdir("3_OUTPUT"):
                if file.startswith("pool_area_") and file.endswith(".json"):
                    if "KAMERA_1" in file or "KAMERA 1" in file:
                        pool_files.append(file)
        
        if pool_files:
            # En son dosyayı kullan
            pool_files.sort(reverse=True)
            pool_file = os.path.join("3_OUTPUT", pool_files[0])
            print(f"📄 Mevcut havuz alanı bulundu: {pool_files[0]}")
            
            try:
                with open(pool_file, 'r') as f:
                    pool_data = json.load(f)
                self.pool_polygon = np.array(pool_data['polygon_points'], dtype=np.int32)
                print(f"✅ Havuz alanı yüklendi: {len(self.pool_polygon)} nokta")
                return True
            except:
                print("❌ Havuz alanı dosyası okunamadı")
        
        # Yeni havuz alanı oluştur
        print("🖱️ Yeni havuz alanı oluşturuluyor...")
        return self.create_pool_area(video_path)
    
    def create_pool_area(self, video_path):
        """Havuz alanını interaktif olarak oluştur"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Video açılamadı!")
            return False
        
        # 5. saniyedeki frame'i al
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(5 * fps))
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("❌ Frame okunamadı!")
            return False
        
        # Büyük ekran için resize
        height, width = frame.shape[:2]
        if width > 1920:
            scale = 1920 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
        
        points = []
        window_name = "🏊 HAVUZ ALANI BELİRLE - Sol tık: Nokta, Sağ tık: Sil, C: Tamamla, ESC: İptal"
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal points, frame
            
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                print(f"✅ Nokta {len(points)}: ({x}, {y})")
                self.draw_pool_area(frame.copy(), points)
                
            elif event == cv2.EVENT_RBUTTONDOWN and points:
                removed = points.pop()
                print(f"❌ Nokta silindi: {removed}")
                self.draw_pool_area(frame.copy(), points)
        
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, mouse_callback)
        
        # İlk görüntüyü göster
        self.draw_pool_area(frame.copy(), points)
        
        print("\n🖱️ HAREKETLERİ:")
        print("   - Sol tık: Havuz köşesi ekle")
        print("   - Sağ tık: Son noktayı sil")
        print("   - C tuşu: Tamamla")
        print("   - ESC: İptal")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                print("⏹️ İptal edildi")
                cv2.destroyAllWindows()
                return False
            
            elif key == ord('c') or key == ord('C'):
                if len(points) >= 3:
                    print("✅ Havuz alanı tanımlandı!")
                    cv2.destroyAllWindows()
                    
                    # Orijinal boyuta geri çevir
                    if width > 1920:
                        scale_back = width / 1920
                        points = [(int(x * scale_back), int(y * scale_back)) for x, y in points]
                    
                    self.pool_polygon = np.array(points, dtype=np.int32)
                    self.save_pool_area(video_path, points)
                    return True
                else:
                    print("⚠️ En az 3 nokta gerekli!")
        
        cv2.destroyAllWindows()
        return False
    
    def draw_pool_area(self, frame, points):
        """Havuz alanını çiz ve göster"""
        if not points:
            cv2.imshow("🏊 HAVUZ ALANI BELİRLE - Sol tık: Nokta, Sağ tık: Sil, C: Tamamla, ESC: İptal", frame)
            return
        
        # Noktaları çiz
        for i, point in enumerate(points):
            cv2.circle(frame, point, 8, (0, 255, 0), -1)
            cv2.putText(frame, str(i+1), (point[0]+15, point[1]+15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Çizgileri çiz
        if len(points) > 1:
            for i in range(len(points)-1):
                cv2.line(frame, points[i], points[i+1], (0, 0, 255), 3)
        
        # İlk ve son noktayı bağla
        if len(points) > 2:
            cv2.line(frame, points[-1], points[0], (0, 0, 255), 3)
            
            # Yarı saydam dolgu
            overlay = frame.copy()
            cv2.fillPoly(overlay, [np.array(points)], (0, 255, 255))
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Bilgi
        info = f"Nokta sayısı: {len(points)}"
        if len(points) >= 3:
            info += " - 'C' ile tamamla"
        
        cv2.putText(frame, info, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.imshow("🏊 HAVUZ ALANI BELİRLE - Sol tık: Nokta, Sağ tık: Sil, C: Tamamla, ESC: İptal", frame)
    
    def save_pool_area(self, video_path, points):
        """Havuz alanını kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = os.path.basename(video_path).replace('.mp4', '').replace('.MOV', '').replace(' ', '_')
        filename = f"pool_area_{video_name}_{timestamp}.json"
        filepath = os.path.join("3_OUTPUT", filename)
        
        pool_data = {
            'video_name': os.path.basename(video_path),
            'timestamp': timestamp,
            'polygon_points': points,
            'point_count': len(points)
        }
        
        os.makedirs("3_OUTPUT", exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pool_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Havuz alanı kaydedildi: {filename}")
    
    def is_point_in_pool(self, x, y):
        """Nokta havuz içinde mi?"""
        if self.pool_polygon is None:
            return False
        result = cv2.pointPolygonTest(self.pool_polygon, (x, y), False)
        return result >= 0
    
    def smart_zone_test(self, video_path, model_path, duration_seconds=120):
        """Akıllı zone test"""
        print(f"\n🏊 AKILLI ZONE TEST BAŞLIYOR")
        print(f"📹 Video: {video_path}")
        print(f"🤖 Model: {model_path}")
        print(f"⏱️ Süre: {duration_seconds} saniye")
        
        # Model yükle
        try:
            model = YOLO(model_path)
            print("✅ Model yüklendi")
        except Exception as e:
            print(f"❌ Model yüklenemedi: {e}")
            return
        
        # Video aç
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Video açılamadı!")
            return
        
        # Video özellikleri
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Çıktı video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"3_OUTPUT/SMART_ZONE_TEST_{timestamp}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Sayaçlar
        start_time = time.time()
        frame_count = 0
        pool_detections = 0
        outside_detections = 0
        
        print(f"\n🚀 Test başladı...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            elapsed = time.time() - start_time
            if elapsed >= duration_seconds:
                break
            
            frame_count += 1
            
            # Havuz alanını çiz
            if self.pool_polygon is not None:
                cv2.polylines(frame, [self.pool_polygon], True, (0, 255, 255), 3)
                overlay = frame.copy()
                cv2.fillPoly(overlay, [self.pool_polygon], (0, 255, 255))
                cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
            
            # HAVUZ İÇİ TESPİT (Yüksek hassasiyet)
            pool_results = model(frame, conf=0.15, classes=[0], verbose=False)
            
            # HAVUZ DIŞI TESPİT (Düşük hassasiyet)  
            outside_results = model(frame, conf=0.5, classes=[0], verbose=False)
            
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
                            # Yeşil kutu (havuz içi)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                            cv2.putText(frame, f"POOL {conf:.2f}", (x1, y1-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
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
                            # Mavi kutu (havuz dışı)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                            cv2.putText(frame, f"OUT {conf:.2f}", (x1, y1-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            # Bilgi paneli
            progress = (elapsed / duration_seconds) * 100
            cv2.rectangle(frame, (10, 10), (600, 120), (0, 0, 0), -1)
            cv2.putText(frame, f"SMART ZONE TEST | Kare: {frame_count} | %{progress:.1f}", 
                       (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Havuz Ici: {frame_pool_count} (conf>0.15) | Toplam: {pool_detections}", 
                       (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Havuz Disi: {frame_outside_count} (conf>0.5) | Toplam: {outside_detections}", 
                       (15, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame, f"Süre: {elapsed:.1f}s / {duration_seconds}s", 
                       (15, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            out.write(frame)
            
            # İlerleme
            if frame_count % 60 == 0:  # Her 2 saniyede
                print(f"   ⏱️ {elapsed:.1f}s - Havuz İçi: {pool_detections}, Dışı: {outside_detections}")
        
        cap.release()
        out.release()
        
        # Sonuçlar
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time
        
        print(f"\n✅ SMART ZONE TEST TAMAMLANDI!")
        print(f"   ⏱️ Süre: {total_time:.1f} saniye")
        print(f"   🎬 Kare: {frame_count}")
        print(f"   🏊 Havuz İçi Tespit: {pool_detections} (conf>0.15)")
        print(f"   🚶 Havuz Dışı Tespit: {outside_detections} (conf>0.5)")
        print(f"   🚀 FPS: {avg_fps:.1f}")
        print(f"   💾 Video: {output_path}")

def main():
    tracker = SmartZoneTracker()
    
    # Video ve model yolları
    video_path = "0_DATA/KAMERA 1.mp4"
    model_path = "drowning_detection_v12_working.pt"
    
    print("🏊 SMART ZONE TRACKER")
    print("=" * 50)
    
    # Havuz alanını yükle veya oluştur
    if tracker.load_or_create_pool_area(video_path):
        # Test başlat
        tracker.smart_zone_test(video_path, model_path, duration_seconds=120)
    else:
        print("❌ Havuz alanı oluşturulamadı!")

if __name__ == "__main__":
    main()
