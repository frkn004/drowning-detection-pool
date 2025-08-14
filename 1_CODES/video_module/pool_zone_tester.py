#!/usr/bin/env python3

"""
🏊 HAVUZ ALANI TEST MODÜLÜ
=========================
Havuz içi ve dışı kişileri ayrı ayrı tespit eder.
"""

import cv2
import os
import sys
import time
import json
import numpy as np
from datetime import datetime

# Ana dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Paths, Detection, System, get_project_info

class PoolZoneTester:
    """
    🏊 Havuz alanı test sınıfı
    """
    
    def __init__(self):
        self.info = get_project_info()
        self.pool_polygon = None
        print(f"🏊 {System.PROJECT_NAME} - Havuz Alanı Tester")
        print(f"📊 {len(self.info['videos'])} video, {len(self.info['models'])} model bulundu")
    
    def load_pool_area(self):
        """
        Kaydedilmiş havuz alanını yükle
        """
        if not os.path.exists(Paths.OUTPUT_DIR):
            print("❌ OUTPUT klasörü bulunamadı!")
            return False
        
        # En son oluşturulan pool_area dosyasını bul
        pool_files = []
        for file in os.listdir(Paths.OUTPUT_DIR):
            if file.startswith("pool_area_") and file.endswith(".json"):
                pool_files.append(file)
        
        if not pool_files:
            print("❌ Havuz alanı dosyası bulunamadı!")
            print("🔧 Önce pool_area_definer.py ile havuz alanını belirleyin")
            return False
        
        # En son olanı seç
        pool_files.sort(reverse=True)
        latest_pool_file = pool_files[0]
        pool_path = os.path.join(Paths.OUTPUT_DIR, latest_pool_file)
        
        try:
            with open(pool_path, 'r', encoding='utf-8') as f:
                pool_data = json.load(f)
            
            self.pool_polygon = np.array(pool_data['polygon_points'], dtype=np.int32)
            
            print(f"✅ Havuz alanı yüklendi: {latest_pool_file}")
            print(f"🔢 Nokta sayısı: {len(self.pool_polygon)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Havuz alanı yüklenemedi: {e}")
            return False
    
    def is_point_in_pool(self, x, y):
        """
        Nokta havuz içinde mi kontrol et
        
        Args:
            x, y: Kontrol edilecek nokta koordinatları
            
        Returns:
            bool: True ise havuz içinde
        """
        if self.pool_polygon is None:
            return False
        
        result = cv2.pointPolygonTest(self.pool_polygon, (x, y), False)
        return result >= 0
    
    def create_output_folder(self, model_name, video_name):
        """Model ve video için özel klasör oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_short = os.path.splitext(model_name)[0]
        video_short = os.path.splitext(video_name)[0]
        
        folder_name = f"POOL_{model_short}_{video_short}_{timestamp}"
        output_path = os.path.join(Paths.OUTPUT_DIR, folder_name)
        
        os.makedirs(output_path, exist_ok=True)
        
        print(f"📁 Çıktı klasörü: {folder_name}")
        return output_path
    
    def test_with_pool_zones(self, model_name, max_duration=120):
        """
        Havuz alanı ile model testi
        
        Args:
            model_name: Model dosyası adı
            max_duration: Maksimum test süresi (saniye)
        """
        # Havuz alanını yükle
        if not self.load_pool_area():
            return False
        
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
        
        print(f"\n🏊 HAVUZ ALANI TEST BAŞLIYOR")
        print(f"📹 Video: {video_name}")
        print(f"🤖 Model: {model_name}")
        print(f"🏊 Havuz alanı: {len(self.pool_polygon)} nokta")
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
        output_video_path = os.path.join(output_folder, f"pool_zone_result.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        # Test log dosyası
        log_path = os.path.join(output_folder, "pool_zone_log.txt")
        
        # Sayaçlar
        start_time = time.time()
        frame_count = 0
        total_detections = 0
        pool_inside_count = 0
        pool_outside_count = 0
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
                
                # Havuz alanını çiz (yarı saydam)
                overlay = frame.copy()
                cv2.fillPoly(overlay, [self.pool_polygon], (0, 255, 255))  # Sarı
                cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
                
                # Havuz sınırını çiz
                cv2.polylines(frame, [self.pool_polygon], True, (0, 255, 255), 3)
                
                # Kişi tespiti
                results = model(frame, conf=Detection.CONFIDENCE_THRESHOLD, verbose=False)
                
                # Bu karedeki sayaçlar
                frame_detections = 0
                frame_inside = 0
                frame_outside = 0
                
                # Tespitleri işle
                for r in results:
                    boxes = r.boxes
                    if boxes is not None:
                        for box in boxes:
                            cls = int(box.cls.item())
                            if cls == 0:  # person
                                frame_detections += 1
                                
                                # Koordinatları al
                                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                                conf = float(box.conf.item())
                                
                                # Minimum alan kontrolü
                                area = (x2 - x1) * (y2 - y1)
                                if area > Detection.MIN_AREA:
                                    # Merkez noktayı hesapla
                                    center_x = (x1 + x2) // 2
                                    center_y = (y1 + y2) // 2
                                    
                                    # Havuz içinde mi?
                                    is_in_pool = self.is_point_in_pool(center_x, center_y)
                                    
                                    if is_in_pool:
                                        frame_inside += 1
                                        # Havuz içi - Yeşil
                                        color = (0, 255, 0)
                                        label = f"HAVUZ ICI: {conf:.2f}"
                                    else:
                                        frame_outside += 1
                                        # Havuz dışı - Kırmızı
                                        color = (0, 0, 255)
                                        label = f"HAVUZ DISI: {conf:.2f}"
                                    
                                    # Kutuyu çiz
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                    cv2.putText(frame, label, 
                                              (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                                              0.6, color, 2)
                                    
                                    # Merkez noktayı işaretle
                                    cv2.circle(frame, (center_x, center_y), 5, color, -1)
                
                # Sayaçları güncelle
                total_detections += frame_detections
                pool_inside_count += frame_inside
                pool_outside_count += frame_outside
                
                # İlerleme bilgisi ekle
                elapsed = time.time() - start_time
                info_text1 = f"Kare: {frame_count} | Toplam: {frame_detections}"
                info_text2 = f"Havuz Ici: {frame_inside} | Havuz Disi: {frame_outside}"
                info_text3 = f"TOPLAM - Ici: {pool_inside_count} | Disi: {pool_outside_count}"
                
                cv2.putText(frame, info_text1, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, info_text2, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, info_text3, (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # FPS
                fps_text = f"FPS: {frame_count/elapsed:.1f}"
                cv2.putText(frame, fps_text, (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Model adı
                cv2.putText(frame, f"Model: {model_name}", (10, height-50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
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
                          f"İçi: {pool_inside_count} | Dışı: {pool_outside_count}")
        
        except KeyboardInterrupt:
            print("⏹️  Test durduruldu")
        
        finally:
            cap.release()
            out.release()
        
        # Sonuçları hesapla ve kaydet
        elapsed_total = time.time() - start_time
        avg_fps = frame_count / elapsed_total if elapsed_total > 0 else 0
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Log dosyasına yaz
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"🏊 HAVUZ ALANI TEST RAPORU\n")
            f.write(f"==========================\n\n")
            f.write(f"📹 Video: {video_name}\n")
            f.write(f"🤖 Model: {model_name}\n")
            f.write(f"🏊 Havuz alanı nokta sayısı: {len(self.pool_polygon)}\n")
            f.write(f"📊 Video Özellikleri: {width}x{height} @ {fps:.1f} FPS\n")
            f.write(f"⏱️  Test Süresi: {elapsed_total:.2f} saniye\n")
            f.write(f"🎬 İşlenen Kare: {frame_count}\n")
            f.write(f"🚀 Ortalama FPS: {avg_fps:.2f}\n")
            f.write(f"👥 Toplam Tespit: {total_detections}\n")
            f.write(f"🏊 Havuz İçi: {pool_inside_count}\n")
            f.write(f"🚶 Havuz Dışı: {pool_outside_count}\n")
            f.write(f"📈 Havuz İçi Oranı: {(pool_inside_count/total_detections*100):.1f}%\n")
            f.write(f"⚡ Ortalama İşleme Süresi: {avg_processing_time:.3f}s/kare\n")
            f.write(f"💾 Çıktı Video: pool_zone_result.mp4\n")
        
        print(f"\n📊 HAVUZ ALANI TEST SONUÇLARI:")
        print(f"   🎬 İşlenen kare: {frame_count}")
        print(f"   ⏱️  Toplam süre: {elapsed_total:.2f} saniye")
        print(f"   🚀 Ortalama FPS: {avg_fps:.2f}")
        print(f"   👥 Toplam tespit: {total_detections}")
        print(f"   🏊 Havuz içi: {pool_inside_count}")
        print(f"   🚶 Havuz dışı: {pool_outside_count}")
        print(f"   📈 Havuz içi oranı: {(pool_inside_count/total_detections*100):.1f}%")
        print(f"   📁 Çıktı klasörü: {os.path.basename(output_folder)}")
        
        return True

def test_yolov8x_with_pool_zones():
    """YOLOv8x modelini havuz alanları ile test et"""
    tester = PoolZoneTester()
    
    # Mevcut modelleri listele
    available_models = [os.path.basename(m) for m in tester.info['models']]
    
    # YOLOv8x modelini bul
    yolo8x_model = None
    for model in available_models:
        if "yolov8x" in model.lower():
            yolo8x_model = model
            break
    
    if not yolo8x_model:
        print("❌ YOLOv8x modeli bulunamadı!")
        return False
    
    print(f"\n🏊 HAVUZ ALANI TESTİ")
    print(f"🎯 Model: {yolo8x_model}")
    print(f"📹 Video: KAMERA 2 KISA DATA.mov")
    print(f"⏱️  Test süresi: 2 dakika")
    print(f"🟢 Havuz içi: Yeşil kutular")
    print(f"🔴 Havuz dışı: Kırmızı kutular")
    
    # Onay iste
    response = input(f"\n▶️  Havuz alanı testi başlatılsın mı? (y/N): ")
    if response.lower() not in ['y', 'yes', 'evet', 'e']:
        print("❌ Test iptal edildi")
        return False
    
    # Testi çalıştır
    success = tester.test_with_pool_zones(yolo8x_model, max_duration=120)
    
    if success:
        print(f"\n✅ Havuz alanı testi başarıyla tamamlandı!")
        print(f"📁 Sonuçlar OUTPUT klasöründe")
    else:
        print(f"\n❌ Havuz alanı testi başarısız!")
    
    return success

if __name__ == "__main__":
    test_yolov8x_with_pool_zones()
