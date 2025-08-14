import cv2
import os
import numpy as np
from pathlib import Path

class AdvancedEditor:
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
        self.header_height = 100  # Büyük header için
        
        # İstatistikler
        self.total_annotations = 0
        self.session_start_frame = 0

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
        
        print(f"💾 Frame {frame_idx + 1} kaydedildi")

    def draw_advanced_header(self):
        """Gelişmiş header çiz"""
        header = np.zeros((self.header_height, self.display_image.shape[1], 3), dtype=np.uint8)
        header.fill(45)  # Koyu gri arka plan
        
        # İlerleme çubuğu
        progress = (self.current_idx + 1) / len(self.frame_files)
        bar_width = self.display_image.shape[1] - 40
        bar_height = 20
        bar_x = 20
        bar_y = 10
        
        # İlerleme çubuğu arka plan (gri)
        cv2.rectangle(header, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (70, 70, 70), -1)
        
        # İlerleme çubuğu (mavi)
        progress_width = int(bar_width * progress)
        cv2.rectangle(header, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), (255, 140, 0), -1)
        
        # İlerleme metni
        progress_text = f"Frame {self.current_idx + 1}/{len(self.frame_files)} ({progress*100:.1f}%)"
        cv2.putText(header, progress_text, (bar_x, bar_y + bar_height + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Renk rehberi - ikinci satır
        legend_y = 50
        cv2.putText(header, "RENKLER:", (20, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Renk kutuları ve açıklamalar
        colors_info = [
            ("HAVUZDA", (0, 255, 0), 100),
            ("BOGULAN", (0, 0, 255), 200),
            ("KENAR", (255, 0, 0), 290),
            ("EKIPMAN", (0, 255, 255), 360)
        ]
        
        for text, color, x_pos in colors_info:
            # Renk kutusu
            cv2.rectangle(header, (x_pos, legend_y - 15), (x_pos + 15, legend_y), color, -1)
            cv2.rectangle(header, (x_pos, legend_y - 15), (x_pos + 15, legend_y), (255, 255, 255), 1)
            # Açıklama
            cv2.putText(header, text, (x_pos + 20, legend_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # İstatistikler - üçüncü satır
        stats_y = 75
        total_in_frame = len(self.current_annotations)
        
        # Class sayıları
        class_counts = {}
        for ann in self.current_annotations:
            class_name = self.classes[ann['class_id']]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        stats_text = f"Bu Frame: {total_in_frame} etiket"
        if class_counts:
            counts_text = " | ".join([f"{name.split('_')[1] if '_' in name else name}:{count}" 
                                    for name, count in class_counts.items()])
            stats_text += f" ({counts_text})"
        
        cv2.putText(header, stats_text, (20, stats_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Seçili annotation bilgisi
        if 0 <= self.selected_annotation < len(self.current_annotations):
            selected_class = self.classes[self.current_annotations[self.selected_annotation]['class_id']]
            selected_text = f"Secili: #{self.selected_annotation + 1} ({selected_class.split('_')[1] if '_' in selected_class else selected_class})"
            cv2.putText(header, selected_text, (300, stats_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Kontroller - en alt
        controls_y = 95
        controls = "SOL DRAG: Yeni | SAG CLICK: Sec | 1-4: Class | DEL/TAB: Sil | SPACE/D/A: Frame"
        cv2.putText(header, controls, (20, controls_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
        
        return header

    def draw_annotations(self):
        """Annotation'ları çiz"""
        if self.current_idx >= len(self.frame_files):
            return
            
        frame_path = self.frame_files[self.current_idx]
        self.original_image = cv2.imread(str(frame_path))
        
        if self.original_image is None:
            return
        
        h, w = self.original_image.shape[:2]
        self.display_image = self.original_image.copy()
        
        # Scaling hesapla
        max_width = 1200
        if w > max_width:
            self.scale_factor = max_width / w
            new_width = int(w * self.scale_factor)
            new_height = int(h * self.scale_factor)
            self.display_image = cv2.resize(self.display_image, (new_width, new_height))
        else:
            self.scale_factor = 1.0
        
        # Annotation'ları çiz - SADECE RENKLER
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
            
            # Seçili annotation çok kalın çerçeve + glow effect
            if i == self.selected_annotation:
                # Glow effect (büyük, şeffaf)
                cv2.rectangle(self.display_image, (x1-3, y1-3), (x2+3, y2+3), color, 2)
                # Ana çerçeve
                cv2.rectangle(self.display_image, (x1, y1), (x2, y2), color, 4)
                # Köşe noktaları
                cv2.circle(self.display_image, (x1, y1), 5, color, -1)
                cv2.circle(self.display_image, (x2, y2), 5, color, -1)
                cv2.circle(self.display_image, (x1, y2), 5, color, -1)
                cv2.circle(self.display_image, (x2, y1), 5, color, -1)
            else:
                cv2.rectangle(self.display_image, (x1, y1), (x2, y2), color, 2)
        
        # Çizilen kutu göster
        if self.drawing and self.start_point and self.end_point:
            cv2.rectangle(self.display_image, self.start_point, self.end_point, (255, 255, 255), 3)
            cv2.putText(self.display_image, "YENI KUTU", 
                       (self.start_point[0], self.start_point[1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Header ekle
        header = self.draw_advanced_header()
        final_image = np.vstack([header, self.display_image])
        
        cv2.imshow('🚀 Gelişmiş Editör', final_image)

    def find_clicked_annotation(self, x, y):
        """Tıklanan yerdeki annotation'ı bul"""
        # Header yüksekliğini çıkar
        display_y = y - self.header_height
        if display_y < 0:
            return -1
            
        h, w = self.original_image.shape[:2]
        
        for i, ann in enumerate(self.current_annotations):
            # YOLO koordinatlarını display koordinatlarına çevir
            x_center = ann['x_center'] * w * self.scale_factor
            y_center = ann['y_center'] * h * self.scale_factor
            box_width = ann['width'] * w * self.scale_factor
            box_height = ann['height'] * h * self.scale_factor
            
            x1 = int(x_center - box_width / 2)
            y1 = int(y_center - box_height / 2)
            x2 = int(x_center + box_width / 2)
            y2 = int(y_center + box_height / 2)
            
            # Tıklama bu kutu içinde mi?
            if x1 <= x <= x2 and y1 <= display_y <= y2:
                return i
        
        return -1

    def mouse_callback(self, event, x, y, flags, param):
        """Mouse işlemleri - Sol drag: yeni kutu, Sağ click: seç"""
        # Header alanında ise işlem yapma
        if y < self.header_height:
            return
            
        display_y = y - self.header_height
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Sol click - yeni kutu çizmeye başla
            self.drawing = True
            self.start_point = (x, display_y)
            self.end_point = (x, display_y)
            print(f"🖱️  Yeni kutu çiziliyor...")
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, display_y)
                self.draw_annotations()
                
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                self.end_point = (x, display_y)
                self.add_new_annotation()
                self.start_point = None
                self.end_point = None
                
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Sağ click - annotation seç
            clicked_annotation = self.find_clicked_annotation(x, y)
            if clicked_annotation >= 0:
                self.selected_annotation = clicked_annotation
                ann = self.current_annotations[clicked_annotation]
                class_name = self.classes[ann['class_id']]
                print(f"👆 #{clicked_annotation + 1} seçildi: {class_name}")
                self.draw_annotations()
            else:
                print("📍 Hiçbir etiket seçilmedi")

    def add_new_annotation(self):
        """Yeni annotation ekle"""
        if not self.start_point or not self.end_point:
            return
            
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        
        # Minimum kutu boyutu kontrolü
        if abs(x2 - x1) < 15 or abs(y2 - y1) < 15:
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
        
        # Yeni annotation ekle
        new_annotation = {
            'class_id': 0,  # Varsayılan person_swimming
            'x_center': x_center,
            'y_center': y_center,
            'width': width,
            'height': height
        }
        
        self.current_annotations.append(new_annotation)
        self.selected_annotation = len(self.current_annotations) - 1
        
        # OTOMATİK KAYDET
        self.save_annotations(self.current_idx)
        
        print(f"✅ Yeni etiket eklendi ve kaydedildi!")
        self.draw_annotations()

    def change_class(self, new_class_id):
        """Seçili annotation'ın class'ını değiştir"""
        if 0 <= self.selected_annotation < len(self.current_annotations):
            old_class = self.current_annotations[self.selected_annotation]['class_id']
            self.current_annotations[self.selected_annotation]['class_id'] = new_class_id
            old_name = self.classes[old_class].split('_')[1] if '_' in self.classes[old_class] else self.classes[old_class]
            new_name = self.classes[new_class_id].split('_')[1] if '_' in self.classes[new_class_id] else self.classes[new_class_id]
            print(f"🔄 Class: {old_name} → {new_name}")
            self.save_annotations(self.current_idx)  # Otomatik kaydet
            self.draw_annotations()
        else:
            print("⚠️  Önce bir etiket seç!")

    def delete_selected(self):
        """Seçili annotation'ı sil"""
        if 0 <= self.selected_annotation < len(self.current_annotations):
            self.current_annotations.pop(self.selected_annotation)
            print(f"🗑️  Etiket silindi")
            if self.selected_annotation >= len(self.current_annotations):
                self.selected_annotation = len(self.current_annotations) - 1
            self.save_annotations(self.current_idx)  # Otomatik kaydet
            self.draw_annotations()
        else:
            print("⚠️  Silinecek etiket yok!")

    def next_annotation(self):
        """Sonraki annotation'ı seç"""
        if self.current_annotations:
            self.selected_annotation = (self.selected_annotation + 1) % len(self.current_annotations)
            ann = self.current_annotations[self.selected_annotation]
            class_name = self.classes[ann['class_id']].split('_')[1] if '_' in self.classes[ann['class_id']] else self.classes[ann['class_id']]
            print(f"➡️  #{self.selected_annotation + 1}: {class_name}")
            self.draw_annotations()

    def prev_annotation(self):
        """Önceki annotation'ı seç"""
        if self.current_annotations:
            self.selected_annotation = (self.selected_annotation - 1) % len(self.current_annotations)
            ann = self.current_annotations[self.selected_annotation]
            class_name = self.classes[ann['class_id']].split('_')[1] if '_' in self.classes[ann['class_id']] else self.classes[ann['class_id']]
            print(f"⬅️  #{self.selected_annotation + 1}: {class_name}")
            self.draw_annotations()

    def run(self):
        """Ana döngü"""
        print("\n🚀 GELİŞMİŞ EDİTÖR")
        print("=" * 60)
        print("🖱️  SOL DRAG: Yeni etiket çiz")
        print("🖱️  SAĞ CLICK: Etiket seç")
        print("⌨️  1-4: Class değiştir | Q/W: Etiket seç")
        print("⌨️  SPACE/D: Sonraki frame | A: Önceki frame")
        print("⌨️  DEL/TAB: Sil | ESC: Çıkış")
        print("=" * 60)
        
        # İlk frame yükle
        self.session_start_frame = self.current_idx
        self.load_annotations(self.current_idx)
        self.draw_annotations()
        
        # Mouse callback ayarla
        cv2.setMouseCallback('🚀 Gelişmiş Editör', self.mouse_callback)
        
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
            elif key == ord('d') or key == ord('D'):  # D - Sonraki frame
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
            elif key == 127 or key == 8 or key == 9:  # DEL/Backspace/TAB - Sil
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
        print("👋 Gelişmiş editör kapatıldı!")

def main():
    frames_dir = "01_frames"
    labels_dir = "02_labels"
    classes_file = "classes.txt"
    
    editor = AdvancedEditor(frames_dir, labels_dir, classes_file)
    editor.run()

if __name__ == "__main__":
    main() 