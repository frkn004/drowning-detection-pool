#!/usr/bin/env python3
"""
🎬 LIVE VIDEO TESTER - YOLOv8x Real-Time Detection
🎯 KAMERA 2 için koordinat tabanlı test sistemi

📋 Features:
- YOLOv8x model ile detection
- Frame-by-frame koordinat analizi
- OUTPUT klasörüne organize kayıt
- Real-time performance tracking
- Comprehensive logging

👥 Team: FURKAN & NISA
📅 Date: 31 Temmuz 2025
"""

import cv2
import os
import sys
from datetime import datetime
import json
import csv
from pathlib import Path
import time
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from ultralytics import YOLO
import logging

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
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

class LiveVideoTester:
    def __init__(self, video_path, model_path="yolov8x.pt"):
        """
        🎯 Live Video Tester Initialization
        
        Args:
            video_path (str): Input video dosya yolu
            model_path (str): YOLO model dosya yolu
        """
        self.video_path = video_path
        self.model_path = model_path
        
        # Video dosya ismini al
        self.video_name = Path(video_path).stem
        
        # Timestamp oluştur
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Output klasörü oluştur
        self.output_dir = self._create_output_directory()
        
        # Logger setup
        self.logger = setup_logger(
            name="live_tester",
            log_file=os.path.join(self.output_dir, "detection_log.txt")
        )
        
        # Performance tracking
        self.frame_count = 0
        self.detection_count = 0
        self.total_time = 0
        
        # Detection data storage
        self.detection_data = []
        
        self.logger.info(f"🚀 Live Video Tester başlatıldı")
        self.logger.info(f"📹 Video: {self.video_name}")
        self.logger.info(f"🤖 Model: {self.model_path}")
        self.logger.info(f"📂 Output: {self.output_dir}")

    def _create_output_directory(self):
        """📁 OUTPUT klasörü oluştur"""
        base_output = Path(__file__).parent.parent.parent / "OUTPUT"
        base_output.mkdir(exist_ok=True)
        
        folder_name = f"LIVE_TEST_yolov8x_{self.video_name}_{self.timestamp}"
        output_dir = base_output / folder_name
        output_dir.mkdir(exist_ok=True)
        
        return str(output_dir)

    def load_model(self):
        """🤖 YOLO model yükle"""
        try:
            models_dir = Path(__file__).parent.parent.parent / "MODELS"
            model_full_path = models_dir / self.model_path
            
            if not model_full_path.exists():
                # Eğer MODELS klasöründe yoksa, default model kullan
                self.logger.warning(f"⚠️ Model bulunamadı: {model_full_path}")
                self.logger.info(f"🔄 Default YOLOv8x model kullanılıyor...")
                self.model = YOLO('yolov8x.pt')
            else:
                self.logger.info(f"📥 Model yükleniyor: {model_full_path}")
                self.model = YOLO(str(model_full_path))
            
            self.logger.info(f"✅ Model başarıyla yüklendi: {self.model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Model yükleme hatası: {e}")
            return False

    def detect_objects(self, frame, frame_number, timestamp):
        """
        🎯 Tek frame'de object detection yap
        
        Args:
            frame: OpenCV frame
            frame_number: Frame numarası
            timestamp: Frame timestamp
        
        Returns:
            tuple: (annotated_frame, detections_list)
        """
        try:
            # YOLO detection
            start_time = time.time()
            results = self.model(frame, verbose=False)
            detection_time = time.time() - start_time
            
            detections = []
            annotated_frame = frame.copy()
            
            # Results process et
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
                        
                        # Center point hesapla
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        
                        # Detection data kaydet
                        detection_info = {
                            'frame_number': frame_number,
                            'timestamp': timestamp,
                            'detection_id': f"{frame_number}_{i}",
                            'class_id': class_id,
                            'class_name': class_name,
                            'confidence': float(confidence),
                            'bbox': {
                                'x1': float(x1), 'y1': float(y1),
                                'x2': float(x2), 'y2': float(y2)
                            },
                            'center': {'x': center_x, 'y': center_y},
                            'detection_time': detection_time
                        }
                        detections.append(detection_info)
                        
                        # Sadece 'person' sınıfını işle (class_id = 0)
                        if class_id == 0 and confidence > 0.3:
                            self.detection_count += 1
                            
                            # Bounding box çiz
                            color = self._get_color_for_confidence(confidence)
                            cv2.rectangle(annotated_frame, 
                                        (int(x1), int(y1)), (int(x2), int(y2)), 
                                        color, 2)
                            
                            # Center point çiz
                            cv2.circle(annotated_frame, (center_x, center_y), 5, color, -1)
                            
                            # Text bilgileri
                            label = f"Person {confidence:.2f}"
                            coord_text = f"({center_x},{center_y})"
                            
                            # Label background
                            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                            cv2.rectangle(annotated_frame, 
                                        (int(x1), int(y1-25)), (int(x1+label_w), int(y1)), 
                                        color, -1)
                            
                            # Label text
                            cv2.putText(annotated_frame, label,
                                      (int(x1), int(y1-5)), cv2.FONT_HERSHEY_SIMPLEX, 
                                      0.6, (255, 255, 255), 2)
                            
                            # Koordinat text
                            cv2.putText(annotated_frame, coord_text,
                                      (int(x1), int(y2+20)), cv2.FONT_HERSHEY_SIMPLEX, 
                                      0.5, color, 1)
            
            return annotated_frame, detections
            
        except Exception as e:
            self.logger.error(f"❌ Detection hatası frame {frame_number}: {e}")
            return frame, []

    def _get_color_for_confidence(self, confidence):
        """🎨 Confidence'a göre renk belirle"""
        if confidence > 0.8:
            return (0, 255, 0)    # Yeşil - yüksek confidence
        elif confidence > 0.6:
            return (0, 255, 255)  # Sarı - orta confidence
        else:
            return (0, 165, 255)  # Turuncu - düşük confidence

    def process_video(self):
        """🎬 Video'yu frame-by-frame işle"""
        self.logger.info("🎬 Video işleme başladı...")
        
        # Video aç
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            self.logger.error(f"❌ Video açılamadı: {self.video_path}")
            return False
        
        # Video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        self.logger.info(f"📊 Video özellikleri: {frame_width}x{frame_height}, {fps} FPS, {total_frames} frame")
        
        # Output video writer
        output_video_path = os.path.join(self.output_dir, "live_test_result.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
        
        # CSV dosyası için başlık
        csv_path = os.path.join(self.output_dir, "coordinates_log.csv")
        csv_headers = ['frame_number', 'timestamp', 'detection_id', 'class_name', 
                      'confidence', 'x1', 'y1', 'x2', 'y2', 'center_x', 'center_y', 'detection_time']
        
        start_time = time.time()
        
        # 🎯 1 DAKİKALIK TEST: 14 FPS * 60 saniye = 840 frame
        max_frames_1min = 840
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                writer.writeheader()
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # 🎯 1 dakika limit
                    if self.frame_count >= max_frames_1min:
                        self.logger.info(f"🎯 1 dakikalık test tamamlandı! ({max_frames_1min} frame)")
                        break
                    
                    self.frame_count += 1
                    frame_timestamp = self.frame_count / fps
                    
                    # Detection yap
                    annotated_frame, detections = self.detect_objects(
                        frame, self.frame_count, frame_timestamp
                    )
                    
                    # Frame info overlay
                    self._add_frame_info(annotated_frame, self.frame_count, 
                                       len(detections), frame_timestamp)
                    
                    # Video'ya yaz
                    out.write(annotated_frame)
                    
                    # CSV'ye detection'ları yaz
                    for detection in detections:
                        if detection['class_name'] == 'person':
                            csv_row = {
                                'frame_number': detection['frame_number'],
                                'timestamp': f"{detection['timestamp']:.2f}",
                                'detection_id': detection['detection_id'],
                                'class_name': detection['class_name'],
                                'confidence': f"{detection['confidence']:.3f}",
                                'x1': f"{detection['bbox']['x1']:.1f}",
                                'y1': f"{detection['bbox']['y1']:.1f}",
                                'x2': f"{detection['bbox']['x2']:.1f}",
                                'y2': f"{detection['bbox']['y2']:.1f}",
                                'center_x': detection['center']['x'],
                                'center_y': detection['center']['y'],
                                'detection_time': f"{detection['detection_time']:.4f}"
                            }
                            writer.writerow(csv_row)
                    
                    # Detection data'yı kaydet
                    self.detection_data.extend(detections)
                    
                    # Progress log (her 50 frame'de bir)
                    if self.frame_count % 50 == 0:
                        progress = (self.frame_count / total_frames) * 100
                        self.logger.info(f"📈 İlerleme: {self.frame_count}/{total_frames} ({progress:.1f}%)")
                    
        except Exception as e:
            self.logger.error(f"❌ Video işleme hatası: {e}")
            return False
        
        finally:
            cap.release()
            out.release()
        
        self.total_time = time.time() - start_time
        self.logger.info(f"✅ Video işleme tamamlandı!")
        
        return True

    def _add_frame_info(self, frame, frame_number, detection_count, timestamp):
        """📊 Frame'e bilgi overlay'i ekle"""
        # Background rectangle
        cv2.rectangle(frame, (10, 10), (400, 80), (0, 0, 0), -1)
        
        # Frame info
        frame_text = f"Frame: {frame_number}"
        time_text = f"Time: {timestamp:.2f}s"
        detection_text = f"Detections: {detection_count}"
        
        cv2.putText(frame, frame_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, time_text, (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, detection_text, (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    def save_performance_metrics(self):
        """📈 Performance metrics'leri kaydet"""
        if self.total_time == 0:
            return
        
        avg_fps = self.frame_count / self.total_time
        avg_detection_time = self.total_time / self.frame_count if self.frame_count > 0 else 0
        detection_density = self.detection_count / self.frame_count if self.frame_count > 0 else 0
        
        metrics = {
            'test_info': {
                'video_name': self.video_name,
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
            'quality_metrics': {
                'frames_with_detections': len([d for d in self.detection_data if d['class_name'] == 'person']),
                'average_confidence': round(np.mean([d['confidence'] for d in self.detection_data if d['class_name'] == 'person']), 3) if self.detection_data else 0,
                'high_confidence_detections': len([d for d in self.detection_data if d['class_name'] == 'person' and d['confidence'] > 0.8])
            }
        }
        
        # JSON olarak kaydet
        metrics_path = os.path.join(self.output_dir, "performance_metrics.json")
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        # Log'a yazdır
        self.logger.info("📊 PERFORMANCE METRICS")
        self.logger.info(f"⏱️  Total Time: {metrics['test_info']['total_processing_time']}s")
        self.logger.info(f"🎬 Processed Frames: {metrics['frame_stats']['total_frames']}")
        self.logger.info(f"🎯 Total Detections: {metrics['frame_stats']['total_detections']}")
        self.logger.info(f"🚀 Average FPS: {metrics['performance']['average_fps']}")
        self.logger.info(f"📈 Detection Density: {metrics['frame_stats']['detection_density']}")
        self.logger.info(f"🎯 Average Confidence: {metrics['quality_metrics']['average_confidence']}")
        
        return metrics

def main():
    """🚀 Main execution function"""
    print("🎬 LIVE VIDEO TESTER - YOLOv8x Detection")
    print("=" * 50)
    
    # Video path belirle
    data_dir = Path(__file__).parent.parent.parent / "0_DATA"
    video_path = data_dir / "kamera2.mov"
    
    if not video_path.exists():
        print(f"❌ Video bulunamadı: {video_path}")
        print(f"📂 DATA klasörü içeriği:")
        for file in data_dir.glob("*"):
            print(f"   - {file.name}")
        return
    
    print(f"📹 Test Video: {video_path.name}")
    print(f"🤖 Model: YOLOv8x")
    print("🚀 Test başlatılıyor...\n")
    
    # Tester oluştur ve çalıştır
    tester = LiveVideoTester(str(video_path), "yolov8x.pt")
    
    # Model yükle
    if not tester.load_model():
        print("❌ Model yüklenemedi!")
        return
    
    # Video işle
    if tester.process_video():
        print("\n✅ Video işleme başarılı!")
        
        # Performance metrics kaydet
        metrics = tester.save_performance_metrics()
        
        print(f"\n📂 Output Klasörü: {tester.output_dir}")
        print("📁 Oluşturulan dosyalar:")
        print("   📹 live_test_result.mp4")
        print("   📊 coordinates_log.csv") 
        print("   📝 detection_log.txt")
        print("   📈 performance_metrics.json")
        
        print(f"\n🎯 SONUÇLAR:")
        print(f"   ⏱️  İşlem Süresi: {metrics['test_info']['total_processing_time']}s")
        print(f"   🎬 İşlenen Frame: {metrics['frame_stats']['total_frames']}")
        print(f"   🎯 Tespit Sayısı: {metrics['frame_stats']['total_detections']}")
        print(f"   🚀 Ortalama FPS: {metrics['performance']['average_fps']}")
        
    else:
        print("❌ Video işleme başarısız!")

if __name__ == "__main__":
    main()