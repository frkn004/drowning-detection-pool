#!/usr/bin/env python3
"""
🤖 YOLOV8X OTOMATIK ETİKETLEME - TÜM FRAMELER
============================================
5354 frame'i YOLOv8x ile otomatik etiketler
"""

import os
import sys
from pathlib import Path

def auto_label_all_frames():
    """Tüm frame'leri YOLOv8x ile otomatik etiketle"""
    
    try:
        from ultralytics import YOLO
        print("✅ YOLO import başarılı")
    except ImportError:
        print("❌ YOLO import hatası! pip install ultralytics gerekiyor")
        return False
    
    # Paths
    frames_dir = "../01_frames"
    labels_dir = "../02_labels"
    model_path = "../models/yolov8x.pt"
    
    print("🤖 YOLOV8X OTOMATIK ETİKETLEME BAŞLIYOR")
    print("=" * 60)
    print(f"📸 Frames: {frames_dir}")
    print(f"🏷️  Labels: {labels_dir}")
    print(f"🤖 Model: {model_path}")
    
    # Model kontrolü
    if not os.path.exists(model_path):
        print(f"❌ Model bulunamadı: {model_path}")
        return False
    
    # Model yükle
    print(f"🤖 YOLOv8x model yükleniyor...")
    model = YOLO(model_path)
    print(f"✅ Model yüklendi!")
    
    # Klasör oluştur
    os.makedirs(labels_dir, exist_ok=True)
    
    # Frame dosyalarını bul
    frame_files = []
    for ext in ['.jpg', '.jpeg', '.png']:
        frame_files.extend(list(Path(frames_dir).glob(f"*{ext}")))
    
    frame_files.sort()
    print(f"📸 {len(frame_files)} frame bulundu")
    
    if len(frame_files) == 0:
        print("❌ Frame bulunamadı!")
        return False
    
    total_detections = 0
    successful_frames = 0
    
    print(f"\n🔄 Otomatik etiketleme başlıyor...")
    
    # Her frame'i işle
    for i, frame_path in enumerate(frame_files, 1):
        
        # İlerleme göster
        if i % 100 == 0 or i == 1:
            progress = (i / len(frame_files)) * 100
            print(f"🔍 İşleniyor {i}/{len(frame_files)}: {progress:.1f}% - {frame_path.name}")
        
        # YOLO inference
        try:
            results = model(str(frame_path), conf=0.3, verbose=False)
        except Exception as e:
            print(f"❌ Model inference hatası {frame_path.name}: {e}")
            continue
        
        # Label dosya yolu
        label_file = os.path.join(labels_dir, frame_path.stem + '.txt')
        
        # Tespit edilen objeler
        detections = []
        frame_detections = 0
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Class ID
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Sadece person class'ı (0) al
                    if class_id == 0 and confidence > 0.3:
                        # Bounding box koordinatları (normalized)
                        x_center, y_center, width, height = box.xywhn[0]
                        
                        # YOLO format: class_id x_center y_center width height
                        # Varsayılan olarak person_swimming (0) ata
                        yolo_class = 0  # person_swimming
                        detection_line = f"{yolo_class} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                        detections.append(detection_line)
                        frame_detections += 1
                        total_detections += 1
        
        # Label dosyasını yaz
        with open(label_file, 'w') as f:
            if detections:
                f.write('\n'.join(detections))
            else:
                f.write('')  # Boş dosya oluştur
        
        if detections:
            successful_frames += 1
    
    print(f"\n🎉 Otomatik etiketleme tamamlandı!")
    print(f"   📊 İşlenen frame: {len(frame_files)}")
    print(f"   ✅ Etiketli frame: {successful_frames}")
    print(f"   🏷️  Toplam tespit: {total_detections}")
    print(f"   📁 Label klasörü: {labels_dir}")
    print(f"   📈 Ortalama tespit/frame: {total_detections/len(frame_files):.1f}")
    
    return True

def main():
    """Ana fonksiyon"""
    
    print("🤖 YOLOV8X OTOMATİK ETİKETLEME")
    print("=" * 60)
    
    # Auto labeling
    success = auto_label_all_frames()
    
    if success:
        print(f"\n✅ Otomatik etiketleme başarılı!")
        print(f"🔧 Sonraki adım: Advanced Editor ile etiketleri düzelt")
        print(f"   python advanced_editor.py")
        print(f"\n📋 ÖNEMLİ: Tüm etiketler 'person_swimming' olarak atandı")
        print(f"   Advanced Editor ile şunları düzelt:")
        print(f"   • Havuz dışındaki kişiler → person_poolside")
        print(f"   • Boğulma riski olan kişiler → person_drowning")
        print(f"   • Ekipmanlar → pool_equipment")
        print(f"   • Yanlış tespitleri sil")
    else:
        print("❌ Otomatik etiketleme başarısız!")
        return False
    
    return True

if __name__ == "__main__":
    main()



