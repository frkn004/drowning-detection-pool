#!/usr/bin/env python3
"""
İki Aşamalı Boğulma Tespit Sistemi:
1. YOLO8X ile tüm insanları tespit et (yüksek recall)
2. YENİ_MODEL ile durumlarını sınıflandır (yüksek precision)
"""

from ultralytics import YOLO
import cv2
import numpy as np

class TwoStageDetector:
    def __init__(self):
        print("🤖 İki Aşamalı Sistem Yükleniyor...")
        
        # Aşama 1: Genel insan tespiti (yüksek recall)
        self.general_model = YOLO('4_MODELS/yolov8x.pt')
        print("✅ YOLO8X yüklendi (Genel insan tespiti)")
        
        # Aşama 2: Spesifik durum sınıflandırması (yüksek precision)
        self.specific_model = YOLO('drowning_detection_v12_working.pt')
        print("✅ YENİ_MODEL yüklendi (Durum sınıflandırması)")
        
        self.class_names = {
            0: 'person_swimming',
            1: 'person_drowning', 
            2: 'person_poolside',
            3: 'pool_equipment'
        }
        
    def detect_two_stage(self, frame):
        """İki aşamalı tespit"""
        results = {
            'stage1_persons': [],
            'stage2_classifications': [],
            'total_persons': 0,
            'swimming': 0,
            'drowning': 0,
            'poolside': 0
        }
        
        # AŞAMA 1: Genel insan tespiti (düşük threshold - tüm insanları yakala)
        stage1_results = self.general_model(frame, conf=0.01, classes=[0], verbose=False)
        
        for r in stage1_results:
            if r.boxes is not None:
                for box in r.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf.item())
                    
                    # İnsan bounding box'ını kaydet
                    person_box = {
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'conf': conf,
                        'stage1_class': 'person'
                    }
                    results['stage1_persons'].append(person_box)
                    results['total_persons'] += 1
                    
                    # AŞAMA 2: Bu bölgeyi crop edip spesifik model ile sınıflandır
                    crop = frame[int(y1):int(y2), int(x1):int(x2)]
                    if crop.size > 0:
                        stage2_results = self.specific_model(crop, conf=0.01, verbose=False)
                        
                        best_class = None
                        best_conf = 0
                        
                        for r2 in stage2_results:
                            if r2.boxes is not None:
                                for box2 in r2.boxes:
                                    cls = int(box2.cls.item())
                                    conf2 = float(box2.conf.item())
                                    
                                    if conf2 > best_conf:
                                        best_conf = conf2
                                        best_class = cls
                        
                        # Sınıflandırma sonucunu ekle
                        if best_class is not None:
                            class_name = self.class_names[best_class]
                            person_box['stage2_class'] = class_name
                            person_box['stage2_conf'] = best_conf
                            
                            # Sayaçları güncelle
                            if best_class == 0:  # swimming
                                results['swimming'] += 1
                            elif best_class == 1:  # drowning
                                results['drowning'] += 1
                            elif best_class == 2:  # poolside
                                results['poolside'] += 1
                        else:
                            person_box['stage2_class'] = 'unknown'
                            person_box['stage2_conf'] = 0
        
        return results
    
    def draw_results(self, frame, results):
        """Sonuçları çiz"""
        drawn_frame = frame.copy()
        
        for person in results['stage1_persons']:
            x1, y1, x2, y2 = person['bbox']
            stage1_conf = person['conf']
            stage2_class = person.get('stage2_class', 'unknown')
            stage2_conf = person.get('stage2_conf', 0)
            
            # Renk seçimi
            if stage2_class == 'person_swimming':
                color = (0, 255, 0)  # Yeşil
            elif stage2_class == 'person_drowning':
                color = (0, 0, 255)  # Kırmızı
            elif stage2_class == 'person_poolside':
                color = (255, 0, 0)  # Mavi
            else:
                color = (128, 128, 128)  # Gri
            
            # Bounding box çiz
            cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), color, 3)
            
            # Label çiz
            if stage2_class != 'unknown':
                label = f"{stage2_class.split('_')[1]} ({stage2_conf:.2f})"
            else:
                label = f"person ({stage1_conf:.2f})"
            cv2.putText(drawn_frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # İstatistikleri çiz - BÜYÜK PANEL
        panel_height = 150
        overlay = drawn_frame.copy()
        cv2.rectangle(overlay, (10, 10), (600, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, drawn_frame, 0.3, 0, drawn_frame)
        
        # Başlık
        cv2.putText(drawn_frame, "IKI ASAMALI BOGULMA TESPIT SISTEMI", 
                   (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # İstatistikler
        stats_text = [
            f"TOPLAM INSAN: {results['total_persons']}",
            f"YUZENLER: {results['swimming']} (Yesil)",
            f">>> BOGULANLAR: {results['drowning']} <<< (Kirmizi)",
            f"HAVUZ KENARI: {results['poolside']} (Mavi)"
        ]
        
        for i, text in enumerate(stats_text):
            if 'BOGULAN' in text:
                color = (0, 0, 255)  # Kırmızı - ALARM
                cv2.putText(drawn_frame, text, (20, 65 + i*20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 3)
            elif 'YUZEN' in text:
                color = (0, 255, 0)  # Yeşil
                cv2.putText(drawn_frame, text, (20, 65 + i*20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            elif 'KENARI' in text:
                color = (255, 0, 0)  # Mavi
                cv2.putText(drawn_frame, text, (20, 65 + i*20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            else:
                color = (255, 255, 255)  # Beyaz
                cv2.putText(drawn_frame, text, (20, 65 + i*20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return drawn_frame

def test_two_stage():
    """Test fonksiyonu"""
    print("🎬 İki Aşamalı Test Başlıyor...")
    
    detector = TwoStageDetector()
    
    # Video aç
    cap = cv2.VideoCapture('0_DATA/KAMERA 1.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Video çıktı dosyası
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"3_OUTPUT/TWO_STAGE_DETECTION_{timestamp}.mp4"
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"💾 Video kaydediliyor: {output_path}")
    
    # Test: İlk 300 frame (20 saniye)
    frame_count = 0
    total_stats = {
        'total_persons': 0,
        'swimming': 0,
        'drowning': 0,
        'poolside': 0
    }
    
    while frame_count < 300:
        ret, frame = cap.read()
        if not ret:
            break
            
        # İki aşamalı tespit
        results = detector.detect_two_stage(frame)
        
        # Sonuçları çiz
        drawn_frame = detector.draw_results(frame, results)
        
        # Video'ya yaz
        out.write(drawn_frame)
        
        # İstatistikleri topla
        total_stats['total_persons'] += results['total_persons']
        total_stats['swimming'] += results['swimming']
        total_stats['drowning'] += results['drowning']
        total_stats['poolside'] += results['poolside']
        
        frame_count += 1
        
        if frame_count % 50 == 0:
            print(f"Frame {frame_count}: {results['total_persons']} kişi tespit edildi")
    
    cap.release()
    out.release()
    print(f"✅ Video kaydedildi: {output_path}")
    
    print("\n🏆 300 FRAME TESTİ SONUÇLARI:")
    print("=" * 50)
    print(f"📊 Toplam İnsan Tespiti: {total_stats['total_persons']}")
    print(f"🏊 Yüzenler: {total_stats['swimming']}")
    print(f"🚨 BOĞULANLAR: {total_stats['drowning']}")
    print(f"🚶 Havuz Kenarı: {total_stats['poolside']}")
    print(f"📈 Ortalama Frame/İnsan: {total_stats['total_persons']/300:.1f}")
    print(f"💾 Video dosyası: {output_path}")

if __name__ == "__main__":
    test_two_stage()
