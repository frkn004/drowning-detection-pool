#!/usr/bin/env python3
"""
🏊 ENTEGRE HAVUZ TAKİP SİSTEMİ
=============================
Havuz alanı + İyileştirilmiş tracking + Adaptive threshold
"""

import cv2
import numpy as np
import json
import os
import time
from datetime import datetime
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from ultralytics import YOLO

@dataclass
class PoolZone:
    """Havuz alanı bilgileri"""
    polygon: np.ndarray
    center: Tuple[int, int]
    area: float
    confidence_threshold: float = 0.15  # Havuz içi daha hassas

@dataclass
class Detection:
    """Gelişmiş detection bilgisi"""
    bbox: Tuple[int, int, int, int]
    center: Tuple[int, int]
    confidence: float
    area: float
    in_pool: bool
    zone_distance: float  # Havuz merkezine uzaklık

class IntegratedPoolTracker:
    """
    🎯 Entegre havuz tracking sistemi
    
    Özellikler:
    1. Adaptive confidence threshold (havuz içi/dışı)
    2. Pool area integration
    3. Zone-based optimization
    4. Advanced tracking algorithm
    5. Real-time performance
    """
    
    def __init__(self, model_path='4_MODELS/yolov8x.pt'):
        """Initialize integrated tracker"""
        
        print("🏊 Integrated Pool Tracker Starting...")
        
        # Model yükle
        self.model = YOLO(model_path)
        print(f"✅ Model loaded: {os.path.basename(model_path)}")
        
        # Pool zones
        self.pool_zones: List[PoolZone] = []
        
        # Tracking parameters
        self.max_track_distance = 80
        self.max_lost_frames = 15
        self.position_history_size = 10
        
        # Adaptive thresholds - ÇOK HASSAS AYARLAR
        self.pool_confidence = 0.05      # Havuz içi - ÇOK HASSAS
        self.outside_confidence = 0.15   # Havuz dışı - HASSAS
        self.water_reflection_threshold = 0.25  # Su yansıması - GEVŞETİLDİ
        
        # Tracking state
        self.tracks = {}
        self.next_track_id = 1
        self.frame_number = 0
        
        # Performance monitoring
        self.fps_tracker = deque(maxlen=30)  # Son 30 frame FPS
        self.detection_counts = deque(maxlen=100)
        
        print("🚀 Integrated Pool Tracker Ready!")
    
    def load_pool_area_from_json(self, json_path: str) -> bool:
        """JSON dosyasından havuz alanı yükle"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                pool_data = json.load(f)
            
            polygon = np.array(pool_data['polygon_points'], dtype=np.int32)
            
            # Pool zone bilgileri hesapla
            center_x = int(np.mean(polygon[:, 0]))
            center_y = int(np.mean(polygon[:, 1]))
            area = cv2.contourArea(polygon)
            
            pool_zone = PoolZone(
                polygon=polygon,
                center=(center_x, center_y),
                area=area,
                confidence_threshold=self.pool_confidence
            )
            
            self.pool_zones = [pool_zone]  # Tek havuz şimdilik
            
            print(f"✅ Pool area loaded: {os.path.basename(json_path)}")
            print(f"📐 Pool center: {pool_zone.center}")
            print(f"📏 Pool area: {area:.0f} pixels")
            
            return True
            
        except Exception as e:
            print(f"❌ Pool area loading error: {e}")
            return False
    
    def find_pool_json_for_video(self, video_name: str) -> Optional[str]:
        """Video için havuz JSON dosyasını otomatik bul"""
        
        output_dir = "3_OUTPUT"
        if not os.path.exists(output_dir):
            return None
        
        video_base = os.path.splitext(video_name)[0].replace(" ", "_")
        
        # Pool area JSON files ara
        pool_files = []
        for file in os.listdir(output_dir):
            if file.startswith("pool_area_") and file.endswith(".json"):
                if video_base.upper() in file.upper():
                    pool_files.append(os.path.join(output_dir, file))
        
        if pool_files:
            # En son dosyayı seç
            pool_files.sort(reverse=True)
            return pool_files[0]
        
        return None
    
    def get_adaptive_confidence(self, center_x: int, center_y: int) -> float:
        """Adaptive confidence threshold - havuz içi/dışı"""
        
        if not self.pool_zones:
            return self.outside_confidence
        
        pool_zone = self.pool_zones[0]
        
        # Havuz içinde mi kontrol et
        result = cv2.pointPolygonTest(pool_zone.polygon, (center_x, center_y), True)
        
        if result >= 0:  # Havuz içi
            # Havuz merkezine uzaklığa göre ayarla
            distance_to_center = np.sqrt(
                (center_x - pool_zone.center[0])**2 + 
                (center_y - pool_zone.center[1])**2
            )
            
            # Merkeze yakınsa daha hassas
            if distance_to_center < 100:
                return self.pool_confidence * 0.8  # %20 daha hassas
            else:
                return self.pool_confidence
        else:  # Havuz dışı
            return self.outside_confidence
    
    def is_water_reflection_area(self, center_x: int, center_y: int) -> bool:
        """Su yansıması alanında mı kontrol et"""
        
        if not self.pool_zones:
            return False
        
        pool_zone = self.pool_zones[0]
        
        # Havuz merkezine çok yakınsa yansıma olabilir
        distance_to_center = np.sqrt(
            (center_x - pool_zone.center[0])**2 + 
            (center_y - pool_zone.center[1])**2
        )
        
        # Merkeze çok yakın alanlar yansıma riski taşır
        return distance_to_center < 50
    
    def detect_with_adaptive_threshold(self, frame: np.ndarray) -> List[Detection]:
        """Adaptive threshold ile detection"""
        
        # İlk geçiş - düşük threshold ile tüm potansiyel detections
        results = self.model(frame, conf=0.1, classes=[0], verbose=False)
        
        detections = []
        
        if results[0].boxes is not None:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                confidence = float(box.conf.item())
                
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                area = (x2 - x1) * (y2 - y1)
                
                # Adaptive threshold hesapla
                required_confidence = self.get_adaptive_confidence(center_x, center_y)
                
                # Su yansıması kontrolü
                if self.is_water_reflection_area(center_x, center_y):
                    required_confidence = self.water_reflection_threshold
                
                # Confidence check
                if confidence >= required_confidence:
                    # Pool membership
                    in_pool = self.is_point_in_pool(center_x, center_y)
                    
                    # Zone distance
                    zone_distance = 0
                    if self.pool_zones:
                        pool_center = self.pool_zones[0].center
                        zone_distance = np.sqrt(
                            (center_x - pool_center[0])**2 + 
                            (center_y - pool_center[1])**2
                        )
                    
                    detection = Detection(
                        bbox=(x1, y1, x2, y2),
                        center=(center_x, center_y),
                        confidence=confidence,
                        area=area,
                        in_pool=in_pool,
                        zone_distance=zone_distance
                    )
                    
                    detections.append(detection)
        
        self.detection_counts.append(len(detections))
        return detections
    
    def is_point_in_pool(self, x: int, y: int) -> bool:
        """Nokta havuz içinde mi?"""
        if not self.pool_zones:
            return False
        
        result = cv2.pointPolygonTest(self.pool_zones[0].polygon, (x, y), False)
        return result >= 0
    
    def process_video_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Tek frame işle - detection + tracking + visualization"""
        
        frame_start = time.time()
        
        # Detection with adaptive threshold
        detections = self.detect_with_adaptive_threshold(frame)
        
        # Tracking (simplified for demo)
        self.frame_number += 1
        
        # Performance monitoring
        frame_time = time.time() - frame_start
        fps = 1.0 / frame_time if frame_time > 0 else 0
        self.fps_tracker.append(fps)
        
        # Visualization
        vis_frame = self.visualize_frame(frame, detections)
        
        # Statistics
        stats = {
            'frame_number': self.frame_number,
            'detections': len(detections),
            'pool_detections': sum(1 for d in detections if d.in_pool),
            'fps': fps,
            'avg_fps': np.mean(self.fps_tracker) if self.fps_tracker else 0
        }
        
        return vis_frame, stats
    
    def visualize_frame(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """Frame visualization with advanced features"""
        
        vis_frame = frame.copy()
        
        # Pool area çiz
        if self.pool_zones:
            pool_zone = self.pool_zones[0]
            cv2.polylines(vis_frame, [pool_zone.polygon], True, (0, 255, 255), 3)
            
            # Pool center
            cv2.circle(vis_frame, pool_zone.center, 10, (0, 255, 255), -1)
            cv2.putText(vis_frame, "POOL CENTER", 
                       (pool_zone.center[0] + 15, pool_zone.center[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Detections çiz
        pool_count = 0
        outside_count = 0
        
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            
            # Renk seçimi - havuz içi/dışı + confidence
            if detection.in_pool:
                pool_count += 1
                # Havuz içi - yeşil tonları
                if detection.confidence > 0.7:
                    color = (0, 255, 0)      # Yüksek confidence - parlak yeşil
                elif detection.confidence > 0.4:
                    color = (0, 200, 0)      # Orta confidence - yeşil
                else:
                    color = (0, 150, 0)      # Düşük confidence - koyu yeşil
            else:
                outside_count += 1
                # Havuz dışı - mavi tonları
                if detection.confidence > 0.7:
                    color = (255, 0, 0)      # Yüksek confidence - parlak mavi
                else:
                    color = (200, 0, 0)      # Düşük confidence - koyu mavi
            
            # Bounding box
            thickness = 3 if detection.in_pool else 2
            cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, thickness)
            
            # Info text
            info_text = f"{detection.confidence:.2f}"
            if detection.in_pool:
                info_text += " POOL"
            
            cv2.putText(vis_frame, info_text, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Center point
            cv2.circle(vis_frame, detection.center, 5, color, -1)
        
        # Statistics panel
        self.draw_stats_panel(vis_frame, pool_count, outside_count)
        
        return vis_frame
    
    def draw_stats_panel(self, frame: np.ndarray, pool_count: int, outside_count: int):
        """İstatistik paneli çiz"""
        
        # Panel background
        panel_height = 150
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (500, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Title
        cv2.putText(frame, "INTEGRATED POOL TRACKER", 
                   (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Statistics
        avg_fps = np.mean(self.fps_tracker) if self.fps_tracker else 0
        avg_detections = np.mean(self.detection_counts) if self.detection_counts else 0
        
        stats_text = [
            f"Frame: {self.frame_number}",
            f"Pool Detections: {pool_count}",
            f"Outside Detections: {outside_count}",
            f"FPS: {avg_fps:.1f}",
            f"Avg Detections: {avg_detections:.1f}"
        ]
        
        for i, text in enumerate(stats_text):
            if "Pool" in text:
                color = (0, 255, 0)  # Yeşil
            elif "Outside" in text:
                color = (255, 0, 0)  # Mavi
            else:
                color = (255, 255, 255)  # Beyaz
            
            cv2.putText(frame, text, (20, 65 + i*18),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    def test_integrated_system(self, video_path: str, duration: int = 60):
        """Entegre sistemi test et"""
        
        print(f"\n🧪 INTEGRATED SYSTEM TEST")
        print(f"📹 Video: {os.path.basename(video_path)}")
        print(f"⏱️ Duration: {duration} seconds")
        
        # Pool area otomatik yükle
        video_name = os.path.basename(video_path)
        pool_json = self.find_pool_json_for_video(video_name)
        
        if pool_json:
            self.load_pool_area_from_json(pool_json)
        else:
            print("⚠️ Pool area not found - using full frame")
        
        # Video aç
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Output video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"3_OUTPUT/INTEGRATED_POOL_TEST_{timestamp}.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print(f"💾 Output: {output_path}")
        print(f"🎬 Processing...")
        
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break
            
            # Process frame
            vis_frame, stats = self.process_video_frame(frame)
            
            # Save
            out.write(vis_frame)
            
            # Progress
            if stats['frame_number'] % 30 == 0:  # Her saniye
                print(f"  Frame {stats['frame_number']}: "
                      f"Pool={stats['pool_detections']}, "
                      f"FPS={stats['avg_fps']:.1f}")
        
        cap.release()
        out.release()
        
        # Final statistics
        total_detections = sum(self.detection_counts)
        avg_fps = np.mean(self.fps_tracker)
        
        print(f"\n✅ TEST COMPLETED!")
        print(f"📊 Processed frames: {self.frame_number}")
        print(f"🎯 Total detections: {total_detections}")
        print(f"🚀 Average FPS: {avg_fps:.1f}")
        print(f"💾 Video saved: {output_path}")
        
        return output_path

def main():
    """Ana test fonksiyonu"""
    
    print("🏊 INTEGRATED POOL TRACKER STARTING")
    print("="*50)
    
    # Tracker initialize
    tracker = IntegratedPoolTracker()
    
    # Test video
    video_path = "0_DATA/KAMERA 1.mp4"
    
    if os.path.exists(video_path):
        output_path = tracker.test_integrated_system(video_path, duration=30)
        print(f"\n🎉 SUCCESS! Video saved to: {output_path}")
    else:
        print(f"❌ Video not found: {video_path}")

if __name__ == "__main__":
    main()
