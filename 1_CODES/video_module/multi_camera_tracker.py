#!/usr/bin/env python3
"""
🎬🎬 MULTI-CAMERA TRACKER - Advanced Dual Camera System
🎯 İki kameradan senkronize tracking ve zone-based fusion

Özellikler:
- Dual camera synchronized tracking
- Zone-based coverage optimization
- Cross-camera object matching
- Unified tracking results
- Performance comparison analytics

📅 Date: 4 Ağustos 2025
"""

import numpy as np
import cv2
import json
import csv
import time
import threading
import logging
from pathlib import Path
from collections import defaultdict, OrderedDict
from datetime import datetime
import os
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from ultralytics import YOLO
from object_tracker import ObjectTracker

def setup_logger(name, log_file):
    """Simple logger setup"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger

class MultiCameraTracker:
    def __init__(self, camera1_path, camera2_path, model_path="yolov8x.pt"):
        """
        🎬🎬 Multi-Camera Tracker Initialization
        
        Args:
            camera1_path (str): KAMERA 1 video path
            camera2_path (str): KAMERA 2 video path
            model_path (str): YOLO model path
        """
        self.camera1_path = Path(camera1_path)
        self.camera2_path = Path(camera2_path)
        self.model_path = model_path
        
        # Timestamp for output naming
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Output directory
        self.output_dir = self._create_output_directory()
        
        # Logger setup
        log_file = os.path.join(self.output_dir, "multi_camera_log.txt")
        self.logger = setup_logger("multi_camera", log_file)
        
        # Performance tracking
        self.frame_count = 0
        self.detection_count = 0
        self.total_time = 0
        
        # Detection data storage
        self.camera1_data = []
        self.camera2_data = []
        self.merged_data = []
        
        # Pool areas
        self.pool_area_cam1 = None
        self.pool_area_cam2 = None
        
        # Models and trackers
        self.model = None
        self.tracker_cam1 = None
        self.tracker_cam2 = None
        
        # Cross-camera matching data
        self.cross_matches = {}
        self.global_track_id = 1
        
        self.logger.info(f"🎬🎬 Multi-Camera Tracker başlatıldı")
        self.logger.info(f"📹 Camera 1: {self.camera1_path.name}")
        self.logger.info(f"📹 Camera 2: {self.camera2_path.name}")
        self.logger.info(f"📂 Output: {self.output_dir}")

    def _create_output_directory(self):
        """📁 OUTPUT klasörü oluştur"""
        base_output = Path(__file__).parent.parent.parent / "3_OUTPUT"
        base_output.mkdir(exist_ok=True)
        
        output_name = f"MULTI_CAMERA_yolov8x_{self.timestamp}"
        output_dir = base_output / output_name
        output_dir.mkdir(exist_ok=True)
        
        return str(output_dir)

    def _load_pool_areas(self):
        """🏊 Pool area'larını yükle"""
        pool_dir = Path(__file__).parent.parent.parent / "3_OUTPUT"
        
        # KAMERA 1 pool area
        cam1_pattern = "pool_area_KAMERA_1_*.json"
        cam1_files = list(pool_dir.glob(cam1_pattern))
        if cam1_files:
            with open(cam1_files[0], 'r') as f:
                self.pool_area_cam1 = json.load(f)
            self.logger.info(f"✅ Camera 1 pool area yüklendi: {len(self.pool_area_cam1)} nokta")
        
        # KAMERA 2 pool area (varsa)
        cam2_pattern = "pool_area_KAMERA_2_*.json"
        cam2_files = list(pool_dir.glob(cam2_pattern))
        if cam2_files:
            with open(cam2_files[0], 'r') as f:
                self.pool_area_cam2 = json.load(f)
            self.logger.info(f"✅ Camera 2 pool area yüklendi: {len(self.pool_area_cam2)} nokta")
        else:
            # Camera 1'in pool area'sını Camera 2 için de kullan (geçici)
            self.pool_area_cam2 = self.pool_area_cam1
            self.logger.warning("⚠️ Camera 2 pool area bulunamadı, Camera 1'in area'sı kullanılıyor")

    def _load_model(self):
        """🤖 YOLO model yükle"""
        try:
            # Model path kontrolü
            models_dir = Path(__file__).parent.parent.parent / "MODELS"
            full_model_path = models_dir / self.model_path
            
            if full_model_path.exists():
                self.model = YOLO(str(full_model_path))
                self.logger.info(f"✅ Model yüklendi: {full_model_path}")
            else:
                self.logger.warning(f"⚠️ Model bulunamadı: {full_model_path}")
                self.logger.info(f"🔄 Default YOLOv8x model kullanılıyor...")
                self.model = YOLO(self.model_path)
                self.logger.info(f"✅ Model başarıyla yüklendi: {self.model_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Model yükleme hatası: {e}")
            return False

    def _point_in_polygon(self, point, polygon):
        """📍 Nokta polygon içinde mi kontrol et"""
        if not polygon:
            return False
        
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside

    def _classify_location(self, center_x, center_y, camera_id):
        """🏊 Konum sınıflandırması"""
        pool_area = self.pool_area_cam1 if camera_id == 1 else self.pool_area_cam2
        
        if pool_area and self._point_in_polygon((center_x, center_y), pool_area):
            return "person_swimming"
        else:
            return "person_poolside"

    def detect_objects_single_camera(self, frame, frame_number, timestamp, camera_id, tracker):
        """
        🎯 Tek kamera için object detection + tracking
        
        Args:
            frame: OpenCV frame
            frame_number: Frame numarası
            timestamp: Frame timestamp
            camera_id: Kamera ID (1 veya 2)
            tracker: Object tracker instance
        
        Returns:
            tuple: (annotated_frame, detections_list, track_assignments)
        """
        try:
            # YOLO detection
            start_time = time.time()
            results = self.model(frame, verbose=False)
            detection_time = time.time() - start_time
            
            detections = []
            annotated_frame = frame.copy()
            
            # Results process et - sadece person detection'ları al
            person_detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for i, box in enumerate(boxes):
                        # Koordinatları al
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Class name al
                        class_name = self.model.names[class_id]
                        
                        # Sadece person ve yeterli confidence
                        if class_id == 0 and confidence > 0.3:
                            # Center point hesapla
                            center_x = int((x1 + x2) / 2)
                            center_y = int((y1 + y2) / 2)
                            
                            # Pool area sınıflandırması
                            classified_class = self._classify_location(center_x, center_y, camera_id)
                            
                            # Detection data hazırla
                            detection_info = {
                                'frame_number': frame_number,
                                'timestamp': timestamp,
                                'camera_id': camera_id,
                                'detection_id': f"cam{camera_id}_{frame_number}_{i}",
                                'class_id': class_id,
                                'class_name': class_name,
                                'classified_class': classified_class,
                                'confidence': float(confidence),
                                'bbox': {
                                    'x1': float(x1), 'y1': float(y1),
                                    'x2': float(x2), 'y2': float(y2)
                                },
                                'center': {'x': center_x, 'y': center_y},
                                'detection_time': detection_time
                            }
                            person_detections.append(detection_info)
            
            # Tracking update
            track_assignments = tracker.update(person_detections)
            
            # Tracked objects'i çiz
            for track_id, detection in track_assignments.items():
                self.detection_count += 1
                
                # Track bilgilerini al
                track_info = tracker.get_object_info(track_id)
                
                # Detection bilgilerini güncelle
                detection['local_track_id'] = track_id
                detection['track_stable'] = track_info['stable'] if track_info else False
                detections.append(detection)
                
                # Çizim bilgileri
                x1, y1 = int(detection['bbox']['x1']), int(detection['bbox']['y1'])
                x2, y2 = int(detection['bbox']['x2']), int(detection['bbox']['y2'])
                center_x, center_y = detection['center']['x'], detection['center']['y']
                confidence = detection['confidence']
                classified_class = detection['classified_class']
                
                # Kameraya göre base renk
                if camera_id == 1:
                    base_color = (255, 100, 100)  # Kırmızımsı - Camera 1
                else:
                    base_color = (100, 100, 255)  # Mavimsi - Camera 2
                
                # Sınıflandırmaya göre renk ayarla
                if classified_class == "person_swimming":
                    color = (0, 255, 0)  # Yeşil - havuz içi
                    label_prefix = "Swimming"
                else:  # person_poolside
                    color = base_color  # Kameraya özel renk - havuz dışı
                    label_prefix = "Poolside"
                
                # Track stability'ye göre kalınlık
                thickness = 3 if track_info and track_info['stable'] else 2
                
                # Bounding box çiz
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)
                
                # Center point çiz
                cv2.circle(annotated_frame, (center_x, center_y), 6, color, -1)
                
                # Trajectory çiz
                tracker.draw_trajectory(annotated_frame, track_id, color, 2)
                
                # Text bilgileri
                stability = "✓" if track_info and track_info['stable'] else "○"
                label = f"CAM{camera_id} {stability} ID:{track_id} {label_prefix} {confidence:.2f}"
                
                # Label background
                (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(annotated_frame, 
                            (x1, y1-25), (x1+label_w+5, y1), 
                            color, -1)
                
                # Label text
                cv2.putText(annotated_frame, label,
                          (x1+2, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 
                          0.5, (255, 255, 255), 1)
            
            return annotated_frame, detections, track_assignments
            
        except Exception as e:
            self.logger.error(f"❌ Camera {camera_id} detection hatası frame {frame_number}: {e}")
            return frame, [], {}

    def process_multi_camera(self):
        """
        🎬🎬 Multi-camera processing ana fonksiyonu
        
        Returns:
            bool: İşlem başarılı mı
        """
        try:
            # Model yükle
            if not self._load_model():
                return False
            
            # Pool areas yükle
            self._load_pool_areas()
            
            # Object trackers başlat
            self.tracker_cam1 = ObjectTracker(max_disappeared=30, max_distance=150)
            self.tracker_cam2 = ObjectTracker(max_disappeared=30, max_distance=150)
            
            # Video'ları aç
            cap1 = cv2.VideoCapture(str(self.camera1_path))
            cap2 = cv2.VideoCapture(str(self.camera2_path))
            
            if not cap1.isOpened() or not cap2.isOpened():
                self.logger.error("❌ Video dosyaları açılamadı")
                return False
            
            # Video özellikleri
            fps1 = int(cap1.get(cv2.CAP_PROP_FPS))
            fps2 = int(cap2.get(cv2.CAP_PROP_FPS))
            width1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
            height1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
            height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Side-by-side video için boyut
            combined_width = width1 + width2
            combined_height = max(height1, height2)
            
            self.logger.info(f"📊 Camera 1: {width1}x{height1}, {fps1} FPS")
            self.logger.info(f"📊 Camera 2: {width2}x{height2}, {fps2} FPS")
            
            # Output video writer
            output_video_path = os.path.join(self.output_dir, "multi_camera_result.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, min(fps1, fps2), (combined_width, combined_height))
            
            # CSV dosyası için başlık
            csv_path = os.path.join(self.output_dir, "multi_camera_coordinates.csv")
            csv_headers = ['frame_number', 'timestamp', 'camera_id', 'detection_id', 'local_track_id', 'global_track_id',
                          'class_name', 'classified_class', 'confidence', 'x1', 'y1', 'x2', 'y2', 
                          'center_x', 'center_y', 'detection_time', 'track_stable']
            
            start_time = time.time()
            
            # 🎯 1 DAKİKALIK TEST: 14 FPS * 60 saniye = 840 frame
            max_frames_1min = 840
            
            self.logger.info(f"🎬 Multi-camera işleme başladı...")
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                writer.writeheader()
                
                while True:
                    # Her iki kameradan frame oku
                    ret1, frame1 = cap1.read()
                    ret2, frame2 = cap2.read()
                    
                    if not ret1 or not ret2:
                        self.logger.info("📹 Video sonuna ulaşıldı")
                        break
                    
                    # 1 dakika limit kontrolü
                    if self.frame_count > max_frames_1min:
                        self.logger.info(f"🎯 1 dakikalık test tamamlandı! ({max_frames_1min} frame)")
                        break
                    
                    frame_timestamp = self.frame_count / min(fps1, fps2)
                    
                    # Her iki kameradan detection yap
                    annotated_frame1, detections1, tracks1 = self.detect_objects_single_camera(
                        frame1, self.frame_count, frame_timestamp, 1, self.tracker_cam1
                    )
                    
                    annotated_frame2, detections2, tracks2 = self.detect_objects_single_camera(
                        frame2, self.frame_count, frame_timestamp, 2, self.tracker_cam2
                    )
                    
                    # Frame'leri yan yana birleştir
                    # Frame2'yi Camera 1 boyutuna scale et
                    if height2 != height1:
                        frame2_resized = cv2.resize(annotated_frame2, (width2, height1))
                    else:
                        frame2_resized = annotated_frame2
                    
                    combined_frame = np.hstack((annotated_frame1, frame2_resized))
                    
                    # Divider line çiz
                    cv2.line(combined_frame, (width1, 0), (width1, height1), (255, 255, 255), 3)
                    
                    # Frame info overlay
                    info_text = f"Frame: {self.frame_count} | Cam1: {len(detections1)} | Cam2: {len(detections2)} | Time: {frame_timestamp:.1f}s"
                    cv2.putText(combined_frame, info_text,
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Camera labels
                    cv2.putText(combined_frame, "CAMERA 1",
                              (10, height1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 100), 2)
                    cv2.putText(combined_frame, "CAMERA 2",
                              (width1+10, height1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 255), 2)
                    
                    # Video'ya yaz
                    out.write(combined_frame)
                    
                    # CSV'ye her iki kameranın detection'larını yaz
                    for detection in detections1 + detections2:
                        if detection['class_name'] == 'person':
                            csv_row = {
                                'frame_number': detection['frame_number'],
                                'timestamp': f"{detection['timestamp']:.2f}",
                                'camera_id': detection['camera_id'],
                                'detection_id': detection['detection_id'],
                                'local_track_id': detection.get('local_track_id', 'N/A'),
                                'global_track_id': 'N/A',  # TODO: Cross-camera matching
                                'class_name': detection['class_name'],
                                'classified_class': detection['classified_class'],
                                'confidence': f"{detection['confidence']:.3f}",
                                'x1': f"{detection['bbox']['x1']:.1f}",
                                'y1': f"{detection['bbox']['y1']:.1f}",
                                'x2': f"{detection['bbox']['x2']:.1f}",
                                'y2': f"{detection['bbox']['y2']:.1f}",
                                'center_x': detection['center']['x'],
                                'center_y': detection['center']['y'],
                                'detection_time': f"{detection['detection_time']:.4f}",
                                'track_stable': detection.get('track_stable', False)
                            }
                            writer.writerow(csv_row)
                    
                    # Detection data'yı kaydet
                    self.camera1_data.extend(detections1)
                    self.camera2_data.extend(detections2)
                    
                    # Progress log (her 50 frame'de bir)
                    if self.frame_count % 50 == 0 and self.frame_count > 0:
                        progress = (self.frame_count / max_frames_1min) * 100
                        self.logger.info(f"📈 İlerleme: {self.frame_count}/{max_frames_1min} ({progress:.1f}%)")
                    
                    self.frame_count += 1
                    
            # Cleanup
            cap1.release()
            cap2.release()
            out.release()
            
            # İşlem süresi
            self.total_time = time.time() - start_time
            
            self.logger.info("✅ Multi-camera işleme tamamlandı!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Multi-camera işleme hatası: {e}")
            return False

    def generate_performance_metrics(self):
        """📊 Performance metrics oluştur"""
        if self.frame_count == 0:
            return {}
        
        avg_fps = self.frame_count / self.total_time
        avg_detection_time = self.total_time / self.frame_count if self.frame_count > 0 else 0
        detection_density = self.detection_count / self.frame_count if self.frame_count > 0 else 0
        
        # Camera-specific stats
        cam1_detections = [d for d in self.camera1_data if d['class_name'] == 'person']
        cam2_detections = [d for d in self.camera2_data if d['class_name'] == 'person']
        
        cam1_swimming = [d for d in cam1_detections if d['classified_class'] == 'person_swimming']
        cam1_poolside = [d for d in cam1_detections if d['classified_class'] == 'person_poolside']
        
        cam2_swimming = [d for d in cam2_detections if d['classified_class'] == 'person_swimming']
        cam2_poolside = [d for d in cam2_detections if d['classified_class'] == 'person_poolside']
        
        # Tracker stats
        cam1_stats = self.tracker_cam1.get_statistics()
        cam2_stats = self.tracker_cam2.get_statistics()
        
        metrics = {
            'test_info': {
                'camera1_video': self.camera1_path.name,
                'camera2_video': self.camera2_path.name,
                'model_used': self.model_path,
                'test_timestamp': self.timestamp,
                'total_processing_time': round(self.total_time, 2)
            },
            'frame_stats': {
                'total_frames': self.frame_count,
                'total_detections': self.detection_count,
                'detection_density': round(detection_density, 3)
            },
            'performance': {
                'average_fps': round(avg_fps, 2),
                'average_detection_time_per_frame': round(avg_detection_time, 4),
                'real_time_capable': avg_fps >= 25
            },
            'camera1_metrics': {
                'total_detections': len(cam1_detections),
                'swimming_detections': len(cam1_swimming),
                'poolside_detections': len(cam1_poolside),
                'swimming_ratio': round(len(cam1_swimming) / len(cam1_detections) * 100, 2) if cam1_detections else 0,
                'average_confidence': round(np.mean([d['confidence'] for d in cam1_detections]), 3) if cam1_detections else 0,
                'tracks_created': cam1_stats['total_created'],
                'tracks_lost': cam1_stats['total_lost'],
                'active_tracks': cam1_stats['active_objects']
            },
            'camera2_metrics': {
                'total_detections': len(cam2_detections),
                'swimming_detections': len(cam2_swimming),
                'poolside_detections': len(cam2_poolside),
                'swimming_ratio': round(len(cam2_swimming) / len(cam2_detections) * 100, 2) if cam2_detections else 0,
                'average_confidence': round(np.mean([d['confidence'] for d in cam2_detections]), 3) if cam2_detections else 0,
                'tracks_created': cam2_stats['total_created'],
                'tracks_lost': cam2_stats['total_lost'],
                'active_tracks': cam2_stats['active_objects']
            },
            'combined_metrics': {
                'total_combined_detections': len(cam1_detections) + len(cam2_detections),
                'total_swimming': len(cam1_swimming) + len(cam2_swimming),
                'total_poolside': len(cam1_poolside) + len(cam2_poolside),
                'overall_swimming_ratio': round((len(cam1_swimming) + len(cam2_swimming)) / (len(cam1_detections) + len(cam2_detections)) * 100, 2) if (cam1_detections or cam2_detections) else 0,
                'total_tracks': cam1_stats['total_created'] + cam2_stats['total_created']
            }
        }
        
        # JSON olarak kaydet
        metrics_path = os.path.join(self.output_dir, "multi_camera_metrics.json")
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        # Log'a yazdır
        self.logger.info("📊 MULTI-CAMERA PERFORMANCE METRICS")
        self.logger.info(f"⏱️  Total Time: {metrics['test_info']['total_processing_time']}s")
        self.logger.info(f"🎬 Processed Frames: {metrics['frame_stats']['total_frames']}")
        self.logger.info(f"🚀 Average FPS: {metrics['performance']['average_fps']}")
        self.logger.info("📹 CAMERA 1 METRICS")
        self.logger.info(f"🎯 Detections: {metrics['camera1_metrics']['total_detections']}")
        self.logger.info(f"🏊 Swimming: {metrics['camera1_metrics']['swimming_detections']} ({metrics['camera1_metrics']['swimming_ratio']}%)")
        self.logger.info(f"🆔 Tracks: {metrics['camera1_metrics']['tracks_created']}")
        self.logger.info("📹 CAMERA 2 METRICS")
        self.logger.info(f"🎯 Detections: {metrics['camera2_metrics']['total_detections']}")
        self.logger.info(f"🏊 Swimming: {metrics['camera2_metrics']['swimming_detections']} ({metrics['camera2_metrics']['swimming_ratio']}%)")
        self.logger.info(f"🆔 Tracks: {metrics['camera2_metrics']['tracks_created']}")
        self.logger.info("🎬🎬 COMBINED METRICS")
        self.logger.info(f"🎯 Total Detections: {metrics['combined_metrics']['total_combined_detections']}")
        self.logger.info(f"🏊 Total Swimming: {metrics['combined_metrics']['total_swimming']} ({metrics['combined_metrics']['overall_swimming_ratio']}%)")
        self.logger.info(f"🆔 Total Tracks: {metrics['combined_metrics']['total_tracks']}")
        
        return metrics

def main():
    """🚀 Main execution function"""
    print("🎬🎬 MULTI-CAMERA TRACKER - YOLOv8x Detection")
    print("=" * 60)
    
    # Video paths
    data_dir = Path(__file__).parent.parent.parent / "0_DATA"
    camera1_path = data_dir / "kamera1.mov"
    camera2_path = data_dir / "kamera2.mov"
    
    # Path kontrolleri
    if not camera1_path.exists():
        print(f"❌ Camera 1 bulunamadı: {camera1_path}")
        return
    
    if not camera2_path.exists():
        print(f"❌ Camera 2 bulunamadı: {camera2_path}")
        return
    
    print(f"📹 Camera 1: {camera1_path.name}")
    print(f"📹 Camera 2: {camera2_path.name}")
    print(f"🤖 Model: YOLOv8x")
    print(f"🚀 Test başlatılıyor...")
    
    # Multi-camera tracker oluştur
    tracker = MultiCameraTracker(camera1_path, camera2_path)
    
    # Process videos
    success = tracker.process_multi_camera()
    
    if success:
        print("✅ Multi-camera işleme başarılı!")
        
        # Performance metrics
        metrics = tracker.generate_performance_metrics()
        
        print(f"\n📂 Output Klasörü: {tracker.output_dir}")
        print("📁 Oluşturulan dosyalar:")
        print("   📹 multi_camera_result.mp4")
        print("   📊 multi_camera_coordinates.csv") 
        print("   📝 multi_camera_log.txt")
        print("   📈 multi_camera_metrics.json")
        
        print(f"\n🎯 SONUÇLAR:")
        print(f"   ⏱️  İşlem Süresi: {metrics['test_info']['total_processing_time']}s")
        print(f"   🎬 İşlenen Frame: {metrics['frame_stats']['total_frames']}")
        print(f"   🚀 Ortalama FPS: {metrics['performance']['average_fps']}")
        
        print(f"\n📹 CAMERA 1:")
        print(f"   🎯 Detection: {metrics['camera1_metrics']['total_detections']}")
        print(f"   🏊 Swimming: {metrics['camera1_metrics']['swimming_detections']} ({metrics['camera1_metrics']['swimming_ratio']}%)")
        print(f"   🆔 Tracks: {metrics['camera1_metrics']['tracks_created']}")
        
        print(f"\n📹 CAMERA 2:")
        print(f"   🎯 Detection: {metrics['camera2_metrics']['total_detections']}")
        print(f"   🏊 Swimming: {metrics['camera2_metrics']['swimming_detections']} ({metrics['camera2_metrics']['swimming_ratio']}%)")
        print(f"   🆔 Tracks: {metrics['camera2_metrics']['tracks_created']}")
        
        print(f"\n🎬🎬 TOPLAM:")
        print(f"   🎯 Total Detection: {metrics['combined_metrics']['total_combined_detections']}")
        print(f"   🏊 Total Swimming: {metrics['combined_metrics']['total_swimming']} ({metrics['combined_metrics']['overall_swimming_ratio']}%)")
        print(f"   🆔 Total Tracks: {metrics['combined_metrics']['total_tracks']}")
        
    else:
        print("❌ Multi-camera işleme başarısız!")

if __name__ == "__main__":
    main()