#!/usr/bin/env python3
"""
🤖 OTOMATİK TESPİT + ETİKET OLUŞTURMA
====================================
Mevcut YOLO modeli ile framelerde kişi tespiti yapıp
YOLO format etiketler oluşturur.
"""

import cv2
import os
import sys
from pathlib import Path

def auto_detect_and_create_labels(frames_dir, labels_dir, model_path=None):
    """
    Framelerde otomatik tespit yapıp YOLO format etiketler oluştur
    
    Args:
        frames_dir: Frame'lerin bulunduğu klasör
        labels_dir: Etiket dosyalarının kaydedileceği klasör  
        model_path: YOLO model yolu (None ise default)
    """
    
    try:
        from ultralytics import YOLO
        print("✅ YOLO import başarılı")
    except ImportError:
        print("❌ YOLO import hatası! pip install ultralytics gerekiyor")
        return False
    
    # Model yükle
    if model_path is None:
        # Mevcut en iyi modeli kullan
        available_models = []
        models_dir = "../MODELS"
        if os.path.exists(models_dir):
            for file in os.listdir(models_dir):
                if file.endswith('.pt'):
                    available_models.append(os.path.join(models_dir, file))
        
        if available_models:
            # Öncelik sırası
            preferred = ["yolov8x.pt", "yolov8m.pt", "yolo11l.pt"]
            model_path = None
            
            for pref in preferred:
                for model in available_models:
                    if pref in model:
                        model_path = model
                        break
                if model_path:
                    break
            
            if not model_path:
                model_path = available_models[0]
        else:
            model_path = "yolov8m.pt"  # Online download
    
    print(f"🤖 Model yükleniyor: {model_path}")
    model = YOLO(model_path)
    
    # Klasör oluştur
    os.makedirs(labels_dir, exist_ok=True)
    
    # Frame dosyalarını bul
    frame_files = []
    for ext in ['.jpg', '.jpeg', '.png']:
        frame_files.extend(list(Path(frames_dir).glob(f"*{ext}")))
    
    frame_files.sort()
    print(f"📸 {len(frame_files)} frame bulundu")
    
    # Class mapping - YOLO'dan bizim class'lara
    # YOLO class 0 = person → bizim class'larımıza map et
    class_mapping = {
        0: 0,  # person → person_swimming (default, sonra manuel düzeltiriz)
    }
    
    total_detections = 0
    
    # Her frame'i işle
    for i, frame_path in enumerate(frame_files, 1):
        print(f"🔍 İşleniyor {i}/{len(frame_files)}: {frame_path.name}")
        
        # YOLO inference
        results = model(str(frame_path), conf=0.3, verbose=False)
        
        # Label dosya yolu
        label_file = os.path.join(labels_dir, frame_path.stem + '.txt')
        
        # Tespit edilen objeler
        detections = []
        
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
                        yolo_class = 0  # person_swimming default
                        detection_line = f"{yolo_class} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                        detections.append(detection_line)
                        total_detections += 1
        
        # Label dosyasını yaz
        with open(label_file, 'w') as f:
            f.write('\n'.join(detections))
        
        if detections:
            print(f"   ✅ {len(detections)} kişi tespit edildi")
        else:
            print(f"   ⚠️  Kişi tespit edilmedi")
    
    print(f"\n🎉 Otomatik tespit tamamlandı!")
    print(f"   📊 Toplam tespit: {total_detections}")
    print(f"   📁 Etiket klasörü: {labels_dir}")
    print(f"\n🔧 Sonraki adım: LabelImg ile hataları düzelt")
    print(f"   labelImg {frames_dir} ../classes.txt")
    
    return True

def main():
    """Ana fonksiyon"""
    
    frames_dir = "01_frames"
    labels_dir = "02_labels"
    
    print("🤖 Otomatik Tespit Başlıyor...")
    print("=" * 50)
    
    # Auto detection
    success = auto_detect_and_create_labels(frames_dir, labels_dir)
    
    if success:
        print(f"\n📋 SONUÇ:")
        print(f"   ✅ Framelerdeki kişiler otomatik tespit edildi")
        print(f"   📄 YOLO format etiketler oluşturuldu")
        print(f"   🔧 Şimdi LabelImg ile hataları düzelt:")
        print(f"      - Havuz içi kişiler: person_swimming")  
        print(f"      - Havuz kenarı: person_poolside")
        print(f"      - Boğulma riski: person_drowning")
        print(f"      - Gözden kaçan kişileri ekle")
        print(f"      - Yanlış tespitleri sil")
    else:
        print("❌ Otomatik tespit başarısız!")

if __name__ == "__main__":
    main() 