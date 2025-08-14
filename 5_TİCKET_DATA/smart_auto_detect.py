#!/usr/bin/env python3
"""
🤖 AKILLI OTOMATIK TESPİT SİSTEMİ
=================================
YOLOv8x + Havuz Koordinatları ile akıllı annotation
"""

import cv2
import os
import json
import numpy as np
from pathlib import Path
from ultralytics import YOLO

class SmartAutoDetect:
    def __init__(self, frames_dir="01_frames", labels_dir="02_labels", pool_area_file="pool_area.json"):
        self.frames_dir = frames_dir
        self.labels_dir = labels_dir
        self.pool_area_file = pool_area_file
        
        # Havuz koordinatlarını yükle
        self.pool_polygon = self.load_pool_area()
        
        # Model yükle (YOLOv8x)
        print("🤖 YOLOv8x model yükleniyor...")
        self.model = YOLO("../4_MODELS/yolov8x.pt")
        print("✅ Model yüklendi!")
    
    def load_pool_area(self):
        """Havuz alanı koordinatlarını yükle"""
        try:
            with open(self.pool_area_file, 'r') as f:
                pool_data = json.load(f)
            
            polygon = np.array(pool_data['polygon_points'], dtype=np.int32)
            print(f"✅ Havuz alanı yüklendi: {len(polygon)} nokta")
            return polygon
            
        except Exception as e:
            print(f"❌ Havuz alanı yüklenemedi: {e}")
            return None
    
    def point_in_polygon(self, point, polygon):
        """Nokta polygon içinde mi kontrol et"""
        if polygon is None:
            return True
            
        x, y = point
        return cv2.pointPolygonTest(polygon, (float(x), float(y)), False) >= 0
    
    def get_unannotated_frames(self):
        """Annotation'sız frame'leri bul"""
        frame_files = list(Path(self.frames_dir).glob("*.jpg"))
        frame_files.sort()
        
        unannotated = []
        
        for frame_file in frame_files:
            label_file = Path(self.labels_dir) / f"{frame_file.stem}.txt"
            
            if not label_file.exists() or label_file.stat().st_size == 0:
                unannotated.append(frame_file)
        
        print(f"📊 Annotation analizi:")
        print(f"   📁 Toplam frame: {len(frame_files)}")
        print(f"   🔍 Annotation'sız: {len(unannotated)}")
        print(f"   ✅ Annotation'lı: {len(frame_files) - len(unannotated)}")
        
        return unannotated
    
    def detect_and_classify(self, frame_path):
        """Frame'de tespit yap ve sınıflandır"""
        results = self.model(str(frame_path), conf=0.4, verbose=False)
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    if class_id == 0 and confidence > 0.4:
                        x_center, y_center, width, height = box.xywhn[0]
                        
                        img = cv2.imread(str(frame_path))
                        img_h, img_w = img.shape[:2]
                        
                        real_x = int(x_center * img_w)
                        real_y = int(y_center * img_h)
                        
                        if self.point_in_polygon((real_x, real_y), self.pool_polygon):
                            yolo_class = 0  # person_swimming
                            class_name = "swimming"
                        else:
                            yolo_class = 2  # person_poolside
                            class_name = "poolside"
                        
                        detection_line = f"{yolo_class} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                        detections.append({
                            'line': detection_line,
                            'class': class_name,
                            'confidence': confidence
                        })
        
        return detections
    
    def process_unannotated_frames(self):
        """Annotation'sız frame'leri işle"""
        unannotated_frames = self.get_unannotated_frames()
        
        if not unannotated_frames:
            print("✅ Tüm frame'ler zaten annotation'lı!")
            return
        
        print(f"\n🎯 {len(unannotated_frames)} frame işlenecek...")
        
        total_detections = 0
        swimming_count = 0
        poolside_count = 0
        
        for i, frame_path in enumerate(unannotated_frames, 1):
            print(f"🔍 İşleniyor {i}/{len(unannotated_frames)}: {frame_path.name}")
            
            detections = self.detect_and_classify(frame_path)
            
            label_file = Path(self.labels_dir) / f"{frame_path.stem}.txt"
            
            detection_lines = []
            frame_swimming = 0
            frame_poolside = 0
            
            for detection in detections:
                detection_lines.append(detection['line'])
                if detection['class'] == 'swimming':
                    frame_swimming += 1
                    swimming_count += 1
                else:
                    frame_poolside += 1
                    poolside_count += 1
            
            with open(label_file, 'w') as f:
                f.write('\n'.join(detection_lines))
            
            total_detections += len(detections)
            
            if detections:
                print(f"   ✅ {len(detections)} kişi: {frame_swimming} swimming, {frame_poolside} poolside")
            else:
                print(f"   ⚠️  Kişi tespit edilmedi")
            
            if i % 50 == 0:
                print(f"   📊 İlerleme: {i}/{len(unannotated_frames)} - Toplam tespit: {total_detections}")
        
        print(f"\n🎉 OTOMATIK TESPİT TAMAMLANDI!")
        print(f"   📊 Toplam tespit: {total_detections}")
        print(f"   🏊 Havuz içi: {swimming_count}")
        print(f"   🚶 Havuz dışı: {poolside_count}")
        print(f"   ✅ {len(unannotated_frames)} frame otomatik etiketlendi")
        
        return True

def main():
    print("🚀 AKILLI OTOMATIK TESPİT BAŞLIYOR!")
    print("="*50)
    
    detector = SmartAutoDetect()
    detector.process_unannotated_frames()
    
    print(f"\n🔧 SONRAKI ADIM:")
    print(f"   🖼️  Advanced Editor ile fine-tuning yap")

if __name__ == "__main__":
    main()
