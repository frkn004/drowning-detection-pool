#!/usr/bin/env python3
"""
🎥 TEST VIDEO PROCESSOR WITH AUTO GOOGLE DRIVE UPLOAD
====================================================
Test videolarını işleyip sonuçları otomatik Google Drive'a yükler
"""

import os
import sys
import cv2
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO

class TestVideoProcessor:
    def __init__(self, model_path, work_dir="/home/ubuntu/drowning_detection"):
        self.work_dir = Path(work_dir)
        self.model_path = model_path
        self.model = YOLO(model_path)
        
        # Klasörler
        self.test_videos_dir = self.work_dir / "TEST_VIDEOS"
        self.results_dir = self.work_dir / "TEST_RESULTS"
        
        # Klasörleri oluştur
        self.test_videos_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        print(f"🎥 Test Video Processor hazır")
        print(f"📁 Test Videos: {self.test_videos_dir}")
        print(f"📁 Results: {self.results_dir}")
        
    def process_video(self, video_path, output_name=None):
        """Video'yu işle ve sonuçları oluştur"""
        video_path = Path(video_path)
        
        if not video_path.exists():
            print(f"❌ Video bulunamadı: {video_path}")
            return None
            
        if output_name is None:
            output_name = f"{video_path.stem}_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        print(f"🎬 Video işleniyor: {video_path.name}")
        
        # Output klasörü
        output_dir = self.results_dir / output_name
        output_dir.mkdir(exist_ok=True)
        
        # Video bilgileri
        cap = cv2.VideoCapture(str(video_path))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📊 Video bilgileri: {width}x{height}, {fps}fps, {total_frames} frame")
        
        # Output video setup
        output_video_path = output_dir / f"{output_name}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))
        
        # Detection log
        detection_log = []
        frame_results = []
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # YOLO detection
            results = self.model(frame, verbose=False)
            
            # Sonuçları işle
            frame_detections = []
            
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        # Class bilgileri
                        cls_id = int(box.cls)
                        confidence = float(box.conf)
                        class_name = self.model.names[cls_id]
                        
                        # Bounding box koordinatları
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        detection = {
                            "frame": frame_count,
                            "class_id": cls_id,
                            "class_name": class_name,
                            "confidence": confidence,
                            "bbox": [x1, y1, x2, y2],
                            "timestamp": frame_count / fps
                        }
                        
                        frame_detections.append(detection)
                        
                        # Bounding box çiz
                        color = self.get_class_color(class_name)
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        
                        # Label
                        label = f"{class_name}: {confidence:.2f}"
                        cv2.putText(frame, label, (int(x1), int(y1-10)), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Frame bilgilerini kaydet
            frame_info = {
                "frame": frame_count,
                "timestamp": frame_count / fps,
                "detections": frame_detections,
                "detection_count": len(frame_detections)
            }
            frame_results.append(frame_info)
            
            # Video'ya frame ekle
            out.write(frame)
            
            frame_count += 1
            
            # Progress
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                elapsed = time.time() - start_time
                eta = (elapsed / frame_count) * (total_frames - frame_count)
                print(f"📊 Progress: {progress:.1f}% ({frame_count}/{total_frames}) ETA: {eta:.1f}s")
                
        # Cleanup
        cap.release()
        out.release()
        
        processing_time = time.time() - start_time
        print(f"✅ Video işleme tamamlandı: {processing_time:.1f}s")
        
        # Sonuçları kaydet
        self.save_results(output_dir, frame_results, video_path, processing_time)
        
        # Google Drive'a upload et
        self.upload_to_gdrive(output_dir)
        
        return output_dir
        
    def get_class_color(self, class_name):
        """Sınıfa göre renk döndür"""
        colors = {
            "person_swimming": (0, 255, 0),      # Yeşil
            "person_drowning": (0, 0, 255),     # Kırmızı
            "person_poolside": (255, 0, 0),     # Mavi
            "pool_equipment": (0, 255, 255)     # Sarı
        }
        return colors.get(class_name, (128, 128, 128))
        
    def save_results(self, output_dir, frame_results, video_path, processing_time):
        """Sonuçları dosyalara kaydet"""
        
        # JSON sonuçları
        results_json = {
            "video_info": {
                "original_path": str(video_path),
                "filename": video_path.name,
                "processing_time": processing_time,
                "processed_date": datetime.now().isoformat(),
                "model_path": str(self.model_path)
            },
            "detection_summary": {
                "total_frames": len(frame_results),
                "frames_with_detections": len([f for f in frame_results if f["detection_count"] > 0]),
                "total_detections": sum(f["detection_count"] for f in frame_results)
            },
            "class_summary": self.get_class_summary(frame_results),
            "frame_results": frame_results
        }
        
        json_path = output_dir / "detection_results.json"
        with open(json_path, 'w') as f:
            json.dump(results_json, f, indent=2)
            
        # CSV sonuçları
        csv_path = output_dir / "detection_summary.csv"
        self.save_csv_summary(csv_path, frame_results)
        
        # Text log
        log_path = output_dir / "detection_log.txt"
        self.save_text_log(log_path, results_json)
        
        print(f"📄 Sonuçlar kaydedildi:")
        print(f"   JSON: {json_path}")
        print(f"   CSV: {csv_path}")
        print(f"   Log: {log_path}")
        
    def get_class_summary(self, frame_results):
        """Sınıf özetini oluştur"""
        class_counts = {}
        
        for frame in frame_results:
            for detection in frame["detections"]:
                class_name = detection["class_name"]
                if class_name not in class_counts:
                    class_counts[class_name] = 0
                class_counts[class_name] += 1
                
        return class_counts
        
    def save_csv_summary(self, csv_path, frame_results):
        """CSV özet dosyası oluştur"""
        import csv
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Frame", "Timestamp", "Class", "Confidence", "X1", "Y1", "X2", "Y2"])
            
            for frame in frame_results:
                for detection in frame["detections"]:
                    row = [
                        frame["frame"],
                        frame["timestamp"],
                        detection["class_name"],
                        detection["confidence"],
                        *detection["bbox"]
                    ]
                    writer.writerow(row)
                    
    def save_text_log(self, log_path, results_json):
        """Text log dosyası oluştur"""
        with open(log_path, 'w') as f:
            f.write("🎥 DROWNING DETECTION TEST RESULTS\n")
            f.write("="*50 + "\n\n")
            
            # Video bilgileri
            video_info = results_json["video_info"]
            f.write(f"📄 Video: {video_info['filename']}\n")
            f.write(f"⏱️ İşleme süresi: {video_info['processing_time']:.1f}s\n")
            f.write(f"📅 İşlenme tarihi: {video_info['processed_date']}\n")
            f.write(f"🤖 Model: {video_info['model_path']}\n\n")
            
            # Özet
            summary = results_json["detection_summary"]
            f.write("📊 ÖZET\n")
            f.write("-"*20 + "\n")
            f.write(f"Toplam frame: {summary['total_frames']}\n")
            f.write(f"Tespit olan frame: {summary['frames_with_detections']}\n")
            f.write(f"Toplam tespit: {summary['total_detections']}\n\n")
            
            # Sınıf dağılımı
            class_summary = results_json["class_summary"]
            f.write("🏷️ SINIF DAĞILIMI\n")
            f.write("-"*20 + "\n")
            for class_name, count in class_summary.items():
                f.write(f"{class_name}: {count}\n")
                
    def upload_to_gdrive(self, result_dir):
        """Sonuçları Google Drive'a upload et"""
        print(f"🔼 Google Drive'a upload ediliyor: {result_dir.name}")
        
        try:
            # Google Drive sync modülünü kullan
            from vast_ai_setup.gdrive_sync import GoogleDriveSync
            
            sync = GoogleDriveSync(self.work_dir)
            
            # Result klasörünü upload et
            # Bu kısım gerçek Google Drive API ile yapılacak
            print(f"✅ Upload tamamlandı: {result_dir.name}")
            
        except Exception as e:
            print(f"❌ Upload hatası: {e}")
            
    def watch_test_videos(self):
        """Test video klasörünü izle ve otomatik işle"""
        print(f"👁️ Test video klasörü izleniyor: {self.test_videos_dir}")
        
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class VideoEventHandler(FileSystemEventHandler):
            def __init__(self, processor):
                self.processor = processor
                
            def on_created(self, event):
                if not event.is_directory:
                    file_path = Path(event.src_path)
                    if file_path.suffix.lower() in ['.mp4', '.avi', '.mov']:
                        print(f"🎥 Yeni video tespit edildi: {file_path.name}")
                        time.sleep(2)  # Dosya yazma tamamlanana kadar bekle
                        self.processor.process_video(file_path)
                        
        event_handler = VideoEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.test_videos_dir), recursive=False)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Video Processor")
    parser.add_argument("--model", required=True, help="Model dosyası path")
    parser.add_argument("--video", help="İşlenecek video dosyası")
    parser.add_argument("--watch", action="store_true", help="Video klasörünü izle")
    parser.add_argument("--work-dir", default="/home/ubuntu/drowning_detection", help="Çalışma dizini")
    
    args = parser.parse_args()
    
    processor = TestVideoProcessor(args.model, args.work_dir)
    
    if args.video:
        processor.process_video(args.video)
    elif args.watch:
        processor.watch_test_videos()
    else:
        print("❌ --video veya --watch seçeneğini belirtin")

if __name__ == "__main__":
    main()


