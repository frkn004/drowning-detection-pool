#!/usr/bin/env python3

"""
🎬 ÇOK VİDEO HAVUZ ALANI BELİRLEME
=================================
Her video için ayrı havuz alanı belirleme.
"""

import cv2
import os
import sys
import json
import numpy as np
from datetime import datetime

# Ana dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Paths, get_project_info

class MultiVideoPoolDefiner:
    """
    🎬 Çok video havuz alanı belirleme sınıfı
    """
    
    def __init__(self):
        self.points = []
        self.image = None
        self.original_image = None
        self.window_name = ""
        self.completed = False
        self.current_video_name = ""
    
    def mouse_callback(self, event, x, y, flags, param):
        """Fare olaylarını işle"""
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Sol tık - nokta ekle
            self.points.append([x, y])
            self.draw_polygon()
            print(f"✅ Nokta {len(self.points)} eklendi: ({x}, {y})")
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Sağ tık - son noktayı sil
            if self.points:
                removed = self.points.pop()
                self.draw_polygon()
                print(f"❌ Son nokta silindi: {removed}")
    
    def draw_polygon(self):
        """Poligonu çiz"""
        if self.original_image is None:
            return
        
        # Temiz görüntüyle başla
        self.image = self.original_image.copy()
        
        if len(self.points) == 0:
            cv2.imshow(self.window_name, self.image)
            return
        
        # Noktaları çiz
        for i, point in enumerate(self.points):
            cv2.circle(self.image, tuple(point), 8, (0, 255, 0), -1)  # Yeşil nokta
            cv2.putText(self.image, str(i+1), 
                       (point[0]+15, point[1]+15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Çizgileri çiz
        if len(self.points) > 1:
            for i in range(len(self.points)-1):
                cv2.line(self.image, tuple(self.points[i]), tuple(self.points[i+1]), 
                        (0, 0, 255), 3)  # Kırmızı çizgi
        
        # İlk ve son noktayı bağla (3+ nokta varsa)
        if len(self.points) > 2:
            cv2.line(self.image, tuple(self.points[-1]), tuple(self.points[0]), 
                    (0, 0, 255), 3)  # Kırmızı çizgi
            
            # Yarı saydam dolgu
            if len(self.points) >= 3:
                overlay = self.image.copy()
                cv2.fillPoly(overlay, [np.array(self.points)], (0, 255, 255))  # Sarı dolgu
                cv2.addWeighted(overlay, 0.3, self.image, 0.7, 0, self.image)
        
        # Video adını ekle
        cv2.putText(self.image, self.current_video_name, (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
        cv2.putText(self.image, self.current_video_name, (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
        
        # Bilgi metni
        info_text = f"Nokta sayisi: {len(self.points)}"
        if len(self.points) >= 3:
            info_text += " - 'C' tusu ile tamamla"
        elif len(self.points) == 0:
            info_text = "Havuz koselerini tiklayin"
        
        cv2.putText(self.image, info_text, (20, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
        cv2.putText(self.image, info_text, (20, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        
        cv2.imshow(self.window_name, self.image)
    
    def define_pool_for_video(self, video_path, frame_time=10.0):
        """
        Belirli video için havuz alanı belirle
        
        Args:
            video_path: Video dosyası yolu
            frame_time: Kullanılacak kare zamanı (saniye)
            
        Returns:
            list: Havuz polygon noktaları veya None
        """
        video_name = os.path.basename(video_path)
        self.current_video_name = video_name
        self.window_name = f"🏊 {video_name} - Havuz Alanı Seçin"
        
        # Önceki noktaları temizle
        self.points = []
        self.completed = False
        
        if not os.path.exists(video_path):
            print(f"❌ Video bulunamadı: {video_path}")
            return None
        
        # Video aç
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Video açılamadı: {video_path}")
            return None
        
        # Video özellikleri
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"\n🎬 {video_name}")
        print(f"📊 Video: {width}x{height} @ {fps:.1f} FPS")
        print(f"⏱️  Toplam: {total_frames} kare ({total_frames/fps:.1f} saniye)")
        
        # Belirtilen zamana git
        frame_number = int(frame_time * fps)
        if frame_number >= total_frames:
            frame_number = total_frames // 2
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Kare okunamadı!")
            cap.release()
            return None
        
        cap.release()
        
        # Görüntüyü hazırla
        self.original_image = frame.copy()
        self.image = frame.copy()
        
        # Pencere oluştur ve ayarla
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 1200, 800)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        print(f"🖱️  {video_name} için havuz alanının köşelerini tıklayın...")
        print("📺 Sol tık: Nokta ekle | Sağ tık: Sil | C: Tamamla | ESC: İptal")
        
        # İlk görüntüyü göster
        self.draw_polygon()
        
        # Kullanıcı girişini bekle
        while True:
            key = cv2.waitKey(30) & 0xFF
            
            if key == 27:  # ESC
                print(f"⏹️  {video_name} için işlem iptal edildi")
                self.points = []
                break
            
            elif key == ord('c') or key == ord('C'):
                if len(self.points) >= 3:
                    print(f"✅ {video_name} için havuz alanı tanımlandı!")
                    self.completed = True
                    break
                else:
                    print("⚠️  En az 3 nokta gerekli!")
            
            elif key == ord('r') or key == ord('R'):
                # Reset - tüm noktaları sil
                self.points = []
                self.draw_polygon()
                print("🔄 Tüm noktalar silindi")
        
        cv2.destroyAllWindows()
        
        return self.points if self.completed else None
    
    def save_pool_area(self, points, video_name):
        """Havuz alanını dosyaya kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_base = os.path.splitext(video_name)[0].replace(" ", "_")
        filename = f"pool_area_{video_base}_{timestamp}.json"
        filepath = os.path.join(Paths.OUTPUT_DIR, filename)
        
        pool_data = {
            'video_name': video_name,
            'timestamp': timestamp,
            'polygon_points': points,
            'point_count': len(points)
        }
        
        os.makedirs(Paths.OUTPUT_DIR, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pool_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 {video_name} havuz alanı kaydedildi: {filename}")
        return filepath

def define_all_pool_areas():
    """Tüm videolar için havuz alanlarını belirle"""
    
    info = get_project_info()
    
    if not info['videos']:
        print("❌ Test edilecek video bulunamadı!")
        return []
    
    print(f"🎯 {len(info['videos'])} video için havuz alanları belirlenecek")
    
    definer = MultiVideoPoolDefiner()
    defined_areas = []
    
    for i, video_path in enumerate(info['videos'], 1):
        video_name = os.path.basename(video_path)
        
        print(f"\n{'='*60}")
        print(f"🎬 VIDEO {i}/{len(info['videos'])}: {video_name}")
        print(f"{'='*60}")
        
        # Bu video için havuz alanı var mı kontrol et
        existing_files = []
        if os.path.exists(Paths.OUTPUT_DIR):
            for file in os.listdir(Paths.OUTPUT_DIR):
                if file.startswith("pool_area_") and video_name.replace(" ", "_").replace(".", "_") in file:
                    existing_files.append(file)
        
        if existing_files:
            existing_files.sort(reverse=True)
            latest_file = existing_files[0]
            print(f"⚠️  Bu video için zaten havuz alanı var: {latest_file}")
            
            choice = input(f"   Yeniden belirlemek istiyor musun? (y/N): ").lower()
            if choice not in ['y', 'yes', 'evet', 'e']:
                print(f"✅ Mevcut havuz alanı kullanılacak")
                defined_areas.append(os.path.join(Paths.OUTPUT_DIR, latest_file))
                continue
        
        # Havuz alanını belirle
        pool_points = definer.define_pool_for_video(video_path, frame_time=10.0)
        
        if pool_points:
            print(f"✅ {len(pool_points)} noktalı havuz alanı belirlendi")
            
            # Kaydet
            save_path = definer.save_pool_area(pool_points, video_name)
            defined_areas.append(save_path)
            
            # Koordinatları göster
            print(f"\n📋 {video_name} Havuz Koordinatları:")
            for j, (x, y) in enumerate(pool_points, 1):
                print(f"   {j}. nokta: ({x}, {y})")
        else:
            print(f"❌ {video_name} için havuz alanı belirlenmedi")
    
    print(f"\n🎉 {len(defined_areas)} video için havuz alanı hazır!")
    return defined_areas

if __name__ == "__main__":
    define_all_pool_areas()
