#!/usr/bin/env python3
"""
👁️ ANNOTATION VIEWER - MacOS GUI Alternative
============================================
LabelImg alternatifi: Etiketleri görüntüle ve manuel düzenle
"""

import cv2
import os
import json
from pathlib import Path

class SimpleAnnotationViewer:
    def __init__(self, frames_dir, labels_dir, classes_file):
        self.frames_dir = frames_dir
        self.labels_dir = labels_dir
        
        # Classes yükle
        with open(classes_file, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        print(f"📋 Classes: {self.classes}")
        
        # Frame ve label dosyaları
        self.frame_files = sorted(list(Path(frames_dir).glob("*.jpg")))
        self.current_idx = 0
        
        print(f"📸 {len(self.frame_files)} frame bulundu")
        
    def load_annotations(self, frame_path):
        """YOLO format annotations yükle"""
        label_file = Path(self.labels_dir) / f"{frame_path.stem}.txt"
        
        annotations = []
        if label_file.exists():
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        class_id = int(parts[0])
                        x_center = float(parts[1])
                        y_center = float(parts[2])
                        width = float(parts[3])
                        height = float(parts[4])
                        
                        annotations.append({
                            'class_id': class_id,
                            'class_name': self.classes[class_id],
                            'x_center': x_center,
                            'y_center': y_center,
                            'width': width,
                            'height': height
                        })
        
        return annotations
    
    def draw_annotations(self, image, annotations):
        """Annotations'ları resim üzerine çiz"""
        h, w = image.shape[:2]
        
        for i, ann in enumerate(annotations):
            # Normalized'dan pixel koordinatlara çevir
            x_center = int(ann['x_center'] * w)
            y_center = int(ann['y_center'] * h)
            box_w = int(ann['width'] * w)
            box_h = int(ann['height'] * h)
            
            # Bounding box köşeleri
            x1 = x_center - box_w // 2
            y1 = y_center - box_h // 2
            x2 = x_center + box_w // 2
            y2 = y_center + box_h // 2
            
            # Renk seç (class'a göre)
            colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0)]
            color = colors[ann['class_id'] % len(colors)]
            
            # Rectangle çiz
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Class label
            label = f"{i+1}: {ann['class_name']}"
            cv2.putText(image, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return image
    
    def show_current_frame(self):
        """Mevcut frame'i göster"""
        if self.current_idx >= len(self.frame_files):
            print("🏁 Tüm frameler görüntülendi!")
            return False
        
        frame_path = self.frame_files[self.current_idx]
        print(f"\n📸 Frame {self.current_idx + 1}/{len(self.frame_files)}: {frame_path.name}")
        
        # Resmi yükle
        image = cv2.imread(str(frame_path))
        if image is None:
            print(f"❌ Resim yüklenemedi: {frame_path}")
            return False
        
        # Annotations yükle
        annotations = self.load_annotations(frame_path)
        print(f"🏷️  {len(annotations)} annotation bulundu:")
        
        for i, ann in enumerate(annotations, 1):
            print(f"   {i}. {ann['class_name']} "
                  f"(center: {ann['x_center']:.2f}, {ann['y_center']:.2f})")
        
        # Annotations çiz
        image_with_annotations = self.draw_annotations(image, annotations)
        
        # Resmi küçült (ekrana sığdır)
        height, width = image_with_annotations.shape[:2]
        if width > 1200:
            scale = 1200 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_with_annotations = cv2.resize(image_with_annotations, 
                                              (new_width, new_height))
        
        # Göster
        cv2.imshow('Annotation Viewer - Press SPACE=next, ESC=quit', image_with_annotations)
        
        return True
    
    def run(self):
        """Ana döngü"""
        print("\n🎯 ANNOTATION VIEWER")
        print("=" * 40)
        print("⌨️  SPACE: Sonraki frame")
        print("⌨️  ESC: Çıkış")
        print("=" * 40)
        
        while True:
            if not self.show_current_frame():
                break
            
            # Klavye kontrolü
            key = cv2.waitKey(0) & 0xFF
            
            if key == 27:  # ESC
                print("👋 Çıkılıyor...")
                break
            elif key == 32:  # SPACE
                self.current_idx += 1
            
        cv2.destroyAllWindows()

def main():
    """Ana fonksiyon"""
    
    frames_dir = "01_frames"
    labels_dir = "02_labels"
    classes_file = "classes.txt"
    
    print("👁️ Simple Annotation Viewer Başlıyor...")
    
    # Viewer oluştur ve çalıştır
    viewer = SimpleAnnotationViewer(frames_dir, labels_dir, classes_file)
    viewer.run()

if __name__ == "__main__":
    main() 