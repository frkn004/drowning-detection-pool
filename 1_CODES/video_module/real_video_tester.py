#!/usr/bin/env python3

"""
🎬 GERÇEK VIDEO TEST MODÜLÜ - 10 MODEL
=====================================
Gerçek kamera videolarını 10 farklı modelle test eder.
Her model için ayrı klasör oluşturur.
"""

import cv2
import os
import sys
import time
from datetime import datetime

# Ana dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Paths, Detection, System, get_project_info

class RealVideoTester:
    """
    🎥 Gerçek video test sınıfı - 10 Model
    """
    
    def __init__(self):
        self.info = get_project_info()
        print(f"🎬 {System.PROJECT_NAME} - 10 Model Video Tester")
        print(f"📊 {len(self.info['videos'])} video, {len(self.info['models'])} model bulundu")
    
    def create_output_folder(self, model_name, video_name):
        """
        Model ve video için özel klasör oluştur
        
        Format: OUTPUT/model_video_YYYYMMDD_HHMMSS/
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_short = os.path.splitext(model_name)[0]  # .pt uzantısını kaldır
        video_short = os.path.splitext(video_name)[0]  # uzantısını kaldır
        
        folder_name = f"{model_short}_{video_short}_{timestamp}"
        output_path = os.path.join(Paths.OUTPUT_DIR, folder_name)
        
        os.makedirs(output_path, exist_ok=True)
        
        print(f"📁 Çıktı klasörü: {folder_name}")
        return output_path
    
    def test_video_with_model(self, video_path, model_path, max_duration=120):
        """
        Belirli video + model kombinasyonunu test et
        
        Args:
            video_path: Video dosyası yolu
            model_path: Model dosyası yolu  
            max_duration: Maksimum test süresi (saniye)
        """
        video_name = os.path.basename(video_path)
        model_name = os.path.basename(model_path)
        
        print(f"\n🧪 TEST BAŞLIYOR")
        print(f"📹 Video: {video_name}")
        print(f"🤖 Model: {model_name}")
        print(f"⏱️  Maksimum süre: {max_duration} saniye")
        print("-" * 50)
        
        # Çıktı klasörü oluştur
        output_folder = self.create_output_folder(model_name, video_name)
        
        # Video aç
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Video açılamadı: {video_path}")
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
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # FPS
                fps_text = f"FPS: {frame_count/elapsed:.1f}"
                cv2.putText(frame, fps_text, (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Model adı
                cv2.putText(frame, model_name, (10, height-30), 
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
                
                # Her 100 karede bilgi ver
                if frame_count % 100 == 0:
                    avg_fps = frame_count / elapsed
                    print(f"   📊 {frame_count} kare | {avg_fps:.1f} FPS | "
                          f"Toplam tespit: {total_detections}")
        
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
            f.write(f"🧪 TEST RAPORU\n")
            f.write(f"===============\n\n")
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
        print(f"   �� Toplam tespit: {total_detections}")
        print(f"   📈 Kare başına tespit: {avg_detections_per_frame:.2f}")
        print(f"   📁 Çıktı klasörü: {os.path.basename(output_folder)}")
        
        return True

def test_kamera2_with_all_models():
    """KAMERA 2 videosuyla 10 modelin tamamını test et"""
    tester = RealVideoTester()
    
    # KAMERA 2 videosunu bul
    kamera2_video = None
    for video in tester.info['videos']:
        if 'KAMERA 2' in video:
            kamera2_video = video
            break
    
    if not kamera2_video:
        print("❌ KAMERA 2 videosu bulunamadı!")
        return
    
    print(f"🎯 Seçilen video: {os.path.basename(kamera2_video)}")
    
    # Tüm modelleri al
    available_models = [os.path.basename(m) for m in tester.info['models']]
    
    print(f"\n🧪 {len(available_models)} model ile test edilecek:")
    for i, model_name in enumerate(available_models, 1):
        print(f"   {i:2d}. ✅ {model_name}")
    
    print(f"\n⏱️  Her test 2 dakika sürecek")
    print(f"📁 Her model için ayrı klasör oluşacak")
    
    # Onay iste
    response = input(f"\n▶️  {len(available_models)} model testini başlatmak istiyor musun? (y/N): ")
    if response.lower() not in ['y', 'yes', 'evet', 'e']:
        print("❌ Test iptal edildi")
        return
    
    # Testleri çalıştır
    successful_tests = 0
    failed_tests = 0
    
    for i, model_name in enumerate(available_models, 1):
        model_path = os.path.join(Paths.MODELS_DIR, model_name)
        
        print(f"\n{'='*70}")
        print(f"🧪 TEST {i}/{len(available_models)}: {model_name}")
        print(f"{'='*70}")
        
        success = tester.test_video_with_model(
            kamera2_video, 
            model_path, 
            max_duration=120  # 2 dakika
        )
        
        if success:
            print(f"✅ Test {i} tamamlandı!")
            successful_tests += 1
        else:
            print(f"❌ Test {i} başarısız!")
            failed_tests += 1
        
        # Sonraki test için kısa bekleme (son test değilse)
        if i < len(available_models):
            print("\n⏳ 5 saniye sonra sonraki test...")
            time.sleep(5)
    
    print(f"\n🎉 TÜM TESTLER TAMAMLANDI!")
    print(f"✅ Başarılı: {successful_tests}")
    print(f"❌ Başarısız: {failed_tests}")
    print(f"📁 Sonuçlar: {Paths.OUTPUT_DIR}")
    
    return successful_tests, failed_tests

if __name__ == "__main__":
    test_kamera2_with_all_models()
