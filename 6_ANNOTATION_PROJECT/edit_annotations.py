#!/usr/bin/env python3
"""
✏️ MANUEL ETIKET DÜZELTME ARACI
================================
Hatalı etiketleri el ile düzelt:
- Class değiştir (person_swimming → person_poolside)
- Etiket sil
- Yeni etiket ekle
"""

import cv2
import os
import json
import numpy as np
from pathlib import Path

class ManualAnnotationEditor:
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
        self.selected_annotation = -1
        self.scale_factor = 1.0
        self.display_image = None
        self.original_image = None
        
        # Mouse state
        self.drawing_box = False
        self.start_point = None
        self.end_point = None
        
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
        print(f"   📁 Dosya: {label_file.name}")
    
    def draw_annotations(self):
        """Annotation'ları çiz"""
        if self.original_image is None:
            return
        
        # Original image kopyala
        self.display_image = self.original_image.copy()
        h, w = self.original_image.shape[:2]
        
        # Scale factor hesapla
        if w > 1200:
            self.scale_factor = 1200 / w
            new_width = int(w * self.scale_factor)
            new_height = int(h * self.scale_factor)
            self.display_image = cv2.resize(self.display_image, (new_width, new_height))
        else:
            self.scale_factor = 1.0
        
        # Mevcut annotation'ları çiz (scale edilmiş koordinatlarda)
        for i, ann in enumerate(self.current_annotations):
            class_id = ann['class_id']
            x_center = ann['x_center']
            y_center = ann['y_center']
            width = ann['width']
            height = ann['height']
            
            # Original pixel koordinatlarına çevir, sonra scale uygula
            orig_x = int((x_center - width/2) * w)
            orig_y = int((y_center - height/2) * h)
            orig_x2 = int((x_center + width/2) * w)
            orig_y2 = int((y_center + height/2) * h)
            
            # Scale edilmiş koordinatlara çevir
            x = int(orig_x * self.scale_factor)
            y = int(orig_y * self.scale_factor)
            x2 = int(orig_x2 * self.scale_factor)
            y2 = int(orig_y2 * self.scale_factor)
            
            # Renk seç
            color = self.colors[class_id] if class_id < len(self.colors) else (128, 128, 128)
            thickness = 3 if i == self.selected_annotation else 2
            
            # Kutu çiz
            cv2.rectangle(self.display_image, (x, y), (x2, y2), color, thickness)
            
            # Label çiz
            label = f"{i+1}: {self.classes[class_id]}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Label background
            cv2.rectangle(self.display_image, 
                         (x, y - label_size[1] - 10), 
                         (x + label_size[0], y), 
                         color, -1)
            
            # Label text
            cv2.putText(self.display_image, label, 
                       (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Yeni kutu çiziyor musun? (Scale edilmiş koordinatlarda)
        if self.drawing_box and self.start_point and self.end_point:
            scaled_start = (int(self.start_point[0] * self.scale_factor), 
                           int(self.start_point[1] * self.scale_factor))
            scaled_end = (int(self.end_point[0] * self.scale_factor), 
                         int(self.end_point[1] * self.scale_factor))
            cv2.rectangle(self.display_image, scaled_start, scaled_end, (255, 255, 255), 2)
        
        # Header - Frame bilgisi
        header_bg = np.zeros((120, self.display_image.shape[1], 3), dtype=np.uint8)
        header_bg[:] = (50, 50, 50)
        
        # Frame numarası büyük yazı
        frame_text = f"FRAME {self.current_frame_idx + 1}/{len(self.frame_files)}"
        cv2.putText(header_bg, frame_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Annotation sayısı
        ann_text = f"Annotations: {len(self.current_annotations)}"
        cv2.putText(header_bg, ann_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Seçili annotation bilgisi
        if self.selected_annotation >= 0 and self.selected_annotation < len(self.current_annotations):
            selected_ann = self.current_annotations[self.selected_annotation]
            selected_text = f"SELECTED: #{self.selected_annotation + 1} - {self.classes[selected_ann['class_id']]}"
            cv2.putText(header_bg, selected_text, (300, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Class değiştirme bilgisi
            class_text = "1:Swimming 2:DROWNING 3:Poolside 4:Equipment B:Quick-Drowning"
            cv2.putText(header_bg, class_text, (300, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Seçim bilgisi
            select_text = "Select: 5-9 keys or click annotation"
            cv2.putText(header_bg, select_text, (300, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        else:
            no_selection_text = "Press 5-9 to select annotation by number OR click annotation"
            cv2.putText(header_bg, no_selection_text, (300, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
        
        # Controls
        controls = [
            "SPACE: Next | A/D: Prev/Next | S: Save | DEL: Delete | B: Quick-Drowning | ESC: Exit",
        ]
        
        cv2.putText(header_bg, controls[0], (10, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Header'ı ana resme ekle
        self.display_image = np.vstack([header_bg, self.display_image])
        
        cv2.imshow('Manual Annotation Editor', self.display_image)
    
    def mouse_callback(self, event, x, y, flags, param):
        """Mouse olayları"""
        if self.original_image is None:
            return
        
        # Header yüksekliğini çıkar (120 pixel)
        header_height = 120
        if y < header_height:
            return  # Header alanında tıklama ignore et
        
        display_y = y - header_height
        
        # Koordinatları original boyuta çevir
        orig_x = int(x / self.scale_factor)
        orig_y = int(display_y / self.scale_factor)
        h, w = self.original_image.shape[:2]
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Mevcut annotation'ı seç
            print(f"🖱️  Tıklanan nokta: ({orig_x}, {orig_y}) - Image boyutu: {w}x{h}")
            clicked_annotation = self.find_clicked_annotation(orig_x, orig_y, w, h)
            print(f"🎯 Bulunan annotation index: {clicked_annotation}")
            if clicked_annotation >= 0:
                self.selected_annotation = clicked_annotation
                ann = self.current_annotations[clicked_annotation]
                print(f"\n🎯 ANNOTATİON SEÇİLDİ:")
                print(f"   📍 Annotation #{clicked_annotation + 1}")
                print(f"   🏷️  Class: {self.classes[ann['class_id']]}")
                print(f"   📐 Konum: center({ann['x_center']:.3f}, {ann['y_center']:.3f})")
                print(f"   📏 Boyut: {ann['width']:.3f} x {ann['height']:.3f}")
                print(f"   ⌨️  Class değiştirmek için 1-4 tuşlarını kullan")
            else:
                # Yeni kutu çizmeye başla
                self.drawing_box = True
                self.start_point = (orig_x, orig_y)
                self.selected_annotation = -1
                print(f"\n🖱️  Yeni kutu başlatıldı: ({orig_x}, {orig_y})")
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing_box:
                self.end_point = (orig_x, orig_y)
        
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing_box:
                self.drawing_box = False
                if self.start_point and self.end_point:
                    print(f"🖱️  Kutu tamamlandı: {self.start_point} → {self.end_point}")
                    self.add_new_annotation(self.start_point, self.end_point, w, h)
                self.start_point = None
                self.end_point = None
        
        self.draw_annotations()
    
    def find_clicked_annotation(self, x, y, w, h):
        """Tıklanan annotation'ı bul"""
        for i, ann in enumerate(self.current_annotations):
            # Original pixel koordinatlarına çevir
            orig_x1 = int((ann['x_center'] - ann['width']/2) * w)
            orig_y1 = int((ann['y_center'] - ann['height']/2) * h)
            orig_x2 = int((ann['x_center'] + ann['width']/2) * w)
            orig_y2 = int((ann['y_center'] + ann['height']/2) * h)
            
            # Tıklanan nokta annotation alanında mı?
            if orig_x1 <= x <= orig_x2 and orig_y1 <= y <= orig_y2:
                return i
        
        return -1
    
    def add_new_annotation(self, start, end, w, h):
        """Yeni annotation ekle"""
        x1, y1 = start
        x2, y2 = end
        
        # Sıralama
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        # Çok küçük kutular kabul etme
        if (x2 - x1) < 20 or (y2 - y1) < 20:
            print("⚠️  Kutu çok küçük!")
            return
        
        # YOLO formatına çevir
        x_center = (x1 + x2) / 2 / w
        y_center = (y1 + y2) / 2 / h
        width = (x2 - x1) / w
        height = (y2 - y1) / h
        
        # Yeni annotation ekle (default: person_swimming)
        new_annotation = {
            'class_id': 0,
            'x_center': x_center,
            'y_center': y_center,
            'width': width,
            'height': height
        }
        
        self.current_annotations.append(new_annotation)
        self.selected_annotation = len(self.current_annotations) - 1
        print(f"\n✅ YENİ ANNOTATİON EKLENDİ:")
        print(f"   📍 Annotation #{len(self.current_annotations)}")
        print(f"   🏷️  Class: {self.classes[new_annotation['class_id']]} (default)")
        print(f"   📏 Boyut: {new_annotation['width']:.3f} x {new_annotation['height']:.3f}")
        print(f"   ⌨️  Class değiştirmek için 1-4 tuşlarını kullan")
    
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
            print(f"\n⚠️  Önce bir annotation seç! (Tıkla)")
            print(f"   📝 Mevcut annotation sayısı: {len(self.current_annotations)}")
    
    def delete_selected(self):
        """Seçili annotation'ı sil"""
        if self.selected_annotation >= 0 and self.selected_annotation < len(self.current_annotations):
            deleted = self.current_annotations.pop(self.selected_annotation)
            print(f"\n🗑️  ANNOTATİON SİLİNDİ:")
            print(f"   📍 Annotation #{self.selected_annotation + 1}")
            print(f"   🏷️  Class: {self.classes[deleted['class_id']]}")
            print(f"   📝 Kalan annotation sayısı: {len(self.current_annotations)}")
            print(f"   💾 Kaydetmek için 'S' tuşuna bas")
            self.selected_annotation = -1
            self.draw_annotations()
        else:
            print(f"\n⚠️  Silinecek annotation seçilmedi!")
            print(f"   📝 Mevcut annotation sayısı: {len(self.current_annotations)}")
    
    def run(self):
        """Ana döngü"""
        if not self.frame_files:
            print("❌ Frame bulunamadı!")
            return
        
        cv2.namedWindow('Manual Annotation Editor', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('Manual Annotation Editor', self.mouse_callback)
        
        print("\n✏️ MANUEL ETIKET DÜZELTME")
        print("=" * 70)
        print("📍 ANNOTATION SEÇME:")
        print("   🖱️  Mouse: Annotation üzerine tıkla")
        print("   ⌨️  5-9 tuşları: Annotation numarasına göre seç (5=1.annotation, 6=2.annotation...)")
        print("")
        print("🏷️ CLASS DEĞİŞTİRME:")
        print("   ⌨️  1: person_swimming (Yüzüyor)")
        print("   ⌨️  2: person_drowning (Boğuluyor) ⚠️")
        print("   ⌨️  3: person_poolside (Havuz kenarında)")
        print("   ⌨️  4: pool_equipment (Ekipman)")
        print("   ⌨️  B: Hızlı drowning (Seçili annotation'ı drowning yap)")
        print("")
        print("🎮 KONTROLLER:")
        print("   ⌨️  S: Kaydet | DEL: Sil | SPACE: Sonraki frame | A/D: Önceki/Sonraki | ESC: Çıkış")
        print("=" * 70)
        
        while True:
            # Mevcut frame'i yükle
            self.original_image = cv2.imread(str(self.frame_files[self.current_frame_idx]))
            self.load_annotations(self.current_frame_idx)
            self.draw_annotations()
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                break
            
            elif key == ord(' '):  # SPACE - Next frame
                old_frame = self.current_frame_idx + 1
                self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frame_files)
                new_frame = self.current_frame_idx + 1
                self.selected_annotation = -1
                print(f"\n➡️  Frame {old_frame} → {new_frame}")
            
            elif key == ord('a') or key == ord('A'):  # A - Previous frame
                old_frame = self.current_frame_idx + 1
                self.current_frame_idx = (self.current_frame_idx - 1) % len(self.frame_files)
                new_frame = self.current_frame_idx + 1
                self.selected_annotation = -1
                print(f"\n⬅️  Frame {old_frame} → {new_frame}")
            
            elif key == ord('d') or key == ord('D'):  # D - Next frame
                old_frame = self.current_frame_idx + 1
                self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frame_files)
                new_frame = self.current_frame_idx + 1
                self.selected_annotation = -1
                print(f"\n➡️  Frame {old_frame} → {new_frame}")
            
            elif key == ord('s') or key == ord('S'):  # S - Save
                self.save_annotations(self.current_frame_idx)
            
            elif key == ord('r') or key == ord('R'):  # R - Reset selection
                self.selected_annotation = -1
                self.draw_annotations()
            
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
            
            # Annotation ID ile seçim (5-9 tuşları)
            elif key >= ord('5') and key <= ord('9'):  # 5-9 arası annotation seç
                annotation_id = key - ord('5')  # 5 → 0, 6 → 1, etc.
                if annotation_id < len(self.current_annotations):
                    self.selected_annotation = annotation_id
                    ann = self.current_annotations[annotation_id]
                    print(f"\n⌨️  KLAVYE İLE SEÇİLDİ:")
                    print(f"   📍 Annotation #{annotation_id + 1}")
                    print(f"   🏷️  Class: {self.classes[ann['class_id']]}")
                    print(f"   ⌨️  Class değiştirmek için 1-4 tuşlarını kullan")
                    self.draw_annotations()
                else:
                    print(f"\n⚠️  Annotation #{annotation_id + 1} bulunamadı!")
                    print(f"   📝 Toplam annotation sayısı: {len(self.current_annotations)}")
            
            # Otomatik drowning ataması için 'B' tuşu
            elif key == ord('b') or key == ord('B'):  # B - Boğulma
                if self.selected_annotation >= 0:
                    self.change_class(1)  # person_drowning
                else:
                    print(f"\n⚠️  Önce bir annotation seç!")
                    print(f"   ⌨️  5-9 tuşları ile annotation seç veya mouse ile tıkla")
        
        cv2.destroyAllWindows()
        print("👋 Manuel düzeltme tamamlandı!")

def main():
    """Ana fonksiyon"""
    
    frames_dir = "01_frames"
    labels_dir = "02_labels"
    classes_file = "classes.txt"
    
    print("✏️ Manuel Annotation Düzeltme Aracı")
    print("=" * 50)
    
    editor = ManualAnnotationEditor(frames_dir, labels_dir, classes_file)
    editor.run()

if __name__ == "__main__":
    main() 