#!/usr/bin/env python3
"""
🎮 BASİT KLAVYE ETİKET EDİTÖRÜ
===============================
Mouse problemi yok! Sadece klavye ile kontrol.
"""

import cv2
import os
import json
import numpy as np
from pathlib import Path

class SimpleKeyboardEditor:
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
        self.selected_annotation = 0  # İlk annotation seçili
        self.scale_factor = 1.0
        
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
        
        print(f"\n💾 FRAME {frame_idx + 1} KAYDEDİLDİ:")
        print(f"   📝 Toplam annotation: {len(self.current_annotations)}")
        for class_name, count in class_counts.items():
            print(f"   🏷️  {class_name}: {count}")
    
    def draw_annotations(self):
        """Annotation'ları çiz"""
        if self.current_frame_idx >= len(self.frame_files):
            return
        
        # Frame yükle
        image = cv2.imread(str(self.frame_files[self.current_frame_idx]))
        if image is None:
            return
        
        h, w = image.shape[:2]
        
        # Scale
        if w > 1000:
            self.scale_factor = 1000 / w
            new_width = int(w * self.scale_factor)
            new_height = int(h * self.scale_factor)
            image = cv2.resize(image, (new_width, new_height))
        else:
            self.scale_factor = 1.0
        
        # Annotation'ları çiz
        for i, ann in enumerate(self.current_annotations):
            class_id = ann['class_id']
            
            # Pixel koordinatlarına çevir
            orig_x = int((ann['x_center'] - ann['width']/2) * w)
            orig_y = int((ann['y_center'] - ann['height']/2) * h)
            orig_x2 = int((ann['x_center'] + ann['width']/2) * w)
            orig_y2 = int((ann['y_center'] + ann['height']/2) * h)
            
            # Scale uygula
            x = int(orig_x * self.scale_factor)
            y = int(orig_y * self.scale_factor)
            x2 = int(orig_x2 * self.scale_factor)
            y2 = int(orig_y2 * self.scale_factor)
            
            # Renk ve kalınlık
            color = self.colors[class_id] if class_id < len(self.colors) else (128, 128, 128)
            thickness = 4 if i == self.selected_annotation else 2
            
            # Kutu çiz
            cv2.rectangle(image, (x, y), (x2, y2), color, thickness)
            
            # Label
            label = f"{i+1}: {self.classes[class_id]}"
            if i == self.selected_annotation:
                label = f">>> {label} <<<"
            
            # Label background
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(image, (x, y - label_size[1] - 10), (x + label_size[0], y), color, -1)
            
            # Label text
            cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Header bilgisi
        header_height = 100
        header = np.zeros((header_height, image.shape[1], 3), dtype=np.uint8)
        header[:] = (40, 40, 40)
        
        # Frame bilgisi
        frame_text = f"FRAME {self.current_frame_idx + 1}/{len(self.frame_files)}"
        cv2.putText(header, frame_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Annotation bilgisi
        if self.current_annotations and self.selected_annotation >= 0:
            selected_ann = self.current_annotations[self.selected_annotation]
            selected_text = f"SELECTED: #{self.selected_annotation + 1} - {self.classes[selected_ann['class_id']]}"
            cv2.putText(header, selected_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Controls
            controls = "Q/W:Select | 1-4:Class | B:Drowning | S:Save | SPACE:Next | ESC:Exit"
            cv2.putText(header, controls, (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            no_ann_text = f"No annotations or none selected. Total: {len(self.current_annotations)}"
            cv2.putText(header, no_ann_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
            
            controls = "SPACE:Next | ESC:Exit"
            cv2.putText(header, controls, (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Combine header and image
        final_image = np.vstack([header, image])
        
        cv2.imshow('Simple Keyboard Editor', final_image)
    
    def change_class(self, new_class_id):
        """Seçili annotation'ın class'ını değiştir"""
        if self.selected_annotation >= 0 and self.selected_annotation < len(self.current_annotations):
            old_class = self.current_annotations[self.selected_annotation]['class_id']
            self.current_annotations[self.selected_annotation]['class_id'] = new_class_id
            
            print(f"\n🔄 CLASS DEĞİŞTİRİLDİ:")
            print(f"   📍 Annotation #{self.selected_annotation + 1}")
            print(f"   🔄 {self.classes[old_class]} → {self.classes[new_class_id]}")
            print(f"   💾 Kaydetmek için 'S' tuşuna bas")
            
            self.draw_annotations()
        else:
            print(f"\n⚠️  Seçili annotation yok!")
    
    def delete_selected(self):
        """Seçili annotation'ı sil"""
        if self.selected_annotation >= 0 and self.selected_annotation < len(self.current_annotations):
            deleted = self.current_annotations.pop(self.selected_annotation)
            print(f"\n🗑️  ANNOTATİON SİLİNDİ:")
            print(f"   🏷️  Class: {self.classes[deleted['class_id']]}")
            print(f"   📝 Kalan: {len(self.current_annotations)}")
            
            # Seçimi ayarla
            if self.current_annotations:
                self.selected_annotation = min(self.selected_annotation, len(self.current_annotations) - 1)
            else:
                self.selected_annotation = -1
            
            self.draw_annotations()
        else:
            print(f"\n⚠️  Silinecek annotation yok!")
    
    def next_annotation(self):
        """Sonraki annotation'ı seç"""
        if self.current_annotations:
            self.selected_annotation = (self.selected_annotation + 1) % len(self.current_annotations)
            ann = self.current_annotations[self.selected_annotation]
            print(f"\n➡️  SEÇİM DEĞİŞTİ:")
            print(f"   📍 Annotation #{self.selected_annotation + 1}/{len(self.current_annotations)}")
            print(f"   🏷️  Class: {self.classes[ann['class_id']]}")
            self.draw_annotations()
    
    def prev_annotation(self):
        """Önceki annotation'ı seç"""
        if self.current_annotations:
            self.selected_annotation = (self.selected_annotation - 1) % len(self.current_annotations)
            ann = self.current_annotations[self.selected_annotation]
            print(f"\n⬅️  SEÇİM DEĞİŞTİ:")
            print(f"   📍 Annotation #{self.selected_annotation + 1}/{len(self.current_annotations)}")
            print(f"   🏷️  Class: {self.classes[ann['class_id']]}")
            self.draw_annotations()
    
    def print_status(self):
        """Mevcut durumu yazdır"""
        print(f"\n📊 DURUM RAPORU:")
        print(f"   📸 Frame: {self.current_frame_idx + 1}/{len(self.frame_files)}")
        print(f"   📝 Toplam annotation: {len(self.current_annotations)}")
        
        if self.current_annotations:
            print(f"   🎯 Seçili: #{self.selected_annotation + 1}")
            
            # Class dağılımı
            class_counts = {}
            for ann in self.current_annotations:
                class_name = self.classes[ann['class_id']]
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            for class_name, count in class_counts.items():
                print(f"   🏷️  {class_name}: {count}")
    
    def run(self):
        """Ana döngü"""
        if not self.frame_files:
            print("❌ Frame bulunamadı!")
            return
        
        cv2.namedWindow('Simple Keyboard Editor', cv2.WINDOW_AUTOSIZE)
        
        print("\n🎮 BASİT KLAVYE EDİTÖRÜ")
        print("=" * 60)
        print("📍 ANNOTATION SEÇİMİ:")
        print("   Q: Önceki annotation | W: Sonraki annotation")
        print("")
        print("🏷️ CLASS DEĞİŞTİRME:")
        print("   1: person_swimming | 2: person_drowning ⚠️")
        print("   3: person_poolside | 4: pool_equipment")
        print("   B: Hızlı drowning (Seçili annotation'ı drowning yap)")
        print("")
        print("🎮 KONTROLLER:")
        print("   SPACE: Sonraki frame | A/D: Önceki/Sonraki frame")
        print("   S: Kaydet | DEL: Sil | I: Durum bilgisi")
        print("   ESC: Çıkış")
        print("=" * 60)
        
        while True:
            # Mevcut frame'i yükle
            self.load_annotations(self.current_frame_idx)
            self.draw_annotations()
            self.print_status()
            
            key = cv2.waitKey(0) & 0xFF
            
            if key == 27:  # ESC
                break
            
            elif key == ord(' '):  # SPACE - Next frame
                old_frame = self.current_frame_idx + 1
                self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frame_files)
                new_frame = self.current_frame_idx + 1
                print(f"\n➡️  Frame {old_frame} → {new_frame}")
            
            elif key == ord('a') or key == ord('A'):  # A - Previous frame
                old_frame = self.current_frame_idx + 1
                self.current_frame_idx = (self.current_frame_idx - 1) % len(self.frame_files)
                new_frame = self.current_frame_idx + 1
                print(f"\n⬅️  Frame {old_frame} → {new_frame}")
            
            elif key == ord('d') or key == ord('D'):  # D - Next frame
                old_frame = self.current_frame_idx + 1
                self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frame_files)
                new_frame = self.current_frame_idx + 1
                print(f"\n➡️  Frame {old_frame} → {new_frame}")
            
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
    
    print("🎮 Basit Klavye Editörü")
    print("=" * 50)
    
    editor = SimpleKeyboardEditor(frames_dir, labels_dir, classes_file)
    editor.run()

if __name__ == "__main__":
    main() 