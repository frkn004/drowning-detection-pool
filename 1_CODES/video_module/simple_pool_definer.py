#!/usr/bin/env python3
"""
🏊 SIMPLE POOL AREA DEFINER
🎯 KAMERA 2 için havuz alanını belirleme aracı

Kullanım:
- Sol tık: Havuz köşelerini işaretle
- Sağ tık: Son noktayı sil
- SPACE: Tamamla ve kaydet
- ESC: İptal et

📅 Date: 31 Temmuz 2025
"""

import cv2
import json
import os
from pathlib import Path
import numpy as np

class SimplePoolDefiner:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_name = Path(video_path).stem
        
        # Mouse callback için
        self.points = []
        self.drawing = False
        self.frame = None
        self.original_frame = None
        
        # Output
        self.output_file = f"pool_area_{self.video_name}.json"
        
        print(f"🏊 Pool Area Definer - {self.video_name}")
        print(f"📹 Video: {video_path}")
        print("\n🎯 Kontroller:")
        print("   🖱️  Sol tık: Havuz köşesi ekle")
        print("   🖱️  Sağ tık: Son noktayı sil")
        print("   ⌨️  SPACE: Kaydet ve çık")
        print("   ⌨️  ESC: İptal et")
        print("   ⌨️  R: Sıfırla")
        print("\n📍 En az 4 köşe işaretleyin...")

    def mouse_callback(self, event, x, y, flags, param):
        """Mouse olaylarını yakala"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Sol tık - nokta ekle
            self.points.append((x, y))
            print(f"📍 Nokta {len(self.points)}: ({x}, {y})")
            self.draw_points()
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Sağ tık - son noktayı sil
            if self.points:
                removed = self.points.pop()
                print(f"🗑️  Nokta silindi: {removed}")
                self.draw_points()

    def draw_points(self):
        """Noktaları ve çizgileri çiz"""
        self.frame = self.original_frame.copy()
        
        if len(self.points) > 0:
            # Noktaları çiz
            for i, point in enumerate(self.points):
                cv2.circle(self.frame, point, 8, (0, 255, 0), -1)
                cv2.putText(self.frame, str(i+1), 
                          (point[0]+10, point[1]-10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Çizgileri çiz
            if len(self.points) > 1:
                for i in range(len(self.points) - 1):
                    cv2.line(self.frame, self.points[i], self.points[i+1], (255, 0, 0), 2)
                
                # Eğer 3'ten fazla nokta varsa, son nokta ile ilki arasında da çizgi çiz
                if len(self.points) > 2:
                    cv2.line(self.frame, self.points[-1], self.points[0], (255, 0, 0), 2)
                    
                    # Polygon'u doldur (şeffaf)
                    if len(self.points) >= 3:
                        overlay = self.frame.copy()
                        pts = np.array(self.points, np.int32)
                        cv2.fillPoly(overlay, [pts], (0, 255, 255))
                        cv2.addWeighted(overlay, 0.3, self.frame, 0.7, 0, self.frame)
        
        # Info text
        info_text = f"Noktalar: {len(self.points)} | SPACE: Kaydet | ESC: Iptal | R: Sifirla"
        cv2.putText(self.frame, info_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Pool Area Definer", self.frame)

    def save_pool_area(self):
        """Havuz alanını JSON olarak kaydet"""
        if len(self.points) < 3:
            print("❌ En az 3 nokta gerekli!")
            return False
        
        pool_data = {
            "video_name": self.video_name,
            "pool_area": self.points,
            "point_count": len(self.points),
            "frame_size": {
                "width": self.original_frame.shape[1],
                "height": self.original_frame.shape[0]
            }
        }
        
        # 3_OUTPUT klasörüne kaydet
        output_dir = Path(__file__).parent.parent.parent / "3_OUTPUT"
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / self.output_file
        
        with open(output_path, 'w') as f:
            json.dump(pool_data, f, indent=2)
        
        print(f"\n✅ Havuz alanı kaydedildi: {output_path}")
        print(f"📊 Nokta sayısı: {len(self.points)}")
        print(f"📍 Koordinatlar: {self.points}")
        
        return True

    def run(self):
        """Ana çalışma döngüsü"""
        # Video aç
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"❌ Video açılamadı: {self.video_path}")
            return
        
        # İlk frame'i al
        ret, frame = cap.read()
        if not ret:
            print("❌ Video frame alınamadı!")
            cap.release()
            return
        
        self.original_frame = frame.copy()
        self.frame = frame.copy()
        
        # Pencere ve mouse callback
        cv2.namedWindow("Pool Area Definer", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Pool Area Definer", self.mouse_callback)
        
        # İlk çizimi yap
        self.draw_points()
        
        print(f"🎬 Video yüklendi: {frame.shape[1]}x{frame.shape[0]}")
        print("🖱️  Havuz köşelerini işaretleyin...")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '):  # SPACE - kaydet
                if self.save_pool_area():
                    break
                    
            elif key == 27:  # ESC - iptal
                print("❌ İptal edildi")
                break
                
            elif key == ord('r') or key == ord('R'):  # R - sıfırla
                self.points = []
                print("🔄 Noktalar temizlendi")
                self.draw_points()
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    """Ana fonksiyon"""
    # Video path
    video_path = Path(__file__).parent.parent.parent / "0_DATA" / "kamera1.mov"
    
    if not video_path.exists():
        print(f"❌ Video bulunamadı: {video_path}")
        return
    
    # Pool definer çalıştır
    definer = SimplePoolDefiner(str(video_path))
    definer.run()

if __name__ == "__main__":
    main()