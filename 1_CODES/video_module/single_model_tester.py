#!/usr/bin/env python3

"""
🎯 TEK MODEL TEST MODÜLÜ
========================
Belirtilen bir modelle KAMERA 2 videosunu test eder.
"""

import cv2
import os
import sys
import time
from datetime import datetime

# Ana dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Paths, Detection, System, get_project_info

class SingleModelTester:
    """
    🎯 Tek model test sınıfı
    """
    
    def __init__(self):
        self.info = get_project_info()
        print(f"🎬 {System.PROJECT_NAME} - Tek Model Tester")
        print(f"📊 {len(self.info['videos'])} video, {len(self.info['models'])} model bulundu")
    
    def create_output_folder(self, model_name, video_name):
        """Model ve video için özel klasör oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_short = os.path.splitext(model_name)[0]
        video_short = os.path.splitext(video_name)[0]
        
        folder_name = f"{model_short}_{video_short}_{timestamp}"
        output_path = os.path.join(Paths.OUTPUT_DIR, folder_name)
        
        os.makedirs(output_path, exist_ok=True)
        
        print(f"📁 Çıktı klasörü: {folder_name}")
        return output_path
    
    def test_single_model(self, model_name, max_duration=120):
        """
        Belirtilen modelle KAMERA 2 videosunu test et
        
        Args:
            model_name: Model dosyası adı
            max_duration: Maksimum test süresi (saniye)
        """
        # KAMERA 2 videosunu bul
        kamera2_video = None
        for video in self.info['videos']:
            if 'KAMERA 2' in video:
                kamera2_video = video
                break
        
        if not kamera2_video:
            print("❌ KAMERA 2 videosu bulunamadı!")
            return False
        
        # Model dosyasını bul
        model_path = None
        for model in self.info['models']:
            if model_name in os.path.basename(model):
                model_path = model
                break
        
        if not model_path:
            print(f"❌ Model bulunamadı: {model_name}")
            return False
        
        video_name = os.path.basename(kamera2_video)
        
        print(f"\n🧪 TEK MODEL TEST BAŞLIYOR")
        print(f"📹 Video: {video_name}")
        print(f"🤖 Model: {model_name}")
        print(f"⏱️  Maksimum süre: {max_duration} saniye")
        print("-" * 50)
        
        # Çıktı klasörü oluştur
        output_folder = self.create_output_folder(model_name, video_name)
        
        # Video aç
        cap = cv2.VideoCapture(kamera2_video)
        if not cap.isOpened():
            print(f"❌ Video açılamadı: {kamera2_video}")
            return False
        
        # Video özellikleri
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📊 Video: {width}x{height} @ {fps:.1f} FPS")
        print(f"🎬 Toplam: {total_frames} kare ({total_frames/fps:.1f} saniye)")
        
        # Model yükle
        try:
            from ultralytics import YOLO
            model = YOLO(model_path)
            print(f"✅ Model yüklendi: {model_name}")
        except Exception as e:
            print(f"❌ Model yüklenemedi: {e}")
            cap.release()
            return False
        
        # Çıktı video
        output_video_path = os.path.join(output_folder, f"detection_result.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        # Test log dosyası
        log_path = os.path.join(output_folder, "test_log.txt")
        
        # İşleme döngüsü
        start_time = time.time()
        frame_count = 0
        total_detections = 0
        processing_times = []
        
        print(f"🔄 İşleme başlıyor... (Ctrl+C ile durdurun)")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("📹 Video sonu")
                    break
                
                frame_count += 1
                frame_start = time.time()
                
                # Kişi tespiti
                results = model(frame, conf=Detection.CONFIDENCE_THRESHOLD, verbose=False)
                
                # Tespitleri say ve çiz
                detections = 0
                for r in results:
                    boxes = r.boxes
                    if boxes is not None:
                        for box in boxes:
                            cls = int(box.cls.item())
                            if cls == 0:  # person
                                detections += 1
                                
                                # Koordinatları al
                                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                                conf = float(box.conf.item())
                                
                                # Minimum alan kontrolü
                                area = (x2 - x1) * (y2 - y1)
                                if area > Detection.MIN_AREA:
                                    # Çiz
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                    cv2.putText(frame, f"Person: {conf:.2f}", 
                                              (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                                              0.6, (0, 255, 0), 2)
                
                total_detections += detections
                
                # İlerleme bilgisi ekle
                elapsed = time.time() - start_time
                info_text = f"Kare: {frame_count} | Tespit: {detections} | " \
                           f"Toplam: {total_detections} | Süre: {elapsed:.1f}s"
                cv2.putText(frame, info_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # FPS
                fps_text = f"FPS: {frame_count/elapsed:.1f}"
                cv2.putText(frame, fps_text, (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Model adı
                cv2.putText(frame, model_name, (10, height-50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                # Video'ya yaz
                out.write(frame)
                
                # Performans takibi
                frame_time = time.time() - frame_start
                processing_times.append(frame_time)
                
                # Süre kontrolü
                if elapsed >= max_duration:
                    print(f"⏰ {max_duration} saniye doldu, test sonlandırılıyor...")
                    break
                
                # Her 50 karede bilgi ver
                if frame_count % 50 == 0:
                    avg_fps = frame_count / elapsed
                    print(f"   📊 {frame_count} kare | {avg_fps:.1f} FPS | "
                          f"Tespit: {total_detections} | Son: {detections}")
        
        except KeyboardInterrupt:
            print("⏹️  Test durduruldu")
        
        finally:
            cap.release()
            out.release()
        
        # Sonuçları hesapla ve kaydet
        elapsed_total = time.time() - start_time
        avg_fps = frame_count / elapsed_total if elapsed_total > 0 else 0
        avg_detections_per_frame = total_detections / frame_count if frame_count > 0 else 0
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Log dosyasına yaz
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"🧪 TEK MODEL TEST RAPORU\n")
            f.write(f"=======================\n\n")
            f.write(f"📹 Video: {video_name}\n")
            f.write(f"🤖 Model: {model_name}\n")
            f.write(f"📊 Video Özellikleri: {width}x{height} @ {fps:.1f} FPS\n")
            f.write(f"⏱️  Test Süresi: {elapsed_total:.2f} saniye\n")
            f.write(f"🎬 İşlenen Kare: {frame_count}\n")
            f.write(f"🚀 Ortalama FPS: {avg_fps:.2f}\n")
            f.write(f"👥 Toplam Tespit: {total_detections}\n")
            f.write(f"📈 Kare Başına Tespit: {avg_detections_per_frame:.2f}\n")
            f.write(f"⚡ Ortalama İşleme Süresi: {avg_processing_time:.3f}s/kare\n")
            f.write(f"💾 Çıktı Video: detection_result.mp4\n")
        
        print(f"\n📊 TEST SONUÇLARI:")
        print(f"   🎬 İşlenen kare: {frame_count}")
        print(f"   ⏱️  Toplam süre: {elapsed_total:.2f} saniye")
        print(f"   🚀 Ortalama FPS: {avg_fps:.2f}")
        print(f"   👥 Toplam tespit: {total_detections}")
        print(f"   📈 Kare başına tespit: {avg_detections_per_frame:.2f}")
        print(f"   📁 Çıktı klasörü: {os.path.basename(output_folder)}")
        
        return True

def test_yolov8x():
    """YOLOv8x modelini test et"""
    tester = SingleModelTester()
    
    # Mevcut modelleri listele
    available_models = [os.path.basename(m) for m in tester.info['models']]
    
    print(f"\n🔍 Mevcut modeller:")
    for i, model in enumerate(available_models, 1):
        highlight = "🎯" if "yolov8x" in model else "  "
        print(f"   {highlight} {i:2d}. {model}")
    
    # YOLOv8x modelini bul
    yolo8x_model = None
    for model in available_models:
        if "yolov8x" in model.lower():
            yolo8x_model = model
            break
    
    if not yolo8x_model:
        print("❌ YOLOv8x modeli bulunamadı!")
        return False
    
    print(f"\n🎯 Seçilen model: {yolo8x_model}")
    print(f"📹 Test videosu: KAMERA 2 KISA DATA.mov")
    print(f"⏱️  Test süresi: 2 dakika")
    
    # Onay iste
    response = input(f"\n▶️  YOLOv8x testi başlatılsın mı? (y/N): ")
    if response.lower() not in ['y', 'yes', 'evet', 'e']:
        print("❌ Test iptal edildi")
        return False
    
    # Testi çalıştır
    success = tester.test_single_model(yolo8x_model, max_duration=120)
    
    if success:
        print(f"\n✅ YOLOv8x testi başarıyla tamamlandı!")
        print(f"📁 Sonuçlar OUTPUT klasöründe")
    else:
        print(f"\n❌ YOLOv8x testi başarısız!")
    
    return success

if __name__ == "__main__":
    test_yolov8x()
