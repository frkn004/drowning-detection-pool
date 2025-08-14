#!/usr/bin/env python3
"""
🔧 ANNOTATION DÜZELTME ARACI
============================
1. Havuz alanını tanımla
2. Etiketleri havuz içi/dışı'na göre sınıflandır
3. Manuel düzeltme imkanı
"""

import cv2
import os
import json
import numpy as np
from pathlib import Path

class AnnotationFixer:
    def __init__(self, frames_dir, labels_dir, classes_file):
        self.frames_dir = frames_dir
        self.labels_dir = labels_dir
        
        # Classes yükle
        with open(classes_file, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        # Class mapping
        self.class_mapping = {
            'person_swimming': 0,
            'person_drowning': 1,
            'person_poolside': 2,
            'pool_equipment': 3
        }
        
        self.pool_polygon = None
        self.current_frame_idx = 0
        self.frame_files = sorted(list(Path(frames_dir).glob("*.jpg")))
        
        # Mouse koordinat düzeltme için
        self.scale_factor = 1.0
        self.original_image = None
        self.display_image = None
        
        print(f"📋 Classes: {self.classes}")
        print(f"📸 {len(self.frame_files)} frame bulundu")
    
    def define_pool_area(self):
        """İlk frame'de havuz alanını belirle"""
        
        if not self.frame_files:
            print("❌ Frame bulunamadı!")
            return False
        
        # İlk frame'i yükle
        self.original_image = cv2.imread(str(self.frame_files[0]))
        if self.original_image is None:
            print("❌ İlk frame yüklenemedi!")
            return False
        
        print("\n🏊 HAVUZ ALANI BELİRLEME")
        print("=" * 40)
        print("🖱️  Sol tık: Havuz köşesi ekle")
        print("🖱️  Sağ tık: Son noktayı sil")
        print("⌨️  ENTER: Havuz alanını tamamla")
        print("⌨️  ESC: İptal et")
        print("⌨️  R: Yeniden başla (tüm noktaları sil)")
        print("=" * 40)
        
        # Resim boyutunu ayarla
        height, width = self.original_image.shape[:2]
        max_width = 1000
        if width > max_width:
            self.scale_factor = max_width / width
            new_width = int(width * self.scale_factor)
            new_height = int(height * self.scale_factor)
            self.display_image = cv2.resize(self.original_image, (new_width, new_height))
            print(f"📏 Resim boyutu: {width}x{height} → {new_width}x{new_height} (scale: {self.scale_factor:.2f})")
        else:
            self.scale_factor = 1.0
            self.display_image = self.original_image.copy()
            print(f"📏 Resim boyutu: {width}x{height} (scale: 1.0)")
        
        # Mouse callback için değişkenler
        self.temp_points = []
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                # Mouse koordinatlarını original boyuta çevir
                orig_x = int(x / self.scale_factor)
                orig_y = int(y / self.scale_factor)
                
                # Sol tık - nokta ekle
                self.temp_points.append([orig_x, orig_y])
                self.draw_temp_polygon()
                print(f"✅ Havuz köşesi {len(self.temp_points)}: Display({x}, {y}) → Original({orig_x}, {orig_y})")
                
            elif event == cv2.EVENT_RBUTTONDOWN:
                # Sağ tık - son noktayı sil
                if self.temp_points:
                    removed = self.temp_points.pop()
                    self.draw_temp_polygon()
                    print(f"❌ Son nokta silindi: {removed}")
        
        # Pencere oluştur
        cv2.namedWindow('Havuz Alanı Belirleme', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('Havuz Alanı Belirleme', mouse_callback)
        
        self.draw_temp_polygon()
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                print("⏹️  Havuz alanı belirleme iptal edildi")
                self.temp_points = []
                break
            
            elif key == ord('r') or key == ord('R'):  # R - Reset
                print("🔄 Tüm noktalar silindi - yeniden başla")
                self.temp_points = []
                self.draw_temp_polygon()
            
            elif key == 13:  # ENTER
                if len(self.temp_points) >= 3:
                    self.pool_polygon = self.temp_points.copy()
                    print(f"✅ Havuz alanı belirlendi! {len(self.pool_polygon)} nokta")
                    break
                else:
                    print("⚠️  En az 3 nokta gerekli!")
        
        cv2.destroyAllWindows()
        
        # Havuz alanını kaydet
        if self.pool_polygon:
            pool_data = {
                'polygon_points': self.pool_polygon,
                'frame_reference': str(self.frame_files[0].name),
                'original_size': [width, height]
            }
            
            with open('pool_area.json', 'w') as f:
                json.dump(pool_data, f, indent=2)
            
            print(f"💾 Havuz alanı pool_area.json'a kaydedildi")
            return True
        
        return False
    
    def draw_temp_polygon(self):
        """Temp polygon çiz"""
        self.display_image = cv2.resize(self.original_image, 
                                       (int(self.original_image.shape[1] * self.scale_factor),
                                        int(self.original_image.shape[0] * self.scale_factor)))
        
        if len(self.temp_points) > 0:
            # Display koordinatlarına çevir
            display_points = []
            for point in self.temp_points:
                display_x = int(point[0] * self.scale_factor)
                display_y = int(point[1] * self.scale_factor)
                display_points.append([display_x, display_y])
            
            # Noktaları çiz
            for i, point in enumerate(display_points):
                cv2.circle(self.display_image, tuple(point), 5, (0, 255, 0), -1)
                cv2.putText(self.display_image, str(i+1), 
                           (point[0]+10, point[1]), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (0, 255, 0), 2)
            
            # Çizgileri çiz
            if len(display_points) > 1:
                pts = np.array(display_points, np.int32)
                cv2.polylines(self.display_image, [pts], False, (255, 0, 0), 2)
            
            # Kapalı polygon ise fill
            if len(display_points) > 2:
                pts = np.array(display_points, np.int32)
                overlay = self.display_image.copy()
                cv2.fillPoly(overlay, [pts], (0, 255, 0))
                cv2.addWeighted(overlay, 0.3, self.display_image, 0.7, 0, self.display_image)
        
        cv2.imshow('Havuz Alanı Belirleme', self.display_image)
    
    def load_pool_area(self):
        """Kaydedilmiş havuz alanını yükle"""
        if os.path.exists('pool_area.json'):
            with open('pool_area.json', 'r') as f:
                pool_data = json.load(f)
                self.pool_polygon = pool_data['polygon_points']
                print(f"✅ Havuz alanı yüklendi: {len(self.pool_polygon)} nokta")
                return True
        return False
    
    def point_in_polygon(self, point, polygon):
        """Nokta polygon içinde mi kontrol et"""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def fix_all_annotations(self):
        """Tüm etiketleri havuz içi/dışı'na göre düzelt"""
        
        if not self.pool_polygon:
            print("❌ Önce havuz alanını belirlemelisin!")
            return
        
        print(f"\n🔧 TÜM ETİKETLER DÜZELTİLİYOR...")
        print("=" * 40)
        
        fixed_count = 0
        inside_count = 0
        outside_count = 0
        
        for frame_file in self.frame_files:
            label_file = Path(self.labels_dir) / f"{frame_file.stem}.txt"
            
            if not label_file.exists():
                continue
            
            # Mevcut annotations yükle
            annotations = []
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        class_id = int(parts[0])
                        x_center = float(parts[1])
                        y_center = float(parts[2])
                        width = float(parts[3])
                        height = float(parts[4])
                        
                        # Pixel koordinatlara çevir (approximation)
                        img = cv2.imread(str(frame_file))
                        h, w = img.shape[:2]
                        pixel_x = int(x_center * w)
                        pixel_y = int(y_center * h)
                        
                        # Havuz içinde mi kontrol et
                        is_in_pool = self.point_in_polygon([pixel_x, pixel_y], self.pool_polygon)
                        
                        # Class'ı düzelt
                        if is_in_pool:
                            new_class = 0  # person_swimming
                            inside_count += 1
                        else:
                            new_class = 2  # person_poolside
                            outside_count += 1
                        
                        if new_class != class_id:
                            fixed_count += 1
                        
                        annotations.append(f"{new_class} {x_center} {y_center} {width} {height}")
            
            # Düzeltilmiş annotations kaydet
            with open(label_file, 'w') as f:
                f.write('\n'.join(annotations))
        
        print(f"✅ Düzeltme tamamlandı!")
        print(f"   🏊 Havuz içi: {inside_count}")
        print(f"   🏖️ Havuz dışı: {outside_count}")
        print(f"   🔧 Düzeltilen: {fixed_count}")

def main():
    """Ana fonksiyon"""
    
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    frames_dir = os.path.join(script_dir, "01_frames")
    labels_dir = os.path.join(script_dir, "02_labels")
    classes_file = os.path.join(script_dir, "classes.txt")
    
    print("🔧 Annotation Düzeltme Aracı")
    print("=" * 50)
    
    fixer = AnnotationFixer(frames_dir, labels_dir, classes_file)
    
    # Mevcut havuz alanını kontrol et
    pool_exists = fixer.load_pool_area()
    
    print(f"\n{'='*50}")
    if pool_exists:
        print("🏊 Mevcut havuz alanı bulundu!")
        print("1️⃣  ENTER: Mevcut havuz alanı ile devam et")
        print("2️⃣  N: Yeni havuz alanı belirle") 
        print("3️⃣  ESC: Çıkış")
        print("="*50)
        
        while True:
            key = input("Seçiminiz (ENTER/N/ESC): ").lower()
            if key == 'n':
                if not fixer.define_pool_area():
                    print("❌ Havuz alanı belirlenemedi!")
                    return
                break
            elif key == '' or key == 'enter':
                break
            elif key == 'esc':
                return
            else:
                print("⚠️  Geçersiz seçim!")
    else:
        print("🏊 Havuz alanı belirlenecek...")
        if not fixer.define_pool_area():
            print("❌ Havuz alanı belirlenemedi!")
            return
    
    # Tüm etiketleri düzelt
    fixer.fix_all_annotations()
    
    print(f"\n🎉 İşlem tamamlandı!")
    print(f"   Şimdi view_annotations.py ile kontrol edebilirsin")

if __name__ == "__main__":
    main() 