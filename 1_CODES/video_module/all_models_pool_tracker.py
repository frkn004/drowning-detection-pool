#!/usr/bin/env python3

"""
🤖 TÜM MODELLER HAVUZ TAKİP SİSTEMİ
===================================
10 modelin tamamı ile 1:32 dakikalık gelişmiş havuz takibi
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

class AllModelsPoolTracker:
    """
    🤖 Tüm modeller havuz takip sınıfı
    """
    
    def __init__(self):
        self.info = get_project_info()
        print(f"🤖 {System.PROJECT_NAME} - 10 Model Havuz Takip Sistemi")
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
    
    def create_output_folder(self, model_name, video_name):
        """Model ve video için özel klasör oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_short = os.path.splitext(model_name)[0]
        video_short = os.path.splitext(video_name)[0].replace(" ", "_")
        
        folder_name = f"ALL10_{model_short}_{video_short}_{timestamp}"
        output_path = os.path.join(Paths.OUTPUT_DIR, folder_name)
        
        os.makedirs(output_path, exist_ok=True)
        
        return output_path
    
    def test_single_model_with_tracking(self, video_path, model_path, pool_polygon, max_duration=92):
        """
        Tek model ile gelişmiş havuz takip testi
        """
        video_name = os.path.basename(video_path)
        model_name = os.path.basename(model_path)
        
        # Çıktı klasörü oluştur
        output_folder = self.create_output_folder(model_name, video_name)
        
        # Video aç
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Video açılamadı: {video_path}")
            return None
        
        # Video özellikleri
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Model yükle
        try:
            from ultralytics import YOLO
            model = YOLO(model_path)
        except Exception as e:
            print(f"❌ {model_name} yüklenemedi: {e}")
            cap.release()
            return None
        
        # Çıktı video (sadece ilk 3 model için video kaydet - disk alanı tasarrufu)
        save_video = model_name in ['yolov8x.pt', 'yolov12m_drowning_best.pt', 'yolo11l.pt']
        
        if save_video:
            output_video_path = os.path.join(output_folder, f"tracking_result.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        else:
            out = None
        
        # Sayaçlar
        start_time = time.time()
        frame_count = 0
        total_detections = 0
        pool_inside_count = 0
        pool_outside_count = 0
        unique_pool_persons = set()
        unique_outside_persons = set()
        
        # Kişi takip sistemi
        person_tracks = {}
        next_track_id = 1
        max_track_distance = 100
        
        # İşleme döngüsü
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                frame_start = time.time()
                
                # Süre kontrolü önce
                elapsed = time.time() - start_time
                if elapsed >= max_duration:
                    break
                
                # Havuz alanını çiz (sadece video kaydediliyorsa)
                if save_video:
                    overlay = frame.copy()
                    cv2.fillPoly(overlay, [pool_polygon], (0, 255, 255))
                    cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
                    cv2.polylines(frame, [pool_polygon], True, (0, 255, 255), 3)
                
                # Normal tespit
                results = model(frame, conf=Detection.CONFIDENCE_THRESHOLD, verbose=False)
                
                # Havuz içi için düşük confidence
                pool_confidence = max(0.3, Detection.CONFIDENCE_THRESHOLD - 0.2)
                results_pool = model(frame, conf=pool_confidence, verbose=False)
                
                # Tespitleri topla
                current_frame_persons = []
                
                # Normal tespitler
                for r in results:
                    boxes = r.boxes
                    if boxes is not None:
                        for box in boxes:
                            cls = int(box.cls.item())
                            if cls == 0:  # person
                                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                                conf = float(box.conf.item())
                                area = (x2 - x1) * (y2 - y1)
                                
                                if area > Detection.MIN_AREA:
                                    center_x = (x1 + x2) // 2
                                    center_y = (y1 + y2) // 2
                                    
                                    current_frame_persons.append({
                                        'bbox': (x1, y1, x2, y2),
                                        'center': (center_x, center_y),
                                        'conf': conf,
                                        'area': area
                                    })
                
                # Havuz içi enhanced tespitler
                for r in results_pool:
                    boxes = r.boxes
                    if boxes is not None:
                        for box in boxes:
                            cls = int(box.cls.item())
                            if cls == 0:  # person
                                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                                conf = float(box.conf.item())
                                center_x = (x1 + x2) // 2
                                center_y = (y1 + y2) // 2
                                
                                # Sadece havuz içindekiler için düşük confidence
                                if self.is_point_in_pool(pool_polygon, center_x, center_y):
                                    area = (x2 - x1) * (y2 - y1)
                                    if area > Detection.MIN_AREA // 2:
                                        # Dublicate kontrolü
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
                                                'enhanced': True
                                            })
                
                # Track ID atama ve sayaçları güncelleme
                frame_inside = 0
                frame_outside = 0
                
                for person in current_frame_persons:
                    center_x, center_y = person['center']
                    
                    # Track ID ata
                    current_pos = (center_x, center_y)
                    best_match_id = None
                    min_distance = float('inf')
                    
                    for track_id, track_info in person_tracks.items():
                        if frame_count - track_info['last_frame'] < 30:
                            last_pos = track_info['positions'][-1]
                            distance = self.calculate_distance(current_pos, last_pos)
                            
                            if distance < max_track_distance and distance < min_distance:
                                min_distance = distance
                                best_match_id = track_id
                    
                    if best_match_id is not None:
                        person_tracks[best_match_id]['positions'].append(current_pos)
                        person_tracks[best_match_id]['last_frame'] = frame_count
                        track_id = best_match_id
                    else:
                        track_id = next_track_id
                        next_track_id += 1
                        person_tracks[track_id] = {
                            'positions': [current_pos],
                            'first_frame': frame_count,
                            'last_frame': frame_count
                        }
                    
                    # Havuz içi/dışı sayımı
                    is_in_pool = self.is_point_in_pool(pool_polygon, center_x, center_y)
                    
                    if is_in_pool:
                        frame_inside += 1
                        unique_pool_persons.add(track_id)
                    else:
                        frame_outside += 1
                        unique_outside_persons.add(track_id)
                    
                    # Video çizimleri (sadece kayıt yapılıyorsa)
                    if save_video:
                        x1, y1, x2, y2 = person['bbox']
                        conf = person['conf']
                        is_enhanced = person.get('enhanced', False)
                        
                        if is_in_pool:
                            color = (0, 255, 0)
                            thickness = 3
                            label = f"#{track_id}: {conf:.2f}"
                            if is_enhanced:
                                label += " [E]"
                        else:
                            color = (0, 0, 255)
                            thickness = 2
                            label = f"#{track_id}: {conf:.2f}"
                        
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                        cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        cv2.circle(frame, (center_x, center_y), 5, color, -1)
                
                # Sayaçları güncelle
                total_detections += len(current_frame_persons)
                pool_inside_count += frame_inside
                pool_outside_count += frame_outside
                
                # Video bilgileri ekle (sadece kayıt yapılıyorsa)
                if save_video:
                    progress_percent = (elapsed / max_duration) * 100
                    
                    # Bilgi paneli
                    cv2.rectangle(frame, (5, 5), (width-5, 100), (0, 0, 0), -1)
                    cv2.rectangle(frame, (5, 5), (width-5, 100), (255, 255, 255), 2)
                    
                    cv2.putText(frame, f"Model: {model_name} | Kare: {frame_count} | %{progress_percent:.1f}", 
                               (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(frame, f"Bu kare - Havuz: {frame_inside} | Dis: {frame_outside}", 
                               (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(frame, f"Benzersiz - Havuz: {len(unique_pool_persons)} | Dis: {len(unique_outside_persons)}", 
                               (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(frame, f"FPS: {frame_count/elapsed:.1f} | Süre: {elapsed:.0f}s/92s", 
                               (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    out.write(frame)
        
        except Exception as e:
            print(f"❌ {model_name} işleme hatası: {e}")
        
        finally:
            cap.release()
            if out:
                out.release()
        
        # Sonuçları hesapla
        elapsed_total = time.time() - start_time
        avg_fps = frame_count / elapsed_total if elapsed_total > 0 else 0
        pool_inside_percent = (pool_inside_count / total_detections * 100) if total_detections > 0 else 0
        
        # Log dosyası yaz
        log_path = os.path.join(output_folder, "model_test_log.txt")
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"🤖 MODEL TEST RAPORU\n")
            f.write(f"===================\n\n")
            f.write(f"📹 Video: {video_name}\n")
            f.write(f"🤖 Model: {model_name}\n")
            f.write(f"⏱️  Test Süresi: {elapsed_total:.2f} saniye\n")
            f.write(f"🎬 İşlenen Kare: {frame_count}\n")
            f.write(f"🚀 Ortalama FPS: {avg_fps:.2f}\n")
            f.write(f"👥 Toplam Tespit: {total_detections}\n")
            f.write(f"🏊 Havuz İçi: {pool_inside_count} (%{pool_inside_percent:.1f})\n")
            f.write(f"🚶 Havuz Dışı: {pool_outside_count} (%{100-pool_inside_percent:.1f})\n")
            f.write(f"🆔 Benzersiz Havuz Kişisi: {len(unique_pool_persons)}\n")
            f.write(f"🆔 Benzersiz Dış Kişi: {len(unique_outside_persons)}\n")
            f.write(f"💾 Video Kaydı: {'Evet' if save_video else 'Hayır (disk tasarrufu)'}\n")
        
        return {
            'model_name': model_name,
            'elapsed_time': elapsed_total,
            'frame_count': frame_count,
            'avg_fps': avg_fps,
            'total_detections': total_detections,
            'pool_inside_count': pool_inside_count,
            'pool_outside_count': pool_outside_count,
            'pool_inside_percent': pool_inside_percent,
            'unique_pool_persons': len(unique_pool_persons),
            'unique_outside_persons': len(unique_outside_persons),
            'output_folder': os.path.basename(output_folder)
        }
    
    def test_all_models(self):
        """Tüm modelleri test et"""
        
        available_models = [os.path.basename(m) for m in self.info['models']]
        
        print(f"\n🤖 10 MODEL HAVUZ TAKİP SİSTEMİ")
        print(f"📹 Video sayısı: {len(self.info['videos'])}")
        print(f"⏱️  Her model için: 1:32 dakika test")
        print(f"🔍 Gelişmiş havuz içi tespit")
        print(f"🆔 Kişi takip sistemi")
        
        print(f"\n🤖 Test edilecek {len(available_models)} model:")
        for i, model in enumerate(available_models, 1):
            print(f"   {i:2d}. {model}")
        
        # Video seçimi
        if len(self.info['videos']) > 1:
            print(f"\n📽️  Mevcut videolar:")
            for i, video_path in enumerate(self.info['videos'], 1):
                video_name = os.path.basename(video_path)
                print(f"   {i}. {video_name}")
            
            try:
                choice = input(f"\nHangi video ile test yapalım? (1-{len(self.info['videos'])}): ").strip()
                video_index = int(choice) - 1
                if 0 <= video_index < len(self.info['videos']):
                    selected_video = self.info['videos'][video_index]
                else:
                    print("❌ Geçersiz seçim!")
                    return False
            except ValueError:
                print("❌ Geçersiz giriş!")
                return False
        else:
            selected_video = self.info['videos'][0]
        
        video_name = os.path.basename(selected_video)
        
        # Havuz alanını bul
        pool_file_path = self.find_pool_area_for_video(video_name)
        if not pool_file_path:
            return False
        
        pool_polygon = self.load_pool_area(pool_file_path)
        if pool_polygon is None:
            return False
        
        print(f"\n✅ Seçilen video: {video_name}")
        print(f"✅ Havuz alanı: {len(pool_polygon)} nokta")
        
        # Onay iste
        total_time = len(available_models) * 92 / 60  # dakika
        response = input(f"\n▶️  {len(available_models)} model testi başlatılsın mı? (~{total_time:.1f} dakika sürecek) (y/N): ")
        if response.lower() not in ['y', 'yes', 'evet', 'e']:
            print("❌ Test iptal edildi")
            return False
        
        # Testleri çalıştır
        results = []
        successful_tests = 0
        failed_tests = 0
        
        start_time_all = time.time()
        
        for i, model_name in enumerate(available_models, 1):
            model_path = os.path.join(Paths.MODELS_DIR, model_name)
            
            print(f"\n{'='*70}")
            print(f"🤖 MODEL {i}/{len(available_models)}: {model_name}")
            print(f"{'='*70}")
            print(f"📹 Video: {video_name}")
            print(f"⏱️  Test süresi: 1:32 dakika")
            
            test_start = time.time()
            result = self.test_single_model_with_tracking(
                selected_video, 
                model_path, 
                pool_polygon,
                max_duration=92
            )
            test_duration = time.time() - test_start
            
            if result:
                results.append(result)
                successful_tests += 1
                print(f"✅ {model_name} testi tamamlandı! ({test_duration:.1f}s)")
                print(f"   🏊 Havuz içi: {result['pool_inside_count']} (%{result['pool_inside_percent']:.1f})")
                print(f"   🆔 Benzersiz havuz kişisi: {result['unique_pool_persons']}")
                print(f"   🚀 FPS: {result['avg_fps']:.2f}")
            else:
                failed_tests += 1
                print(f"❌ {model_name} testi başarısız!")
            
            # İlerleme göster
            remaining_models = len(available_models) - i
            if remaining_models > 0:
                estimated_remaining = remaining_models * 92
                print(f"⏳ {remaining_models} model kaldı (~{estimated_remaining/60:.1f} dakika)")
                time.sleep(2)  # Kısa ara
        
        # Genel sonuçları göster
        total_duration = time.time() - start_time_all
        
        print(f"\n🎉 TÜM MODEL TESTLERİ TAMAMLANDI!")
        print(f"⏱️  Toplam süre: {total_duration/60:.1f} dakika")
        print(f"✅ Başarılı: {successful_tests}")
        print(f"❌ Başarısız: {failed_tests}")
        
        if results:
            print(f"\n📊 MODEL PERFORMANS KARŞILAŞTIRMASI:")
            print(f"{'='*80}")
            print(f"{'Model':<25} {'FPS':<6} {'Havuz%':<8} {'H.Kişi':<8} {'D.Kişi':<8} {'Toplam':<8}")
            print(f"{'-'*80}")
            
            # Sonuçları havuz içi yüzdesine göre sırala
            sorted_results = sorted(results, key=lambda x: x['pool_inside_percent'], reverse=True)
            
            for result in sorted_results:
                model_short = result['model_name'][:24]
                print(f"{model_short:<25} {result['avg_fps']:<6.1f} {result['pool_inside_percent']:<8.1f} "
                      f"{result['unique_pool_persons']:<8} {result['unique_outside_persons']:<8} "
                      f"{result['total_detections']:<8}")
            
            # En iyi modeller
            best_pool_detection = max(results, key=lambda x: x['pool_inside_percent'])
            best_fps = max(results, key=lambda x: x['avg_fps'])
            
            print(f"\n🏆 EN İYİ SONUÇLAR:")
            print(f"🏊 En iyi havuz tespiti: {best_pool_detection['model_name']} (%{best_pool_detection['pool_inside_percent']:.1f})")
            print(f"�� En hızlı model: {best_fps['model_name']} ({best_fps['avg_fps']:.1f} FPS)")
        
        print(f"\n📁 Tüm sonuçlar: {Paths.OUTPUT_DIR}")
        
        return True

if __name__ == "__main__":
    tracker = AllModelsPoolTracker()
    tracker.test_all_models()
