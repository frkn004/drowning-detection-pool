#!/usr/bin/env python3
"""
📊 DATASET PREPARATION SCRIPT
============================
5_TİCKET_DATA klasöründen eğitim dataset'ini hazırlar
"""

import os
import shutil
import random
from pathlib import Path
from collections import defaultdict, Counter

class DatasetPreparer:
    def __init__(self, source_dir="5_TİCKET_DATA", target_dir="8_TRAINING/dataset"):
        """
        Dataset Preparer
        
        Args:
            source_dir: Kaynak etiketlenmiş data klasörü
            target_dir: Hedef dataset klasörü
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
        # Kaynak klasörler
        self.frames_dir = self.source_dir / "01_frames"
        self.labels_dir = self.source_dir / "02_labels"
        self.classes_file = self.source_dir / "classes.txt"
        
        # Hedef klasörler
        self.train_images = self.target_dir / "images" / "train"
        self.train_labels = self.target_dir / "labels" / "train"
        self.val_images = self.target_dir / "images" / "val"
        self.val_labels = self.target_dir / "labels" / "val"
        
        self.classes = self.load_classes()
        
    def load_classes(self):
        """Sınıfları yükle"""
        if self.classes_file.exists():
            with open(self.classes_file, 'r') as f:
                return [line.strip() for line in f.readlines()]
        else:
            # Default classes
            return ["person_swimming", "person_drowning", "person_poolside", "pool_equipment"]
    
    def analyze_dataset(self):
        """Dataset analizini yap"""
        print("🔍 Dataset analizi...")
        
        # Frame sayısı
        if self.frames_dir.exists():
            frames = list(self.frames_dir.glob("*.jpg"))
            print(f"📸 Toplam frame: {len(frames)}")
        else:
            print(f"❌ Frame klasörü bulunamadı: {self.frames_dir}")
            return False
            
        # Label sayısı ve dağılımı
        if self.labels_dir.exists():
            labels = list(self.labels_dir.glob("*.txt"))
            print(f"🏷️ Toplam label dosyası: {len(labels)}")
            
            # Sınıf dağılımını analiz et
            class_counts = Counter()
            total_annotations = 0
            
            for label_file in labels:
                with open(label_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            if 0 <= class_id < len(self.classes):
                                class_counts[self.classes[class_id]] += 1
                                total_annotations += 1
            
            print(f"📊 Toplam annotation: {total_annotations}")
            print("📈 Sınıf dağılımı:")
            for class_name in self.classes:
                count = class_counts.get(class_name, 0)
                percentage = (count / total_annotations * 100) if total_annotations > 0 else 0
                print(f"   {class_name}: {count} ({percentage:.1f}%)")
                
        else:
            print(f"❌ Label klasörü bulunamadı: {self.labels_dir}")
            return False
            
        return True
    
    def create_directories(self):
        """Hedef klasörleri oluştur"""
        print("📁 Klasör yapısı oluşturuluyor...")
        
        directories = [
            self.train_images, self.train_labels,
            self.val_images, self.val_labels
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {directory}")
    
    def get_valid_pairs(self):
        """Geçerli frame-label çiftlerini bul"""
        print("🔍 Geçerli frame-label çiftleri bulunuyor...")
        
        frames = set(f.stem for f in self.frames_dir.glob("*.jpg"))
        labels = set(f.stem for f in self.labels_dir.glob("*.txt"))
        
        # Ortak dosyalar
        valid_pairs = frames.intersection(labels)
        
        print(f"📸 Frame dosyaları: {len(frames)}")
        print(f"🏷️ Label dosyaları: {len(labels)}")
        print(f"✅ Geçerli çiftler: {len(valid_pairs)}")
        
        if len(valid_pairs) == 0:
            print("❌ Geçerli çift bulunamadı!")
            return []
            
        return list(valid_pairs)
    
    def split_dataset(self, valid_pairs, val_split=0.2, phase="all"):
        """
        Dataset'i train/val olarak böl
        
        Args:
            valid_pairs: Geçerli dosya çiftleri
            val_split: Validation oranı (0.2 = %20)
            phase: Hangi phase (phase1=200, phase2=500, etc.)
        """
        print(f"📊 Dataset bölünüyor... (val_split: {val_split})")
        
        # Phase'e göre dosya sayısını sınırla
        phase_limits = {
            "phase1": 200,
            "phase2": 500, 
            "phase3": 1000,
            "phase4": 1500,
            "all": len(valid_pairs)
        }
        
        limit = phase_limits.get(phase, len(valid_pairs))
        if len(valid_pairs) > limit:
            # En kaliteli frame'leri seç (dosya boyutuna göre)
            frame_sizes = []
            for pair in valid_pairs:
                frame_path = self.frames_dir / f"{pair}.jpg"
                if frame_path.exists():
                    size = frame_path.stat().st_size
                    frame_sizes.append((pair, size))
            
            # Büyükten küçüğe sırala (daha kaliteli)
            frame_sizes.sort(key=lambda x: x[1], reverse=True)
            valid_pairs = [pair for pair, _ in frame_sizes[:limit]]
            print(f"🎯 {phase} için en kaliteli {limit} frame seçildi")
        
        # Karıştır
        random.shuffle(valid_pairs)
        
        # Train/val split
        val_size = int(len(valid_pairs) * val_split)
        train_pairs = valid_pairs[val_size:]
        val_pairs = valid_pairs[:val_size]
        
        print(f"🚂 Train set: {len(train_pairs)} dosya")
        print(f"✅ Validation set: {len(val_pairs)} dosya")
        
        return train_pairs, val_pairs
    
    def copy_files(self, pairs, target_images_dir, target_labels_dir, set_name):
        """Dosyaları hedef klasöre kopyala"""
        print(f"📋 {set_name} dosyaları kopyalanıyor...")
        
        success_count = 0
        
        for pair in pairs:
            # Frame kopyala
            source_frame = self.frames_dir / f"{pair}.jpg"
            target_frame = target_images_dir / f"{pair}.jpg"
            
            # Label kopyala
            source_label = self.labels_dir / f"{pair}.txt"
            target_label = target_labels_dir / f"{pair}.txt"
            
            try:
                shutil.copy2(source_frame, target_frame)
                shutil.copy2(source_label, target_label)
                success_count += 1
            except Exception as e:
                print(f"⚠️ Hata {pair}: {e}")
        
        print(f"✅ {set_name}: {success_count}/{len(pairs)} dosya kopyalandı")
        return success_count
    
    def prepare_dataset(self, phase="phase1", val_split=0.2):
        """
        Dataset'i hazırla
        
        Args:
            phase: Eğitim fazı
            val_split: Validation split oranı
        """
        print(f"🚀 DATASET HAZIRLIĞI - {phase.upper()}")
        print("=" * 50)
        
        # Analiz
        if not self.analyze_dataset():
            return False
        
        # Klasörler oluştur
        self.create_directories()
        
        # Geçerli çiftleri bul
        valid_pairs = self.get_valid_pairs()
        if not valid_pairs:
            return False
        
        # Train/val split
        train_pairs, val_pairs = self.split_dataset(valid_pairs, val_split, phase)
        
        # Dosyaları kopyala
        train_success = self.copy_files(train_pairs, self.train_images, self.train_labels, "TRAIN")
        val_success = self.copy_files(val_pairs, self.val_images, self.val_labels, "VALIDATION")
        
        # Classes dosyasını kopyala
        target_classes = self.target_dir / "classes.txt"
        shutil.copy2(self.classes_file, target_classes)
        print(f"📋 Classes kopyalandı: {target_classes}")
        
        print(f"\n✅ DATASET HAZIRLIĞI TAMAMLANDI!")
        print(f"📊 Train: {train_success} dosya")
        print(f"📊 Validation: {val_success} dosya")
        print(f"📁 Hedef klasör: {self.target_dir}")
        
        return True

def main():
    """Ana dataset hazırlama fonksiyonu"""
    print("📊 DROWNING DETECTION DATASET PREPARER")
    print("======================================")
    
    phases = {
        '1': 'phase1',  # 200 frame
        '2': 'phase2',  # 500 frame
        '3': 'phase3',  # 1000 frame
        '4': 'phase4',  # 1500 frame
        'a': 'all'      # Tüm frameler
    }
    
    print("📊 Dataset hazırlama seçenekleri:")
    print("   1. Phase 1: Mini Dataset (200 frame)")
    print("   2. Phase 2: Extended Dataset (500 frame)")
    print("   3. Phase 3: Production Dataset (1000 frame)")
    print("   4. Phase 4: Final Dataset (1500 frame)")
    print("   a. All: Tüm Dataset")
    
    try:
        choice = input("\nHangi dataset'i hazırlamak istiyorsunuz? (1-4/a): ").strip()
        phase = phases.get(choice)
        
        if not phase:
            print("❌ Geçersiz seçim!")
            return
        
        val_split = float(input("Validation split oranı (0.2 = %20): ") or "0.2")
        
        # Dataset preparer oluştur
        preparer = DatasetPreparer()
        success = preparer.prepare_dataset(phase, val_split)
        
        if success:
            print(f"\n🎉 {phase.upper()} dataset hazırlığı başarılı!")
        else:
            print(f"\n❌ {phase.upper()} dataset hazırlığı başarısız!")
            
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

if __name__ == "__main__":
    main()