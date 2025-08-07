#!/usr/bin/env python3

"""
🏊 HAVUZ ALANI BELİRLEME MODÜLÜ
===============================
Video üzerinde fare ile havuz alanını çizme aracı.
import numpy as np"""

import cv2
import os
import sys
import json
from datetime import datetime

# Ana dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Paths, Pool

class PoolAreaDefiner:
    """
    🖱️ Havuz alanı çizme sınıfı
    """
    
    def __init__(self):
        self.points = []
        self.image = None
        self.original_image = None
        self.window_name = "Havuz Alanı Belirleme"
        self.completed = False
        
        print("🏊 Havuz Alanı Belirleme Aracı")
        print("🖱️  Sol tık: Nokta ekle")
        print("��️  Sağ tık: Son noktayı sil") 
        print("⌨️  C tuşu: Tamamla")
        print("⌨️  ESC tuşu: İptal")
    
    def mouse_callback(self, event, x, y, flags, param):
        """Fare olaylarını işle"""
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Sol tık - nokta ekle
            self.points.append((x, y))
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
            cv2.circle(self.image, point, 5, Pool.POINT_COLOR, -1)
            cv2.putText(self.image, str(i+1), 
                       (point[0]+10, point[1]+10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, Pool.POINT_COLOR, 2)
        
        # Çizgileri çiz
        if len(self.points) > 1:
            for i in range(len(self.points)-1):
                cv2.line(self.image, self.points[i], self.points[i+1], 
                        Pool.POLYGON_COLOR, Pool.LINE_THICKNESS)
        
        # İlk ve son noktayı bağla (3+ nokta varsa)
        if len(self.points) > 2:
            cv2.line(self.image, self.points[-1], self.points[0], 
                    Pool.POLYGON_COLOR, Pool.LINE_THICKNESS)
            
            # Yarı saydam dolgu
            overlay = self.image.copy()
            cv2.fillPoly(overlay, [np.array(self.points)], (0, 255, 255))
            cv2.addWeighted(overlay, 0.3, self.image, 0.7, 0, self.image)
        
        # Bilgi metni
        info_text = f"Nokta sayisi: {len(self.points)}"
        if len(self.points) >= 3:
            info_text += " - 'C' ile tamamla"
        
        cv2.putText(self.image, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow(self.window_name, self.image)
    
    def define_from_video(self, video_path, frame_time=5.0):
        """
        Video dosyasından havuz alanı belirle
        
        Args:
            video_path: Video dosyası yolu
            frame_time: Kullanılacak kare zamanı (saniye)
            
        Returns:
            list: Havuz polygon noktaları veya None
        """
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
        
        print(f"📊 Video: {width}x{height} @ {fps:.1f} FPS")
        print(f"🎬 Toplam: {total_frames} kare ({total_frames/fps:.1f} saniye)")
        
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
        
        # Pencere oluştur
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        print(f"🎬 {frame_time:.1f}. saniyedeki kare gösteriliyor")
        print("🖱️  Havuz alanının köşelerini tıklayın...")
        
        # İlk görüntüyü göster
        self.draw_polygon()
        
        # Kullanıcı girişini bekle
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                print("⏹️  İşlem iptal edildi")
                self.points = []
                break
            
            elif key == ord('c') or key == ord('C'):
                if len(self.points) >= 3:
                    print("✅ Havuz alanı tanımlandı!")
                    self.completed = True
                    break
                else:
                    print("⚠️  En az 3 nokta gerekli!")
        
        cv2.destroyAllWindows()
        
        return self.points if self.completed else None
    
    def save_pool_area(self, points, video_name, output_dir=None):
        """
        Havuz alanını dosyaya kaydet
        
        Args:
            points: Polygon noktaları
            video_name: Video adı  
            output_dir: Çıktı klasörü
            
        Returns:
            str: Kaydedilen dosya yolu
        """
        if output_dir is None:
            output_dir = Paths.OUTPUT_DIR
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_base = os.path.splitext(video_name)[0]
        filename = f"pool_area_{video_base}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        pool_data = {
            'video_name': video_name,
            'timestamp': timestamp,
            'polygon_points': points,
            'point_count': len(points)
        }
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pool_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Havuz alanı kaydedildi: {filename}")
        return filepath

def test_pool_area_definer():
    """Havuz alanı belirleme aracını test et"""
    from core.config import get_project_info
    
    info = get_project_info()
    
    if not info['videos']:
        print("❌ Test edilecek video bulunamadı!")
        return
    
    # KAMERA 2 videosunu seç
    kamera2_video = None
    for video in info['videos']:
        if 'KAMERA 2' in video:
            kamera2_video = video
            break
    
    if not kamera2_video:
        kamera2_video = info['videos'][0]  # İlk videoyu al
    
    video_name = os.path.basename(kamera2_video)
    print(f"🎯 Test videosu: {video_name}")
    
    # Havuz alanı belirleme aracını başlat
    definer = PoolAreaDefiner()
    
    # Havuz alanını belirle
    pool_points = definer.define_from_video(kamera2_video, frame_time=10.0)
    
    if pool_points:
        print(f"✅ {len(pool_points)} noktalı havuz alanı belirlendi")
        
        # Kaydet
        save_path = definer.save_pool_area(pool_points, video_name)
        
        # Koordinatları göster
        print("\n📋 Havuz Alanı Koordinatları:")
        for i, (x, y) in enumerate(pool_points, 1):
            print(f"   {i}. nokta: ({x}, {y})")
        
        print(f"\n💾 Kaydedilen dosya: {os.path.basename(save_path)}")
        
        return pool_points
    else:
        print("❌ Havuz alanı belirlenmedi")
        return None

if __name__ == "__main__":
    import numpy as np
