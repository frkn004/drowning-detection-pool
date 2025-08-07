import cv2
import os
import numpy as np
from pathlib import Path

class ColorAnnotationViewer:
    def __init__(self, frames_dir, labels_dir, classes_file):
        self.frames_dir = Path(frames_dir)
        self.labels_dir = Path(labels_dir)
        
        # Sınıfları yükle
        with open(classes_file, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        print(f"📋 Classes: {self.classes}")
        
        # Frame dosyalarını al
        self.frame_files = sorted(list(self.frames_dir.glob("*.jpg")))
        print(f"📸 {len(self.frame_files)} frame bulundu")
        
        # Renkler tanımla (BGR format)
        self.colors = {
            0: (0, 255, 0),     # person_swimming -> YEŞİL
            1: (0, 0, 255),     # person_drowning -> KIRMIZI  
            2: (255, 0, 0),     # person_poolside -> MAVİ
            3: (0, 255, 255)    # pool_equipment -> SARI
        }
        
        self.current_idx = 0
        
    def load_annotations(self, frame_path):
        """Annotation dosyasını yükle"""
        frame_name = frame_path.stem
        label_file = self.labels_dir / f"{frame_name}.txt"
        
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
                            'x_center': x_center,
                            'y_center': y_center,
                            'width': width,
                            'height': height
                        })
        return annotations
    
    def draw_annotations(self, image, annotations):
        """Annotation'ları renkli olarak çiz"""
        h, w = image.shape[:2]
        
        # Class sayılarını say
        class_counts = {}
        for ann in annotations:
            class_name = self.classes[ann['class_id']]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        for i, ann in enumerate(annotations):
            class_id = ann['class_id']
            color = self.colors.get(class_id, (128, 128, 128))  # Varsayılan gri
            class_name = self.classes[class_id]
            
            # YOLO koordinatlarını pixel koordinatlarına çevir
            x_center = ann['x_center'] * w
            y_center = ann['y_center'] * h
            box_width = ann['width'] * w
            box_height = ann['height'] * h
            
            x1 = int(x_center - box_width / 2)
            y1 = int(y_center - box_height / 2)
            x2 = int(x_center + box_width / 2)
            y2 = int(y_center + box_height / 2)
            
            # Kalın çerçeve çiz
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
            
            # Label arka planı
            label = f"{i+1}: {class_name}"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(image, (x1, y1-label_h-5), (x1+label_w, y1), color, -1)
            
            # Beyaz yazı
            cv2.putText(image, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Üst kısma bilgi yaz
        info_text = f"Frame {self.current_idx + 1}/{len(self.frame_files)}"
        if class_counts:
            counts_text = " | ".join([f"{name}:{count}" for name, count in class_counts.items()])
            info_text += f" | {counts_text}"
        else:
            info_text += " | Annotation yok"
            
        cv2.putText(image, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(image, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
        
        return image
    
    def show_current_frame(self):
        """Mevcut frame'i göster"""
        if self.current_idx >= len(self.frame_files):
            return False
            
        frame_path = self.frame_files[self.current_idx]
        image = cv2.imread(str(frame_path))
        
        if image is None:
            print(f"❌ Frame yüklenemedi: {frame_path}")
            return False
        
        # Annotation'ları yükle ve çiz
        annotations = self.load_annotations(frame_path)
        image = self.draw_annotations(image, annotations)
        
        # Pencere boyutunu ayarla
        h, w = image.shape[:2]
        if w > 1200:
            scale = 1200 / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = cv2.resize(image, (new_w, new_h))
        
        cv2.imshow('🎨 Renkli Annotation Viewer', image)
        return True
    
    def run(self):
        """Ana döngü"""
        print("\n🎨 RENKLİ ANNOTATION VIEWER")
        print("=" * 50)
        print("🟢 YEŞİL: person_swimming")
        print("🔴 KIRMIZI: person_drowning") 
        print("🔵 MAVİ: person_poolside")
        print("🟡 SARI: pool_equipment")
        print("=" * 50)
        print("⌨️  SPACE=Sonraki | A=Önceki | ESC=Çıkış")
        print("=" * 50)
        
        if not self.show_current_frame():
            print("❌ İlk frame gösterilemedi!")
            return
        
        while True:
            key = cv2.waitKey(0) & 0xFF
            
            if key == 27:  # ESC
                break
            elif key == ord(' '):  # SPACE - Sonraki frame
                if self.current_idx < len(self.frame_files) - 1:
                    self.current_idx += 1
                    print(f"➡️  Frame {self.current_idx + 1}")
                    self.show_current_frame()
                else:
                    print("📄 Son frame'desin!")
            elif key == ord('a') or key == ord('A'):  # A - Önceki frame
                if self.current_idx > 0:
                    self.current_idx -= 1
                    print(f"⬅️  Frame {self.current_idx + 1}")
                    self.show_current_frame()
                else:
                    print("📄 İlk frame'desin!")
        
        cv2.destroyAllWindows()
        print("👋 Viewer kapatıldı!")

def main():
    frames_dir = "01_frames"
    labels_dir = "02_labels"
    classes_file = "classes.txt"
    
    viewer = ColorAnnotationViewer(frames_dir, labels_dir, classes_file)
    viewer.run()

if __name__ == "__main__":
    main() 