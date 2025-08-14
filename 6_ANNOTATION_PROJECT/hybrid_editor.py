#!/usr/bin/env python3
"""
🎯 HİBRİT ETİKET EDİTÖRÜ
=========================
Mouse: Yeni annotation ekle
Klavye: Mevcut annotation'ları düzelt
"""

import cv2
import os
import json
import numpy as np
from pathlib import Path

class HybridEditor:
    def __init__(self, frames_dir, labels_dir, classes_file):
        self.frames_dir = frames_dir
        self.labels_dir = labels_dir
        
        # Classes yükle
        with open(classes_file, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        # Colors for each class
        self.colors = [
            (0, 255, 0),    # person_swimming - Yeşil
            (0, 0, 255),    # person_drowning - Kırmızı
            (255, 0, 0),    # person_poolside - Mavi
            (0, 255, 255)   # pool_equipment - Sarı
        ]
        
        self.current_frame_idx = 0
        self.frame_files = sorted(list(Path(frames_dir).glob("*.jpg")))
        self.current_annotations = []
        self.selected_annotation = 0
        self.scale_factor = 1.0
        self.original_image = None
        self.display_image = None
        
        # Mouse drawing state
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.temp_rect = None
        
        print(f"📋 Classes: {self.classes}")
        print(f"📸 {len(self.frame_files)} frame bulundu")
    
    def load_annotations(self, frame_idx):
        """Frame'in annotation'larını yükle"""
        frame_file = self.frame_files[frame_idx]
        label_file = Path(self.labels_dir) / f"{frame_file.stem}.txt"
        
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
        frame_file = self.frame_files[frame_idx]
        label_file = Path(self.labels_dir) / f"{frame_file.stem}.txt"
        
        with open(label_file, 'w') as f:
            for ann in self.current_annotations:
                f.write(f"{ann['class_id']} {ann['x_center']:.6f} {ann['y_center']:.6f} {ann['width']:.6f} {ann['height']:.6f}\n")
        
        # Class dağılımını göster
        class_counts = {}
        for ann in self.current_annotations:
            class_name = self.classes[ann['class_id']]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        summary = " | ".join([f"{name}:{count}" for name, count in class_counts.items()])
        print(f"💾 Frame {frame_idx + 1} kaydedildi: {summary} (Toplam:{len(self.current_annotations)})")
    
    def draw_annotations(self):
        """Annotation'ları çiz"""
        if self.current_frame_idx >= len(self.frame_files):
            return
        
        # Original image yükle
        self.original_image = cv2.imread(str(self.frame_files[self.current_frame_idx]))
        if self.original_image is None:
            return
        
        h, w = self.original_image.shape[:2]
        
        # Display image oluştur ve scale
        self.display_image = self.original_image.copy()
        if w > 1000:
            self.scale_factor = 1000 / w
            new_width = int(w * self.scale_factor)
            new_height = int(h * self.scale_factor)
            self.display_image = cv2.resize(self.display_image, (new_width, new_height))
        else:
            self.scale_factor = 1.0
        
        # Annotation'ları çiz
        for i, ann in enumerate(self.current_annotations):
            class_id = ann['class_id']
            
            # Original koordinatlara çevir
            orig_x = int((ann['x_center'] - ann['width']/2) * w)
            orig_y = int((ann['y_center'] - ann['height']/2) * h)
            orig_x2 = int((ann['x_center'] + ann['width']/2) * w)
            orig_y2 = int((ann['y_center'] + ann['height']/2) * h)
            
            # Scale edilmiş koordinatlara çevir
            x = int(orig_x * self.scale_factor)
            y = int(orig_y * self.scale_factor)
            x2 = int(orig_x2 * self.scale_factor)
            y2 = int(orig_y2 * self.scale_factor)
            
            # Renk ve kalınlık
            color = self.colors[class_id] if class_id < len(self.colors) else (128, 128, 128)
            thickness = 4 if i == self.selected_annotation else 2
            
            # Kutu çiz
            cv2.rectangle(self.display_image, (x, y), (x2, y2), color, thickness)
            
            # Label
            label = f"{i+1}: {self.classes[class_id]}"
            if i == self.selected_annotation:
                label = f">>> {label} <<<"
            
            # Label background
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(self.display_image, (x, y - label_size[1] - 10), (x + label_size[0], y), color, -1)
            
            # Label text
            cv2.putText(self.display_image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Çizilen geçici kutu (mouse ile)
        if self.drawing and self.start_point and self.end_point:
            cv2.rectangle(self.display_image, self.start_point, self.end_point, (255, 255, 255), 2)
            # Çizme bilgisi
            cv2.putText(self.display_image, "Yeni kutu - Mouse'u birak", 
                       (self.start_point[0], self.start_point[1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Header bilgisi
        header_height = 120
        header = np.zeros((header_height, self.display_image.shape[1], 3), dtype=np.uint8)
        header[:] = (40, 40, 40)
        
        # Frame bilgisi
        frame_text = f"FRAME {self.current_frame_idx + 1}/{len(self.frame_files)}"
        cv2.putText(header, frame_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Annotation bilgisi
        ann_text = f"Annotations: {len(self.current_annotations)}"
        cv2.putText(header, ann_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        
        if self.current_annotations and self.selected_annotation >= 0:
            selected_ann = self.current_annotations[self.selected_annotation]
            selected_text = f"SELECTED: #{self.selected_annotation + 1} - {self.classes[selected_ann['class_id']]}"
            cv2.putText(header, selected_text, (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        # Controls
        controls1 = "MOUSE: Drag=Yeni kutu (Class sorar) | Q/W=Select 1-4=Class B=Drowning S=Save"
        controls2 = "SPACE=Next A/D=Prev/Next DEL=Delete ESC=Exit"
        cv2.putText(header, controls1, (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(header, controls2, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Combine header and image
        final_image = np.vstack([header, self.display_image])
        
        cv2.imshow('Hybrid Editor', final_image)
    
    def mouse_callback(self, event, x, y, flags, param):
        """Mouse callback - yeni annotation ekleme"""
        
        # Header alanını atla
        header_height = 120
        if y < header_height:
            return
        
        # Display image koordinatları
        display_y = y - header_height
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Çizim başlat
            self.drawing = True
            self.start_point = (x, display_y)
            self.end_point = (x, display_y)
            print(f"🖱️  Kutu başlatıldı")
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, display_y)
                self.draw_annotations()  # Gerçek zamanlı güncelleme
        
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                self.end_point = (x, display_y)
                
                # Yeni annotation ekle
                self.add_new_annotation()
                
                # Reset
                self.start_point = None
                self.end_point = None
    
    def add_new_annotation(self):
        """Mouse ile çizilen kutuyu annotation olarak ekle"""
        if not self.start_point or not self.end_point:
            return
        
        # Koordinatları düzenle
        x1 = min(self.start_point[0], self.end_point[0])
        y1 = min(self.start_point[1], self.end_point[1])
        x2 = max(self.start_point[0], self.end_point[0])
        y2 = max(self.start_point[1], self.end_point[1])
        
        # Çok küçük kutular kabul etme
        if (x2 - x1) < 20 or (y2 - y1) < 20:
            print("⚠️  Kutu çok küçük! (min 20x20 pixel)")
            return
        
        # Original image boyutları
        h, w = self.original_image.shape[:2]
        
        # Display koordinatlarını original koordinatlara çevir
        orig_x1 = int(x1 / self.scale_factor)
        orig_y1 = int(y1 / self.scale_factor)
        orig_x2 = int(x2 / self.scale_factor)
        orig_y2 = int(y2 / self.scale_factor)
        
        # YOLO formatına çevir
        x_center = (orig_x1 + orig_x2) / 2 / w
        y_center = (orig_y1 + orig_y2) / 2 / h
        width = (orig_x2 - orig_x1) / w
        height = (orig_y2 - orig_y1) / h
        
        # CLASS SEÇİMİ - Kullanıcıya sor
        print(f"\n🎯 Class seç: 1:Swimming 2:DROWNING 3:Poolside 4:Equipment (ENTER=Swimming)")
        
        # Geçici annotation ekle (görsel olarak göster)
        temp_annotation = {
            'class_id': 0,  # Temporary
            'x_center': x_center,
            'y_center': y_center,
            'width': width,
            'height': height
        }
        
        self.current_annotations.append(temp_annotation)
        self.selected_annotation = len(self.current_annotations) - 1
        self.draw_annotations()
        
        # Kullanıcıdan class seçimini bekle
        while True:
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('1'):
                chosen_class = 0
                class_name = "person_swimming"
                break
            elif key == ord('2'):
                chosen_class = 1
                class_name = "person_drowning"
                break
            elif key == ord('3'):
                chosen_class = 2
                class_name = "person_poolside"
                break
            elif key == ord('4'):
                chosen_class = 3
                class_name = "pool_equipment"
                break
            elif key == 13:  # ENTER - default swimming
                chosen_class = 0
                class_name = "person_swimming"
                break
            elif key == 27:  # ESC - iptal
                print("❌ İptal edildi")
                self.current_annotations.pop()  # Son eklenen annotation'ı sil
                if self.current_annotations:
                    self.selected_annotation = len(self.current_annotations) - 1
                else:
                    self.selected_annotation = -1
                self.draw_annotations()
                return
        
        # Seçilen class'ı ata
        self.current_annotations[self.selected_annotation]['class_id'] = chosen_class
        
        print(f"✅ #{len(self.current_annotations)}: {class_name} eklendi")
        
        self.draw_annotations()
    
    def change_class(self, new_class_id):
        """Seçili annotation'ın class'ını değiştir"""
        if self.selected_annotation >= 0 and self.selected_annotation < len(self.current_annotations):
            old_class = self.current_annotations[self.selected_annotation]['class_id']
            self.current_annotations[self.selected_annotation]['class_id'] = new_class_id
            
            print(f"🔄 #{self.selected_annotation + 1}: {self.classes[old_class]} → {self.classes[new_class_id]}")
            
            self.draw_annotations()
        else:
            print(f"⚠️  Seçili annotation yok!")
    
    def delete_selected(self):
        """Seçili annotation'ı sil"""
        if self.selected_annotation >= 0 and self.selected_annotation < len(self.current_annotations):
            deleted = self.current_annotations.pop(self.selected_annotation)
            print(f"🗑️  #{self.selected_annotation + 1} silindi (Kalan: {len(self.current_annotations)})")
            
            # Seçimi ayarla
            if self.current_annotations:
                self.selected_annotation = min(self.selected_annotation, len(self.current_annotations) - 1)
            else:
                self.selected_annotation = -1
            
            self.draw_annotations()
        else:
            print(f"⚠️  Silinecek annotation yok!")
    
    def next_annotation(self):
        """Sonraki annotation'ı seç"""
        if self.current_annotations:
            self.selected_annotation = (self.selected_annotation + 1) % len(self.current_annotations)
            ann = self.current_annotations[self.selected_annotation]
            print(f"➡️  #{self.selected_annotation + 1}/{len(self.current_annotations)}: {self.classes[ann['class_id']]}")
            self.draw_annotations()
    
    def prev_annotation(self):
        """Önceki annotation'ı seç"""
        if self.current_annotations:
            self.selected_annotation = (self.selected_annotation - 1) % len(self.current_annotations)
            ann = self.current_annotations[self.selected_annotation]
            print(f"⬅️  #{self.selected_annotation + 1}/{len(self.current_annotations)}: {self.classes[ann['class_id']]}")
            self.draw_annotations()
    
    def print_status(self):
        """Mevcut durumu yazdır"""
        if self.current_annotations:
            # Class dağılımı
            class_counts = {}
            for ann in self.current_annotations:
                class_name = self.classes[ann['class_id']]
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            summary = " | ".join([f"{name}:{count}" for name, count in class_counts.items()])
            selected_class = self.classes[self.current_annotations[self.selected_annotation]['class_id']] if self.selected_annotation >= 0 else "None"
            print(f"📊 Frame {self.current_frame_idx + 1}/{len(self.frame_files)} | {summary} | Seçili:#{self.selected_annotation + 1}({selected_class})")
        else:
            print(f"📊 Frame {self.current_frame_idx + 1}/{len(self.frame_files)} | Annotation yok")
    
    def run(self):
        """Ana döngü"""
        if not self.frame_files:
            print("❌ Frame bulunamadı!")
            return
        
        cv2.namedWindow('Hybrid Editor', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('Hybrid Editor', self.mouse_callback)
        
        print("\n🎯 HİBRİT EDİTÖR - TEMİZ VERSİYON")
        print("=" * 60)
        print("🖱️ MOUSE: Drag=Yeni kutu | ⌨️ KLAVYE: Q/W=Seç 1-4=Class B=Drowning S=Kaydet")
        print("SPACE=Sonraki A/D=Önceki/Sonraki DEL=Sil ESC=Çıkış")
        print("=" * 60)
        
        # İlk frame yükle
        self.load_annotations(self.current_frame_idx)
        self.draw_annotations()
        self.print_status()
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                break
            
            elif key == ord(' '):  # SPACE - Next frame
                self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frame_files)
                print(f"📄 Frame {self.current_frame_idx + 1}")
                self.load_annotations(self.current_frame_idx)
                self.draw_annotations()
                self.print_status()
            
            elif key == ord('a') or key == ord('A'):  # A - Previous frame
                self.current_frame_idx = (self.current_frame_idx - 1) % len(self.frame_files)
                print(f"📄 Frame {self.current_frame_idx + 1}")
                self.load_annotations(self.current_frame_idx)
                self.draw_annotations()
                self.print_status()
            
            elif key == ord('d') or key == ord('D'):  # D - Next frame
                self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frame_files)
                print(f"📄 Frame {self.current_frame_idx + 1}")
                self.load_annotations(self.current_frame_idx)
                self.draw_annotations()
                self.print_status()
            
            elif key == ord('q') or key == ord('Q'):  # Q - Previous annotation
                self.prev_annotation()
            
            elif key == ord('w') or key == ord('W'):  # W - Next annotation
                self.next_annotation()
            
            elif key == ord('s') or key == ord('S'):  # S - Save
                self.save_annotations(self.current_frame_idx)
            
            elif key == ord('i') or key == ord('I'):  # I - Info
                self.print_status()
            
            elif key == 8 or key == 127:  # DELETE/BACKSPACE
                self.delete_selected()
            
            elif key == ord('1'):  # person_swimming
                self.change_class(0)
            
            elif key == ord('2'):  # person_drowning
                self.change_class(1)
            
            elif key == ord('3'):  # person_poolside
                self.change_class(2)
            
            elif key == ord('4'):  # pool_equipment
                self.change_class(3)
            
            elif key == ord('b') or key == ord('B'):  # B - Quick drowning
                self.change_class(1)
        
        cv2.destroyAllWindows()
        print("\n👋 Editing tamamlandı!")

def main():
    """Ana fonksiyon"""
    
    frames_dir = "01_frames"
    labels_dir = "02_labels"
    classes_file = "classes.txt"
    
    print("🎯 Hibrit Editör")
    print("=" * 50)
    
    editor = HybridEditor(frames_dir, labels_dir, classes_file)
    editor.run()

if __name__ == "__main__":
    main() 