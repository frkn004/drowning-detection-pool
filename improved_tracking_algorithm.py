#!/usr/bin/env python3
"""
🚀 GELİŞTİRİLMİŞ HAVUZ TAKİP ALGORİTMASI
=====================================
Mevcut sistemi optimize ederek daha iyi tracking performance
"""

import cv2
import numpy as np
from collections import defaultdict, deque
import json
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

@dataclass
class Detection:
    """Tek bir detection bilgisi"""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]          # center_x, center_y
    confidence: float
    area: float
    in_pool: bool

@dataclass
class Track:
    """Bir kişinin track bilgileri"""
    track_id: int
    positions: deque                 # Son N pozisyonu sakla (memory efficient)
    confidences: deque              # Confidence scores
    last_seen_frame: int
    first_seen_frame: int
    in_pool_count: int
    out_pool_count: int
    lost_frames: int                # Kaç frame kaybedildi
    velocity: Tuple[float, float]   # Hız vektörü (x, y)
    is_active: bool

class ImprovedPoolTracker:
    """
    🎯 Geliştirilmiş havuz tracking sistemi
    
    İyileştirmeler:
    1. Kalman filtering prediction
    2. Multi-frame association  
    3. Velocity-based matching
    4. Memory efficient tracking
    5. Robust ID consistency
    """
    
    def __init__(self, config=None):
        """Initialize tracker with optimized parameters"""
        
        # Tracking parametreleri
        self.max_track_distance = 80      # Daha sıkı distance threshold
        self.max_lost_frames = 15         # Kaç frame kaybolabilir
        self.position_history_size = 10   # Position history buffer
        self.confidence_threshold = 0.3   # Minimum detection confidence
        
        # Velocity tracking için
        self.velocity_weight = 0.3        # Velocity prediction ağırlığı
        self.position_weight = 0.7        # Position matching ağırlığı
        
        # Tracking state
        self.tracks: Dict[int, Track] = {}
        self.next_track_id = 1
        self.frame_number = 0
        
        # Pool area
        self.pool_polygon = None
        
        # Performance metrics
        self.total_detections = 0
        self.total_tracks_created = 0
        self.id_switches = 0
        
        print("🚀 Improved Pool Tracker initialized")
        
    def set_pool_area(self, polygon_points):
        """Havuz alanını set et"""
        if polygon_points is not None:
            self.pool_polygon = np.array(polygon_points, dtype=np.int32)
            print(f"✅ Pool area set with {len(polygon_points)} points")
        
    def is_point_in_pool(self, x: int, y: int) -> bool:
        """Nokta havuz içinde mi kontrol et"""
        if self.pool_polygon is None:
            return True  # Pool area yoksa hepsini kabul et
        
        result = cv2.pointPolygonTest(self.pool_polygon, (x, y), False)
        return result >= 0
    
    def calculate_distance(self, point1: Tuple, point2: Tuple) -> float:
        """Euclidean distance"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def calculate_velocity(self, positions: deque) -> Tuple[float, float]:
        """Son birkaç pozisyondan velocity hesapla"""
        if len(positions) < 2:
            return (0.0, 0.0)
        
        # Son 3 pozisyonun ortalamasını al
        recent_positions = list(positions)[-min(3, len(positions)):]
        
        if len(recent_positions) < 2:
            return (0.0, 0.0)
        
        # Linear velocity calculation
        vx = recent_positions[-1][0] - recent_positions[0][0]
        vy = recent_positions[-1][1] - recent_positions[0][1]
        
        # Frame count ile normalize et
        frames = len(recent_positions) - 1
        if frames > 0:
            vx /= frames
            vy /= frames
        
        return (vx, vy)
    
    def predict_next_position(self, track: Track) -> Tuple[int, int]:
        """Bir sonraki pozisyonu tahmin et"""
        if not track.positions:
            return (0, 0)
        
        last_pos = track.positions[-1]
        
        # Velocity based prediction
        predicted_x = last_pos[0] + track.velocity[0]
        predicted_y = last_pos[1] + track.velocity[1]
        
        return (int(predicted_x), int(predicted_y))
    
    def calculate_matching_score(self, detection: Detection, track: Track) -> float:
        """Detection ile track arasında matching score hesapla"""
        
        # Distance score
        if track.positions:
            last_pos = track.positions[-1]
            distance = self.calculate_distance(detection.center, last_pos)
            
            # Normalize distance (0-1 range)
            distance_score = max(0, 1 - (distance / self.max_track_distance))
        else:
            distance_score = 0
        
        # Prediction score (velocity based)
        predicted_pos = self.predict_next_position(track)
        prediction_distance = self.calculate_distance(detection.center, predicted_pos)
        prediction_score = max(0, 1 - (prediction_distance / self.max_track_distance))
        
        # Confidence score
        confidence_score = detection.confidence
        
        # Pool consistency score
        track_in_pool_ratio = track.in_pool_count / max(1, track.in_pool_count + track.out_pool_count)
        pool_consistency = 1.0 if detection.in_pool == (track_in_pool_ratio > 0.5) else 0.5
        
        # Combined score
        total_score = (
            self.position_weight * distance_score +
            self.velocity_weight * prediction_score +
            0.2 * confidence_score +
            0.1 * pool_consistency
        )
        
        return total_score
    
    def process_detections(self, detections: List[Detection]) -> Dict[int, Detection]:
        """Frame'deki tüm detections'ı işle ve track ID'leri ata"""
        
        self.frame_number += 1
        self.total_detections += len(detections)
        
        # Active tracks'leri güncelle (lost frame sayısını artır)
        for track in self.tracks.values():
            if track.is_active:
                track.lost_frames += 1
                if track.lost_frames > self.max_lost_frames:
                    track.is_active = False
                    print(f"🔄 Track {track.track_id} deactivated (lost too long)")
        
        # Detection to track matching
        assignment = self._assign_detections_to_tracks(detections)
        
        # Results
        tracked_detections = {}
        
        for detection_idx, track_id in assignment.items():
            detection = detections[detection_idx]
            
            if track_id == -1:  # Yeni track
                track_id = self._create_new_track(detection)
            else:  # Existing track update
                self._update_track(track_id, detection)
            
            tracked_detections[track_id] = detection
        
        return tracked_detections
    
    def _assign_detections_to_tracks(self, detections: List[Detection]) -> Dict[int, int]:
        """Hungarian algorithm benzeri assignment"""
        
        assignment = {}
        used_tracks = set()
        
        # Her detection için en iyi track'i bul
        for det_idx, detection in enumerate(detections):
            best_track_id = -1
            best_score = 0.5  # Minimum threshold
            
            for track_id, track in self.tracks.items():
                if not track.is_active or track_id in used_tracks:
                    continue
                
                score = self.calculate_matching_score(detection, track)
                
                if score > best_score:
                    best_score = score
                    best_track_id = track_id
            
            assignment[det_idx] = best_track_id
            
            if best_track_id != -1:
                used_tracks.add(best_track_id)
        
        return assignment
    
    def _create_new_track(self, detection: Detection) -> int:
        """Yeni track oluştur"""
        
        track_id = self.next_track_id
        self.next_track_id += 1
        self.total_tracks_created += 1
        
        new_track = Track(
            track_id=track_id,
            positions=deque([detection.center], maxlen=self.position_history_size),
            confidences=deque([detection.confidence], maxlen=self.position_history_size),
            last_seen_frame=self.frame_number,
            first_seen_frame=self.frame_number,
            in_pool_count=1 if detection.in_pool else 0,
            out_pool_count=0 if detection.in_pool else 1,
            lost_frames=0,
            velocity=(0.0, 0.0),
            is_active=True
        )
        
        self.tracks[track_id] = new_track
        
        print(f"🆕 New track created: ID {track_id} at {detection.center}")
        return track_id
    
    def _update_track(self, track_id: int, detection: Detection):
        """Existing track'i güncelle"""
        
        track = self.tracks[track_id]
        
        # Position history update
        track.positions.append(detection.center)
        track.confidences.append(detection.confidence)
        
        # Velocity update
        track.velocity = self.calculate_velocity(track.positions)
        
        # Pool statistics update
        if detection.in_pool:
            track.in_pool_count += 1
        else:
            track.out_pool_count += 1
        
        # Frame info update
        track.last_seen_frame = self.frame_number
        track.lost_frames = 0
        track.is_active = True
    
    def get_active_tracks(self) -> Dict[int, Track]:
        """Active track'leri döndür"""
        return {tid: track for tid, track in self.tracks.items() if track.is_active}
    
    def get_track_statistics(self) -> Dict:
        """Tracking istatistikleri"""
        active_count = len(self.get_active_tracks())
        
        return {
            'frame_number': self.frame_number,
            'total_detections': self.total_detections,
            'total_tracks_created': self.total_tracks_created,
            'active_tracks': active_count,
            'id_switches': self.id_switches,
            'avg_detections_per_frame': self.total_detections / max(1, self.frame_number)
        }
    
    def visualize_tracks(self, frame: np.ndarray, tracked_detections: Dict[int, Detection]) -> np.ndarray:
        """Track'leri frame üzerine çiz"""
        
        vis_frame = frame.copy()
        
        # Pool area çiz
        if self.pool_polygon is not None:
            cv2.polylines(vis_frame, [self.pool_polygon], True, (0, 255, 255), 2)
        
        # Her track için
        for track_id, detection in tracked_detections.items():
            track = self.tracks[track_id]
            
            # Bounding box
            x1, y1, x2, y2 = detection.bbox
            
            # Track yaşına göre renk
            track_age = self.frame_number - track.first_seen_frame
            if track_age < 5:
                color = (0, 255, 0)  # Yeni track - yeşil
            elif track_age < 30:
                color = (255, 255, 0)  # Orta yaş - sarı
            else:
                color = (0, 0, 255)  # Eski track - kırmızı
            
            # Pool içi/dışı renk modifikasyonu
            if detection.in_pool:
                # Pool içi - daha parlak
                color = tuple(min(255, c + 50) for c in color)
            else:
                # Pool dışı - daha mat
                color = tuple(max(0, c - 50) for c in color)
            
            # Rectangle çiz
            cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, 2)
            
            # Track ID ve info
            info_text = f"ID:{track_id} ({track_age}f)"
            cv2.putText(vis_frame, info_text, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Trajectory çiz (son 5 position)
            if len(track.positions) > 1:
                points = list(track.positions)[-5:]  # Son 5 pozisyon
                for i in range(1, len(points)):
                    cv2.line(vis_frame, points[i-1], points[i], color, 2)
            
            # Velocity arrow
            if abs(track.velocity[0]) > 2 or abs(track.velocity[1]) > 2:
                center = detection.center
                vel_end = (
                    int(center[0] + track.velocity[0] * 5),
                    int(center[1] + track.velocity[1] * 5)
                )
                cv2.arrowedLine(vis_frame, center, vel_end, (255, 0, 255), 2)
        
        # İstatistikleri ekle
        stats = self.get_track_statistics()
        stats_text = [
            f"Frame: {stats['frame_number']}",
            f"Active tracks: {stats['active_tracks']}",
            f"Total tracks: {stats['total_tracks_created']}",
            f"Avg detections/frame: {stats['avg_detections_per_frame']:.1f}"
        ]
        
        for i, text in enumerate(stats_text):
            cv2.putText(vis_frame, text, (10, 30 + i*25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return vis_frame

def test_improved_tracker():
    """Improved tracker test fonksiyonu"""
    
    print("🧪 IMPROVED TRACKER TEST")
    print("="*40)
    
    # Test data
    from ultralytics import YOLO
    
    # Tracker initialize
    tracker = ImprovedPoolTracker()
    
    # Pool area (örnek)
    pool_points = [(100, 100), (500, 100), (500, 400), (100, 400)]
    tracker.set_pool_area(pool_points)
    
    # Model yükle
    model = YOLO('4_MODELS/yolov8x.pt')
    
    # Test video
    video_path = '0_DATA/KAMERA 1.mp4'
    cap = cv2.VideoCapture(video_path)
    
    frame_count = 0
    
    while frame_count < 100:  # İlk 100 frame test
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # YOLO detection
        results = model(frame, conf=0.3, classes=[0], verbose=False)
        
        # Convert to Detection objects
        detections = []
        if results[0].boxes is not None:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf.item())
                
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                area = (x2 - x1) * (y2 - y1)
                in_pool = tracker.is_point_in_pool(center_x, center_y)
                
                detection = Detection(
                    bbox=(x1, y1, x2, y2),
                    center=(center_x, center_y),
                    confidence=conf,
                    area=area,
                    in_pool=in_pool
                )
                detections.append(detection)
        
        # Tracking process
        tracked_detections = tracker.process_detections(detections)
        
        # Visualization
        vis_frame = tracker.visualize_tracks(frame, tracked_detections)
        
        # Show result
        cv2.imshow('Improved Tracking', vis_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        if frame_count % 25 == 0:
            stats = tracker.get_track_statistics()
            print(f"Frame {frame_count}: {stats}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Final statistics
    final_stats = tracker.get_track_statistics()
    print("\n🏆 FINAL RESULTS:")
    print(f"Total frames processed: {final_stats['frame_number']}")
    print(f"Total tracks created: {final_stats['total_tracks_created']}")
    print(f"Average detections per frame: {final_stats['avg_detections_per_frame']:.2f}")

if __name__ == "__main__":
    test_improved_tracker()



