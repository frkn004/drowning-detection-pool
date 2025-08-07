import cv2
import os
import numpy as np
from pathlib import Path

class ColorEditor:
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
        self.current_annotations = []
        self.selected_annotation = -1
        
        # Mouse drawing
        self.drawing = False
        self.start_point = None
        self.end_point = None
        
        # Image properties
        self.original_image = None
        self.display_image = None
        self.scale_factor = 1.0
        
    def load_annotations(self, frame_idx):
        """Annotation dosyasını yükle"""
        if frame_idx >= len(self.frame_files):
            return
            
        frame_path = self.frame_files[frame_idx]
        frame_name = frame_path.stem
        label_file = self.labels_dir / f"{frame_name}.txt"
        
        self.current_annotations = []
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
                        self.current_annotations.append({
                            'class_id': class_id,
                            'x_center': x_center,
                            'y_center': y_center,
                            'width': width,
                            'height': height
                        })
        
        # İlk annotation'ı seç
        if self.current_annotations:
            self.selected_annotation = 0
        else:
            self.selected_annotation = -1

    def save_annotations(self, frame_idx):
        """Annotation'ları kaydet"""
        if frame_idx >= len(self.frame_files):
            return
            
        frame_path = self.frame_files[frame_idx]
        frame_name = frame_path.stem
        label_file = self.labels_dir / f"{frame_name}.txt"
        
        with open(label_file, 'w') as f:
            for ann in self.current_annotations:
                f.write(f"{ann['class_id']} {ann['x_center']:.6f} {ann['y_center']:.6f} {ann['width']:.6f} {ann['height']:.6f}\n")
        
        class_counts = {}
        for ann in self.current_annotations:
            class_name = self.classes[ann['class_id']]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        summary = " | ".join([f"{name}:{count}" for name, count in class_counts.items()])
        print(f"💾 Frame {frame_idx + 1} kaydedildi: {summary}")

    def draw_annotations(self):
        """Annotation'ları renkli olarak çiz"""
        if self.current_idx >= len(self.frame_files):
            return
            
        frame_path = self.frame_files[self.current_idx]
        self.original_image = cv2.imread(str(frame_path))
        
        if self.original_image is None:
            return
        
        h, w = self.original_image.shape[:2]
        self.display_image = self.original_image.copy()
        
        # Scaling hesapla
        if w > 1000:
            self.scale_factor = 1000 / w
            new_width = int(w * self.scale_factor)
            new_height = int(h * self.scale_factor)
            self.display_image = cv2.resize(self.display_image, (new_width, new_height))
        else:
            self.scale_factor = 1.0
        
        # Class sayılarını say
        class_counts = {}
        for ann in self.current_annotations:
            class_name = self.classes[ann['class_id']]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
                 # Mevcut annotation'ları çiz - SADECE RENKLER
        for i, ann in enumerate(self.current_annotations):
            class_id = ann['class_id']
            color = self.colors.get(class_id, (128, 128, 128))
            
            # YOLO koordinatlarını display koordinatlarına çevir
            x_center = ann['x_center'] * w * self.scale_factor
            y_center = ann['y_center'] * h * self.scale_factor
            box_width = ann['width'] * w * self.scale_factor
            box_height = ann['height'] * h * self.scale_factor
            
            x1 = int(x_center - box_width / 2)
            y1 = int(y_center - box_height / 2)
            x2 = int(x_center + box_width / 2)
            y2 = int(y_center + box_height / 2)
            
            # Seçili annotation çok kalın çerçeve
            thickness = 6 if i == self.selected_annotation else 3
            cv2.rectangle(self.display_image, (x1, y1), (x2, y2), color, thickness)
        
        # Çizilen kutu göster
        if self.drawing and self.start_point and self.end_point:
            cv2.rectangle(self.display_image, self.start_point, self.end_point, (255, 255, 255), 2)
            cv2.putText(self.display_image, "YENİ KUTU - Bırak", 
                       (self.start_point[0], self.start_point[1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
                 # RENK REHBERİ - ÜST KISIM
        legend_y = 25
        cv2.putText(self.display_image, "🟢 HAVUZDA YUZEN", (10, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(self.display_image, "🔴 BOGULAN", (200, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(self.display_image, "🔵 HAVUZ KENARI", (350, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(self.display_image, "🟡 EKIPMAN", (550, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Basit bilgi
        info_text = f"Frame {self.current_idx + 1}/{len(self.frame_files)} | Toplam: {len(self.current_annotations)}"
        cv2.putText(self.display_image, info_text, (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(self.display_image, info_text, (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        cv2.imshow('🎨 Renkli Editör', self.display_image)

    def mouse_callback(self, event, x, y, flags, param):
        """Mouse işlemleri"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            print(f"🖱️  Yeni kutu başlatıldı")
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
                self.draw_annotations()
                
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                self.end_point = (x, y)
                self.add_new_annotation()
                self.start_point = None
                self.end_point = None

    def add_new_annotation(self):
        """Yeni annotation ekle"""
        if not self.start_point or not self.end_point:
            return
            
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        
        # Minimum kutu boyutu kontrolü
        if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
            print("⚠️  Kutu çok küçük!")
            self.draw_annotations()
            return
        
        # Koordinatları düzelt
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        # Display koordinatlarını original image koordinatlarına çevir
        h, w = self.original_image.shape[:2]
        orig_x1 = x1 / self.scale_factor
        orig_y1 = y1 / self.scale_factor
        orig_x2 = x2 / self.scale_factor
        orig_y2 = y2 / self.scale_factor
        
        # YOLO formatına çevir
        x_center = (orig_x1 + orig_x2) / 2 / w
        y_center = (orig_y1 + orig_y2) / 2 / h
        width = (orig_x2 - orig_x1) / w
        height = (orig_y2 - orig_y1) / h
        
        # Geçici annotation ekle
        temp_annotation = {
            'class_id': 0,  # Varsayılan person_swimming
            'x_center': x_center,
            'y_center': y_center,
            'width': width,
            'height': height
        }
        
        self.current_annotations.append(temp_annotation)
        self.selected_annotation = len(self.current_annotations) - 1
        
        # OTOMATİK KAYDET
        self.save_annotations(self.current_idx)
        
        print(f"✅ Yeni kutu eklendi ve kaydedildi! Class için 1-4 tuşları")
        self.draw_annotations()

    def change_class(self, new_class_id):
        """Seçili annotation'ın class'ını değiştir"""
        if 0 <= self.selected_annotation < len(self.current_annotations):
            old_class = self.current_annotations[self.selected_annotation]['class_id']
            self.current_annotations[self.selected_annotation]['class_id'] = new_class_id
            print(f"🔄 Class değişti: {self.classes[old_class]} → {self.classes[new_class_id]}")
            self.draw_annotations()
        else:
            print("⚠️  Seçili annotation yok!")

    def delete_selected(self):
        """Seçili annotation'ı sil"""
        if 0 <= self.selected_annotation < len(self.current_annotations):
            deleted = self.current_annotations.pop(self.selected_annotation)
            print(f"🗑️  Annotation silindi")
            if self.selected_annotation >= len(self.current_annotations):
                self.selected_annotation = len(self.current_annotations) - 1
            self.draw_annotations()
        else:
            print("⚠️  Silinecek annotation yok!")

    def next_annotation(self):
        """Sonraki annotation'ı seç"""
        if self.current_annotations:
            self.selected_annotation = (self.selected_annotation + 1) % len(self.current_annotations)
            ann = self.current_annotations[self.selected_annotation]
            print(f"➡️  #{self.selected_annotation + 1}: {self.classes[ann['class_id']]}")
            self.draw_annotations()

    def prev_annotation(self):
        """Önceki annotation'ı seç"""
        if self.current_annotations:
            self.selected_annotation = (self.selected_annotation - 1) % len(self.current_annotations)
            ann = self.current_annotations[self.selected_annotation]
            print(f"⬅️  #{self.selected_annotation + 1}: {self.classes[ann['class_id']]}")
            self.draw_annotations()

    def run(self):
        """Ana döngü"""
        print("\n🎨 RENKLİ EDİTÖR")
        print("=" * 60)
        print("🟢 YEŞİL: person_swimming")
        print("🔴 KIRMIZI: person_drowning") 
        print("🔵 MAVİ: person_poolside")
        print("🟡 SARI: pool_equipment")
        print("=" * 60)
        print("🖱️  MOUSE: Drag ile yeni kutu çiz")
        print("⌨️  Q/W=Seç | 1-4=Class | S=Kaydet | DEL=Sil")
        print("⌨️  SPACE=Sonraki frame | A=Önceki frame | ESC=Çıkış")
        print("=" * 60)
        
        # İlk frame yükle
        self.load_annotations(self.current_idx)
        self.draw_annotations()
        
        # Mouse callback ayarla
        cv2.setMouseCallback('🎨 Renkli Editör', self.mouse_callback)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                break
            elif key == ord(' '):  # SPACE - Sonraki frame
                if self.current_idx < len(self.frame_files) - 1:
                    self.current_idx += 1
                    print(f"📄 Frame {self.current_idx + 1}")
                    self.load_annotations(self.current_idx)
                    self.draw_annotations()
                else:
                    print("📄 Son frame!")
            elif key == ord('a') or key == ord('A'):  # A - Önceki frame
                if self.current_idx > 0:
                    self.current_idx -= 1
                    print(f"📄 Frame {self.current_idx + 1}")
                    self.load_annotations(self.current_idx)
                    self.draw_annotations()
                else:
                    print("📄 İlk frame!")
            elif key == ord('q') or key == ord('Q'):  # Q - Sonraki annotation
                self.next_annotation()
            elif key == ord('w') or key == ord('W'):  # W - Önceki annotation
                self.prev_annotation()
            elif key == ord('s') or key == ord('S'):  # S - Kaydet
                self.save_annotations(self.current_idx)
            elif key == 127 or key == 8:  # DEL/Backspace - Sil
                self.delete_selected()
            elif key == ord('1'):  # 1 - person_swimming
                self.change_class(0)
            elif key == ord('2'):  # 2 - person_drowning
                self.change_class(1)
            elif key == ord('3'):  # 3 - person_poolside
                self.change_class(2)
            elif key == ord('4'):  # 4 - pool_equipment
                self.change_class(3)
        
        cv2.destroyAllWindows()
        print("👋 Editör kapatıldı!")

def main():
    frames_dir = "01_frames"
    labels_dir = "02_labels"
    classes_file = "classes.txt"
    
    editor = ColorEditor(frames_dir, labels_dir, classes_file)
    editor.run()

if __name__ == "__main__":
    main() 