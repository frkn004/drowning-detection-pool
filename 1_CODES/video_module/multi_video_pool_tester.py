#!/usr/bin/env python3

"""
🎬 ÇOK VİDEO HAVUZ TEST MODÜLÜ
=============================
Her video için ayrı havuz alanı ile 5 dakikalık test.
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

class MultiVideoPoolTester:
    """
    🎬 Çok video havuz test sınıfı
    """
    
    def __init__(self):
        self.info = get_project_info()
        print(f"🎬 {System.PROJECT_NAME} - Çok Video Havuz Tester")
        print(f"📊 {len(self.info['videos'])} video, {len(self.info['models'])} model bulundu")
    
    def find_pool_area_for_video(self, video_name):
        """Video için en son havuz alanı dosyasını bul"""
        if not os.path.exists(Paths.OUTPUT_DIR):
            return None
        
        # Video adından dosya adı formatını oluştur
        video_base = os.path.splitext(video_name)[0].replace(" ", "_")
        
        # Eşleşen dosyaları bul
        pool_files = []
        for file in os.listdir(Paths.OUTPUT_DIR):
            if file.startswith("pool_area_") and file.endswith(".json"):
                if video_base.upper() in file.upper():
                    pool_files.append(file)
        
        if not pool_files:
            print(f"❌ {video_name} için havuz alanı bulunamadı!")
            return None
        
        # En son olanı seç
        pool_files.sort(reverse=True)
        latest_pool_file = pool_files[0]
        
        return os.path.join(Paths.OUTPUT_DIR, latest_pool_file)
    
    def load_pool_area(self, pool_file_path):
        """Havuz alanını JSON dosyasından yükle"""
        try:
            with open(pool_file_path, 'r', encoding='utf-8') as f:
                pool_data = json.load(f)
            
            polygon = np.array(pool_data['polygon_points'], dtype=np.int32)
            print(f"✅ Havuz alanı yüklendi: {os.path.basename(pool_file_path)}")
            print(f"🔢 Nokta sayısı: {len(polygon)}")
            
            return polygon
            
        except Exception as e:
            print(f"❌ Havuz alanı yüklenemedi: {e}")
            return None
    
    def is_point_in_pool(self, polygon, x, y):
        """Nokta havuz içinde mi kontrol et"""
        if polygon is None:
            return False
        
        result = cv2.pointPolygonTest(polygon, (x, y), False)
        return result >= 0
    
    def create_output_folder(self, model_name, video_name):
        """Model ve video için özel klasör oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_short = os.path.splitext(model_name)[0]
        video_short = os.path.splitext(video_name)[0].replace(" ", "_")
        
        folder_name = f"5MIN_{model_short}_{video_short}_{timestamp}"
        output_path = os.path.join(Paths.OUTPUT_DIR, folder_name)
        
        os.makedirs(output_path, exist_ok=True)
        
        print(f"📁 Çıktı klasörü: {folder_name}")
        return output_path
    
    def test_video_with_pool(self, video_path, model_path, pool_polygon, max_duration=300):
        """
        Video + model + havuz alanı ile test
        
        Args:
            video_path: Video dosyası yolu
            model_path: Model dosyası yolu
            pool_polygon: Havuz polygon noktaları
            max_duration: Maksimum test süresi (saniye) - 5 dakika = 300
        """
        video_name = os.path.basename(video_path)
        model_name = os.path.basename(model_path)
        
        print(f"\n🏊 5 DAKİKA HAVUZ TEST BAŞLIYOR")
        print(f"📹 Video: {video_name}")
        print(f"🤖 Model: {model_name}")
        print(f"🏊 Havuz noktası: {len(pool_polygon)}")
        print(f"⏱️  Test süresi: {max_duration//60} dakika")
        print("-" * 60)
        
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
        output_video_path = os.path.join(output_folder, f"5min_pool_result.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        # Test log dosyası
        log_path = os.path.join(output_folder, "5min_pool_log.txt")
        
        # Sayaçlar
        start_time = time.time()
        frame_count = 0
        total_detections = 0
        pool_inside_count = 0
        pool_outside_count = 0
        processing_times = []
        
        print(f"🔄 5 dakikalık işleme başlıyor... (Ctrl+C ile durdurun)")
        
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
                cv2.fillPoly(overlay, [pool_polygon], (0, 255, 255))  # Sarı
                cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
                
                # Havuz sınırını çiz
                cv2.polylines(frame, [pool_polygon], True, (0, 255, 255), 3)
                
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
                                    is_in_pool = self.is_point_in_pool(pool_polygon, center_x, center_y)
                                    
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
                                              0.5, color, 2)
                                    
                                    # Merkez noktayı işaretle
                                    cv2.circle(frame, (center_x, center_y), 4, color, -1)
                
                # Sayaçları güncelle
                total_detections += frame_detections
                pool_inside_count += frame_inside
                pool_outside_count += frame_outside
                
                # İlerleme bilgisi ekle
                elapsed = time.time() - start_time
                progress_percent = (elapsed / max_duration) * 100
                
                info_text1 = f"Kare: {frame_count} | {progress_percent:.1f}% | {frame_detections} tespit"
                info_text2 = f"Bu kare - Ici: {frame_inside} | Disi: {frame_outside}"
                info_text3 = f"TOPLAM - Ici: {pool_inside_count} | Disi: {pool_outside_count}"
                
                cv2.putText(frame, info_text1, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, info_text2, (10, 55), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, info_text3, (10, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Süre ve FPS
                time_text = f"Süre: {elapsed:.0f}s/{max_duration}s"
                fps_text = f"FPS: {frame_count/elapsed:.1f}"
                cv2.putText(frame, time_text, (10, 105), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, fps_text, (10, 130), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Video ve model adı
                cv2.putText(frame, video_name, (10, height-50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, model_name, (10, height-25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                # Video'ya yaz
                out.write(frame)
                
                # Performans takibi
                frame_time = time.time() - frame_start
                processing_times.append(frame_time)
                
                # Süre kontrolü
                if elapsed >= max_duration:
                    print(f"⏰ {max_duration} saniye (5 dakika) doldu, test sonlandırılıyor...")
                    break
                
                # Her 100 karede bilgi ver
                if frame_count % 100 == 0:
                    avg_fps = frame_count / elapsed
                    print(f"   📊 {frame_count} kare | {avg_fps:.1f} FPS | "
                          f"İçi: {pool_inside_count} | Dışı: {pool_outside_count} | "
                          f"%{progress_percent:.1f}")
        
        except KeyboardInterrupt:
            print("⏹️  Test durduruldu")
        
        finally:
            cap.release()
            out.release()
        
        # Sonuçları hesapla ve kaydet
        elapsed_total = time.time() - start_time
        avg_fps = frame_count / elapsed_total if elapsed_total > 0 else 0
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        pool_inside_percent = (pool_inside_count / total_detections * 100) if total_detections > 0 else 0
        
        # Log dosyasına yaz
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"🏊 5 DAKİKA HAVUZ TEST RAPORU\n")
            f.write(f"=============================\n\n")
            f.write(f"📹 Video: {video_name}\n")
            f.write(f"🤖 Model: {model_name}\n")
            f.write(f"🏊 Havuz noktası: {len(pool_polygon)}\n")
            f.write(f"📊 Video Özellikleri: {width}x{height} @ {fps:.1f} FPS\n")
            f.write(f"⏱️  Test Süresi: {elapsed_total:.2f} saniye ({elapsed_total/60:.1f} dakika)\n")
            f.write(f"🎬 İşlenen Kare: {frame_count}\n")
            f.write(f"🚀 Ortalama FPS: {avg_fps:.2f}\n")
            f.write(f"👥 Toplam Tespit: {total_detections}\n")
            f.write(f"🏊 Havuz İçi: {pool_inside_count} (%{pool_inside_percent:.1f})\n")
            f.write(f"🚶 Havuz Dışı: {pool_outside_count} (%{100-pool_inside_percent:.1f})\n")
            f.write(f"⚡ Ortalama İşleme Süresi: {avg_processing_time:.3f}s/kare\n")
            f.write(f"💾 Çıktı Video: 5min_pool_result.mp4\n")
        
        print(f"\n📊 5 DAKİKA TEST SONUÇLARI:")
        print(f"   🎬 İşlenen kare: {frame_count}")
        print(f"   ⏱️  Toplam süre: {elapsed_total:.2f} saniye ({elapsed_total/60:.1f} dakika)")
        print(f"   🚀 Ortalama FPS: {avg_fps:.2f}")
        print(f"   👥 Toplam tespit: {total_detections}")
        print(f"   🏊 Havuz içi: {pool_inside_count} (%{pool_inside_percent:.1f})")
        print(f"   🚶 Havuz dışı: {pool_outside_count} (%{100-pool_inside_percent:.1f})")
        print(f"   📁 Çıktı klasörü: {os.path.basename(output_folder)}")
        
        return True
    
    def test_all_videos_with_yolov8x(self):
        """Tüm videolarla YOLOv8x 5 dakika testi"""
        
        # YOLOv8x modelini bul
        yolo8x_model = None
        available_models = [os.path.basename(m) for m in self.info['models']]
        
        for model in available_models:
            if "yolov8x" in model.lower():
                yolo8x_model = model
                break
        
        if not yolo8x_model:
            print("❌ YOLOv8x modeli bulunamadı!")
            return False
        
        model_path = os.path.join(Paths.MODELS_DIR, yolo8x_model)
        
        print(f"\n🎯 ÇOK VİDEO 5 DAKİKA HAVUZ TESTİ")
        print(f"🤖 Model: {yolo8x_model}")
        print(f"📹 Video sayısı: {len(self.info['videos'])}")
        print(f"⏱️  Her video için: 5 dakika test")
        print(f"🏊 Her video kendi havuz alanı ile")
        
        # Onay iste
        response = input(f"\n▶️  {len(self.info['videos'])} video x 5 dakika testi başlatılsın mı? (y/N): ")
        if response.lower() not in ['y', 'yes', 'evet', 'e']:
            print("❌ Test iptal edildi")
            return False
        
        # Her video için test yap
        successful_tests = 0
        failed_tests = 0
        
        for i, video_path in enumerate(self.info['videos'], 1):
            video_name = os.path.basename(video_path)
            
            print(f"\n{'='*70}")
            print(f"🎬 VİDEO {i}/{len(self.info['videos'])}: {video_name}")
            print(f"{'='*70}")
            
            # Bu video için havuz alanını bul
            pool_file_path = self.find_pool_area_for_video(video_name)
            
            if not pool_file_path:
                print(f"❌ {video_name} için havuz alanı bulunamadı!")
                failed_tests += 1
                continue
            
            # Havuz alanını yükle
            pool_polygon = self.load_pool_area(pool_file_path)
            
            if pool_polygon is None:
                print(f"❌ {video_name} için havuz alanı yüklenemedi!")
                failed_tests += 1
                continue
            
            # Testi çalıştır
            success = self.test_video_with_pool(
                video_path, 
                model_path, 
                pool_polygon,
                max_duration=300  # 5 dakika
            )
            
            if success:
                print(f"✅ {video_name} testi tamamlandı!")
                successful_tests += 1
            else:
                print(f"❌ {video_name} testi başarısız!")
                failed_tests += 1
            
            # Sonraki test için bekleme (son test değilse)
            if i < len(self.info['videos']):
                print("\n⏳ 10 saniye sonra sonraki video...")
                time.sleep(10)
        
        print(f"\n🎉 TÜM 5 DAKİKA TESTLERİ TAMAMLANDI!")
        print(f"✅ Başarılı: {successful_tests}")
        print(f"❌ Başarısız: {failed_tests}")
        print(f"📁 Sonuçlar: {Paths.OUTPUT_DIR}")
        
        return successful_tests, failed_tests

if __name__ == "__main__":
    tester = MultiVideoPoolTester()
    tester.test_all_videos_with_yolov8x()
