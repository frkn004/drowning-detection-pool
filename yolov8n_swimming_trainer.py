#!/usr/bin/env python3
"""
🏊 YOLOv8n SWIMMING DETECTION TRAINER
====================================
Hızlı ve verimli yüzme tespiti için YOLOv8n fine-tuning
"""

from ultralytics import YOLO
import os
import time
import yaml

def create_dataset_yaml():
    """Dataset konfigürasyon dosyası oluştur"""
    
    dataset_config = {
        'path': '5_TİCKET_DATA',
        'train': '01_frames',
        'val': '01_frames',  # Validation için aynı dataset (demo)
        'nc': 4,  # Sınıf sayısı
        'names': [
            'person_swimming',
            'person_drowning', 
            'person_poolside',
            'pool_equipment'
        ]
    }
    
    with open('swimming_dataset.yaml', 'w') as f:
        yaml.dump(dataset_config, f)
    
    print("✅ Dataset YAML oluşturuldu: swimming_dataset.yaml")
    return 'swimming_dataset.yaml'

def train_fast_swimming_model():
    """Hızlı yüzme tespiti modeli eğit"""
    
    print("🚀 YOLOv8n Swimming Detection Training Başlıyor...")
    print("="*60)
    
    # Dataset yaml oluştur
    dataset_yaml = create_dataset_yaml()
    
    # YOLOv8n modelini yükle
    print("📦 YOLOv8n base model yükleniyor...")
    model = YOLO('4_MODELS/yolov8n.pt')
    
    # Training parametreleri
    training_params = {
        'data': dataset_yaml,
        'epochs': 50,                # Kısa eğitim
        'imgsz': 640,               # Standard YOLO size
        'batch': 8,                 # Küçük batch (memory efficient)
        'learning_rate': 0.001,     # Düşük learning rate
        'save_period': 10,          # Her 10 epoch'ta kaydet
        'patience': 15,             # Early stopping
        'device': 'cpu',            # CPU training (GPU yoksa)
        'project': 'swimming_training',
        'name': 'yolov8n_swimming_v1'
    }
    
    print(f"🎯 Training Parametreleri:")
    for key, value in training_params.items():
        print(f"   {key}: {value}")
    
    print("\n⏰ Training başlatılıyor... (Bu 30-60 dakika sürebilir)")
    
    try:
        # Model eğitimi
        start_time = time.time()
        results = model.train(**training_params)
        end_time = time.time()
        
        training_duration = end_time - start_time
        print(f"\n✅ Training tamamlandı!")
        print(f"⏰ Süre: {training_duration/60:.1f} dakika")
        
        # En iyi modeli test et
        best_model_path = f"swimming_training/yolov8n_swimming_v1/weights/best.pt"
        if os.path.exists(best_model_path):
            print(f"💾 En iyi model: {best_model_path}")
            
            # Hızlı performans testi
            test_performance(best_model_path)
        else:
            print("⚠️ En iyi model dosyası bulunamadı")
        
        return best_model_path
        
    except Exception as e:
        print(f"❌ Training hatası: {e}")
        return None

def test_performance(model_path):
    """Eğitilmiş modelin performansını test et"""
    
    print(f"\n🧪 Model Performance Testi: {os.path.basename(model_path)}")
    print("-"*50)
    
    try:
        import cv2
        
        # Model yükle
        model = YOLO(model_path)
        
        # Test görüntüsü
        test_img_path = '5_TİCKET_DATA/01_frames/frame_001_0.0s.jpg'
        img = cv2.imread(test_img_path)
        
        if img is None:
            print("❌ Test görüntüsü bulunamadı")
            return
        
        # Resize to 640x640
        img_resized = cv2.resize(img, (640, 640))
        
        # 5 test yap
        times = []
        for i in range(5):
            start = time.time()
            results = model(img_resized, conf=0.3, verbose=False)
            end = time.time()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        fps = 1 / avg_time
        
        # Sonuçları göster
        print(f"⏱️ Ortalama inference time: {avg_time*1000:.1f}ms")
        print(f"🚀 FPS: {fps:.1f}")
        
        if fps >= 15:
            print("✅ MÜKEMMEL! Real-time ready!")
        elif fps >= 10:
            print("🟢 İYİ! Near real-time")
        elif fps >= 5:
            print("🟡 ORTA! Kullanılabilir")
        else:
            print("🔴 YAVAŞ! Daha fazla optimization gerekli")
        
        # Detection sonuçları
        detection_count = len(results[0].boxes) if results[0].boxes else 0
        print(f"🎯 Tespit sayısı: {detection_count}")
        
        if results[0].boxes is not None:
            print("🏊 Tespit detayları:")
            for box in results[0].boxes:
                cls = int(box.cls.item())
                conf = float(box.conf.item())
                class_name = model.names[cls]
                print(f"   • {class_name}: {conf:.3f}")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")

def quick_baseline_comparison():
    """Hızlı baseline karşılaştırması"""
    
    print("\n📊 BASELINE KARŞILAŞTIRMA")
    print("="*40)
    
    models_to_compare = [
        ('4_MODELS/yolov8n.pt', 'YOLOv8n Original'),
        ('drowning_detection_v12_working.pt', 'Mevcut Özel Model')
    ]
    
    import cv2
    
    # Test görüntüsü
    test_img_path = '5_TİCKET_DATA/01_frames/frame_001_0.0s.jpg'
    img = cv2.imread(test_img_path)
    img_640 = cv2.resize(img, (640, 640))
    
    for model_path, model_name in models_to_compare:
        try:
            print(f"\n🧪 {model_name}:")
            
            model = YOLO(model_path)
            
            # Timing test
            start = time.time()
            if 'yolov8n' in model_path:
                results = model(img_640, conf=0.3, classes=[0], verbose=False)
            else:
                results = model(img_640, conf=0.3, verbose=False)
            end = time.time()
            
            fps = 1 / (end - start)
            detection_count = len(results[0].boxes) if results[0].boxes else 0
            
            print(f"   🚀 FPS: {fps:.1f}")
            print(f"   🎯 Tespit: {detection_count}")
            
        except Exception as e:
            print(f"   ❌ Hata: {e}")

if __name__ == "__main__":
    print("🏊 YOLOv8n Swimming Detection Trainer")
    print("="*50)
    
    # Önce baseline karşılaştırma
    quick_baseline_comparison()
    
    # Kullanıcıya sor
    print("\n🤔 YOLOv8n fine-tuning yapmak ister misiniz?")
    print("   Bu işlem 30-60 dakika sürecek.")
    print("   Devam etmek için 'y', iptal için herhangi bir tuş:")
    
    choice = input().lower().strip()
    
    if choice == 'y' or choice == 'yes':
        trained_model = train_fast_swimming_model()
        
        if trained_model:
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Yeni model eğitildi: {trained_model}")
            print("🚀 Bu model çok daha hızlı olacak!")
        else:
            print("\n❌ Training başarısız oldu")
    else:
        print("⏹️ Training iptal edildi")
        print("💡 YOLOv8n original model 14 FPS veriyor - şimdilik bunu kullanabilirsiniz!")



