#!/usr/bin/env python3

"""
🏊 GELİŞMİŞ HAVUZ TAKİP SİSTEMİ
===============================
1:32 dakikalık test + Havuz içi tespit artırma + Kişi takibi
"""

import cv2
import os
import sys
import time
import json
import numpy as np
from datetime import datetime
from collections import defaultdict

# Ana dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Paths, Detection, System, get_project_info

class EnhancedPoolTracker:
    """
    🏊 Gelişmiş havuz takip sınıfı
    """
    
    def __init__(self):
        self.info = get_project_info()
        self.person_tracks = {}  # Kişi takip bilgileri
        self.next_track_id = 1
        self.max_track_distance = 100  # Maksimum takip mesafesi
        
        print(f"🏊 {System.PROJECT_NAME} - Gelişmiş Havuz Takip Sistemi")
        print(f"📊 {len(self.info['videos'])} video, {len(self.info['models'])} model bulundu")
    
    def find_pool_area_for_video(self, video_name):
        """Video için en son havuz alanı dosyasını bul"""
        if not os.path.exists(Paths.OUTPUT_DIR):
            return None
        
        video_base = os.path.splitext(video_name)[0].replace(" ", "_")
        
        pool_files = []
        for file in os.listdir(Paths.OUTPUT_DIR):
            if file.startswith("pool_area_") and file.endswith(".json"):
                if video_base.upper() in file.upper():
                    pool_files.append(file)
        
        if not pool_files:
            print(f"❌ {video_name} için havuz alanı bulunamadı!")
            return None
        
        pool_files.sort(reverse=True)
        return os.path.join(Paths.OUTPUT_DIR, pool_files[0])
    
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
    
    def calculate_distance(self, point1, point2):
        """İki nokta arası mesafe"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def assign_track_id(self, center_x, center_y, frame_number):
        """Kişiye takip ID'si ata"""
        current_pos = (center_x, center_y)
        
        # Mevcut track'ler arasından en yakınını bul
        best_match_id = None
        min_distance = float('inf')
        
        for track_id, track_info in self.person_tracks.items():
            if frame_number - track_info['last_frame'] < 30:  # 30 kare içinde görülmüş
                last_pos = track_info['positions'][-1]
                distance = self.calculate_distance(current_pos, last_pos)
                
                if distance < self.max_track_distance and distance < min_distance:
                    min_distance = distance
                    best_match_id = track_id
        
        # Eşleşme bulundu
        if best_match_id is not None:
            self.person_tracks[best_match_id]['positions'].append(current_pos)
            self.person_tracks[best_match_id]['last_frame'] = frame_number
            return best_match_id
        
        # Yeni track oluştur
        new_id = self.next_track_id
        self.next_track_id += 1
        
        self.person_tracks[new_id] = {
            'positions': [current_pos],
            'first_frame': frame_number,
            'last_frame': frame_number,
            'in_pool_frames': 0,
            'out_pool_frames': 0
        }
        
        return new_id
    
    def create_output_folder(self, model_name, video_name):
        """Model ve video için özel klasör oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_short = os.path.splitext(model_name)[0]
        video_short = os.path.splitext(video_name)[0].replace(" ", "_")
        
        folder_name = f"TRACK_{model_short}_{video_short}_{timestamp}"
        output_path = os.path.join(Paths.OUTPUT_DIR, folder_name)
        
        os.makedirs(output_path, exist_ok=True)
        
        print(f"📁 Çıktı klasörü: {folder_name}")
        return output_path
    
    def test_enhanced_pool_tracking(self, video_path, model_path, pool_polygon, max_duration=92):
        """
        Gelişmiş havuz takip testi - 1:32 dakika
        
        Args:
            video_path: Video dosyası yolu
            model_path: Model dosyası yolu
            pool_polygon: Havuz polygon noktaları
            max_duration: Test süresi (92 saniye = 1:32)
        """
        video_name = os.path.basename(video_path)
        model_name = os.path.basename(model_path)
        
        print(f"\n🏊 GELİŞMİŞ HAVUZ TAKİP TEST BAŞLIYOR")
        print(f"📹 Video: {video_name}")
        print(f"🤖 Model: {model_name}")
        print(f"🏊 Havuz noktası: {len(pool_polygon)}")
        print(f"⏱️  Test süresi: 1:32 dakika ({max_duration} saniye)")
        print(f"🔍 HASSASİYET ARTIRILIYOR!")
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
        output_video_path = os.path.join(output_folder, f"enhanced_pool_tracking.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        # Test log dosyası
        log_path = os.path.join(output_folder, "enhanced_tracking_log.txt")
        
        # Sayaçlar
        start_time = time.time()
        frame_count = 0
        total_detections = 0
        pool_inside_count = 0
        pool_outside_count = 0
        unique_pool_persons = set()
        unique_outside_persons = set()
        processing_times = []
        
        # Takip istatistikleri
        track_stats = defaultdict(lambda: {'pool_time': 0, 'outside_time': 0, 'total_frames': 0})
        
        print(f"🔄 1:32 dakikalık gelişmiş takip başlıyor...")
        print(f"🎯 Havuz içi hassasiyet ARTIRILDI!")
        
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
                cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)
                
                # Havuz sınırını çiz (kalın çizgi)
                cv2.polylines(frame, [pool_polygon], True, (0, 255, 255), 4)
                
                # HAVUZ İÇİ İÇİN DÜŞÜK CONFIDENCE THRESHOLD
                pool_confidence = max(0.3, Detection.CONFIDENCE_THRESHOLD - 0.2)
                
                # Kişi tespiti - NORMAL CONFIDENCE
                results = model(frame, conf=Detection.CONFIDENCE_THRESHOLD, verbose=False)
                
                # Bu karedeki sayaçlar
                frame_detections = 0
                frame_inside = 0
                frame_outside = 0
                current_frame_persons = []
                
                # İlk geçiş - normal tespit
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
                                    
                                    current_frame_persons.append({
                                        'bbox': (x1, y1, x2, y2),
                                        'center': (center_x, center_y),
                                        'conf': conf,
                                        'area': area
                                    })
                
                # HAVUZ İÇİ İÇİN İKİNCİ GEÇIŞ - DÜŞÜK CONFIDENCE
                if pool_confidence < Detection.CONFIDENCE_THRESHOLD:
                    results_pool = model(frame, conf=pool_confidence, verbose=False)
                    
                    for r in results_pool:
                        boxes = r.boxes
                        if boxes is not None:
                            for box in boxes:
                                cls = int(box.cls.item())
                                if cls == 0:  # person
                                    # Koordinatları al
                                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                                    conf = float(box.conf.item())
                                    
                                    # Sadece havuz içindekiler için düşük confidence kabul et
                                    center_x = (x1 + x2) // 2
                                    center_y = (y1 + y2) // 2
                                    
                                    if self.is_point_in_pool(pool_polygon, center_x, center_y):
                                        area = (x2 - x1) * (y2 - y1)
                                        if area > Detection.MIN_AREA // 2:  # Havuz içi için daha küçük alan
                                            # Bu tespit zaten var mı kontrol et
                                            is_duplicate = False
                                            for existing in current_frame_persons:
                                                if self.calculate_distance((center_x, center_y), existing['center']) < 50:
                                                    is_duplicate = True
                                                    break
                                            
                                            if not is_duplicate:
                                                current_frame_persons.append({
                                                    'bbox': (x1, y1, x2, y2),
                                                    'center': (center_x, center_y),
                                                    'conf': conf,
                                                    'area': area,
                                                    'pool_enhanced': True
                                                })
                
                # Tespitleri işle ve çiz
                for person in current_frame_persons:
                    x1, y1, x2, y2 = person['bbox']
                    center_x, center_y = person['center']
                    conf = person['conf']
                    is_enhanced = person.get('pool_enhanced', False)
                    
                    # Takip ID'si ata
                    track_id = self.assign_track_id(center_x, center_y, frame_count)
                    
                    # Havuz içinde mi?
                    is_in_pool = self.is_point_in_pool(pool_polygon, center_x, center_y)
                    
                    if is_in_pool:
                        frame_inside += 1
                        unique_pool_persons.add(track_id)
                        self.person_tracks[track_id]['in_pool_frames'] += 1
                        track_stats[track_id]['pool_time'] += 1
                        
                        # Havuz içi - Yeşil (daha kalın çerçeve)
                        color = (0, 255, 0)
                        thickness = 3
                        if is_enhanced:
                            label = f"HAVUZ ICI #{track_id}: {conf:.2f} [E]"
                        else:
                            label = f"HAVUZ ICI #{track_id}: {conf:.2f}"
                    else:
                        frame_outside += 1
                        unique_outside_persons.add(track_id)
                        self.person_tracks[track_id]['out_pool_frames'] += 1
                        track_stats[track_id]['outside_time'] += 1
                        
                        # Havuz dışı - Kırmızı
                        color = (0, 0, 255)
                        thickness = 2
                        label = f"HAVUZ DISI #{track_id}: {conf:.2f}"
                    
                    track_stats[track_id]['total_frames'] += 1
                    
                    # Kutuyu çiz
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                    cv2.putText(frame, label, 
                              (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.5, color, 2)
                    
                    # Merkez noktayı işaretle (daha büyük)
                    cv2.circle(frame, (center_x, center_y), 6, color, -1)
                    
                    # Track ID'sini merkeze yaz
                    cv2.putText(frame, str(track_id), 
                               (center_x-10, center_y+5), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.6, (255, 255, 255), 2)
                
                # Sayaçları güncelle
                total_detections += len(current_frame_persons)
                pool_inside_count += frame_inside
                pool_outside_count += frame_outside
                
                # İlerleme bilgisi ekle
                elapsed = time.time() - start_time
                progress_percent = (elapsed / max_duration) * 100
                
                # Üst bilgi paneli
                info_text1 = f"Kare: {frame_count} | %{progress_percent:.1f} | Tespit: {len(current_frame_persons)}"
                info_text2 = f"Bu kare - Havuz Ici: {frame_inside} | Havuz Disi: {frame_outside}"
                info_text3 = f"TOPLAM - Ici: {pool_inside_count} | Disi: {pool_outside_count}"
                info_text4 = f"BENZERSIZ - Havuz: {len(unique_pool_persons)} | Dis: {len(unique_outside_persons)}"
                
                # Bilgi paneli arka planı
                cv2.rectangle(frame, (5, 5), (width-5, 140), (0, 0, 0), -1)
                cv2.rectangle(frame, (5, 5), (width-5, 140), (255, 255, 255), 2)
                
                cv2.putText(frame, info_text1, (10, 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, info_text2, (10, 45), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, info_text3, (10, 65), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, info_text4, (10, 85), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Süre ve FPS
                time_text = f"Süre: {elapsed:.0f}s/92s (1:32)"
                fps_text = f"FPS: {frame_count/elapsed:.1f}"
                cv2.putText(frame, time_text, (10, 105), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, fps_text, (10, 125), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Alt bilgi paneli
                cv2.rectangle(frame, (5, height-80), (width-5, height-5), (0, 0, 0), -1)
                cv2.rectangle(frame, (5, height-80), (width-5, height-5), (255, 255, 255), 2)
                
                cv2.putText(frame, f"Video: {video_name}", (10, height-55), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Model: {model_name}", (10, height-35), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, "GELISMIS HAVUZ TAKIP - HASSASIYET ARTIRILDI", (10, height-15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Video'ya yaz
                out.write(frame)
                
                # Performans takibi
                frame_time = time.time() - frame_start
                processing_times.append(frame_time)
                
                # Süre kontrolü
                if elapsed >= max_duration:
                    print(f"⏰ 92 saniye (1:32 dakika) doldu, test sonlandırılıyor...")
                    break
                
                # Her 50 karede bilgi ver
                if frame_count % 50 == 0:
                    avg_fps = frame_count / elapsed
                    print(f"   📊 {frame_count} kare | {avg_fps:.1f} FPS | "
                          f"Havuz: {len(unique_pool_persons)} kişi | "
                          f"Dış: {len(unique_outside_persons)} kişi | %{progress_percent:.1f}")
        
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
        
        # Takip analizi
        long_term_pool_persons = []
        for track_id, stats in track_stats.items():
            if stats['pool_time'] > 10:  # 10+ kare havuzda
                long_term_pool_persons.append(track_id)
        
        # Log dosyasına yaz
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"🏊 GELİŞMİŞ HAVUZ TAKİP RAPORU (1:32 DAKİKA)\n")
            f.write(f"=============================================\n\n")
            f.write(f"📹 Video: {video_name}\n")
            f.write(f"🤖 Model: {model_name}\n")
            f.write(f"🏊 Havuz noktası: {len(pool_polygon)}\n")
            f.write(f"📊 Video Özellikleri: {width}x{height} @ {fps:.1f} FPS\n")
            f.write(f"⏱️  Test Süresi: {elapsed_total:.2f} saniye (1:32 dakika)\n")
            f.write(f"�� İşlenen Kare: {frame_count}\n")
            f.write(f"🚀 Ortalama FPS: {avg_fps:.2f}\n")
            f.write(f"👥 Toplam Tespit: {total_detections}\n")
            f.write(f"🏊 Havuz İçi Tespit: {pool_inside_count} (%{pool_inside_percent:.1f})\n")
            f.write(f"🚶 Havuz Dışı Tespit: {pool_outside_count} (%{100-pool_inside_percent:.1f})\n")
            f.write(f"🆔 Benzersiz Havuz Kişisi: {len(unique_pool_persons)}\n")
            f.write(f"🆔 Benzersiz Dış Kişi: {len(unique_outside_persons)}\n")
            f.write(f"📈 Uzun Süreli Havuz Kullanıcısı: {len(long_term_pool_persons)}\n")
            f.write(f"⚡ Ortalama İşleme Süresi: {avg_processing_time:.3f}s/kare\n")
            f.write(f"💾 Çıktı Video: enhanced_pool_tracking.mp4\n\n")
            
            f.write(f"📋 DETAYLI TAKİP İSTATİSTİKLERİ:\n")
            f.write(f"================================\n")
            for track_id in sorted(track_stats.keys()):
                stats = track_stats[track_id]
                pool_ratio = (stats['pool_time'] / stats['total_frames'] * 100) if stats['total_frames'] > 0 else 0
                f.write(f"Kişi #{track_id}: Havuz {stats['pool_time']} kare (%{pool_ratio:.1f}) | "
                       f"Dış {stats['outside_time']} kare | Toplam {stats['total_frames']} kare\n")
        
        print(f"\n📊 GELİŞMİŞ TAKİP SONUÇLARI (1:32 DAKİKA):")
        print(f"   🎬 İşlenen kare: {frame_count}")
        print(f"   ⏱️  Toplam süre: {elapsed_total:.2f} saniye")
        print(f"   🚀 Ortalama FPS: {avg_fps:.2f}")
        print(f"   👥 Toplam tespit: {total_detections}")
        print(f"   🏊 Havuz içi: {pool_inside_count} (%{pool_inside_percent:.1f})")
        print(f"   🚶 Havuz dışı: {pool_outside_count} (%{100-pool_inside_percent:.1f})")
        print(f"   🆔 Benzersiz havuz kişisi: {len(unique_pool_persons)}")
        print(f"   🆔 Benzersiz dış kişi: {len(unique_outside_persons)}")
        print(f"   📈 Uzun süreli havuz kullanıcısı: {len(long_term_pool_persons)}")
        print(f"   📁 Çıktı klasörü: {os.path.basename(output_folder)}")
        
        return True

def test_enhanced_system():
    """Gelişmiş sistemi test et"""
    
    tracker = EnhancedPoolTracker()
    
    # YOLOv8x modelini bul
    yolo8x_model = None
    available_models = [os.path.basename(m) for m in tracker.info['models']]
    
    for model in available_models:
        if "yolov8x" in model.lower():
            yolo8x_model = model
            break
    
    if not yolo8x_model:
        print("❌ YOLOv8x modeli bulunamadı!")
        return False
    
    model_path = os.path.join(Paths.MODELS_DIR, yolo8x_model)
    
    print(f"\n🏊 GELİŞMİŞ HAVUZ TAKİP SİSTEMİ")
    print(f"🤖 Model: {yolo8x_model}")
    print(f"📹 Video sayısı: {len(tracker.info['videos'])}")
    print(f"⏱️  Test süresi: 1:32 dakika (92 saniye)")
    print(f"🔍 Havuz içi hassasiyet ARTIRILDI")
    print(f"🆔 Kişi takip sistemi AKTİF")
    
    # Hangi videoyu test etmek istiyor?
    if len(tracker.info['videos']) > 1:
        print(f"\n📽️  Mevcut videolar:")
        for i, video_path in enumerate(tracker.info['videos'], 1):
            video_name = os.path.basename(video_path)
            print(f"   {i}. {video_name}")
        
        try:
            choice = input(f"\nHangi videoyu test etmek istiyorsun? (1-{len(tracker.info['videos'])} veya 'all'): ").strip()
            
            if choice.lower() == 'all':
                selected_videos = tracker.info['videos']
            else:
                video_index = int(choice) - 1
                if 0 <= video_index < len(tracker.info['videos']):
                    selected_videos = [tracker.info['videos'][video_index]]
                else:
                    print("❌ Geçersiz seçim!")
                    return False
        except ValueError:
            print("❌ Geçersiz giriş!")
            return False
    else:
        selected_videos = tracker.info['videos']
    
    # Testleri çalıştır
    successful_tests = 0
    failed_tests = 0
    
    for i, video_path in enumerate(selected_videos, 1):
        video_name = os.path.basename(video_path)
        
        print(f"\n{'='*70}")
        print(f"🎬 VİDEO {i}/{len(selected_videos)}: {video_name}")
        print(f"{'='*70}")
        
        # Bu video için havuz alanını bul
        pool_file_path = tracker.find_pool_area_for_video(video_name)
        
        if not pool_file_path:
            print(f"❌ {video_name} için havuz alanı bulunamadı!")
            failed_tests += 1
            continue
        
        # Havuz alanını yükle
        pool_polygon = tracker.load_pool_area(pool_file_path)
        
        if pool_polygon is None:
            print(f"❌ {video_name} için havuz alanı yüklenemedi!")
            failed_tests += 1
            continue
        
        # Testi çalıştır
        success = tracker.test_enhanced_pool_tracking(
            video_path, 
            model_path, 
            pool_polygon,
            max_duration=92  # 1:32 dakika
        )
        
        if success:
            print(f"✅ {video_name} gelişmiş takip testi tamamlandı!")
            successful_tests += 1
        else:
            print(f"❌ {video_name} testi başarısız!")
            failed_tests += 1
        
        # Sonraki test için bekleme (son test değilse)
        if i < len(selected_videos):
            print("\n⏳ 5 saniye sonra sonraki video...")
            time.sleep(5)
    
    print(f"\n🎉 GELİŞMİŞ TAKİP TESTLERİ TAMAMLANDI!")
    print(f"✅ Başarılı: {successful_tests}")
    print(f"❌ Başarısız: {failed_tests}")
    print(f"📁 Sonuçlar: {Paths.OUTPUT_DIR}")
    
    return successful_tests, failed_tests

if __name__ == "__main__":
    test_enhanced_system()
